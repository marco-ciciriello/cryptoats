import uuid
import datetime

from decouple import config
from sqlalchemy import Column, create_engine, DateTime, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db = create_engine(config('DATABASE_URL'))
base = declarative_base()


class Price(base):

    __tablename__ = 'price'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    pair = Column(String, nullable=False)
    curr = Column(Float, nullable=False)
    lowest = Column(Float, nullable=False)
    highest = Column(Float, nullable=False)
    created = Column(DateTime, default=datetime.datetime.utcnow)


Session = sessionmaker(db)
session = Session()

base.metadata.create_all(db)
