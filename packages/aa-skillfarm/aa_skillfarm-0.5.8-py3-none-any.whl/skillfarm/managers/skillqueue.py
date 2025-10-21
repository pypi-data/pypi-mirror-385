# Standard Library
from typing import TYPE_CHECKING

# Django
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.utils import timezone

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from eveuniverse.models import EveType

# AA Skillfarm
from skillfarm import __title__
from skillfarm.app_settings import SKILLFARM_BULK_METHODS_BATCH_SIZE
from skillfarm.decorators import log_timing
from skillfarm.providers import esi
from skillfarm.task_helper import (
    etag_results,
)

if TYPE_CHECKING:
    # AA Skillfarm
    from skillfarm.models.general import UpdateSectionResult
    from skillfarm.models.skillfarm import (
        SkillFarmAudit,
    )

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


class SkillqueueQuerySet(models.QuerySet):
    def finished_skills(self):
        """Return finished skills from a training queue."""
        return self.filter(
            finish_date__isnull=False,
            start_date__isnull=True,
            finish_date__gt=models.F("start_date"),
            finish_date__lt=timezone.now(),
            finished_level=5,
        )

    def extractions(self, character: "SkillFarmAudit") -> bool:
        """Return extraction ready skills from a training queue."""
        try:
            skillsetup = character.skillfarm_setup
            if not skillsetup or not skillsetup.skillset:
                skillset = []
            else:
                skillset = skillsetup.skillset
        except ObjectDoesNotExist:
            skillset = []

        extraction = self.filter(
            finish_date__gt=models.F("start_date"),
            finish_date__lt=timezone.now(),
            finished_level=5,
            eve_type__name__in=skillset,
        )

        return extraction

    def active_skills(self):
        """Return skills from an active training queue.
        Returns empty queryset when training is not active.
        """
        return self.filter(
            finish_date__isnull=False,
            start_date__isnull=False,
        )

    def skill_in_training(self):
        """Return current skill in training.
        Returns empty queryset when training is not active.
        """
        now_ = timezone.now()
        return self.active_skills().filter(
            start_date__lt=now_,
            finish_date__gt=now_,
        )

    def skill_filtered(self, character: "SkillFarmAudit") -> bool:
        """Return filtered skills from a training queue."""
        try:
            skillsetup = character.skillfarm_setup
            if not skillsetup or not skillsetup.skillset:
                skillset = []
            else:
                skillset = skillsetup.skillset
        except ObjectDoesNotExist:
            skillset = []

        skillqueue = self.filter(
            eve_type__name__in=skillset,
        )
        return skillqueue


class SkillqueueManagerBase(models.Manager):
    @log_timing(logger)
    def update_or_create_esi(
        self, character: "SkillFarmAudit", force_refresh: bool = False
    ) -> "UpdateSectionResult":
        """Update or Create skills for a character from ESI."""
        return character.update_section_if_changed(
            section=character.UpdateSection.SKILLQUEUE,
            fetch_func=self._fetch_esi_data,
            force_refresh=force_refresh,
        )

    def _fetch_esi_data(
        self, character: "SkillFarmAudit", force_refresh: bool = False
    ) -> dict:
        """Fetch Skillqueue entries from ESI data."""
        token = character.get_token()

        skillqueue_data = esi.client.Skills.get_characters_character_id_skillqueue(
            character_id=character.character.character_id,
        )

        skillqueue = etag_results(skillqueue_data, token, force_refresh=force_refresh)
        self._update_or_create_objs(character, skillqueue)

    @transaction.atomic()
    def _update_or_create_objs(self, character: "SkillFarmAudit", objs: list):
        """Update or Create skill queue entries from objs data."""
        entries = []

        for entry in objs:
            eve_type_instance, _ = EveType.objects.get_or_create_esi(
                id=entry.get("skill_id")
            )
            entries.append(
                self.model(
                    name=character.name,
                    character=character,
                    eve_type=eve_type_instance,
                    finish_date=entry.get("finish_date"),
                    finished_level=entry.get("finished_level"),
                    level_end_sp=entry.get("level_end_sp"),
                    level_start_sp=entry.get("level_start_sp"),
                    queue_position=entry.get("queue_position"),
                    start_date=entry.get("start_date"),
                    training_start_sp=entry.get("training_start_sp"),
                )
            )

        self.filter(character=character).delete()

        if len(entries) > 0:
            self.bulk_create(entries, batch_size=SKILLFARM_BULK_METHODS_BATCH_SIZE)


SkillqueueManager = SkillqueueManagerBase.from_queryset(SkillqueueQuerySet)
