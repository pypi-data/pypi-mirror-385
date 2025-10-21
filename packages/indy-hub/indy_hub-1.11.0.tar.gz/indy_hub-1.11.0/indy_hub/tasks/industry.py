# Tâches asynchrones pour l'industrie (exemple)
# Copie ici les tâches liées à l'industrie extraites de tasks.py
# Place ici les tâches asynchrones spécifiques à l'industrie extraites de tasks.py si besoin

# Standard Library
import logging
import random
from datetime import datetime, timedelta

# Third Party
from celery import shared_task

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

# Alliance Auth
from allianceauth.authentication.models import CharacterOwnership

from ..models import (
    Blueprint,
    CharacterSettings,
    CorporationSharingSetting,
    IndustryJob,
)
from ..services.esi_client import ESIClientError, ESITokenError, shared_client
from ..services.location_population import populate_location_names
from ..utils.eve import (
    PLACEHOLDER_PREFIX,
    batch_cache_type_names,
    get_character_name,
    get_corporation_name,
    get_type_name,
    resolve_location_name,
)

logger = logging.getLogger(__name__)

BLUEPRINT_SCOPE = "esi-characters.read_blueprints.v1"
JOBS_SCOPE = "esi-industry.read_character_jobs.v1"
STRUCTURE_SCOPE = "esi-universe.read_structures.v1"
CORP_BLUEPRINT_SCOPE = "esi-corporations.read_blueprints.v1"
CORP_JOBS_SCOPE = "esi-industry.read_corporation_jobs.v1"
CORP_ROLES_SCOPE = "esi-characters.read_corporation_roles.v1"
CORP_BLUEPRINT_SCOPE_SET = [
    CORP_BLUEPRINT_SCOPE,
    STRUCTURE_SCOPE,
    CORP_ROLES_SCOPE,
]
CORP_JOBS_SCOPE_SET = [
    CORP_JOBS_SCOPE,
    STRUCTURE_SCOPE,
    CORP_ROLES_SCOPE,
]

MANUAL_REFRESH_KIND_BLUEPRINTS = "blueprints"
MANUAL_REFRESH_KIND_JOBS = "jobs"

_MANUAL_REFRESH_CACHE_PREFIX = "indy_hub:manual_refresh"
_DEFAULT_BULK_WINDOWS = {
    MANUAL_REFRESH_KIND_BLUEPRINTS: 720,
    MANUAL_REFRESH_KIND_JOBS: 120,
}

_MANUAL_REFRESH_CACHE_PREFIX = "indy_hub:manual_refresh"
_DEFAULT_BULK_WINDOWS = {
    MANUAL_REFRESH_KIND_BLUEPRINTS: 720,
    MANUAL_REFRESH_KIND_JOBS: 120,
}

_OPTIONAL_CORPORATION_SCOPES = {STRUCTURE_SCOPE}
REQUIRED_CORPORATION_ROLES = {"DIRECTOR", "FACTORY_MANAGER"}
_CORPORATION_ROLE_CACHE: dict[int, set[str]] = {}


def _normalized_roles(roles: list[str] | tuple[str, ...] | None) -> set[str]:
    if not roles:
        return set()
    return {str(role).upper() for role in roles if role}


def get_character_corporation_roles(character_id: int) -> set[str]:
    if character_id in _CORPORATION_ROLE_CACHE:
        return _CORPORATION_ROLE_CACHE[character_id]

    payload = shared_client.fetch_character_corporation_roles(int(character_id))
    collected: set[str] = set()
    for key in ("roles", "roles_at_hq", "roles_at_base", "roles_at_other"):
        collected.update(_normalized_roles(payload.get(key)))

    _CORPORATION_ROLE_CACHE[character_id] = collected
    return collected


