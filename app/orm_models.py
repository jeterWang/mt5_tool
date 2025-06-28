from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    create_engine,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class TradeHistory(Base):
    __tablename__ = "trade_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, unique=True, index=True)
    account = Column(String, index=True)
    symbol = Column(String)
    volume = Column(Float)
    direction = Column(String)
    open_time = Column(DateTime)
    close_time = Column(DateTime, index=True)
    trading_day = Column(String, index=True)
    open_price = Column(Float)
    close_price = Column(Float)
    profit = Column(Float)
    comment = Column(Text)


class RiskEvent(Base):
    __tablename__ = "risk_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String, index=True)
    event_type = Column(String)
    details = Column(Text)


# Engine/session工厂示例（实际使用时可在database.py等处统一管理）
# engine = create_engine('sqlite:///path/to/trade_history.db')
# Session = sessionmaker(bind=engine)
# Base.metadata.create_all(engine)
