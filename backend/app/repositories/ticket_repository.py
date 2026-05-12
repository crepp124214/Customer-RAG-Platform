from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.app.models.ticket import Ticket


class TicketRepository:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def get_by_id(self, ticket_id: str) -> Ticket | None:
        return self.db_session.get(Ticket, ticket_id)

    def add(self, ticket: Ticket) -> Ticket:
        self.db_session.add(ticket)
        self.db_session.flush()
        return ticket

    def list_tickets(
        self,
        *,
        search: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        product_id: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Ticket]:
        statement = select(Ticket)

        if search:
            statement = statement.where(Ticket.title.ilike(f"%{search}%"))

        if status:
            statement = statement.where(Ticket.status == status)

        if priority:
            statement = statement.where(Ticket.priority == priority)

        if product_id:
            statement = statement.where(Ticket.product_id == product_id)

        statement = statement.order_by(Ticket.created_at.desc())
        statement = statement.offset(offset)
        if limit:
            statement = statement.limit(limit)

        return list(self.db_session.scalars(statement).all())

    def count_tickets(
        self,
        *,
        search: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        product_id: str | None = None,
    ) -> int:
        statement = select(func.count(Ticket.id))

        if search:
            statement = statement.where(Ticket.title.ilike(f"%{search}%"))

        if status:
            statement = statement.where(Ticket.status == status)

        if priority:
            statement = statement.where(Ticket.priority == priority)

        if product_id:
            statement = statement.where(Ticket.product_id == product_id)

        return int(self.db_session.scalar(statement) or 0)

    def update(self, ticket_id: str, **kwargs) -> Ticket | None:
        ticket = self.get_by_id(ticket_id)
        if ticket is None:
            return None
        for key, value in kwargs.items():
            setattr(ticket, key, value)
        self.db_session.flush()
        return ticket

    def delete(self, ticket_id: str) -> bool:
        ticket = self.get_by_id(ticket_id)
        if ticket is None:
            return False
        self.db_session.delete(ticket)
        return True