def _collect_corporation_contexts(
    user: User, required_scopes: list[str]
) -> dict[int, dict[str, int | str]]:
    """Return mapping of corporation id to token context for the user."""

    contexts: dict[int, dict[str, int | str]] = {}

    ownerships = CharacterOwnership.objects.filter(user=user).select_related(
        "character"
    )

    corp_settings = {
        setting.corporation_id: setting
        for setting in CorporationSharingSetting.objects.filter(user=user)
    }

    try:
        # Alliance Auth
        from esi.models import Token
    except ImportError:  # pragma: no cover - defensive fallback
        logger.debug("ESI Token model unavailable; skipping corp context collection")
        return contexts

    for ownership in ownerships:
        corp_id = getattr(ownership.character, "corporation_id", None)
        if not corp_id:
            continue

        setting = corp_settings.get(corp_id)
        if setting is None:
            corp_name = get_corporation_name(corp_id) or str(corp_id)
            setting, _ = CorporationSharingSetting.objects.get_or_create(
                user=user,
                corporation_id=corp_id,
                defaults={
                    "corporation_name": corp_name,
                    "share_scope": CharacterSettings.SCOPE_NONE,
                    "allow_copy_requests": False,
                },
            )
            corp_settings[corp_id] = setting

        char_id = ownership.character.character_id
        base_qs = Token.objects.filter(character_id=char_id, user=user).order_by(
            "-created"
        )

        scope_groups: list[list[str]]
        if required_scopes:
            base_scopes = list(required_scopes)
            scope_groups = [base_scopes]
            for optional_scope in _OPTIONAL_CORPORATION_SCOPES:
                if optional_scope in base_scopes:
                    reduced = [
                        scope for scope in base_scopes if scope != optional_scope
                    ]
                    if reduced not in scope_groups:
                        scope_groups.append(reduced)
        else:
            scope_groups = [[]]

        token_qs = None
        scopes_used: list[str] | None = None
        for scopes in scope_groups:
            candidate_qs = base_qs
            if scopes:
                candidate_qs = candidate_qs.require_scopes(scopes)
            if candidate_qs.exists():
                token_qs = candidate_qs
                scopes_used = scopes
                break

        if token_qs is None:
            continue

        if (
            setting
            and setting.restricts_characters
            and not setting.is_character_authorized(char_id)
        ):
            logger.debug(
                "Character %s skipped for corporation %s: not whitelisted in Indy Hub",
                char_id,
                corp_id,
            )
            continue

        if scopes_used is not None and scopes_used != required_scopes:
            logger.debug(
                "Character %s uses fallback scopes %s for corporation %s",
                char_id,
                scopes_used,
                corp_id,
            )

        try:
            roles = get_character_corporation_roles(char_id)
        except ESITokenError:
            logger.info(
                "Le personnage %s n'a pas le scope corporation roles requis pour la corp %s",
                char_id,
                corp_id,
            )
            continue
        except ESIClientError as exc:
            logger.warning(
                "Unable to load corporation roles for %s (%s); skipping corp %s",
                char_id,
                exc,
                corp_id,
            )
            continue

        if not roles.intersection(REQUIRED_CORPORATION_ROLES):
            logger.info(
                "Le personnage %s n'a pas les rôles %s pour la corp %s",
                char_id,
                ", ".join(sorted(REQUIRED_CORPORATION_ROLES)),
                corp_id,
            )
            continue

        contexts.setdefault(
            corp_id,
            {
                "character_id": char_id,
                "character_name": get_character_name(char_id),
                "corporation_name": get_corporation_name(corp_id),
            },
        )

    return contexts


def _get_manual_refresh_cooldown_seconds() -> int:
    value = getattr(settings, "INDY_HUB_MANUAL_REFRESH_COOLDOWN_SECONDS", 3600)
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = 3600
    return max(value, 0)


def _get_bulk_window_minutes(kind: str) -> int:
    fallback = _DEFAULT_BULK_WINDOWS.get(kind, 720)
    fallback = getattr(settings, "INDY_HUB_BULK_UPDATE_WINDOW_MINUTES", fallback)
    try:
        specific = getattr(
            settings,
            f"INDY_HUB_{kind.upper()}_BULK_WINDOW_MINUTES",
            fallback,
        )
    except AttributeError:
        specific = fallback
    try:
        minutes = int(specific)
    except (TypeError, ValueError):
        minutes = fallback
    return max(minutes, 0)


def _manual_refresh_cache_key(kind: str, user_id: int) -> str:
    return f"{_MANUAL_REFRESH_CACHE_PREFIX}:{kind}:{user_id}"


def _queue_staggered_user_tasks(
    task, user_ids: list[int], *, window_minutes: int, priority: int | None = None
) -> int:
    if not user_ids:
        return 0

    total = len(user_ids)
    window_seconds = max(window_minutes * 60, 0)

    if total == 1 or window_seconds == 0:
        for user_id in user_ids:
            task.apply_async(args=(user_id,), priority=priority)
        return total

    spacing = window_seconds / total
    for index, user_id in enumerate(user_ids):
        countdown = int(round(index * spacing))
        task.apply_async(args=(user_id,), countdown=countdown, priority=priority)
    return total


def _record_manual_refresh(kind: str, user_id: int) -> None:
    if user_id is None:
        return
    cooldown = _get_manual_refresh_cooldown_seconds()
    if cooldown <= 0:
        return
    now = timezone.now()
    cache.set(
        _manual_refresh_cache_key(kind, user_id),
        now.timestamp(),
        timeout=cooldown,
    )


def _remaining_manual_cooldown(kind: str, user_id: int) -> timedelta | None:
    cached = cache.get(_manual_refresh_cache_key(kind, user_id))
    if cached is None:
        return None
    try:
        last_trigger = datetime.fromtimestamp(float(cached), tz=timezone.utc)
    except (TypeError, ValueError):
        return None
    cooldown = _get_manual_refresh_cooldown_seconds()
    if cooldown <= 0:
        return None
    expiry = last_trigger + timedelta(seconds=cooldown)
    remaining = expiry - timezone.now()
    if remaining.total_seconds() <= 0:
        return None
    return remaining


def manual_refresh_allowed(kind: str, user_id: int) -> tuple[bool, timedelta | None]:
    remaining = _remaining_manual_cooldown(kind, user_id)
    if remaining is None:
        return True, None
    return False, remaining


