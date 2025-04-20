from fastapi import BackgroundTasks, status
from fastapi.responses import JSONResponse
from pydantic import UUID4, BaseModel, Field

from app.repo.common import Error as RepoError
from app.repo.orders import OrderFull, OrdersRepoDep
from app.security import UserDep

from ..router import api_router
from .list import manager

__all__ = ("OrderCreateRequest", "OrderCreateResponse", "create_order")


class OrderCreateRequest(BaseModel):
    ingredients: list[UUID4] = Field(min_length=1, max_length=20)


class CreatedOrder(BaseModel):
    id: UUID4
    number: int


class OrderCreateResponse(BaseModel):
    order: CreatedOrder


class OrderCreateFailResponse(BaseModel):
    success: bool
    error: str


@api_router.post(
    "/orders",
    response_model=OrderCreateResponse,
    responses={422: {"model": OrderCreateFailResponse}},
)
async def create_order(
    order: OrderCreateRequest,
    user: UserDep,
    background_tasks: BackgroundTasks,
    orders_repo: OrdersRepoDep,
) -> dict[str, OrderFull] | JSONResponse:
    result = orders_repo.create_order(
        ingredient_ids=order.ingredients,
        user=user,
    )

    if isinstance(result, RepoError):
        return JSONResponse(
            {"success": False, "error": result.message},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    background_tasks.add_task(manager.broadcast_order, result)
    return {"order": result}
