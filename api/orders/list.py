import datetime

from pydantic import UUID4, BaseModel
from sqlalchemy import desc
from sqlmodel import select

from app.di import SessionDep
from db.order import Order as DbOrder

from ..router import api_router


class OrderListItemResponse(BaseModel):
    id: UUID4
    number: int
    created_at: datetime.datetime
    name: str


@api_router.get("/orders/all")
async def get_orders(session: SessionDep) -> list[OrderListItemResponse]:
    return session.exec(
        select(DbOrder).order_by(desc(DbOrder.created_at)).limit(50)
    ).all()