def reset_manual_refresh_cooldown(kind: str, user_id: int) -> None:
    cache.delete(_manual_refresh_cache_key(kind, user_id))


def queue_blueprint_update_for_user(
    user_id: int,
    *,
    countdown: int = 0,
    priority: int | None = None,
    scope: str | None = None,
) -> None:
    kwargs = {}
    if scope:
        kwargs["scope"] = scope
    update_blueprints_for_user.apply_async(
        args=(user_id,), kwargs=kwargs, countdown=countdown, priority=priority
    )


def queue_industry_job_update_for_user(
    user_id: int,
    *,
    countdown: int = 0,
    priority: int | None = None,
    scope: str | None = None,
) -> None:
    kwargs = {}
    if scope:
        kwargs["scope"] = scope
    update_industry_jobs_for_user.apply_async(
        args=(user_id,), kwargs=kwargs, countdown=countdown, priority=priority
    )


def request_manual_refresh(
    kind: str,
    user_id: int,
    *,
    priority: int | None = None,
    scope: str | None = None,
) -> tuple[bool, timedelta | None]:
    allowed, remaining = manual_refresh_allowed(kind, user_id)
    if not allowed:
        return False, remaining

    if kind == MANUAL_REFRESH_KIND_BLUEPRINTS:
        queue_blueprint_update_for_user(user_id, priority=priority, scope=scope)
    elif kind == MANUAL_REFRESH_KIND_JOBS:
        queue_industry_job_update_for_user(user_id, priority=priority, scope=scope)
    else:
        raise ValueError(f"Unknown manual refresh kind: {kind}")

    _record_manual_refresh(kind, user_id)
    return True, None


def _get_location_lookup_budget() -> int:
    try:
        value = int(getattr(settings, "INDY_HUB_LOCATION_LOOKUP_BUDGET", 50))
    except (TypeError, ValueError):
        value = 50
    return max(value, 0)


def _coerce_job_datetime(value):
    if not value:
        return None

    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        dt = parse_datetime(value)
        if dt is None:
            return None
    else:
        return None

    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.utc)
    return dt


