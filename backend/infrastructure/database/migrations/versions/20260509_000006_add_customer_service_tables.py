"""add customer service tables and restructure existing models

Revision ID: 20260509_000006
Revises: 20260413_000005
Create Date: 2026-05-09 12:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260509_000006"
down_revision = "20260413_000005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False, server_default="1.0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_products")),
    )

    op.create_table(
        "product_manuals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=32), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="UPLOADED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_product_manuals_product_id_products"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product_manuals")),
    )

    op.create_table(
        "product_specs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("spec_name", sa.String(length=255), nullable=False),
        sa.Column("spec_value", sa.String(length=500), nullable=False),
        sa.Column("spec_category", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_product_specs_product_id_products"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product_specs")),
    )

    op.create_table(
        "fault_sops",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("fault_type", sa.String(length=255), nullable=False),
        sa.Column("fault_category", sa.String(length=100), nullable=False),
        sa.Column("symptoms", sa.JSON(), nullable=False),
        sa.Column("steps", sa.JSON(), nullable=False),
        sa.Column("resolution", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_fault_sops_product_id_products"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_fault_sops")),
    )

    op.create_table(
        "tickets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("fault_category", sa.String(length=100), nullable=False, server_default=""),
        sa.Column("priority", sa.String(length=32), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("solution", sa.Text(), nullable=False, server_default=""),
        sa.Column("resolution_notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_tickets_product_id_products"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tickets")),
    )

    op.add_column("chunks", sa.Column("product_id", sa.String(length=36), nullable=True))
    op.add_column("chunks", sa.Column("source_category", sa.String(length=32), nullable=False, server_default="manual"))
    op.create_foreign_key(
        op.f("fk_chunks_product_id_products"),
        "chunks", "products",
        ["product_id"], ["id"],
        ondelete="SET NULL",
    )

    op.add_column("sessions", sa.Column("product_id", sa.String(length=36), nullable=True))
    op.add_column("sessions", sa.Column("ticket_id", sa.String(length=36), nullable=True))
    op.create_foreign_key(
        op.f("fk_sessions_product_id_products"),
        "sessions", "products",
        ["product_id"], ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_sessions_ticket_id_tickets"),
        "sessions", "tickets",
        ["ticket_id"], ["id"],
        ondelete="SET NULL",
    )

    op.add_column("messages", sa.Column("diagnosis_context", sa.JSON(), nullable=True))

    op.alter_column("tasks", "document_id", nullable=True)

    op.drop_column("chunks", "asset_index")
    op.drop_column("chunks", "asset_label")
    op.drop_column("chunks", "asset_path")
    op.drop_column("chunks", "bbox")

    op.drop_table("document_tag_relations")
    op.drop_table("document_tags")


def downgrade() -> None:
    op.create_table(
        "document_tags",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("color", sa.String(length=32), nullable=False, server_default="#409EFF"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_tags")),
    )
    op.create_table(
        "document_tag_relations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("tag_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"], ["documents.id"],
            name=op.f("fk_document_tag_relations_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"], ["document_tags.id"],
            name=op.f("fk_document_tag_relations_tag_id_document_tags"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_tag_relations")),
    )

    op.add_column("chunks", sa.Column("asset_index", sa.Integer(), nullable=True))
    op.add_column("chunks", sa.Column("asset_label", sa.String(length=255), nullable=True))
    op.add_column("chunks", sa.Column("asset_path", sa.Text(), nullable=True))
    op.add_column("chunks", sa.Column("bbox", sa.JSON(), nullable=True))

    op.alter_column("tasks", "document_id", nullable=False)

    op.drop_column("messages", "diagnosis_context")

    op.drop_constraint(op.f("fk_sessions_ticket_id_tickets"), "sessions", type_="foreignkey")
    op.drop_constraint(op.f("fk_sessions_product_id_products"), "sessions", type_="foreignkey")
    op.drop_column("sessions", "ticket_id")
    op.drop_column("sessions", "product_id")

    op.drop_constraint(op.f("fk_chunks_product_id_products"), "chunks", type_="foreignkey")
    op.drop_column("chunks", "source_category")
    op.drop_column("chunks", "product_id")

    op.drop_table("tickets")
    op.drop_table("fault_sops")
    op.drop_table("product_specs")
    op.drop_table("product_manuals")
    op.drop_table("products")
