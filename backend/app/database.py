from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, String, Float, DateTime, Boolean, Text, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DB_URL = "sqlite:///./data/skyguard.db"
Path("data").mkdir(exist_ok=True)
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class Reading(Base):
    __tablename__ = "readings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station_id: Mapped[str] = mapped_column(String(100), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    temperature: Mapped[float] = mapped_column(Float)
    pressure: Mapped[float] = mapped_column(Float)
    humidity: Mapped[float] = mapped_column(Float)
    anomaly: Mapped[bool] = mapped_column(Boolean)
    score: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String(20))
    root_cause: Mapped[str] = mapped_column(String(200))
    explanation: Mapped[str] = mapped_column(Text)
    corrected_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    corrected_pressure: Mapped[float | None] = mapped_column(Float, nullable=True)
    corrected_humidity: Mapped[float | None] = mapped_column(Float, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station_id: Mapped[str] = mapped_column(String(100), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    parameter: Mapped[str] = mapped_column(String(50))
    severity: Mapped[str] = mapped_column(String(20))
    score: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="Active")
    root_cause: Mapped[str] = mapped_column(String(200))
    explanation: Mapped[str] = mapped_column(Text)

class Station(Base):
    __tablename__ = "stations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    health: Mapped[float] = mapped_column(Float, default=100)
    status: Mapped[str] = mapped_column(String(20), default="Normal")
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

def init_db():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    defaults = [
        ("AWS01","Chennai AWS-01",13.0827,80.2707,96,"Normal"),
        ("AWS02","Coimbatore AWS-02",11.0168,76.9558,88,"Normal"),
        ("AWS03","Madurai AWS-03",9.9252,78.1198,76,"Warning"),
        ("AWS04","Trichy AWS-04",10.7905,78.7047,65,"Warning"),
        ("AWS05","Ooty AWS-05",11.4102,76.6950,93,"Normal"),
        ("AWS06","Rameswaram AWS-06",9.2885,79.3129,59,"Critical"),
    ]
    for sid,name,lat,lon,h,status in defaults:
        if not db.query(Station).filter_by(station_id=sid).first():
            db.add(Station(station_id=sid,name=name,latitude=lat,longitude=lon,health=h,status=status))
    db.commit()
    db.close()