@shared_task(bind=True, max_retries=3)
def update_blueprints_for_user(self, user_id, scope: str | None = None):
    base_scopes = [BLUEPRINT_SCOPE]
    scope_preferences = [
        base_scopes + [STRUCTURE_SCOPE],
        base_scopes,
    ]
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist as exc:  # pragma: no cover - defensive guard
        logger.warning(
            "Utilisateur %s introuvable pour la synchronisation des plans", user_id
        )
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))

    normalized_scope = (scope or "").strip().lower()
    if normalized_scope not in {"character", "corporation"}:
        normalized_scope = None

    scope_label = normalized_scope or "all"
    logger.info(
        "Synchronisation des blueprints pour %s (scope=%s)",
        user.username,
        scope_label,
    )
    updated_count = 0
    deleted_total = 0
    error_messages: list[str] = []
    corp_contexts: dict[int, dict[str, int | str]] = {}

    process_characters = normalized_scope in {None, "character"}
    process_corporations = normalized_scope in {None, "corporation"}

    if process_corporations and user.has_perm("indy_hub.can_manage_corporate_assets"):
        corp_contexts = _collect_corporation_contexts(user, CORP_BLUEPRINT_SCOPE_SET)
        logger.info(
            "Contexte corporation détecté pour %s: %s",
            user.username,
            ", ".join(str(key) for key in corp_contexts.keys()) or "aucun",
        )
        if not corp_contexts:
            logger.debug(
                "Aucun contexte corporation disponible pour %s lors d'une synchronisation scope=%s",
                user.username,
                scope_label,
            )
    elif normalized_scope == "corporation":
        message = (
            "Synchronisation des blueprints corporate ignorée pour %s: permission manquante"
            % user.username
        )
        logger.info(message)
        error_messages.append(message)

    ownerships = (
        CharacterOwnership.objects.filter(user=user) if process_characters else []
    )
    for ownership in ownerships:
        char_id = ownership.character.character_id
        character_name = get_character_name(char_id)
        try:
            # Alliance Auth
            from esi.models import Token

            token_qs = Token.objects.filter(character_id=char_id, user=user).order_by(
                "-created"
            )

            chosen_scopes: list[str] | None = None
            for scope_set in scope_preferences:
                candidate_qs = token_qs
                if scope_set:
                    candidate_qs = candidate_qs.require_scopes(scope_set)
                if candidate_qs.exists():
                    chosen_scopes = scope_set
                    break

            if chosen_scopes is None:
                message = (
                    f"{character_name} ({char_id}) sans jeton pour les scopes "
                    f"{', '.join(base_scopes)}"
                )
                logger.debug(message)
                error_messages.append(message)
                continue

            if STRUCTURE_SCOPE not in chosen_scopes:
                logger.debug(
                    "Synchronisation des blueprints pour %s via token sans scope structure",
                    character_name,
                )

            blueprints = shared_client.fetch_character_blueprints(char_id)
        except ESITokenError as exc:
            message = f"Jeton invalide pour {character_name} ({char_id}): {exc}"
            logger.warning(message)
            error_messages.append(message)
            continue
        except ESIClientError as exc:
            message = f"Erreur ESI pour {character_name} ({char_id}): {exc}"
            logger.error(message)
            error_messages.append(message)
            continue
        except Exception as exc:  # pragma: no cover - unexpected
            message = f"Erreur inattendue pour {character_name} ({char_id}): {exc}"
            logger.exception(message)
            error_messages.append(message)
            continue

        esi_ids = set()
        with transaction.atomic():
            for bp in blueprints:
                item_id = bp.get("item_id")
                if item_id is None:
                    logger.debug(
                        "Blueprint sans item_id ignoré pour %s (%s)",
                        character_name,
                        bp,
                    )
                    continue
                esi_ids.add(item_id)
                location_id = bp.get("location_id")
                location_name = resolve_location_name(
                    location_id,
                    character_id=char_id,
                    owner_user_id=user.id,
                )
                Blueprint.objects.update_or_create(
                    item_id=item_id,
                    defaults={
                        "owner_user": user,
                        "owner_kind": Blueprint.OwnerKind.CHARACTER,
                        "corporation_id": None,
                        "corporation_name": "",
                        "character_id": char_id,
                        "blueprint_id": bp.get("blueprint_id"),
                        "type_id": bp.get("type_id"),
                        "location_id": location_id,
                        "location_name": location_name,
                        "location_flag": bp.get("location_flag", ""),
                        "quantity": bp.get("quantity"),
                        "time_efficiency": bp.get("time_efficiency", 0),
                        "material_efficiency": bp.get("material_efficiency", 0),
                        "runs": bp.get("runs", 0),
                        "character_name": character_name,
                        "type_name": get_type_name(bp.get("type_id")),
                    },
                )

            deleted, _ = (
                Blueprint.objects.filter(
                    owner_user=user,
                    owner_kind=Blueprint.OwnerKind.CHARACTER,
                    character_id=char_id,
                )
                .exclude(item_id__in=esi_ids)
                .delete()
            )
        deleted_total += deleted
        updated_count += len(blueprints)
        logger.debug(
            "Synchronisation des blueprints terminée pour %s (%s mis à jour, %s supprimés)",
            character_name,
            len(blueprints),
            deleted,
        )

    if process_corporations and corp_contexts:
        for corp_id, context in corp_contexts.items():
            corp_char_id = context.get("character_id")
            corp_name = context.get("corporation_name") or str(corp_id)
            acting_character_name = context.get("character_name") or ""

            if not corp_char_id:
                logger.debug(
                    "Contexte incomplet pour la corporation %s (aucun character_id)",
                    corp_id,
                )
                continue

            try:
                corp_blueprints = shared_client.fetch_corporation_blueprints(
                    int(corp_id), character_id=int(corp_char_id)
                )
            except ESITokenError as exc:
                message = f"Jeton invalide pour la corporation {corp_name} ({corp_id}) via {acting_character_name}: {exc}"
                logger.warning(message)
                error_messages.append(message)
                continue
            except ESIClientError as exc:
                message = f"Erreur ESI pour la corporation {corp_name} ({corp_id}) via {acting_character_name}: {exc}"
                logger.error(message)
                error_messages.append(message)
                continue
            except Exception as exc:  # pragma: no cover - unexpected
                message = f"Erreur inattendue pour la corporation {corp_name} ({corp_id}) via {acting_character_name}: {exc}"
                logger.exception(message)
                error_messages.append(message)
                continue

            corp_esi_ids: set[int] = set()
            with transaction.atomic():
                for bp in corp_blueprints:
                    item_id = bp.get("item_id")
                    if item_id is None:
                        logger.debug(
                            "Blueprint corporate sans item_id ignoré pour %s (%s)",
                            corp_name,
                            bp,
                        )
                        continue
                    corp_esi_ids.add(item_id)
                    location_id = bp.get("location_id")
                    location_name = resolve_location_name(
                        location_id,
                        character_id=int(corp_char_id),
                        owner_user_id=user.id,
                    )
                    Blueprint.objects.update_or_create(
                        item_id=item_id,
                        defaults={
                            "owner_user": user,
                            "owner_kind": Blueprint.OwnerKind.CORPORATION,
                            "corporation_id": corp_id,
                            "corporation_name": corp_name,
                            "character_id": None,
                            "character_name": acting_character_name,
                            "blueprint_id": bp.get("blueprint_id"),
                            "type_id": bp.get("type_id"),
                            "location_id": location_id,
                            "location_name": location_name,
                            "location_flag": bp.get("location_flag", ""),
                            "quantity": bp.get("quantity"),
                            "time_efficiency": bp.get("time_efficiency", 0),
                            "material_efficiency": bp.get("material_efficiency", 0),
                            "runs": bp.get("runs", 0),
                            "type_name": get_type_name(bp.get("type_id")),
                        },
                    )

                deleted, _ = (
                    Blueprint.objects.filter(
                        owner_kind=Blueprint.OwnerKind.CORPORATION,
                        corporation_id=corp_id,
                    )
                    .exclude(item_id__in=corp_esi_ids)
                    .delete()
                )

            updated_count += len(corp_blueprints)
            deleted_total += deleted
            logger.debug(
                "Synchronisation des blueprints corporate terminée pour %s (%s mis à jour, %s supprimés)",
                corp_name,
                len(corp_blueprints),
                deleted,
            )

    logger.info(
        "Blueprints synchronisés pour %s: %s éléments mis à jour, %s supprimés",
        user.username,
        updated_count,
        deleted_total,
    )
    if error_messages:
        logger.warning(
            "Incidents lors de la synchronisation des blueprints %s: %s",
            user.username,
            "; ".join(error_messages),
        )

    return {
        "success": True,
        "blueprints_updated": updated_count,
        "deleted": deleted_total,
        "errors": error_messages,
    }


