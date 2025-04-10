import datetime

from pydantic import UUID4, BaseModel
from sqlalchemy import desc
from sqlmodel import select

from app.app import app
from app.di import SessionDep
from db.order import Order as DbOrder


class OrderListItemResponse(BaseModel):
    id: UUID4
    number: int
    created_at: datetime.datetime
    name: str


@app.get("/api/orders/all")
async def get_orders(session: SessionDep) -> list[OrderListItemResponse]:
    return session.exec(
        select(DbOrder).order_by(desc(DbOrder.created_at)).limit(50)
    ).all()
