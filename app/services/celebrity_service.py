from __future__ import annotations

from app.data.celebrities import Celebrity, get_celebrity_by_id
from app.engine.models import SajuData
from app.llm.prompts.celebrity_compatibility import CELEBRITY_COMPATIBILITY_PROMPT
from app.middleware.error_handler import SajuError
from app.models.request import BirthInput
from app.services.compatibility_service import CompatibilityService


class CelebrityNotFoundError(SajuError):
    """Raised when a celebrity ID does not match any entry."""

    def __init__(self, celebrity_id: str):
        super().__init__(
            message=f"Celebrity not found: {celebrity_id}",
            status_code=404,
        )


class CelebrityService:
    """Thin wrapper over CompatibilityService for celebrity compatibility."""

    def __init__(self, compatibility_service: CompatibilityService):
        self._compat = compatibility_service

    @staticmethod
    def celebrity_to_birth_input(celebrity: Celebrity) -> BirthInput:
        """Convert a Celebrity record to BirthInput (hour=None, solar)."""
        return BirthInput(
            year=celebrity.year,
            month=celebrity.month,
            day=celebrity.day,
            hour=None,
            gender=celebrity.gender,
        )

    async def analyze_compatibility(
        self,
        user_birth: BirthInput,
        celebrity_id: str,
        *,
        language: str = "ko",
    ) -> tuple[SajuData, SajuData, Celebrity, str]:
        """Analyze compatibility between a user and a celebrity.

        Returns (user_saju, celebrity_saju, celebrity, interpretation).
        Raises CelebrityNotFoundError if the celebrity_id is invalid.
        """
        celebrity = get_celebrity_by_id(celebrity_id)
        if celebrity is None:
            raise CelebrityNotFoundError(celebrity_id)

        celeb_birth = self.celebrity_to_birth_input(celebrity)

        user_saju, celeb_saju, interpretation = await self._compat.analyze(
            person1=user_birth,
            person2=celeb_birth,
            prompt_template=CELEBRITY_COMPATIBILITY_PROMPT,
            prompt_kwargs={
                "celebrity_name": celebrity.name_ko,
                "celebrity_group": celebrity.group,
            },
            language=language,
        )

        return user_saju, celeb_saju, celebrity, interpretation