@shared_task(bind=True, max_retries=3)
def update_industry_jobs_for_user(self, user_id, scope: str | None = None):
    try:
        user = User.objects.get(id=user_id)
        logger.info("Starting industry jobs update for user %s", user.username)
        updated_count = 0
        deleted_total = 0
        error_messages: list[str] = []
        location_cache: dict[int, str] = {}
        lookup_budget = _get_location_lookup_budget()
        lookup_budget_warned = False
        ownerships = CharacterOwnership.objects.filter(user=user)
        base_scopes = [JOBS_SCOPE]
        scope_preferences = [
            base_scopes + [STRUCTURE_SCOPE],
            base_scopes,
        ]
        corp_contexts: dict[int, dict[str, int | str]] = {}

        normalized_scope = (scope or "").strip().lower()
        if normalized_scope not in {"character", "corporation"}:
            normalized_scope = None
        scope_label = normalized_scope or "all"
        logger.debug(
            "Industry jobs update for %s using scope=%s",
            user.username,
            scope_label,
        )

        process_characters = normalized_scope in {None, "character"}
        process_corporations = normalized_scope in {None, "corporation"}

        if not process_characters:
            ownerships = []

        if process_corporations and user.has_perm(
            "indy_hub.can_manage_corporate_assets"
        ):
            corp_contexts = _collect_corporation_contexts(user, CORP_JOBS_SCOPE_SET)
            logger.info(
                "Contexte corporation (jobs) détecté pour %s: %s",
                user.username,
                ", ".join(str(key) for key in corp_contexts.keys()) or "aucun",
            )
            if not corp_contexts:
                logger.debug(
                    "No corporate contexts found for %s during scope=%s job sync",
                    user.username,
                    scope_label,
                )
        elif normalized_scope == "corporation":
            message = (
                "Corporate industry job sync skipped for %s due to missing permission"
                % user.username
            )
            logger.info(message)
            error_messages.append(message)

        for ownership in ownerships:
            char_id = ownership.character.character_id
            character_name = get_character_name(char_id)
            try:
                # Alliance Auth
                from esi.models import Token

                token_qs = Token.objects.filter(
                    character_id=char_id, user=user
                ).order_by("-created")

                chosen_scopes: list[str] | None = None
                for scope_set in scope_preferences:
                    candidate_qs = token_qs
                    if scope_set:
                        candidate_qs = candidate_qs.require_scopes(scope_set)
                    if candidate_qs.exists():
                        chosen_scopes = scope_set
                        break

                if chosen_scopes is None:
                    message = (
                        f"{character_name} ({char_id}) sans jeton pour les scopes "
                        f"{', '.join(base_scopes)}"
                    )
                    logger.debug(message)
                    error_messages.append(message)
                    continue

                if STRUCTURE_SCOPE not in chosen_scopes:
                    logger.debug(
                        "Synchronisation des jobs pour %s via token sans scope structure",
                        character_name,
                    )

                jobs = shared_client.fetch_character_industry_jobs(char_id)
            except ESITokenError as exc:
                message = f"Jeton invalide pour {character_name} ({char_id}): {exc}"
                logger.warning(message)
                error_messages.append(message)
                continue
            except ESIClientError as exc:
                message = f"Erreur ESI pour {character_name} ({char_id}): {exc}"
                logger.error(message)
                error_messages.append(message)
                continue
            except Exception as exc:  # pragma: no cover - unexpected
                message = f"Erreur inattendue pour {character_name} ({char_id}): {exc}"
                logger.exception(message)
                error_messages.append(message)
                continue

            esi_job_ids = set()
            with transaction.atomic():
                for job in jobs:
                    job_id = job.get("job_id")
                    if job_id is None:
                        logger.debug(
                            "Job sans identifiant ignoré pour %s: %s",
                            character_name,
                            job,
                        )
                        continue
                    esi_job_ids.add(job_id)
                    station_id = job.get("station_id") or job.get("facility_id")
                    location_name = ""
                    if station_id is not None:
                        try:
                            location_key = int(station_id)
                        except (TypeError, ValueError):
                            location_key = None

                        if location_key is not None:
                            cached_name = location_cache.get(location_key)
                            if cached_name is not None:
                                location_name = cached_name
                            elif lookup_budget > 0:
                                try:
                                    resolved_name = resolve_location_name(
                                        location_key,
                                        character_id=char_id,
                                        owner_user_id=user.id,
                                    )
                                except (
                                    Exception
                                ):  # pragma: no cover - defensive fallback
                                    logger.debug(
                                        "Location resolution failed for %s via %s",
                                        location_key,
                                        character_name,
                                        exc_info=True,
                                    )
                                    resolved_name = None

                                lookup_budget -= 1
                                location_name = (
                                    resolved_name
                                    if resolved_name
                                    else f"{PLACEHOLDER_PREFIX}{location_key}"
                                )
                                location_cache[location_key] = location_name
                            else:
                                if not lookup_budget_warned:
                                    logger.warning(
                                        "Location lookup budget exhausted while syncing industry jobs for %s; remaining locations will use placeholders.",
                                        user.username,
                                    )
                                    lookup_budget_warned = True
                                location_name = location_cache.setdefault(
                                    location_key,
                                    f"{PLACEHOLDER_PREFIX}{location_key}",
                                )
                    start_date = _coerce_job_datetime(job.get("start_date"))
                    end_date = _coerce_job_datetime(job.get("end_date"))
                    pause_date = _coerce_job_datetime(job.get("pause_date"))
                    completed_date = _coerce_job_datetime(job.get("completed_date"))

                    if start_date is None:
                        logger.warning(
                            "Skipping job %s for %s due to invalid start date %r",
                            job_id,
                            character_name,
                            job.get("start_date"),
                        )
                        continue

                    if end_date is None:
                        logger.warning(
                            "Job %s for %s missing end date; defaulting to start date.",
                            job_id,
                            character_name,
                        )
                        end_date = start_date

                    IndustryJob.objects.update_or_create(
                        job_id=job_id,
                        defaults={
                            "owner_user": user,
                            "owner_kind": Blueprint.OwnerKind.CHARACTER,
                            "corporation_id": None,
                            "corporation_name": "",
                            "character_id": char_id,
                            "installer_id": job.get("installer_id"),
                            "station_id": station_id,
                            "location_name": location_name,
                            "activity_id": job.get("activity_id"),
                            "blueprint_id": job.get("blueprint_id"),
                            "blueprint_type_id": job.get("blueprint_type_id"),
                            "runs": job.get("runs"),
                            "cost": job.get("cost"),
                            "licensed_runs": job.get("licensed_runs"),
                            "probability": job.get("probability"),
                            "product_type_id": job.get("product_type_id"),
                            "status": job.get("status"),
                            "duration": job.get("duration"),
                            "start_date": start_date,
                            "end_date": end_date,
                            "pause_date": pause_date,
                            "completed_date": completed_date,
                            "completed_character_id": job.get("completed_character_id"),
                            "successful_runs": job.get("successful_runs"),
                            "blueprint_type_name": get_type_name(
                                job.get("blueprint_type_id")
                            ),
                            "product_type_name": get_type_name(
                                job.get("product_type_id")
                            ),
                            "character_name": character_name,
                        },
                    )

                deleted, _ = (
                    IndustryJob.objects.filter(
                        owner_user=user,
                        owner_kind=Blueprint.OwnerKind.CHARACTER,
                        character_id=char_id,
                    )
                    .exclude(job_id__in=esi_job_ids)
                    .delete()
                )

            deleted_total += deleted
            updated_count += len(jobs)
            logger.debug(
                "Synchronisation des jobs terminée pour %s (%s mis à jour, %s supprimés)",
                character_name,
                len(jobs),
                deleted,
            )

        if process_corporations and corp_contexts:
            for corp_id, context in corp_contexts.items():
                corp_char_id = context.get("character_id")
                corp_name = context.get("corporation_name") or str(corp_id)
                acting_character_name = context.get("character_name") or ""

                if not corp_char_id:
                    logger.debug(
                        "Contexte incomplet pour les jobs corporate de %s (aucun character_id)",
                        corp_id,
                    )
                    continue

                try:
                    corp_jobs = shared_client.fetch_corporation_industry_jobs(
                        int(corp_id), character_id=int(corp_char_id)
                    )
                except ESITokenError as exc:
                    message = f"Jeton invalide pour la corporation {corp_name} ({corp_id}) via {acting_character_name}: {exc}"
                    logger.warning(message)
                    error_messages.append(message)
                    continue
                except ESIClientError as exc:
                    message = f"Erreur ESI pour la corporation {corp_name} ({corp_id}) via {acting_character_name}: {exc}"
                    logger.error(message)
                    error_messages.append(message)
                    continue
                except Exception as exc:  # pragma: no cover - unexpected
                    message = f"Erreur inattendue pour la corporation {corp_name} ({corp_id}) via {acting_character_name}: {exc}"
                    logger.exception(message)
                    error_messages.append(message)
                    continue

                corp_job_ids: set[int] = set()
                with transaction.atomic():
                    for job in corp_jobs:
                        job_id = job.get("job_id")
                        if job_id is None:
                            logger.debug(
                                "Job corporate sans identifiant ignoré pour %s: %s",
                                corp_name,
                                job,
                            )
                            continue

                        corp_job_ids.add(job_id)
                        station_id = job.get("station_id") or job.get("facility_id")
                        location_name = ""
                        if station_id is not None:
                            try:
                                location_key = int(station_id)
                            except (TypeError, ValueError):
                                location_key = None

                            if location_key is not None:
                                cached_name = location_cache.get(location_key)
                                if cached_name is not None:
                                    location_name = cached_name
                                elif lookup_budget > 0:
                                    try:
                                        resolved_name = resolve_location_name(
                                            location_key,
                                            character_id=int(corp_char_id),
                                            owner_user_id=user.id,
                                        )
                                    except Exception:  # pragma: no cover
                                        logger.debug(
                                            "Location resolution failed for %s via %s",
                                            location_key,
                                            acting_character_name,
                                            exc_info=True,
                                        )
                                        resolved_name = None

                                    lookup_budget -= 1
                                    location_name = (
                                        resolved_name
                                        if resolved_name
                                        else f"{PLACEHOLDER_PREFIX}{location_key}"
                                    )
                                    location_cache[location_key] = location_name
                                else:
                                    if not lookup_budget_warned:
                                        logger.warning(
                                            "Location lookup budget exhausted while syncing corporate jobs for %s; remaining locations will use placeholders.",
                                            corp_name,
                                        )
                                        lookup_budget_warned = True
                                    location_name = location_cache.setdefault(
                                        location_key,
                                        f"{PLACEHOLDER_PREFIX}{location_key}",
                                    )

                        start_date = _coerce_job_datetime(job.get("start_date"))
                        end_date = _coerce_job_datetime(job.get("end_date"))
                        pause_date = _coerce_job_datetime(job.get("pause_date"))
                        completed_date = _coerce_job_datetime(job.get("completed_date"))

                        if start_date is None:
                            logger.warning(
                                "Ignoring corporate job %s for %s due to invalid start date %r",
                                job_id,
                                corp_name,
                                job.get("start_date"),
                            )
                            continue

                        if end_date is None:
                            logger.warning(
                                "Corporate job %s for %s missing end date; defaulting to start date.",
                                job_id,
                                corp_name,
                            )
                            end_date = start_date

                        IndustryJob.objects.update_or_create(
                            job_id=job_id,
                            defaults={
                                "owner_user": user,
                                "owner_kind": Blueprint.OwnerKind.CORPORATION,
                                "corporation_id": corp_id,
                                "corporation_name": corp_name,
                                "character_id": None,
                                "character_name": acting_character_name,
                                "installer_id": job.get("installer_id"),
                                "station_id": station_id,
                                "location_name": location_name,
                                "activity_id": job.get("activity_id"),
                                "blueprint_id": job.get("blueprint_id"),
                                "blueprint_type_id": job.get("blueprint_type_id"),
                                "runs": job.get("runs"),
                                "cost": job.get("cost"),
                                "licensed_runs": job.get("licensed_runs"),
                                "probability": job.get("probability"),
                                "product_type_id": job.get("product_type_id"),
                                "status": job.get("status"),
                                "duration": job.get("duration"),
                                "start_date": start_date,
                                "end_date": end_date,
                                "pause_date": pause_date,
                                "completed_date": completed_date,
                                "completed_character_id": job.get(
                                    "completed_character_id"
                                ),
                                "successful_runs": job.get("successful_runs"),
                                "blueprint_type_name": get_type_name(
                                    job.get("blueprint_type_id")
                                ),
                                "product_type_name": get_type_name(
                                    job.get("product_type_id")
                                ),
                            },
                        )

                deleted, _ = (
                    IndustryJob.objects.filter(
                        owner_kind=Blueprint.OwnerKind.CORPORATION,
                        corporation_id=corp_id,
                    )
                    .exclude(job_id__in=corp_job_ids)
                    .delete()
                )

                updated_count += len(corp_jobs)
                deleted_total += deleted
                logger.debug(
                    "Synchronisation des jobs corporate terminée pour %s (%s mis à jour, %s supprimés)",
                    corp_name,
                    len(corp_jobs),
                    deleted,
                )

        logger.info(
            "Jobs synchronisés pour %s: %s mis à jour, %s supprimés",
            user.username,
            updated_count,
            deleted_total,
        )
        if error_messages:
            logger.warning(
                "Incidents lors de la synchronisation des jobs %s: %s",
                user.username,
                "; ".join(error_messages),
            )
        return {
            "success": True,
            "jobs_updated": updated_count,
            "deleted": deleted_total,
            "errors": error_messages,
        }
    except Exception as e:
        logger.error(f"Error updating jobs for user {user_id}: {e}")
        # Error tracking removed in unified settings
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))


