from fastapi import APIRouter

from app.users.schemas import UserRegisteredNotification

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


@router.post("/notify-user-created")
def notify_user_created(info: UserRegisteredNotification):
    """
    This webhook will be called when a new user is created.
    """
