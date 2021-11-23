from sqlalchemy import Column, String, Boolean, Integer, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.core.db.database import Base

# SQLAlchemy models go here

user_model_association_table = Table(
    'user_model_association',
    Base.metadata,
    Column('username', ForeignKey('users.username')),
    Column('model_name', ForeignKey('models.model_name'))
)


class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    password = Column(String)
    approved = Column(Boolean, default=False)

    allowed_models = relationship("ModelItem", secondary=user_model_association_table)


class ModelItem(Base):
    __tablename__ = "models"

    model_name = Column(String, primary_key=True, index=True)
    size = Column(Integer)