@shared_task
def cleanup_old_jobs():
    """
    Supprime uniquement les jobs orphelins :
    - jobs dont le owner_user n'existe plus
    - jobs dont le character_id ne correspond à aucun CharacterOwnership
    - jobs dont le token ESI n'existe plus pour ce user/char
    """
    # Alliance Auth
    from allianceauth.authentication.models import CharacterOwnership
    from esi.models import Token

    # Jobs sans user
    jobs_no_user = IndustryJob.objects.filter(owner_user__isnull=True)
    count_no_user = jobs_no_user.count()
    jobs_no_user.delete()

    # Jobs sans character ownership (uniquement ceux liés à un personnage)
    char_ids = set(
        CharacterOwnership.objects.values_list("character__character_id", flat=True)
    )
    jobs_no_char = IndustryJob.objects.filter(character_id__isnull=False).exclude(
        character_id__in=char_ids
    )
    count_no_char = jobs_no_char.count()
    jobs_no_char.delete()

    # Jobs sans token valide (uniquement ceux associés à un personnage)
    token_pairs = {
        (user_id, character_id)
        for user_id, character_id in Token.objects.values_list(
            "user_id", "character_id"
        )
    }

    orphan_job_ids: list[int] = []
    for job_id, owner_user_id, character_id in IndustryJob.objects.filter(
        character_id__isnull=False,
        owner_user__isnull=False,
    ).values_list("id", "owner_user_id", "character_id"):
        if (owner_user_id, character_id) not in token_pairs:
            orphan_job_ids.append(job_id)

    deleted_tokenless = 0
    if orphan_job_ids:
        deleted_tokenless = IndustryJob.objects.filter(id__in=orphan_job_ids).delete()[
            0
        ]

    total_deleted = count_no_user + count_no_char + deleted_tokenless
    logger.info(
        f"Cleaned up {total_deleted} orphaned industry jobs (no user: {count_no_user}, no char: {count_no_char}, no token: {deleted_tokenless})"
    )
    return {
        "deleted_jobs": total_deleted,
        "no_user": count_no_user,
        "no_char": count_no_char,
        "no_token": deleted_tokenless,
    }


