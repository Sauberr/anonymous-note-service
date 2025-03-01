from fastapi_users import FastAPIUsers

from app.types.user_id import UserIdType
from app.users.models import User
from app.dependencies.user_manager import get_user_manager
from app.dependencies.backend import authentication_backend


fastapi_users = FastAPIUsers[User, UserIdType](
    get_user_manager,
    [authentication_backend],
)
