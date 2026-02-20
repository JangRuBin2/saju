from __future__ import annotations

from app.engine.models import SajuData


def format_saju_for_prompt(data: SajuData) -> str:
    """Format SajuData into a structured text block for LLM prompts."""
    lines = [
        f"생년월일: {data.solar_year}년 {data.solar_month}월 {data.solar_day}일 (양력)",
    ]

    if not data.birth_time_unknown:
        lines.append(f"출생시각: {data.solar_hour}시 {data.solar_minute}분")
    else:
        lines.append("출생시각: 미상 (삼주 해석)")

    lines.append(f"음력: {data.lunar_year}년 {data.lunar_month}월 {data.lunar_day}일"
                 + (" (윤달)" if data.is_leap_month else ""))
    lines.append("")

    # Four pillars table
    lines.append("## 사주팔자 (四柱八字)")
    lines.append("")

    pillars = [
        ("시주(時柱)", data.time_pillar),
        ("일주(日柱)", data.day_pillar),
        ("월주(月柱)", data.month_pillar),
        ("연주(年柱)", data.year_pillar),
    ]

    header = " | ".join(name for name, _ in pillars)
    lines.append(f"| {header} |")
    lines.append("|" + "|".join(["---"] * 4) + "|")

    # Stems row
    stem_row = []
    for _, p in pillars:
        if p is None:
            stem_row.append("(미상)")
        else:
            stem_row.append(f"{p.gan}({p.gan_kor})")
    lines.append("| " + " | ".join(stem_row) + " |")

    # Branches row
    branch_row = []
    for _, p in pillars:
        if p is None:
            branch_row.append("(미상)")
        else:
            branch_row.append(f"{p.zhi}({p.zhi_kor})")
    lines.append("| " + " | ".join(branch_row) + " |")
    lines.append("")

    # Day master
    lines.append(f"일간(日干): {data.day_master}({data.day_master_kor})")
    lines.append(f"일간 오행: {data.day_master_element}")
    lines.append(f"일간 음양: {data.day_master_yin_yang}")
    lines.append("")

    # Wu Xing for each pillar
    lines.append("## 오행 분석")
    for name, p in pillars:
        if p is not None:
            lines.append(f"- {name}: {p.wu_xing} (납음: {p.na_yin})")
    lines.append("")

    # Element counts
    lines.append("## 오행 분포")
    for element, count in data.element_counts.items():
        bar = "■" * count + "□" * (4 - count)
        lines.append(f"- {element}: {count}개 {bar}")
    lines.append("")

    # Ten gods
    lines.append("## 십신(十神)")
    for name, p in pillars:
        if p is not None:
            zhi_str = ", ".join(p.shi_shen_zhi)
            lines.append(f"- {name}: 천간={p.shi_shen_gan}, 지지=[{zhi_str}]")
    lines.append("")

    # Hidden stems
    lines.append("## 지장간(支藏干)")
    for name, p in pillars:
        if p is not None:
            lines.append(f"- {name}: [{', '.join(p.hide_gan)}]")
    lines.append("")

    # 12 fate positions
    lines.append("## 12운성")
    for name, p in pillars:
        if p is not None:
            lines.append(f"- {name}: {p.di_shi}")
    lines.append("")

    # Extra info
    lines.append("## 부가 정보")
    lines.append(f"- 태원(胎元): {data.tai_yuan} ({data.tai_yuan_na_yin})")
    lines.append(f"- 명궁(命宮): {data.ming_gong} ({data.ming_gong_na_yin})")
    lines.append(f"- 신궁(身宮): {data.shen_gong} ({data.shen_gong_na_yin})")
    lines.append("")

    # Da Yun
    lines.append("## 대운(大運)")
    lines.append(f"대운 시작: {data.da_yun_start_age}세")
    for dy in data.da_yun_list:
        lines.append(f"- {dy.start_age}세 ({dy.start_year}년~): {dy.gan_zhi}")

    return "\n".join(lines)
