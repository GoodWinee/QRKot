from fastapi import FastAPI

from app.api.endpoints import google
from app.api.routers import router as api_router
from app.core.config import settings
from app.core.user import UserCreate, auth_backend, fastapi_users
from app.schemas.user import UserRead, UserUpdate

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
)

app.include_router(api_router)

app.include_router(google.router)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    route for route in users_router.routes
    if route.methods != {"DELETE"}
]
app.include_router(users_router, prefix="/users", tags=["users"])
