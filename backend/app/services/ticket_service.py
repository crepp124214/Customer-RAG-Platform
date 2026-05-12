from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.exceptions import AppError
from backend.app.models.chunk import Chunk
from backend.app.models.ticket import Ticket
from backend.app.repositories.ticket_repository import TicketRepository
from backend.infrastructure.vector.store import search_similar_chunks


class TicketService:
    def __init__(self, *, embedding_client: object, reranker_client: object) -> None:
        self.embedding_client = embedding_client
        self.reranker_client = reranker_client

    def create_ticket(
        self,
        db_session: Session,
        *,
        product_id: str | None = None,
        title: str,
        description: str,
        fault_category: str = "",
        priority: str = "medium",
    ) -> Ticket:
        repository = TicketRepository(db_session)
        ticket = Ticket(
            product_id=product_id,
            title=title,
            description=description,
            fault_category=fault_category,
            priority=priority,
        )
        return repository.add(ticket)

    def get_ticket(self, db_session: Session, *, ticket_id: str) -> Ticket:
        repository = TicketRepository(db_session)
        ticket = repository.get_by_id(ticket_id)
        if ticket is None:
            raise AppError("工单不存在", code="ticket_not_found", status_code=404)
        return ticket

    def list_tickets(
        self,
        db_session: Session,
        *,
        search: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        product_id: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Ticket]:
        repository = TicketRepository(db_session)
        return repository.list_tickets(
            search=search,
            status=status,
            priority=priority,
            product_id=product_id,
            limit=limit,
            offset=offset,
        )

    def update_ticket_status(
        self,
        db_session: Session,
        *,
        ticket_id: str,
        status: str,
        solution: str | None = None,
        resolution_notes: str | None = None,
    ) -> Ticket:
        repository = TicketRepository(db_session)
        ticket = repository.get_by_id(ticket_id)
        if ticket is None:
            raise AppError("工单不存在", code="ticket_not_found", status_code=404)

        updates: dict = {"status": status}
        if solution is not None:
            updates["solution"] = solution
        if resolution_notes is not None:
            updates["resolution_notes"] = resolution_notes

        repository.update(ticket_id, **updates)
        db_session.refresh(ticket)
        return ticket

    def search_similar_tickets(
        self,
        db_session: Session,
        *,
        query: str,
        product_id: str | None = None,
        top_k: int = 5,
        threshold: float = 0.6,
    ) -> list[Ticket]:
        query_embedding = self.embedding_client.embed_texts([query])[0]

        candidate_limit = top_k * 4
        candidates = search_similar_chunks(db_session, query_embedding, candidate_limit)

        ticket_chunks: list[dict] = []
        for candidate in candidates:
            if candidate.score < threshold:
                continue

            chunk = db_session.get(Chunk, candidate.chunk_id)
            if chunk is None:
                continue
            if chunk.source_category != "ticket":
                continue
            if product_id is not None and chunk.product_id != product_id:
                continue

            ticket_chunks.append({
                "chunk_id": candidate.chunk_id,
                "content": candidate.content,
                "score": candidate.score,
                "document_id": candidate.document_id,
            })

        if not ticket_chunks:
            return []

        reranked_indexes = self.reranker_client.rerank(
            query=query,
            documents=[item["content"] for item in ticket_chunks],
            top_n=min(top_k, len(ticket_chunks)),
        )

        if reranked_indexes:
            selected = [ticket_chunks[idx] for idx in reranked_indexes if 0 <= idx < len(ticket_chunks)]
        else:
            selected = ticket_chunks[:top_k]

        ticket_ids: list[str] = []
        seen: set[str] = set()
        for item in selected:
            chunk = db_session.get(Chunk, item["chunk_id"])
            if chunk is None:
                continue
            ticket = db_session.scalar(
                select(Ticket).where(Ticket.description.ilike(f"%{chunk.content[:50]}%"))
            )
            if ticket is not None and ticket.id not in seen:
                ticket_ids.append(ticket.id)
                seen.add(ticket.id)

        if not ticket_ids:
            return []

        statement = select(Ticket).where(Ticket.id.in_(ticket_ids))
        tickets = list(db_session.scalars(statement))

        id_order = {tid: idx for idx, tid in enumerate(ticket_ids)}
        tickets.sort(key=lambda t: id_order.get(t.id, len(ticket_ids)))
        return tickets[:top_k]
