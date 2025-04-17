import datetime
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field

from app.db import SessionDep
from db.order import Order as DbOrder

from ..router import api_router

__all__ = ("OrderCreateRequest", "OrderCreateResponse", "create_order")


class OrderCreateRequest(BaseModel):
    name: str = Field(max_length=255)


class OrderCreateResponse(BaseModel):
    id: UUID4
    number: int


@api_router.post("/orders", response_model=OrderCreateResponse)
async def create_order(order: OrderCreateRequest, session: SessionDep) -> DbOrder:
    with session.begin():
        dbOrder = DbOrder(
            id=uuid4(), created_at=datetime.datetime.now(), name=order.name, number=0
        )
        session.add(dbOrder)
    return dbOrder
