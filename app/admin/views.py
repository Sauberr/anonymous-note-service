from sqladmin import ModelView

from app.authentication.models import AccessToken, OAuthAccount
from app.notes.models import Note
from app.users.models import User


class UserAdmin(ModelView, model=User):
    column_list = [u.name for u in User.__table__.columns]
    column_details_exclude_list = [User.hashed_password]
    can_delete = False
    name = "User"
    name_plural = "Users"
    column_searchable_list = ["username", "email"]
    column_filters = ["is_active", "is_superuser", "created_at"]
    icon = "fa-solid fa-user"


class NoteAdmin(ModelView, model=Note):
    column_list = [n.name for n in Note.__table__.columns]
    can_delete = False
    name = "Note"
    name_plural = "Notes"
    column_searchable_list = ["title", "description"]
    column_filters = ["is_ephemeral", "lifetime"]
    icon = "fa-solid fa-sticky-note"


class AccessTokensAdmin(ModelView, model=AccessToken):
    column_list = [a.name for a in AccessToken.__table__.columns]
    can_delete = False
    name = "Access Token"
    name_plural = "Access Tokens"
    icon = "fa-solid fa-key"


class OAuthAccountAdmin(ModelView, model=OAuthAccount):
    column_list = [o.name for o in OAuthAccount.__table__.columns]
    can_delete = False
    name = "OAuth Account"
    name_plural = "OAuth Accounts"
    icon = "fa-solid fa-key"
