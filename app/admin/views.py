from datetime import datetime, timezone
from uuid import UUID

import contextlib

from sqlalchemy import BIGINT, Integer, and_, func, or_, select, text, update
from sqlalchemy.orm import noload, selectinload

from fastadmin import (
    SqlAlchemyModelAdmin,
    WidgetActionChartProps,
    WidgetActionFilter,
    WidgetActionInputSchema,
    WidgetActionResponseSchema,
    WidgetActionType,
    WidgetType,
    action,
    register,
    widget_action,
)

from app.authentication.models import AccessToken, OAuthAccount
from app.core.models.db_helper import db_helper
from app.notes.models import Note
from app.users.models import User

try:
    from fastapi_users.password import PasswordHelper as _PasswordHelper
    _password_helper = _PasswordHelper()
except ImportError:
    _password_helper = None


@register(User, sqlalchemy_sessionmaker=db_helper.session_factory)
class UserAdmin(SqlAlchemyModelAdmin):
    menu_section = "Users"
    verbose_name = "User"
    verbose_name_plural = "Users"

    list_display = ("id", "email", "is_active", "is_superuser", "is_verified")
    list_display_links = ("id", "email")
    list_filter = ("is_active", "is_superuser", "is_verified")
    search_fields = ("email",)
    exclude = ("hashed_password",)
    list_per_page = 20

    actions = ("activate_users", "deactivate_users")

    async def orm_get_list(self, offset=None, limit=None, search=None, sort_by=None, filters=None):
        def _resolve(s):
            s = self._resolve_ordering_field(s)
            return (s[1:] + " desc") if s.startswith("-") else s

        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            qs = select(self.model_cls).options(noload(User.oauth_accounts))
            if filters:
                q = []
                for field_with_condition, value in filters.items():
                    field, condition = field_with_condition[0], field_with_condition[1]
                    model_field = getattr(self.model_cls, field)
                    if condition != "in" and isinstance(model_field.expression.type, BIGINT | Integer):
                        with contextlib.suppress(ValueError, TypeError):
                            value = int(value)
                    match condition:
                        case "lte": q.append(model_field <= value)
                        case "gte": q.append(model_field >= value)
                        case "lt":  q.append(model_field < value)
                        case "gt":  q.append(model_field > value)
                        case "exact": q.append(model_field == value)
                        case "in":
                            if isinstance(model_field.expression.type, BIGINT | Integer):
                                with contextlib.suppress(ValueError, TypeError):
                                    value = [int(x) for x in value]
                            q.append(model_field.in_(value))
                        case "contains":  q.append(model_field.like(f"%{value}%"))
                        case "icontains": q.append(model_field.ilike(f"%{value}%"))
                qs = qs.where(and_(*q))
            if search and self.search_fields:
                q = [c for f in self.search_fields if (c := self._build_search_condition(f, search)) is not None]
                if not q:
                    return [], 0
                qs = qs.where(or_(*q))
            if sort_by:
                qs = qs.order_by(text(_resolve(sort_by)))
            elif self.ordering:
                qs = qs.order_by(text(", ".join(_resolve(f) for f in self.ordering)))
            total = (await session.execute(select(func.count()).select_from(qs.subquery()))).scalar_one()
            for field in self.list_select_related or []:
                qs = qs.options(selectinload(getattr(self.model_cls, field)))
            if offset is not None and limit is not None:
                qs = qs.offset(offset).limit(limit)
            result = await session.scalars(qs)
            return list(result.unique()), total

    widget_actions = (
        "chart_user_status",
        "chart_user_roles",
        "chart_user_verification",
    )

    async def authenticate(self, username: str, password: str) -> int | None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            result = await session.scalars(
                select(User).where(
                    User.email == username,
                    User.is_superuser.is_(True),
                    User.is_active.is_(True),
                )
            )
            user = result.first()
            if not user:
                return None
            if _password_helper is None:
                return None
            verified, _ = _password_helper.verify_and_update(password, user.hashed_password)
            return user.id if verified else None

    async def change_password(self, id: UUID | int | str, password: str) -> None:
        if _password_helper is None:
            return
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            hashed = _password_helper.hash(password)
            await session.execute(
                update(User).where(User.id == id).values(hashed_password=hashed)
            )
            await session.commit()

    @action(description="Activate selected users")
    async def activate_users(self, ids: list) -> None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            await session.execute(
                update(User).where(User.id.in_(ids)).values(is_active=True)
            )
            await session.commit()

    @action(description="Deactivate selected users")
    async def deactivate_users(self, ids: list) -> None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            await session.execute(
                update(User).where(User.id.in_(ids)).values(is_active=False)
            )
            await session.commit()

    @widget_action(
        tab="Overview",
        title="Active vs Inactive Users",
        description="Distribution of active and inactive accounts",
        widget_action_type=WidgetActionType.ChartPie,
        widget_action_props=WidgetActionChartProps(
            x_field="status",
            y_field="count",
            series_color={"Active": "#52c41a", "Inactive": "#ff4d4f"},
        ),
        width=8,
    )
    async def chart_user_status(
        self, payload: WidgetActionInputSchema
    ) -> WidgetActionResponseSchema:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            active = await session.scalar(
                select(func.count()).select_from(User).where(User.is_active.is_(True))
            ) or 0
            inactive = await session.scalar(
                select(func.count()).select_from(User).where(User.is_active.is_(False))
            ) or 0
        return WidgetActionResponseSchema(data=[
            {"status": "Active", "count": active},
            {"status": "Inactive", "count": inactive},
        ])

    @widget_action(
        tab="Overview",
        title="Regular vs Superusers",
        description="Breakdown of user roles",
        widget_action_type=WidgetActionType.ChartPie,
        widget_action_props=WidgetActionChartProps(
            x_field="role",
            y_field="count",
            series_color={"Regular": "#1677ff", "Superuser": "#722ed1"},
        ),
        width=8,
    )
    async def chart_user_roles(
        self, payload: WidgetActionInputSchema
    ) -> WidgetActionResponseSchema:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            regular = await session.scalar(
                select(func.count()).select_from(User).where(User.is_superuser.is_(False))
            ) or 0
            superusers = await session.scalar(
                select(func.count()).select_from(User).where(User.is_superuser.is_(True))
            ) or 0
        return WidgetActionResponseSchema(data=[
            {"role": "Regular", "count": regular},
            {"role": "Superuser", "count": superusers},
        ])

    @widget_action(
        tab="Overview",
        title="Email Verification Status",
        description="How many users have verified their email",
        widget_action_type=WidgetActionType.ChartPie,
        widget_action_props=WidgetActionChartProps(
            x_field="verification",
            y_field="count",
            series_color={"Verified": "#13c2c2", "Unverified": "#faad14"},
        ),
        width=8,
    )
    async def chart_user_verification(
        self, payload: WidgetActionInputSchema
    ) -> WidgetActionResponseSchema:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            verified = await session.scalar(
                select(func.count()).select_from(User).where(User.is_verified.is_(True))
            ) or 0
            unverified = await session.scalar(
                select(func.count()).select_from(User).where(User.is_verified.is_(False))
            ) or 0
        return WidgetActionResponseSchema(data=[
            {"verification": "Verified", "count": verified},
            {"verification": "Unverified", "count": unverified},
        ])


