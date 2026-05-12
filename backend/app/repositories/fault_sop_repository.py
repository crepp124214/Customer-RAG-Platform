from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.fault_sop import FaultSOP


class FaultSOPRepository:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def get_by_id(self, sop_id: str) -> FaultSOP | None:
        return self.db_session.get(FaultSOP, sop_id)

    def add(self, fault_sop: FaultSOP) -> FaultSOP:
        self.db_session.add(fault_sop)
        self.db_session.flush()
        return fault_sop

    def list_by_product_id(self, product_id: str) -> list[FaultSOP]:
        statement = (
            select(FaultSOP)
            .where(FaultSOP.product_id == product_id)
            .order_by(FaultSOP.created_at.desc())
        )
        return list(self.db_session.scalars(statement))

    def find_by_product_and_symptoms(
        self,
        product_id: str,
        symptoms: list[str],
    ) -> list[FaultSOP]:
        statement = (
            select(FaultSOP)
            .where(FaultSOP.product_id == product_id)
            .order_by(FaultSOP.created_at.desc())
        )
        all_sops = list(self.db_session.scalars(statement))
        if not symptoms:
            return all_sops

        matched: list[tuple[int, FaultSOP]] = []
        for sop in all_sops:
            sop_symptoms = sop.symptoms or []
            symptom_texts = [
                s.get("description", "").lower() if isinstance(s, dict) else str(s).lower()
                for s in sop_symptoms
            ]
            score = sum(
                1 for symptom in symptoms
                if any(symptom.lower() in text for text in symptom_texts)
            )
            if score > 0:
                matched.append((score, sop))

        matched.sort(key=lambda item: -item[0])
        return [sop for _, sop in matched]

    def update(self, sop_id: str, **kwargs) -> FaultSOP | None:
        sop = self.get_by_id(sop_id)
        if sop is None:
            return None
        for key, value in kwargs.items():
            setattr(sop, key, value)
        self.db_session.flush()
        return sop

    def delete(self, sop_id: str) -> bool:
        sop = self.get_by_id(sop_id)
        if sop is None:
            return False
        self.db_session.delete(sop)
        return True
