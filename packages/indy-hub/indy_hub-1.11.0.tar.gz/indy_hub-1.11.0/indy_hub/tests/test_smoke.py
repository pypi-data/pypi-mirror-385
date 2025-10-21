"""Basic smoke tests for the Indy Hub app."""

# Standard Library
from datetime import timedelta
from unittest.mock import patch

# Django
from django.apps import apps
from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

# Alliance Auth
from allianceauth.authentication.models import UserProfile
from allianceauth.eveonline.models import EveCharacter

# AA Example App
from indy_hub.models import (
    Blueprint,
    BlueprintCopyOffer,
    BlueprintCopyRequest,
    CharacterSettings,
    CorporationSharingSetting,
    IndustryJob,
    UserOnboardingProgress,
)
from indy_hub.notifications import notify_user
from indy_hub.services.esi_client import ESIForbiddenError
from indy_hub.tasks.industry import (
    MANUAL_REFRESH_KIND_BLUEPRINTS,
    MANUAL_REFRESH_KIND_JOBS,
    manual_refresh_allowed,
    request_manual_refresh,
    reset_manual_refresh_cooldown,
)
from indy_hub.utils import eve as eve_utils
from indy_hub.utils.eve import get_type_name, reset_forbidden_structure_lookup_cache


def assign_main_character(user: User, *, character_id: int) -> EveCharacter:
    """Ensure the given user has a main character to satisfy middleware requirements."""

    profile, _ = UserProfile.objects.get_or_create(user=user)

    character, _ = EveCharacter.objects.get_or_create(
        character_id=character_id,
        defaults={
            "character_name": f"{user.username.title()}",
            "corporation_id": 2000000,
            "corporation_name": "Test Corp",
            "corporation_ticker": "TEST",
            "alliance_id": None,
            "alliance_name": "",
            "alliance_ticker": "",
            "faction_id": None,
            "faction_name": "",
        },
    )
    profile.main_character = character
    profile.save(update_fields=["main_character"])
    return character


def grant_indy_permissions(user: User, *extra_codenames: str) -> None:
    """Attach the requested Indy Hub permissions to the user."""

    required = {"can_access_indy_hub", *extra_codenames}
    permissions = Permission.objects.filter(
        content_type__app_label="indy_hub", codename__in=required
    )
    found = {perm.codename: perm for perm in permissions}
    missing = required - found.keys()
    if missing:
        raise AssertionError(f"Missing permissions: {sorted(missing)}")
    user.user_permissions.add(*found.values())


class IndyHubConfigTests(TestCase):
    def test_app_is_registered(self) -> None:
        """The indy_hub app should be installed and discoverable."""
        app_config = apps.get_app_config("indy_hub")
        self.assertEqual(app_config.name, "indy_hub")

    def test_get_type_name_graceful_fallback(self) -> None:
        """`get_type_name` should fall back to the stringified id when EveUniverse is absent."""
        self.assertEqual(get_type_name(12345), "12345")


class BlueprintModelClassificationTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("classifier", password="secret123")

    def test_original_blueprint_infers_type(self) -> None:
        blueprint = Blueprint.objects.create(
            owner_user=self.user,
            character_id=9001,
            item_id=9001001,
            blueprint_id=9002001,
            type_id=424242,
            location_id=10,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=0,
            material_efficiency=0,
            runs=0,
            character_name="Classifier",
            type_name="Widget Blueprint",
        )
        self.assertEqual(blueprint.bp_type, Blueprint.BPType.ORIGINAL)

        blueprint.quantity = -2
        blueprint.save()
        blueprint.refresh_from_db()
        self.assertEqual(blueprint.bp_type, Blueprint.BPType.COPY)


class CorporationSharingSettingTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("director", password="secret123")
        self.setting = CorporationSharingSetting.objects.create(
            user=self.user,
            corporation_id=4242,
            corporation_name="Directive Industries",
            share_scope=CharacterSettings.SCOPE_CORPORATION,
            allow_copy_requests=True,
        )

    def test_default_allows_all_characters(self) -> None:
        self.assertFalse(self.setting.restricts_characters)
        self.assertTrue(self.setting.is_character_authorized(9001))

    def test_whitelist_filters_characters(self) -> None:
        self.setting.set_authorized_characters([1010, 2020])
        self.setting.save(update_fields=["authorized_characters"])
        self.setting.refresh_from_db()

        self.assertTrue(self.setting.restricts_characters)
        self.assertTrue(self.setting.is_character_authorized(1010))
        self.assertFalse(self.setting.is_character_authorized(3030))

    def test_authorized_character_ids_are_unique_and_sorted(self) -> None:
        self.setting.set_authorized_characters(["5050", None, 4040, 5050])
        self.setting.save(update_fields=["authorized_characters"])
        self.setting.refresh_from_db()

        self.assertEqual(self.setting.authorized_character_ids, [4040, 5050])

    def test_reaction_detection_from_name(self) -> None:
        blueprint = Blueprint.objects.create(
            owner_user=self.user,
            character_id=9002,
            item_id=9002001,
            blueprint_id=9003001,
            type_id=434343,
            location_id=11,
            location_flag="corporate",
            quantity=-1,
            time_efficiency=0,
            material_efficiency=0,
            runs=0,
            character_name="Classifier",
            type_name="Fullerene Reaction Formula",
        )
        blueprint.refresh_from_db()
        self.assertEqual(blueprint.bp_type, Blueprint.BPType.REACTION)

    def test_positive_quantity_classified_as_copy(self) -> None:
        blueprint = Blueprint.objects.create(
            owner_user=self.user,
            character_id=9003,
            item_id=9100100,
            blueprint_id=9100200,
            type_id=565656,
            location_id=12,
            location_flag="hangar",
            quantity=5,
            time_efficiency=0,
            material_efficiency=0,
            runs=2,
            character_name="Classifier",
            type_name="Widget Blueprint Copy",
        )
        self.assertEqual(blueprint.bp_type, Blueprint.BPType.COPY)


class LocationNameSignalTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("locator", password="secret123")

    @patch("indy_hub.signals.resolve_location_name", return_value="Structure Beta")
    def test_blueprint_location_name_refreshes_on_identifier_change(self, mock_resolve):
        blueprint = Blueprint.objects.create(
            owner_user=self.user,
            character_id=7001,
            item_id=5001001,
            blueprint_id=5002001,
            type_id=13579,
            location_id=1111,
            location_name="Alpha Depot",
            location_flag="hangar",
            quantity=-1,
            time_efficiency=0,
            material_efficiency=0,
            runs=0,
            character_name="Locator",
            type_name="Test Blueprint",
        )

        mock_resolve.assert_not_called()

        blueprint.location_id = 2222
        blueprint.location_name = "Alpha Depot"
        blueprint.save()
        blueprint.refresh_from_db()

        mock_resolve.assert_called_once_with(
            2222,
            character_id=7001,
            owner_user_id=self.user.id,
        )
        self.assertEqual(blueprint.location_name, "Structure Beta")

    @patch("indy_hub.signals.resolve_location_name", return_value="Station Gamma")
    def test_industry_job_location_name_refreshes_on_station_change(self, mock_resolve):
        start = timezone.now()
        end = start + timedelta(hours=1)

        job = IndustryJob.objects.create(
            owner_user=self.user,
            character_id=8001,
            job_id=9101112,
            installer_id=self.user.id,
            station_id=3333,
            location_name="Outpost Alpha",
            activity_id=1,
            blueprint_id=6001001,
            blueprint_type_id=6002001,
            runs=1,
            status="active",
            duration=3600,
            start_date=start,
            end_date=end,
            activity_name="Manufacturing",
            blueprint_type_name="Widget",
            product_type_name="Widget Product",
            character_name="Locator",
        )

        mock_resolve.assert_not_called()

        job.station_id = 4444
        job.location_name = "Outpost Alpha"
        job.save()
        job.refresh_from_db()

        mock_resolve.assert_called_once_with(
            4444,
            character_id=8001,
            owner_user_id=self.user.id,
        )
        self.assertEqual(job.location_name, "Station Gamma")


class JobNotificationSignalTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("notifier", password="secret123")
        CharacterSettings.objects.create(
            user=self.user,
            character_id=0,
            jobs_notify_completed=True,
        )

    @patch("indy_hub.signals.notify_user")
    def test_notification_sent_for_completed_job(self, mock_notify):
        start = timezone.now() - timedelta(hours=2)
        end = timezone.now() - timedelta(minutes=5)

        job = IndustryJob.objects.create(
            owner_user=self.user,
            character_id=9101,
            job_id=88001,
            installer_id=self.user.id,
            station_id=6001,
            location_name="Factory",
            activity_id=1,
            blueprint_id=7001,
            blueprint_type_id=7002,
            blueprint_type_name="Widget Blueprint",
            runs=1,
            status="delivered",
            duration=3600,
            start_date=start,
            end_date=end,
            activity_name="Manufacturing",
            product_type_name="Widget",
            character_name="Notifier",
        )

        job.refresh_from_db()

        mock_notify.assert_called_once()
        args, kwargs = mock_notify.call_args
        self.assertEqual(args[0], self.user)
        self.assertEqual(args[1], "Industry Job Completed")
        self.assertIn("88001", args[2])
        self.assertTrue(job.job_completed_notified)

    @patch("indy_hub.signals.notify_user")
    def test_notification_skipped_when_preference_disabled(self, mock_notify):
        other_user = User.objects.create_user("silent", password="secret123")
        CharacterSettings.objects.create(
            user=other_user,
            character_id=0,
            jobs_notify_completed=False,
        )

        start = timezone.now() - timedelta(hours=1)
        end = timezone.now() - timedelta(minutes=10)

        job = IndustryJob.objects.create(
            owner_user=other_user,
            character_id=9201,
            job_id=88002,
            installer_id=other_user.id,
            station_id=6002,
            location_name="Research Lab",
            activity_id=1,
            blueprint_id=7003,
            blueprint_type_id=7004,
            blueprint_type_name="Widget Blueprint",
            runs=1,
            status="delivered",
            duration=3600,
            start_date=start,
            end_date=end,
            activity_name="Manufacturing",
            product_type_name="Widget",
            character_name="Silent",
        )

        job.refresh_from_db()

        mock_notify.assert_not_called()
        self.assertTrue(job.job_completed_notified)

    @patch("indy_hub.signals.notify_user")
    def test_notification_handles_string_end_date(self, mock_notify):
        start = timezone.now() - timedelta(hours=2)
        future_end = timezone.now() + timedelta(hours=1)

        job = IndustryJob.objects.create(
            owner_user=self.user,
            character_id=9301,
            job_id=88003,
            installer_id=self.user.id,
            station_id=6003,
            location_name="Factory",
            activity_id=1,
            blueprint_id=7005,
            blueprint_type_id=7006,
            blueprint_type_name="Widget Blueprint",
            runs=1,
            status="manufacturing",
            duration=3600,
            start_date=start,
            end_date=future_end,
            activity_name="Manufacturing",
            product_type_name="Widget",
            character_name="Notifier",
        )

        job.refresh_from_db()
        self.assertFalse(job.job_completed_notified)

        past_end_iso = (timezone.now() - timedelta(minutes=5)).isoformat()
        job.end_date = past_end_iso
        job.status = "delivered"

        mock_notify.reset_mock()

        # AA Example App
        from indy_hub import signals as indy_signals

        indy_signals._handle_job_completion_notification(job)

        job.refresh_from_db()

        mock_notify.assert_called_once()
        self.assertTrue(job.job_completed_notified)


class BlueprintCopyFulfillViewTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("capsuleer", password="test12345")
        assign_main_character(self.user, character_id=101001)
        CharacterSettings.objects.create(
            user=self.user,
            character_id=0,
            allow_copy_requests=True,
            copy_sharing_scope=CharacterSettings.SCOPE_CORPORATION,
        )
        grant_indy_permissions(self.user, "can_manage_copy_requests")
        self.client.force_login(self.user)

    def test_request_visible_for_own_blueprint(self) -> None:
        blueprint = Blueprint.objects.create(
            owner_user=self.user,
            character_id=42,
            item_id=1001,
            blueprint_id=2001,
            type_id=987654,
            location_id=3001,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=10,
            material_efficiency=5,
            runs=0,
            character_name="Capsuleer",
            type_name="Test Blueprint",
        )
        buyer = User.objects.create_user("requester", password="test12345")
        request_obj = BlueprintCopyRequest.objects.create(
            type_id=blueprint.type_id,
            material_efficiency=blueprint.material_efficiency,
            time_efficiency=blueprint.time_efficiency,
            requested_by=buyer,
            runs_requested=2,
            copies_requested=1,
        )

        response = self.client.get(reverse("indy_hub:bp_copy_fulfill_requests"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("metrics", response.context)
        self.assertEqual(response.context["metrics"]["total"], 1)
        requests = response.context["requests"]
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]["id"], request_obj.id)
        self.assertEqual(requests[0]["status_key"], "awaiting_response")
        self.assertTrue(requests[0]["show_offer_actions"])
        self.assertFalse(requests[0]["is_self_request"])

    def test_self_request_visible_but_read_only(self) -> None:
        blueprint = Blueprint.objects.create(
            owner_user=self.user,
            character_id=42,
            item_id=2001,
            blueprint_id=3001,
            type_id=555,
            location_id=4001,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=8,
            material_efficiency=7,
            runs=0,
            character_name="Capsuleer",
            type_name="Another Blueprint",
        )
        request_obj = BlueprintCopyRequest.objects.create(
            type_id=blueprint.type_id,
            material_efficiency=blueprint.material_efficiency,
            time_efficiency=blueprint.time_efficiency,
            requested_by=self.user,
            runs_requested=2,
            copies_requested=1,
        )

        response = self.client.get(reverse("indy_hub:bp_copy_fulfill_requests"))

        self.assertEqual(response.status_code, 200)
        requests = response.context["requests"]
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]["id"], request_obj.id)
        self.assertEqual(response.context["metrics"]["total"], 1)
        self.assertEqual(response.context["metrics"]["awaiting_response"], 0)
        self.assertTrue(requests[0]["is_self_request"])
        self.assertEqual(requests[0]["status_key"], "self_request")
        self.assertFalse(requests[0]["show_offer_actions"])
        self.assertFalse(requests[0]["can_mark_delivered"])

    def test_rejected_offer_hidden_from_queue(self) -> None:
        blueprint = Blueprint.objects.create(
            owner_user=self.user,
            character_id=44,
            item_id=2101,
            blueprint_id=3101,
            type_id=999001,
            location_id=4101,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=12,
            material_efficiency=9,
            runs=0,
            character_name="Capsuleer",
            type_name="Hidden Blueprint",
        )
        buyer = User.objects.create_user("rejecting_requester", password="test12345")
        request_obj = BlueprintCopyRequest.objects.create(
            type_id=blueprint.type_id,
            material_efficiency=blueprint.material_efficiency,
            time_efficiency=blueprint.time_efficiency,
            requested_by=buyer,
            runs_requested=1,
            copies_requested=1,
        )
        BlueprintCopyOffer.objects.create(
            request=request_obj,
            owner=self.user,
            status="rejected",
            message="No time",
        )

        response = self.client.get(reverse("indy_hub:bp_copy_fulfill_requests"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["requests"], [])
        self.assertEqual(response.context["metrics"]["total"], 0)

    def test_requester_notified_when_all_providers_reject(self) -> None:
        blueprint = Blueprint.objects.create(
            owner_user=self.user,
            character_id=45,
            item_id=2201,
            blueprint_id=3201,
            type_id=999002,
            location_id=4201,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=10,
            material_efficiency=6,
            runs=0,
            character_name="Capsuleer",
            type_name="Shared Blueprint",
        )
        other_provider = User.objects.create_user(
            "second_builder", password="test12345"
        )
        assign_main_character(other_provider, character_id=101005)
        CharacterSettings.objects.create(
            user=other_provider,
            character_id=0,
            allow_copy_requests=True,
            copy_sharing_scope=CharacterSettings.SCOPE_CORPORATION,
        )
        grant_indy_permissions(other_provider, "can_manage_copy_requests")
        Blueprint.objects.create(
            owner_user=other_provider,
            character_id=55,
            item_id=2202,
            blueprint_id=3202,
            type_id=blueprint.type_id,
            location_id=4202,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=blueprint.time_efficiency,
            material_efficiency=blueprint.material_efficiency,
            runs=0,
            character_name="Second Builder",
            type_name="Shared Blueprint",
        )
        requester = User.objects.create_user("bp_customer", password="request123")
        assign_main_character(requester, character_id=201001)
        request_obj = BlueprintCopyRequest.objects.create(
            type_id=blueprint.type_id,
            material_efficiency=blueprint.material_efficiency,
            time_efficiency=blueprint.time_efficiency,
            requested_by=requester,
            runs_requested=2,
            copies_requested=1,
        )

        with patch("indy_hub.views.industry.notify_user") as mock_notify:
            response = self.client.post(
                reverse("indy_hub:bp_offer_copy_request", args=[request_obj.id]),
                {"action": "reject", "message": "Can't right now"},
            )
            self.assertRedirects(response, reverse("indy_hub:bp_copy_fulfill_requests"))
            self.assertTrue(
                BlueprintCopyRequest.objects.filter(id=request_obj.id).exists()
            )
            mock_notify.assert_not_called()

            self.client.logout()
            self.client.force_login(other_provider)
            response = self.client.post(
                reverse("indy_hub:bp_offer_copy_request", args=[request_obj.id]),
                {"action": "reject", "message": "Also unavailable"},
            )
            self.assertRedirects(response, reverse("indy_hub:bp_copy_fulfill_requests"))

            self.assertFalse(
                BlueprintCopyRequest.objects.filter(id=request_obj.id).exists()
            )
            mock_notify.assert_called_once()
            args, kwargs = mock_notify.call_args
            self.assertEqual(args[0], requester)
            self.assertIn("declined", str(args[2]))

        self.client.logout()
        self.client.force_login(self.user)

    def test_busy_blueprints_flagged_in_context(self) -> None:
        blueprint = Blueprint.objects.create(
            owner_user=self.user,
            character_id=42,
            item_id=3001,
            blueprint_id=4001,
            type_id=987001,
            location_id=5001,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=10,
            material_efficiency=7,
            runs=0,
            character_name="Capsuleer",
            type_name="Busy Blueprint",
        )
        buyer = User.objects.create_user("busy_requester", password="test12345")
        BlueprintCopyRequest.objects.create(
            type_id=blueprint.type_id,
            material_efficiency=blueprint.material_efficiency,
            time_efficiency=blueprint.time_efficiency,
            requested_by=buyer,
            runs_requested=3,
            copies_requested=2,
        )

        IndustryJob.objects.create(
            owner_user=self.user,
            character_id=blueprint.character_id,
            job_id=7770001,
            installer_id=self.user.id,
            station_id=blueprint.location_id,
            location_name="Busy Location",
            activity_id=5,
            blueprint_id=blueprint.item_id,
            blueprint_type_id=blueprint.type_id,
            runs=1,
            status="active",
            duration=3600,
            start_date=timezone.now() - timedelta(minutes=10),
            end_date=timezone.now() + timedelta(hours=2),
            activity_name="Copying",
            blueprint_type_name=blueprint.type_name,
            product_type_name="Busy Product",
            character_name=blueprint.character_name,
        )
        response = self.client.get(reverse("indy_hub:bp_copy_fulfill_requests"))

        self.assertEqual(response.status_code, 200)
        requests = response.context["requests"]
        self.assertEqual(len(requests), 1)
        request_entry = requests[0]
        self.assertTrue(request_entry["all_copies_busy"])
        self.assertEqual(request_entry["owned_blueprints"], 1)
        self.assertEqual(request_entry["available_blueprints"], 0)
        self.assertGreater(request_entry["active_copy_jobs"], 0)
        self.assertIsNotNone(request_entry["busy_until"])
        self.assertFalse(request_entry["busy_overdue"])

    def test_non_copy_job_blocks_blueprint(self) -> None:
        blueprint = Blueprint.objects.create(
            owner_user=self.user,
            character_id=42,
            item_id=4001,
            blueprint_id=5001,
            type_id=987002,
            location_id=6001,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=12,
            material_efficiency=9,
            runs=0,
            character_name="Capsuleer",
            type_name="Manufacturing Blueprint",
        )
        buyer = User.objects.create_user(
            "manufacturing_requester", password="test12345"
        )
        BlueprintCopyRequest.objects.create(
            type_id=blueprint.type_id,
            material_efficiency=blueprint.material_efficiency,
            time_efficiency=blueprint.time_efficiency,
            requested_by=buyer,
            runs_requested=1,
            copies_requested=1,
        )

        IndustryJob.objects.create(
            owner_user=self.user,
            character_id=blueprint.character_id,
            job_id=8880001,
            installer_id=self.user.id,
            station_id=blueprint.location_id,
            location_name="Manufacturing Hub",
            activity_id=1,
            blueprint_id=blueprint.item_id,
            blueprint_type_id=blueprint.type_id,
            runs=1,
            status="active",
            duration=7200,
            start_date=timezone.now() - timedelta(minutes=30),
            end_date=timezone.now() + timedelta(hours=1),
            activity_name="Manufacturing",
            blueprint_type_name=blueprint.type_name,
            product_type_name="Manufactured Product",
            character_name=blueprint.character_name,
        )

        response = self.client.get(reverse("indy_hub:bp_copy_fulfill_requests"))

        self.assertEqual(response.status_code, 200)
        requests = response.context["requests"]
        self.assertEqual(len(requests), 1)
        request_entry = requests[0]
        self.assertTrue(request_entry["all_copies_busy"])
        self.assertEqual(request_entry["owned_blueprints"], 1)
        self.assertEqual(request_entry["available_blueprints"], 0)

    def test_job_with_zero_blueprint_id_matches_original(self) -> None:
        blueprint = Blueprint.objects.create(
            owner_user=self.user,
            character_id=43,
            item_id=0,
            blueprint_id=0,
            type_id=987003,
            location_id=7001,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=6,
            material_efficiency=4,
            runs=0,
            character_name="Capsuleer",
            type_name="Zero Blueprint",
        )
        buyer = User.objects.create_user("zero_requester", password="test12345")
        BlueprintCopyRequest.objects.create(
            type_id=blueprint.type_id,
            material_efficiency=blueprint.material_efficiency,
            time_efficiency=blueprint.time_efficiency,
            requested_by=buyer,
            runs_requested=1,
            copies_requested=1,
        )

        IndustryJob.objects.create(
            owner_user=self.user,
            character_id=blueprint.character_id,
            job_id=8890001,
            installer_id=self.user.id,
            station_id=blueprint.location_id,
            location_name="Zero Yard",
            activity_id=5,
            blueprint_id=0,
            blueprint_type_id=blueprint.type_id,
            runs=1,
            status="active",
            duration=5400,
            start_date=timezone.now() - timedelta(minutes=15),
            end_date=timezone.now() + timedelta(hours=1),
            activity_name="Copying",
            blueprint_type_name=blueprint.type_name,
            product_type_name="Zero Product",
            character_name=blueprint.character_name,
        )

        response = self.client.get(reverse("indy_hub:bp_copy_fulfill_requests"))

        self.assertEqual(response.status_code, 200)
        requests = response.context["requests"]
        self.assertEqual(len(requests), 1)
        request_entry = requests[0]
        self.assertTrue(request_entry["all_copies_busy"])
        self.assertEqual(request_entry["active_copy_jobs"], 1)

    def test_job_with_mismatched_blueprint_id_does_not_block(self) -> None:
        blueprint = Blueprint.objects.create(
            owner_user=self.user,
            character_id=45,
            item_id=6001,
            blueprint_id=7001,
            type_id=555001,
            location_id=8001,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=20,
            material_efficiency=10,
            runs=0,
            character_name="Capsuleer",
            type_name="Ambiguous Blueprint",
        )
        buyer = User.objects.create_user("ambiguous_requester", password="test12345")
        BlueprintCopyRequest.objects.create(
            type_id=blueprint.type_id,
            material_efficiency=blueprint.material_efficiency,
            time_efficiency=blueprint.time_efficiency,
            requested_by=buyer,
            runs_requested=1,
            copies_requested=1,
        )

        IndustryJob.objects.create(
            owner_user=self.user,
            character_id=blueprint.character_id,
            job_id=8895001,
            installer_id=self.user.id,
            station_id=blueprint.location_id,
            location_name="Ambiguous Site",
            activity_id=5,
            blueprint_id=9999999,
            blueprint_type_id=blueprint.type_id,
            runs=1,
            status="active",
            duration=3600,
            start_date=timezone.now() - timedelta(minutes=5),
            end_date=timezone.now() + timedelta(hours=1),
            activity_name="Copying",
            blueprint_type_name=blueprint.type_name,
            product_type_name="Ambiguous Product",
            character_name=blueprint.character_name,
        )

        response = self.client.get(reverse("indy_hub:bp_copy_fulfill_requests"))

        self.assertEqual(response.status_code, 200)
        requests = response.context["requests"]
        self.assertEqual(len(requests), 1)
        request_entry = requests[0]
        self.assertFalse(request_entry["all_copies_busy"])
        self.assertEqual(request_entry["owned_blueprints"], 1)
        self.assertEqual(request_entry["available_blueprints"], 1)
        self.assertEqual(request_entry["active_copy_jobs"], 0)
        self.assertIsNone(request_entry["busy_until"])

    def test_job_past_end_date_still_blocks(self) -> None:
        blueprint = Blueprint.objects.create(
            owner_user=self.user,
            character_id=46,
            item_id=6101,
            blueprint_id=7101,
            type_id=565001,
            location_id=8101,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=12,
            material_efficiency=8,
            runs=0,
            character_name="Capsuleer",
            type_name="Late Delivery Blueprint",
        )
        buyer = User.objects.create_user("late_requester", password="test12345")
        BlueprintCopyRequest.objects.create(
            type_id=blueprint.type_id,
            material_efficiency=blueprint.material_efficiency,
            time_efficiency=blueprint.time_efficiency,
            requested_by=buyer,
            runs_requested=1,
            copies_requested=1,
        )

        job_end = timezone.now() - timedelta(hours=2)
        IndustryJob.objects.create(
            owner_user=self.user,
            character_id=blueprint.character_id,
            job_id=8897001,
            installer_id=self.user.id,
            station_id=blueprint.location_id,
            location_name="Late Facility",
            activity_id=5,
            blueprint_id=blueprint.item_id,
            blueprint_type_id=blueprint.type_id,
            runs=1,
            status="active",
            duration=3600,
            start_date=timezone.now() - timedelta(hours=3),
            end_date=job_end,
            activity_name="Copying",
            blueprint_type_name=blueprint.type_name,
            product_type_name="Late Product",
            character_name=blueprint.character_name,
        )

        response = self.client.get(reverse("indy_hub:bp_copy_fulfill_requests"))

        self.assertEqual(response.status_code, 200)
        requests = response.context["requests"]
        self.assertEqual(len(requests), 1)
        request_entry = requests[0]
        self.assertTrue(request_entry["all_copies_busy"])
        self.assertEqual(request_entry["owned_blueprints"], 1)
        self.assertEqual(request_entry["available_blueprints"], 0)
        self.assertEqual(request_entry["active_copy_jobs"], 1)
        self.assertTrue(request_entry["busy_overdue"])
        self.assertEqual(request_entry["busy_until"], job_end)

    def test_reaction_blueprint_not_listed(self) -> None:
        Blueprint.objects.create(
            owner_user=self.user,
            character_id=42,
            item_id=3001,
            blueprint_id=4001,
            type_id=777777,
            location_id=5001,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=0,
            material_efficiency=0,
            runs=0,
            character_name="Capsuleer",
            type_name="Fullerene Reaction Formula",
        )
        buyer = User.objects.create_user("reaction-buyer", password="reactpass")
        BlueprintCopyRequest.objects.create(
            type_id=777777,
            material_efficiency=0,
            time_efficiency=0,
            requested_by=buyer,
            runs_requested=1,
            copies_requested=1,
        )

        response = self.client.get(reverse("indy_hub:bp_copy_fulfill_requests"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["requests"], [])
        self.assertEqual(response.context["metrics"]["total"], 0)


class BlueprintCopyRequestPageTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("requester", password="secret123")
        assign_main_character(self.user, character_id=103001)
        grant_indy_permissions(self.user, "can_manage_copy_requests")
        self.client.force_login(self.user)

        self.owner = User.objects.create_user("supplier", password="supply123")
        CharacterSettings.objects.create(
            user=self.owner,
            character_id=0,
            allow_copy_requests=True,
            copy_sharing_scope=CharacterSettings.SCOPE_CORPORATION,
        )
        Blueprint.objects.create(
            owner_user=self.owner,
            character_id=501,
            item_id=9050001,
            blueprint_id=9050002,
            type_id=605001,
            location_id=705001,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=12,
            material_efficiency=8,
            runs=0,
            character_name="Supplier",
            type_name="Duplicated Widget Blueprint",
        )

    def test_duplicate_submission_creates_additional_request(self) -> None:
        url = reverse("indy_hub:bp_copy_request_page")
        post_data = {
            "type_id": 605001,
            "material_efficiency": 8,
            "time_efficiency": 12,
            "runs_requested": 2,
            "copies_requested": 1,
        }

        with patch("indy_hub.views.industry.notify_user") as mock_notify:
            response = self.client.post(url, post_data)
            self.assertRedirects(response, url)

            initial_requests = BlueprintCopyRequest.objects.filter(
                type_id=605001,
                material_efficiency=8,
                time_efficiency=12,
                requested_by=self.user,
                fulfilled=False,
            )
            self.assertEqual(initial_requests.count(), 1)
            first_request = initial_requests.first()
            self.assertIsNotNone(first_request)
            self.assertEqual(first_request.runs_requested, 2)
            self.assertEqual(first_request.copies_requested, 1)

            followup_data = {
                "type_id": 605001,
                "material_efficiency": 8,
                "time_efficiency": 12,
                "runs_requested": 3,
                "copies_requested": 2,
            }
            response = self.client.post(url, followup_data)
            self.assertRedirects(response, url)

            open_requests = BlueprintCopyRequest.objects.filter(
                type_id=605001,
                material_efficiency=8,
                time_efficiency=12,
                requested_by=self.user,
                fulfilled=False,
            )

            self.assertEqual(open_requests.count(), 2)
            self.assertEqual(mock_notify.call_count, 2)


class BlueprintCopyMyRequestsTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("buyer", password="secret123")
        assign_main_character(self.user, character_id=104001)
        grant_indy_permissions(self.user, "can_manage_copy_requests")
        self.client.force_login(self.user)

        self.provider = User.objects.create_user("seller", password="sell123")
        CharacterSettings.objects.create(
            user=self.provider,
            character_id=0,
            allow_copy_requests=True,
            copy_sharing_scope=CharacterSettings.SCOPE_CORPORATION,
        )
        Blueprint.objects.create(
            owner_user=self.provider,
            character_id=8801,
            item_id=50001,
            blueprint_id=60001,
            type_id=700001,
            location_id=123456,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=10,
            material_efficiency=8,
            runs=0,
            character_name="Provider",
            type_name="Sample Blueprint",
        )

    def test_update_requires_post(self) -> None:
        request_obj = BlueprintCopyRequest.objects.create(
            type_id=700001,
            material_efficiency=8,
            time_efficiency=10,
            requested_by=self.user,
            runs_requested=2,
            copies_requested=1,
        )

        response = self.client.get(
            reverse("indy_hub:bp_update_copy_request", args=[request_obj.id])
        )

        self.assertRedirects(response, reverse("indy_hub:bp_copy_my_requests"))
        request_obj.refresh_from_db()
        self.assertEqual(request_obj.runs_requested, 2)
        self.assertEqual(request_obj.copies_requested, 1)

    def test_update_changes_runs_and_copies_and_notifies(self) -> None:
        request_obj = BlueprintCopyRequest.objects.create(
            type_id=700001,
            material_efficiency=8,
            time_efficiency=10,
            requested_by=self.user,
            runs_requested=2,
            copies_requested=1,
        )

        with patch("indy_hub.views.industry.notify_user") as mock_notify:
            response = self.client.post(
                reverse("indy_hub:bp_update_copy_request", args=[request_obj.id]),
                {"runs_requested": 5, "copies_requested": 4},
            )

            self.assertRedirects(response, reverse("indy_hub:bp_copy_my_requests"))

            request_obj.refresh_from_db()
            self.assertEqual(request_obj.runs_requested, 5)
            self.assertEqual(request_obj.copies_requested, 4)
            mock_notify.assert_called()

    def test_cancel_redirects_back_to_my_requests(self) -> None:
        request_obj = BlueprintCopyRequest.objects.create(
            type_id=700001,
            material_efficiency=8,
            time_efficiency=10,
            requested_by=self.user,
            runs_requested=2,
            copies_requested=1,
        )

        response = self.client.post(
            reverse("indy_hub:bp_cancel_copy_request", args=[request_obj.id]),
            {"next": reverse("indy_hub:bp_copy_my_requests")},
        )

        self.assertRedirects(response, reverse("indy_hub:bp_copy_my_requests"))
        self.assertFalse(
            BlueprintCopyRequest.objects.filter(id=request_obj.id).exists()
        )


class StructureLookupForbiddenCacheTests(TestCase):
    def tearDown(self) -> None:
        reset_forbidden_structure_lookup_cache()
        eve_utils._LOCATION_NAME_CACHE.clear()

    def test_character_skipped_after_forbidden_error(self) -> None:
        reset_forbidden_structure_lookup_cache()
        structure_id = 610000001
        character_id = 7001

        with patch(
            "indy_hub.utils.eve.shared_client.fetch_structure_name"
        ) as mock_fetch:
            mock_fetch.side_effect = ESIForbiddenError(
                "forbidden",
                character_id=character_id,
                structure_id=structure_id,
            )

            result = eve_utils.resolve_location_name(
                structure_id,
                character_id=character_id,
                owner_user_id=None,
                force_refresh=True,
            )
            self.assertEqual(result, f"Structure {structure_id}")
            self.assertEqual(mock_fetch.call_count, 1)

            mock_fetch.side_effect = RuntimeError(
                "fetch_structure_name should not run again"
            )

            second_result = eve_utils.resolve_location_name(
                structure_id,
                character_id=character_id,
                owner_user_id=None,
                force_refresh=True,
            )
            self.assertEqual(second_result, f"Structure {structure_id}")
            self.assertEqual(mock_fetch.call_count, 1)


class ManualRefreshCooldownTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("manual", password="secret123")
        reset_manual_refresh_cooldown(MANUAL_REFRESH_KIND_BLUEPRINTS, self.user.id)
        reset_manual_refresh_cooldown(MANUAL_REFRESH_KIND_JOBS, self.user.id)

    def tearDown(self) -> None:
        reset_manual_refresh_cooldown(MANUAL_REFRESH_KIND_BLUEPRINTS, self.user.id)
        reset_manual_refresh_cooldown(MANUAL_REFRESH_KIND_JOBS, self.user.id)

    def test_manual_refresh_sets_cooldown(self) -> None:
        with patch(
            "indy_hub.tasks.industry.update_blueprints_for_user.apply_async"
        ) as mock_apply:
            scheduled, remaining = request_manual_refresh(
                MANUAL_REFRESH_KIND_BLUEPRINTS,
                self.user.id,
            )
        self.assertTrue(scheduled)
        self.assertIsNone(remaining)
        mock_apply.assert_called_once()

        allowed, cooldown = manual_refresh_allowed(
            MANUAL_REFRESH_KIND_BLUEPRINTS, self.user.id
        )
        self.assertFalse(allowed)
        self.assertIsNotNone(cooldown)

    def test_reset_clears_cooldown(self) -> None:
        with patch(
            "indy_hub.tasks.industry.update_industry_jobs_for_user.apply_async"
        ) as mock_apply:
            scheduled, _ = request_manual_refresh(
                MANUAL_REFRESH_KIND_JOBS,
                self.user.id,
            )
        self.assertTrue(scheduled)
        mock_apply.assert_called_once()

        reset_manual_refresh_cooldown(MANUAL_REFRESH_KIND_JOBS, self.user.id)

        allowed, cooldown = manual_refresh_allowed(
            MANUAL_REFRESH_KIND_JOBS, self.user.id
        )
        self.assertTrue(allowed)
        self.assertIsNone(cooldown)


class NotificationRoutingTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("notify", password="secret123")

    @patch("indy_hub.notifications._send_via_discordnotify", autospec=True)
    @patch("indy_hub.notifications.Notification.objects.notify_user", autospec=True)
    @patch("indy_hub.notifications._send_via_aadiscordbot", autospec=True)
    def test_prefers_aadiscordbot_without_creating_auth_notification(
        self,
        mock_bot,
        mock_notify,
        mock_discordnotify,
    ) -> None:
        mock_bot.return_value = True

        notify_user(self.user, "Ping", "Message", level="info")

        mock_bot.assert_called_once()
        mock_notify.assert_not_called()
        mock_discordnotify.assert_not_called()

    @patch("indy_hub.notifications._send_via_discordnotify", autospec=True)
    @patch("indy_hub.notifications.Notification.objects.notify_user", autospec=True)
    @patch("indy_hub.notifications._send_via_aadiscordbot", autospec=True)
    def test_falls_back_to_auth_when_bot_unavailable(
        self,
        mock_bot,
        mock_notify,
        mock_discordnotify,
    ) -> None:
        mock_bot.return_value = False
        mock_discordnotify.return_value = False

        notify_user(self.user, "Ping", "Message", level="info")

        mock_bot.assert_called_once()
        mock_notify.assert_called_once()
        mock_discordnotify.assert_called_once()

    @patch("indy_hub.notifications._send_via_discordnotify", autospec=True)
    @patch("indy_hub.notifications.Notification.objects.notify_user", autospec=True)
    @patch("indy_hub.notifications._send_via_aadiscordbot", autospec=True)
    def test_link_information_propagates_to_all_channels(
        self,
        mock_bot,
        mock_notify,
        mock_discordnotify,
    ) -> None:
        mock_bot.return_value = False
        mock_discordnotify.return_value = False

        link = "https://example.com/bp-copy/fulfill/"
        link_label = "Open queue"
        expected_cta = f"{link_label}: {link}"
        expected_message = f"Message body\n\n{expected_cta}"

        notify_user(
            self.user,
            "Ping",
            "Message body",
            level="warning",
            link=link,
            link_label=link_label,
        )

        mock_bot.assert_called_once()
        bot_args, bot_kwargs = mock_bot.call_args
        self.assertEqual(bot_args[2], expected_message)
        self.assertEqual(bot_kwargs.get("link"), link)

        mock_notify.assert_called_once()
        notify_kwargs = mock_notify.call_args.kwargs
        self.assertEqual(notify_kwargs.get("message"), expected_message)
        mock_discordnotify.assert_called_once()


class DashboardNotificationCountsTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("foreman", password="test12345")
        assign_main_character(self.user, character_id=101002)
        CharacterSettings.objects.create(
            user=self.user,
            character_id=0,
            allow_copy_requests=True,
            copy_sharing_scope=CharacterSettings.SCOPE_CORPORATION,
        )
        grant_indy_permissions(self.user, "can_manage_copy_requests")
        self.client.force_login(self.user)

        self.blueprint = Blueprint.objects.create(
            owner_user=self.user,
            character_id=7,
            item_id=4001,
            blueprint_id=5001,
            type_id=123456,
            location_id=6001,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=14,
            material_efficiency=8,
            runs=0,
            character_name="Foreman",
            type_name="Widget Blueprint",
        )

    def test_dashboard_counts_include_fulfill_and_my_requests(self) -> None:
        other_user = User.objects.create_user("buyer", password="buyerpass")
        BlueprintCopyRequest.objects.create(
            type_id=self.blueprint.type_id,
            material_efficiency=self.blueprint.material_efficiency,
            time_efficiency=self.blueprint.time_efficiency,
            requested_by=other_user,
            runs_requested=1,
            copies_requested=2,
        )

        IndustryJob.objects.create(
            owner_user=self.user,
            character_id=self.blueprint.character_id,
            job_id=7770001,
            installer_id=self.user.id,
            station_id=self.blueprint.location_id,
            location_name="Busy Location",
            activity_id=5,
            blueprint_id=self.blueprint.item_id,
            blueprint_type_id=self.blueprint.type_id,
            runs=1,
            status="active",
            duration=3600,
            start_date=timezone.now() - timedelta(minutes=10),
            end_date=timezone.now() + timedelta(hours=2),
            activity_name="Copying",
            blueprint_type_name=self.blueprint.type_name,
            product_type_name="Busy Product",
            character_name=self.blueprint.character_name,
        )
        response = self.client.get(reverse("indy_hub:index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["copy_fulfill_count"], 2)
        self.assertEqual(response.context["copy_my_requests_open"], 1)
        self.assertEqual(response.context["copy_my_requests_pending_delivery"], 1)
        self.assertEqual(response.context["copy_my_requests_total"], 2)


class PersonnalBlueprintViewTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("industrialist", password="secret123")
        assign_main_character(self.user, character_id=102001)
        grant_indy_permissions(self.user)
        self.client.force_login(self.user)

    def test_reaction_blueprint_hides_efficiency_bars(self) -> None:
        Blueprint.objects.create(
            owner_user=self.user,
            character_id=11,
            item_id=91001,
            blueprint_id=91002,
            type_id=999001,
            location_id=91003,
            location_flag="hangar",
            quantity=-1,
            time_efficiency=0,
            material_efficiency=0,
            runs=0,
            character_name="Industrialist",
            type_name="Polymer Reaction",
        )

        with patch("indy_hub.views.industry.connection") as mock_connection:
            cursor = mock_connection.cursor.return_value.__enter__.return_value
            cursor.fetchall.return_value = [(999001,)]

            response = self.client.get(reverse("indy_hub:personnal_bp_list"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "efficiency-grid")
        self.assertContains(response, "type-badge reaction")


class BlueprintCopyMyRequestsViewTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("buyer", password="test12345")
        assign_main_character(self.user, character_id=101003)
        grant_indy_permissions(self.user, "can_manage_copy_requests")
        self.client.force_login(self.user)

    def test_my_requests_metrics_and_statuses(self) -> None:
        # Open request (no offers yet)
        BlueprintCopyRequest.objects.create(
            type_id=11,
            material_efficiency=0,
            time_efficiency=0,
            requested_by=self.user,
            runs_requested=1,
            copies_requested=1,
        )

        # Conditional offer awaiting decision
        pending_req = BlueprintCopyRequest.objects.create(
            type_id=12,
            material_efficiency=2,
            time_efficiency=4,
            requested_by=self.user,
            runs_requested=2,
            copies_requested=1,
        )
        seller = User.objects.create_user("seller", password="sellerpass")
        BlueprintCopyOffer.objects.create(
            request=pending_req,
            owner=seller,
            status="conditional",
            message="2 runs for 10m each",
        )

        # Accepted and awaiting delivery
        BlueprintCopyRequest.objects.create(
            type_id=13,
            material_efficiency=8,
            time_efficiency=10,
            requested_by=self.user,
            runs_requested=3,
            copies_requested=1,
            fulfilled=True,
        )

        # Completed delivery
        BlueprintCopyRequest.objects.create(
            type_id=14,
            material_efficiency=6,
            time_efficiency=8,
            requested_by=self.user,
            runs_requested=1,
            copies_requested=1,
            fulfilled=True,
            delivered=True,
        )

        response = self.client.get(reverse("indy_hub:bp_copy_my_requests"))

        self.assertEqual(response.status_code, 200)
        metrics = response.context["metrics"]
        self.assertEqual(metrics["total"], 4)
        self.assertEqual(metrics["open"], 1)
        self.assertEqual(metrics["action_required"], 1)
        self.assertEqual(metrics["awaiting_delivery"], 1)
        self.assertEqual(metrics["delivered"], 1)

        statuses = {req["status_key"] for req in response.context["my_requests"]}
        self.assertIn("open", statuses)
        self.assertIn("action_required", statuses)
        self.assertIn("awaiting_delivery", statuses)
        self.assertIn("delivered", statuses)


class OnboardingViewsTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("rookie", password="rookiepass")
        assign_main_character(self.user, character_id=2024001)
        grant_indy_permissions(self.user)
        self.client.force_login(self.user)
        self.toggle_url = reverse("indy_hub:onboarding_toggle_task")
        self.visibility_url = reverse("indy_hub:onboarding_set_visibility")

    def test_manual_task_completion_marks_progress(self) -> None:
        response = self.client.post(
            self.toggle_url,
            {
                "task": "review_guides",
                "action": "complete",
            },
        )

        self.assertRedirects(response, reverse("indy_hub:index"))
        progress = UserOnboardingProgress.objects.get(user=self.user)
        self.assertTrue(progress.manual_steps.get("review_guides"))
        self.assertFalse(progress.dismissed)

    def test_non_manual_task_rejected(self) -> None:
        self.client.post(
            self.toggle_url,
            {
                "task": "review_guides",
                "action": "complete",
            },
        )
        response = self.client.post(
            self.toggle_url,
            {
                "task": "connect_blueprints",
                "action": "complete",
            },
        )

        self.assertRedirects(response, reverse("indy_hub:index"))
        progress = UserOnboardingProgress.objects.get(user=self.user)
        self.assertIn("review_guides", progress.manual_steps)
        self.assertNotIn("connect_blueprints", progress.manual_steps)

    def test_visibility_toggle_dismisses_and_restores(self) -> None:
        response = self.client.post(
            self.visibility_url,
            {
                "action": "dismiss",
            },
        )
        self.assertRedirects(response, reverse("indy_hub:index"))
        progress = UserOnboardingProgress.objects.get(user=self.user)
        self.assertTrue(progress.dismissed)

        response = self.client.post(
            self.visibility_url,
            {
                "action": "restore",
            },
        )
        self.assertRedirects(response, reverse("indy_hub:index"))
        progress.refresh_from_db()
        self.assertFalse(progress.dismissed)