@register(Note, sqlalchemy_sessionmaker=db_helper.session_factory)
class NoteAdmin(SqlAlchemyModelAdmin):
    menu_section = "Notes"
    verbose_name = "Note"
    verbose_name_plural = "Notes"

    list_display = ("id", "note_hash", "is_ephemeral", "lifetime", "image")
    list_display_links = ("id",)
    list_filter = ("is_ephemeral",)
    search_fields = ("note_hash",)
    exclude = ("text", "secret")
    list_per_page = 20

    actions = ("delete_expired_notes",)
    widget_actions = (
        "chart_note_types",
        "chart_note_media",
        "chart_note_lifetime",
    )

    @action(description="Delete expired notes")
    async def delete_expired_notes(self, ids: list) -> None:
        now = datetime.now(tz=timezone.utc)
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            result = await session.scalars(
                select(Note).where(
                    Note.id.in_(ids),
                    Note.lifetime.isnot(None),
                    Note.lifetime < now,
                )
            )
            for note in result.all():
                await session.delete(note)
            await session.commit()


    @widget_action(
        tab="Overview",
        title="Ephemeral vs Permanent Notes",
        description="One-time notes vs reusable notes",
        widget_action_type=WidgetActionType.ChartPie,
        widget_action_props=WidgetActionChartProps(
            x_field="type",
            y_field="count",
            series_color={"Ephemeral": "#ff7a45", "Permanent": "#36cfc9"},
        ),
        width=8,
    )
    async def chart_note_types(
        self, payload: WidgetActionInputSchema
    ) -> WidgetActionResponseSchema:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            ephemeral = await session.scalar(
                select(func.count()).select_from(Note).where(Note.is_ephemeral.is_(True))
            ) or 0
            permanent = await session.scalar(
                select(func.count()).select_from(Note).where(Note.is_ephemeral.is_(False))
            ) or 0
        return WidgetActionResponseSchema(data=[
            {"type": "Ephemeral", "count": ephemeral},
            {"type": "Permanent", "count": permanent},
        ])

    @widget_action(
        tab="Overview",
        title="Notes with Attachments",
        description="Notes that have an image attached",
        widget_action_type=WidgetActionType.ChartPie,
        widget_action_props=WidgetActionChartProps(
            x_field="media",
            y_field="count",
            series_color={"With Image": "#9254de", "Text Only": "#597ef7"},
        ),
        width=8,
    )
    async def chart_note_media(
        self, payload: WidgetActionInputSchema
    ) -> WidgetActionResponseSchema:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            with_image = await session.scalar(
                select(func.count()).select_from(Note).where(Note.image.isnot(None))
            ) or 0
            without_image = await session.scalar(
                select(func.count()).select_from(Note).where(Note.image.is_(None))
            ) or 0
        return WidgetActionResponseSchema(data=[
            {"media": "With Image", "count": with_image},
            {"media": "Text Only", "count": without_image},
        ])

    @widget_action(
        tab="Overview",
        title="Lifetime Notes Status",
        description="Active vs expired vs no-expiry notes",
        widget_action_type=WidgetActionType.ChartColumn,
        widget_action_props=WidgetActionChartProps(
            x_field="status",
            y_field="count",
            series_color={"Active": "#52c41a", "Expired": "#ff4d4f", "No Expiry": "#1677ff"},
        ),
        width=8,
    )
    async def chart_note_lifetime(
        self, payload: WidgetActionInputSchema
    ) -> WidgetActionResponseSchema:
        now = datetime.now(tz=timezone.utc)
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            active = await session.scalar(
                select(func.count()).select_from(Note).where(
                    Note.lifetime.isnot(None), Note.lifetime > now
                )
            ) or 0
            expired = await session.scalar(
                select(func.count()).select_from(Note).where(
                    Note.lifetime.isnot(None), Note.lifetime <= now
                )
            ) or 0
            no_expiry = await session.scalar(
                select(func.count()).select_from(Note).where(Note.lifetime.is_(None))
            ) or 0
        return WidgetActionResponseSchema(data=[
            {"status": "Active", "count": active},
            {"status": "Expired", "count": expired},
            {"status": "No Expiry", "count": no_expiry},
        ])