@shared_task
def update_type_names():
    blueprints_without_names = Blueprint.objects.filter(type_name="")
    type_ids = list(blueprints_without_names.values_list("type_id", flat=True))
    if type_ids:
        batch_cache_type_names(type_ids)
        for bp in blueprints_without_names:
            bp.refresh_from_db()
    jobs_without_names = IndustryJob.objects.filter(blueprint_type_name="")
    job_type_ids = list(jobs_without_names.values_list("blueprint_type_id", flat=True))
    product_type_ids = list(
        jobs_without_names.exclude(product_type_id__isnull=True).values_list(
            "product_type_id", flat=True
        )
    )
    all_type_ids = list(set(job_type_ids + product_type_ids))
    if all_type_ids:
        batch_cache_type_names(all_type_ids)
        for job in jobs_without_names:
            job.refresh_from_db()
    logger.info("Updated type names for blueprints and jobs")


@shared_task(bind=True, max_retries=0)
def populate_location_names_async(
    self, location_ids=None, force_refresh=False, dry_run=False
):
    """Populate location names for blueprints and industry jobs asynchronously."""

    logger.info(
        "Starting async population job for location names%s",
        f" (limited to {len(location_ids)} IDs)" if location_ids else "",
    )

    normalized_ids = None
    if location_ids is not None:
        normalized_ids = [int(value) for value in location_ids if value]
        if not normalized_ids:
            logger.info("No valid location IDs supplied; skipping population job")
            return {"blueprints": 0, "jobs": 0, "locations": 0}

    summary = populate_location_names(
        location_ids=normalized_ids,
        force_refresh=force_refresh,
        dry_run=dry_run,
        schedule_async=not force_refresh,
    )

    logger.info(
        "Location population completed: %s blueprints, %s jobs (%s locations)",
        summary.get("blueprints", 0),
        summary.get("jobs", 0),
        summary.get("locations", 0),
    )
    return summary


