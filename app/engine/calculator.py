from __future__ import annotations

from lunar_python import Lunar, Solar

from app.engine.constants import (
    CHEON_GAN_TO_OH_HAENG,
    CHEON_GAN_YIN_YANG,
    DI_SHI_HANJA_TO_KOR,
    HANJA_TO_KOR,
    SIP_SHIN_HANJA_TO_KOR,
)
from app.engine.models import DaYunInfo, PillarInfo, SajuData
from app.engine.night_zi import get_sect_value
from app.engine.summer_time import adjust_for_dst
from app.engine.true_solar_time import adjust_for_true_solar_time
from app.middleware.error_handler import (
    InvalidBirthDateError,
    LeapMonthError,
    LunarConversionError,
)


class SajuCalculator:
    """Core saju (four pillars) calculator wrapping lunar-python."""

    def calculate(
        self,
        year: int,
        month: int,
        day: int,
        hour: int | None = None,
        minute: int | None = None,
        *,
        gender_male: bool = True,
        calendar_type: str = "solar",
        is_leap_month: bool = False,
        use_night_zi: bool = True,
        use_true_solar_time: bool = False,
    ) -> SajuData:
        """Calculate complete saju data from birth information.

        Args:
            year: Birth year
            month: Birth month
            day: Birth day
            hour: Birth hour (0-23), None if unknown
            minute: Birth minute (0-59), None if unknown
            gender_male: True for male, False for female
            calendar_type: "solar" or "lunar"
            is_leap_month: True if lunar leap month
            use_night_zi: True to use night zi (야자시) approach

        Returns:
            Complete SajuData with four pillars and supplementary info
        """
        birth_time_unknown = hour is None
        if hour is None:
            hour = 12  # default to noon for calculation
        if minute is None:
            minute = 0

        solar = self._resolve_solar(
            year, month, day, hour, minute,
            calendar_type=calendar_type,
            is_leap_month=is_leap_month,
        )

        solar_year = solar.getYear()
        solar_month = solar.getMonth()
        solar_day = solar.getDay()

        # Apply Korean DST correction
        solar_year, solar_month, solar_day, hour, minute = adjust_for_dst(
            solar_year, solar_month, solar_day, hour, minute,
        )

        # Apply true solar time correction (after DST)
        if use_true_solar_time:
            solar_year, solar_month, solar_day, hour, minute = (
                adjust_for_true_solar_time(
                    solar_year, solar_month, solar_day, hour, minute,
                )
            )

        # Rebuild solar with corrected time
        solar = Solar(solar_year, solar_month, solar_day, hour, minute, 0)
        lunar = solar.getLunar()

        # Get eight characters
        eight_char = lunar.getEightChar()
        sect = get_sect_value(use_night_zi)
        eight_char.setSect(sect)

        # Build pillars
        year_pillar = self._build_pillar(eight_char, "Year")
        month_pillar = self._build_pillar(eight_char, "Month")
        day_pillar = self._build_pillar(eight_char, "Day")
        time_pillar = None if birth_time_unknown else self._build_pillar(eight_char, "Time")

        # Day master info
        day_master = eight_char.getDayGan()
        day_master_element = CHEON_GAN_TO_OH_HAENG.get(day_master, "")
        day_master_yin_yang = CHEON_GAN_YIN_YANG.get(day_master, "")

        # Extra info
        tai_yuan = eight_char.getTaiYuan()
        ming_gong = eight_char.getMingGong()
        shen_gong = eight_char.getShenGong()

        # Da Yun (major luck periods)
        yun = eight_char.getYun(1 if gender_male else 0)
        da_yun_start_age = yun.getStartYear()
        da_yun_raw = yun.getDaYun()

        da_yun_list = []
        for dy in da_yun_raw:
            gz = dy.getGanZhi()
            if gz:  # skip the first empty entry
                da_yun_list.append(DaYunInfo(
                    start_age=dy.getStartAge(),
                    start_year=dy.getStartYear(),
                    gan_zhi=gz,
                ))

        # Count five elements
        element_counts = self._count_elements(eight_char, birth_time_unknown)

        return SajuData(
            solar_year=solar_year,
            solar_month=solar_month,
            solar_day=solar_day,
            solar_hour=None if birth_time_unknown else hour,
            solar_minute=None if birth_time_unknown else minute,
            lunar_year=lunar.getYear(),
            lunar_month=lunar.getMonth(),
            lunar_day=lunar.getDay(),
            is_leap_month=is_leap_month,
            year_pillar=year_pillar,
            month_pillar=month_pillar,
            day_pillar=day_pillar,
            time_pillar=time_pillar,
            day_master=day_master,
            day_master_kor=HANJA_TO_KOR.get(day_master, day_master),
            day_master_element=day_master_element,
            day_master_yin_yang=day_master_yin_yang,
            tai_yuan=tai_yuan,
            tai_yuan_na_yin=eight_char.getTaiYuanNaYin(),
            ming_gong=ming_gong,
            ming_gong_na_yin=eight_char.getMingGongNaYin(),
            shen_gong=shen_gong,
            shen_gong_na_yin=eight_char.getShenGongNaYin(),
            da_yun_start_age=da_yun_start_age,
            da_yun_list=da_yun_list,
            element_counts=element_counts,
            used_night_zi=use_night_zi,
            used_true_solar_time=use_true_solar_time,
            birth_time_unknown=birth_time_unknown,
        )

    def _resolve_solar(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        *,
        calendar_type: str,
        is_leap_month: bool,
    ) -> Solar:
        """Convert input date to Solar, handling lunar conversion."""
        try:
            if calendar_type == "lunar":
                lunar_month = -month if is_leap_month else month
                try:
                    lunar = Lunar.fromYmd(year, lunar_month, day)
                except Exception as exc:
                    if is_leap_month:
                        raise LeapMonthError(
                            f"Year {year} month {month} does not have a leap month"
                        ) from exc
                    raise LunarConversionError(
                        f"Invalid lunar date: {year}-{month}-{day}"
                    ) from exc
                solar = lunar.getSolar()
                return Solar(
                    solar.getYear(), solar.getMonth(), solar.getDay(),
                    hour, minute, 0,
                )
            return Solar(year, month, day, hour, minute, 0)
        except (InvalidBirthDateError, LunarConversionError, LeapMonthError):
            raise
        except Exception as exc:
            raise InvalidBirthDateError(
                f"Invalid date: {year}-{month}-{day} {hour}:{minute}"
            ) from exc

    def _build_pillar(self, eight_char, position: str) -> PillarInfo:
        """Build a PillarInfo from an EightChar position."""
        getter = {
            "Year": {
                "gan": eight_char.getYearGan,
                "zhi": eight_char.getYearZhi,
                "wu_xing": eight_char.getYearWuXing,
                "na_yin": eight_char.getYearNaYin,
                "shi_shen_gan": eight_char.getYearShiShenGan,
                "shi_shen_zhi": eight_char.getYearShiShenZhi,
                "di_shi": eight_char.getYearDiShi,
                "hide_gan": eight_char.getYearHideGan,
            },
            "Month": {
                "gan": eight_char.getMonthGan,
                "zhi": eight_char.getMonthZhi,
                "wu_xing": eight_char.getMonthWuXing,
                "na_yin": eight_char.getMonthNaYin,
                "shi_shen_gan": eight_char.getMonthShiShenGan,
                "shi_shen_zhi": eight_char.getMonthShiShenZhi,
                "di_shi": eight_char.getMonthDiShi,
                "hide_gan": eight_char.getMonthHideGan,
            },
            "Day": {
                "gan": eight_char.getDayGan,
                "zhi": eight_char.getDayZhi,
                "wu_xing": eight_char.getDayWuXing,
                "na_yin": eight_char.getDayNaYin,
                "shi_shen_gan": eight_char.getDayShiShenGan,
                "shi_shen_zhi": eight_char.getDayShiShenZhi,
                "di_shi": eight_char.getDayDiShi,
                "hide_gan": eight_char.getDayHideGan,
            },
            "Time": {
                "gan": eight_char.getTimeGan,
                "zhi": eight_char.getTimeZhi,
                "wu_xing": eight_char.getTimeWuXing,
                "na_yin": eight_char.getTimeNaYin,
                "shi_shen_gan": eight_char.getTimeShiShenGan,
                "shi_shen_zhi": eight_char.getTimeShiShenZhi,
                "di_shi": eight_char.getTimeDiShi,
                "hide_gan": eight_char.getTimeHideGan,
            },
        }

        g = getter[position]
        gan = g["gan"]()
        zhi = g["zhi"]()
        shi_shen_zhi_raw = g["shi_shen_zhi"]()
        hide_gan_raw = g["hide_gan"]()

        return PillarInfo(
            gan=gan,
            zhi=zhi,
            gan_kor=HANJA_TO_KOR.get(gan, gan),
            zhi_kor=HANJA_TO_KOR.get(zhi, zhi),
            wu_xing=g["wu_xing"](),
            na_yin=g["na_yin"](),
            shi_shen_gan=SIP_SHIN_HANJA_TO_KOR.get(g["shi_shen_gan"](), g["shi_shen_gan"]()),
            shi_shen_zhi=[SIP_SHIN_HANJA_TO_KOR.get(s, s) for s in shi_shen_zhi_raw],
            di_shi=DI_SHI_HANJA_TO_KOR.get(g["di_shi"](), g["di_shi"]()),
            hide_gan=[HANJA_TO_KOR.get(h, h) for h in hide_gan_raw],
        )

    def _count_elements(self, eight_char, birth_time_unknown: bool) -> dict[str, int]:
        """Count occurrences of each element across all stems and branches."""
        counts: dict[str, int] = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}

        stems = [
            eight_char.getYearGan(),
            eight_char.getMonthGan(),
            eight_char.getDayGan(),
        ]
        branches = [
            eight_char.getYearZhi(),
            eight_char.getMonthZhi(),
            eight_char.getDayZhi(),
        ]

        if not birth_time_unknown:
            stems.append(eight_char.getTimeGan())
            branches.append(eight_char.getTimeZhi())

        for stem in stems:
            element = CHEON_GAN_TO_OH_HAENG.get(stem)
            if element:
                counts[element] += 1

        from app.engine.constants import JI_JI_TO_OH_HAENG

        for branch in branches:
            element = JI_JI_TO_OH_HAENG.get(branch)
            if element:
                counts[element] += 1

        return counts
