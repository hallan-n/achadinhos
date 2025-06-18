from datetime import datetime

from database.connection import metadata
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table

logins = Table(
    "logins",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user", String(255)),
    Column("password", String(255)),
    Column("role", String(255)),
    Column("url_base_site", String(255)),
    Column("url_base_affiliate", String(255)),
)


products = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(255), nullable=False),
    Column("description", String(255)),
    Column("original_price", Integer),
    Column("price_discount", Integer),
    Column("discount_percentage", Integer),
    Column("url", String(255)),
    Column("thumbnail", String(255)),
    Column("fetched_at", DateTime, default=datetime.utcnow),
    # Column("user_id", Integer, ForeignKey("users.id"))
)
