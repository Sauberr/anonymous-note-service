from fastapi_users import FastAPIUsers

from app.dependencies.backend import authentication_backend
from app.dependencies.user_manager import get_user_manager
from app.core.types.user_id import UserIdType
from app.users.models import User

fastapi_users = FastAPIUsers[User, UserIdType](
    get_user_manager,
    [authentication_backend],
)

current_active_user = fastapi_users.current_user(active=True)
current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
