from sqlalchemy import Column, Integer, String, Text, DateTime, text, UniqueConstraint
from sqlalchemy.orm import declarative_base


Base = declarative_base()
from .notes import Notes