@shared_task
def update_all_blueprints():
    """
    Update blueprints for all users - scheduled via Celery beat
    """
    logger.info("Starting bulk blueprint update for all users")

    user_ids = list(
        User.objects.filter(token__isnull=False).distinct().values_list("id", flat=True)
    )
    random.shuffle(user_ids)

    window_minutes = _get_bulk_window_minutes("blueprints")
    queued = _queue_staggered_user_tasks(
        update_blueprints_for_user,
        user_ids,
        window_minutes=window_minutes,
        priority=7,
    )

    logger.info(
        "Queued blueprint updates for %s users across a %s minute window",
        queued,
        window_minutes,
    )
    return {"users_queued": queued, "window_minutes": window_minutes}


@shared_task
def update_all_industry_jobs():
    """
    Update industry jobs for all users - scheduled via Celery beat
    """
    logger.info("Starting bulk industry jobs update for all users")

    user_ids = list(
        User.objects.filter(token__isnull=False).distinct().values_list("id", flat=True)
    )
    random.shuffle(user_ids)

    window_minutes = _get_bulk_window_minutes("industry_jobs")
    queued = _queue_staggered_user_tasks(
        update_industry_jobs_for_user,
        user_ids,
        window_minutes=window_minutes,
        priority=7,
    )

    logger.info(
        "Queued industry job updates for %s users across a %s minute window",
        queued,
        window_minutes,
    )
    return {"users_queued": queued, "window_minutes": window_minutes}
