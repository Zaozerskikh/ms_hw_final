from sqlalchemy import Column, Integer, String
from database import Base


class URLItem(Base):
    __tablename__ = "short_urls"

    id = Column(Integer, primary_key=True, index=True)
    short_id = Column(String(6), unique=True, index=True, nullable=False)
    full_url = Column(String, nullable=False)
