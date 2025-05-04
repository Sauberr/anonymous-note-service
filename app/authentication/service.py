from fastapi import APIRouter

from app.core.config import settings
from app.requests_count_middleware import requests_count_middleware_dispatch
from fastapi import status

router = APIRouter(
    prefix=settings.api.v1.service,
    tags=["Service"],
)


@router.get(
    "/stats",
    summary="Get stats",
    response_description="Stats",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Bad request",
        },
    },
)
def get_path_stats():
    return {
        path: {
            "count": stats.count,
            "statuses": dict(stats.statuses_counts),
        }
        for path, stats in requests_count_middleware_dispatch.counts.items()
    }
