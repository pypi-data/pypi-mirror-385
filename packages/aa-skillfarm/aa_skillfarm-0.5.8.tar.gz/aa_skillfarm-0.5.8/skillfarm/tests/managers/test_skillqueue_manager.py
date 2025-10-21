# Standard Library
from unittest.mock import patch

# Django
from django.test import override_settings

# Alliance Auth (External Libs)
from app_utils.testing import NoSocketsTestCase
from eveuniverse.models import EveType

# AA Skillfarm
from skillfarm.tests.testdata.allianceauth import load_allianceauth
from skillfarm.tests.testdata.esi_stub import esi_client_stub
from skillfarm.tests.testdata.eveuniverse import load_eveuniverse
from skillfarm.tests.testdata.skillfarm import (
    create_skillfarm_character,
)

MODULE_PATH = "skillfarm.managers.skillqueue"


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(MODULE_PATH + ".esi")
@patch(MODULE_PATH + ".etag_results")
class TestSkillQueueManager(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_eveuniverse()

        cls.audit = create_skillfarm_character(1001)

        cls.eve_type = EveType.objects.get(id=1)
        cls.eve_type_2 = EveType.objects.get(id=2)

    def test_update_skillqueue(self, mock_etag, mock_esi):
        # given
        mock_esi.client = esi_client_stub
        mock_etag.return_value = [
            {
                "finish_date": "2023-10-01T00:00:00Z",
                "queue_position": 1,
                "skill_id": 1,
                "start_date": "2023-09-01T00:00:00Z",
                "training_start_sp": 312345,
                "level_start_sp": 128000,
                "level_end_sp": 512000,
                "finished_level": 5,
            },
            {
                "finish_date": "2023-10-02T00:00:00Z",
                "queue_position": 2,
                "skill_id": 2,
                "start_date": "2023-09-02T00:00:00Z",
                "training_start_sp": 5000,
                "level_start_sp": 4000,
                "level_end_sp": 16000,
                "finished_level": 4,
            },
        ]

        self.audit.update_skillqueue(force_refresh=False)

        self.assertSetEqual(
            set(self.audit.skillfarm_skillqueue.values_list("eve_type__id", flat=True)),
            {1, 2},
        )
        obj = self.audit.skillfarm_skillqueue.get(eve_type__id=1)
        self.assertEqual(obj.training_start_sp, 312345)
        self.assertEqual(obj.level_start_sp, 128000)
        self.assertEqual(obj.level_end_sp, 512000)
        self.assertEqual(obj.finished_level, 5)

        obj = self.audit.skillfarm_skillqueue.get(eve_type__id=2)
        self.assertEqual(obj.training_start_sp, 5000)
        self.assertEqual(obj.level_start_sp, 4000)
        self.assertEqual(obj.level_end_sp, 16000)
        self.assertEqual(obj.finished_level, 4)
