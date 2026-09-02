from datetime import datetime, timedelta
from pathlib import Path
import csv, io, random
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import init_db, SessionLocal, Station, Reading, Alert
from app.schemas import SensorReading, AlertUpdate, StationCreate, SimulationRequest
from app.services.anomaly_service import process, engine

app=FastAPI(
    title="SkyGuard AI API",
    version="1.0.0",
    description="Real-time AI/ML anomaly detection backend for Automatic Weather Stations."
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

def db():
    s=SessionLocal()
    try: yield s
    finally: s.close()

@app.get("/api/health")
def health():
    return {"status":"ok","service":"SkyGuard AI","model":"IsolationForest","time":datetime.utcnow()}

@app.get("/api/stations")
def stations(db:Session=Depends(db)):
    rows=db.query(Station).order_by(Station.station_id).all()
    return [{
        "station_id":x.station_id,"name":x.name,"latitude":x.latitude,"longitude":x.longitude,
        "health":round(x.health,1),"status":x.status,"last_seen":x.last_seen
    } for x in rows]

@app.post("/api/stations")
def add_station(payload:StationCreate,db:Session=Depends(db)):
    if db.query(Station).filter_by(station_id=payload.station_id).first():
        raise HTTPException(409,"Station already exists")
    x=Station(**payload.model_dump())
    db.add(x);db.commit()
    return {"message":"Station created","station_id":x.station_id}

@app.get("/api/stations/{station_id}")
def station(station_id:str,db:Session=Depends(db)):
    x=db.query(Station).filter_by(station_id=station_id).first()
    if not x: raise HTTPException(404,"Station not found")
    return {"station_id":x.station_id,"name":x.name,"latitude":x.latitude,"longitude":x.longitude,
            "health":round(x.health,1),"status":x.status,"last_seen":x.last_seen}

@app.post("/api/readings")
def ingest(payload:SensorReading):
    return process(payload)

@app.get("/api/stations/{station_id}/latest")
def latest(station_id:str,db:Session=Depends(db)):
    r=db.query(Reading).filter_by(station_id=station_id).order_by(Reading.timestamp.desc()).first()
    if not r: raise HTTPException(404,"No readings for station")
    return _reading(r)

@app.get("/api/stations/{station_id}/trend")
def trend(station_id:str,hours:int=Query(1,ge=1,le=168),db:Session=Depends(db)):
    since=datetime.utcnow()-timedelta(hours=hours)
    rows=db.query(Reading).filter(Reading.station_id==station_id,Reading.timestamp>=since).order_by(Reading.timestamp.asc()).all()
    return [_reading(r) for r in rows]

@app.get("/api/alerts")
def alerts(limit:int=Query(50,ge=1,le=500),status:str|None=None,db:Session=Depends(db)):
    q=db.query(Alert).order_by(Alert.timestamp.desc())
    if status: q=q.filter(Alert.status==status)
    return [_alert(a) for a in q.limit(limit).all()]

@app.patch("/api/alerts/{alert_id}")
def update_alert(alert_id:int,payload:AlertUpdate,db:Session=Depends(db)):
    a=db.query(Alert).filter_by(id=alert_id).first()
    if not a: raise HTTPException(404,"Alert not found")
    a.status=payload.status;db.commit()
    return _alert(a)

@app.post("/api/simulate")
def simulate(payload:SimulationRequest):
    base={"temperature":31.4,"pressure":1007.8,"humidity":71}
    if payload.anomaly_type=="temperature_spike": base["temperature"]=55
    elif payload.anomaly_type=="pressure_shift": base["pressure"]=975
    elif payload.anomaly_type=="humidity_spike": base["humidity"]=99
    elif payload.anomaly_type=="frozen_value": base.update(temperature=42,pressure=990,humidity=18)
    elif payload.anomaly_type=="communication_error":
        base.update(temperature=0,pressure=0,humidity=0)
    return process(SensorReading(station_id=payload.station_id,**base))

@app.get("/api/dashboard/{station_id}")
def dashboard(station_id:str,db:Session=Depends(db)):
    s=db.query(Station).filter_by(station_id=station_id).first()
    if not s: raise HTTPException(404,"Station not found")
    latest_r=db.query(Reading).filter_by(station_id=station_id).order_by(Reading.timestamp.desc()).first()
    recent=db.query(Reading).filter_by(station_id=station_id).order_by(Reading.timestamp.desc()).limit(50).all()
    active=db.query(Alert).filter(Alert.station_id==station_id,Alert.status=="Active").order_by(Alert.timestamp.desc()).first()
    return {
        "station":{"station_id":s.station_id,"name":s.name,"latitude":s.latitude,"longitude":s.longitude,"health":s.health,"status":s.status},
        "latest":_reading(latest_r) if latest_r else None,
        "trend":[_reading(x) for x in reversed(recent)],
        "latest_alert":_alert(active) if active else None
    }

@app.get("/api/export/readings")
def export_readings(station_id:str|None=None,db:Session=Depends(db)):
    q=db.query(Reading).order_by(Reading.timestamp.asc())
    if station_id:q=q.filter(Reading.station_id==station_id)
    rows=q.all()
    out=io.StringIO()
    w=csv.writer(out)
    w.writerow(["timestamp","station_id","temperature","pressure","humidity","anomaly","score","confidence","severity","root_cause"])
    for r in rows:
        w.writerow([r.timestamp,r.station_id,r.temperature,r.pressure,r.humidity,r.anomaly,r.score,r.confidence,r.severity,r.root_cause])
    return StreamingResponse(iter([out.getvalue()]),media_type="text/csv",
        headers={"Content-Disposition":"attachment; filename=skyguard_readings.csv"})

@app.post("/api/model/retrain")
def retrain():
    # Recreate model from its deterministic synthetic normal baseline.
    engine._train_or_load()
    return {"message":"Model retrained/loaded","model":"IsolationForest"}

def _reading(r):
    if r is None:return None
    return {"id":r.id,"station_id":r.station_id,"timestamp":r.timestamp,
            "temperature":r.temperature,"pressure":r.pressure,"humidity":r.humidity,
            "anomaly":r.anomaly,"anomaly_score":r.score,"confidence":r.confidence,
            "severity":r.severity,"root_cause":r.root_cause,"explanation":r.explanation,
            "corrected_values":{
                "temperature":r.corrected_temperature,
                "pressure":r.corrected_pressure,
                "humidity":r.corrected_humidity
            } if r.corrected_temperature is not None else None}

def _alert(a):
    if a is None:return None
    return {"id":a.id,"station_id":a.station_id,"timestamp":a.timestamp,
            "parameter":a.parameter,"severity":a.severity,"score":a.score,
            "status":a.status,"root_cause":a.root_cause,"explanation":a.explanation}