@register(AccessToken, sqlalchemy_sessionmaker=db_helper.session_factory)
class AccessTokenAdmin(SqlAlchemyModelAdmin):
    menu_section = "Auth & Security"
    verbose_name = "Access Token"
    verbose_name_plural = "Access Tokens"

    list_display = ("token", "user_id", "created_at")
    list_display_links = ("token",)
    list_per_page = 20

    widget_actions = ("chart_tokens_activity",)

    @staticmethod
    def get_model_pk_name(orm_model_cls) -> str:
        return "token"

    async def has_add_permission(self, user_id: UUID | int | None = None) -> bool:
        return False

    async def has_change_permission(self, user_id: UUID | int | None = None) -> bool:
        return False

    async def has_delete_permission(self, user_id: UUID | int | None = None) -> bool:
        return False

    @widget_action(
        tab="Overview",
        title="Tokens Issued",
        description="Total number of active access tokens",
        widget_action_type=WidgetActionType.ChartBar,
        widget_action_props=WidgetActionChartProps(
            x_field="metric",
            y_field="count",
        ),
        width=12,
    )
    async def chart_tokens_activity(
        self, payload: WidgetActionInputSchema
    ) -> WidgetActionResponseSchema:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            total = await session.scalar(
                select(func.count()).select_from(AccessToken)
            ) or 0
        return WidgetActionResponseSchema(data=[
            {"metric": "Total Tokens", "count": total},
        ])


@register(OAuthAccount, sqlalchemy_sessionmaker=db_helper.session_factory)
class OAuthAccountAdmin(SqlAlchemyModelAdmin):
    menu_section = "Auth & Security"
    verbose_name = "OAuth Account"
    verbose_name_plural = "OAuth Accounts"

    list_display = ("id", "oauth_name", "account_email", "user_id")
    list_display_links = ("id",)
    list_filter = ("oauth_name",)
    search_fields = ("account_email",)
    list_per_page = 20

    widget_actions = ("chart_oauth_providers",)

    @widget_action(
        tab="Overview",
        title="OAuth Providers Distribution",
        description="Breakdown of connected OAuth providers",
        widget_action_type=WidgetActionType.ChartBar,
        widget_action_props=WidgetActionChartProps(
            x_field="provider",
            y_field="count",
        ),
        widget_action_filters=[
            WidgetActionFilter(
                field_name="limit",
                widget_type=WidgetType.Select,
                widget_props={
                    "options": [
                        {"label": "Top 5", "value": "5"},
                        {"label": "Top 10", "value": "10"},
                        {"label": "All", "value": "100"},
                    ],
                    "defaultValue": "10",
                },
            )
        ],
        width=12,
    )
    async def chart_oauth_providers(
        self, payload: WidgetActionInputSchema
    ) -> WidgetActionResponseSchema:
        limit = 10
        for q in payload.query:
            if q.field_name == "limit":
                try:
                    limit = int(q.value)
                except (TypeError, ValueError):
                    pass

        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            rows = await session.execute(
                select(OAuthAccount.oauth_name, func.count().label("count"))
                .group_by(OAuthAccount.oauth_name)
                .order_by(func.count().desc())
                .limit(limit)
            )
        return WidgetActionResponseSchema(data=[
            {"provider": row.oauth_name, "count": row.count}
            for row in rows.all()
        ])