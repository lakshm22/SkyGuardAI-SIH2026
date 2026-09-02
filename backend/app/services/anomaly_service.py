from datetime import datetime, timedelta
from sqlalchemy import desc
from app.database import SessionLocal, Reading, Alert, Station
from app.services.ml_engine import AnomalyEngine
import numpy as np

engine = AnomalyEngine()

def _recent(db, station_id, limit=24):
    return db.query(Reading).filter(Reading.station_id==station_id).order_by(desc(Reading.timestamp)).limit(limit).all()

def _neighbor_deviation(db, station_id, t,p,h):
    stations = db.query(Station).all()
    vals=[]
    for s in stations:
        if s.station_id != station_id:
            r=db.query(Reading).filter(Reading.station_id==s.station_id).order_by(desc(Reading.timestamp)).first()
            if r: vals.append([r.temperature,r.pressure,r.humidity])
    if not vals: return 0.0
    a=np.array(vals)
    d=np.array([t,p,h])
    scale=np.array([5,5,15])
    return float(np.clip(np.mean(np.abs(a-d)/scale)/2,0,1))

def _temporal(db, station_id,t,p,h):
    recent=_recent(db,station_id,12)
    if len(recent)<3: return 0.0,0.0
    a=np.array([[r.temperature,r.pressure,r.humidity] for r in recent])
    current=np.array([t,p,h])
    scale=np.array([5,5,15])
    dev=float(np.clip(np.mean(np.abs(current-a.mean(axis=0))/scale),0,1))
    frozen=float(len(set(tuple(x) for x in a[:6])) <= 1)
    return dev,frozen

def corrected(db,station_id,t,p,h):
    recent=_recent(db,station_id,20)
    if not recent:
        return None
    a=np.array([[r.temperature,r.pressure,r.humidity] for r in recent])
    pred=np.median(a,axis=0)
    return {"temperature":round(float(pred[0]),2),"pressure":round(float(pred[1]),2),"humidity":round(float(pred[2]),2)}

def process(reading):
    db=SessionLocal()
    ts=reading.timestamp or datetime.utcnow()
    temporal,frozen=_temporal(db,reading.station_id,reading.temperature,reading.pressure,reading.humidity)
    spatial=_neighbor_deviation(db,reading.station_id,reading.temperature,reading.pressure,reading.humidity)
    score,confidence,severity,anomaly,root,components=engine.analyze(
        reading.temperature,reading.pressure,reading.humidity,temporal,spatial,frozen
    )
    corr=corrected(db,reading.station_id,reading.temperature,reading.pressure,reading.humidity) if anomaly else None
    explanation = (
        f"{root}. Detection combines multivariate Isolation Forest scoring with "
        f"temporal deviation ({temporal:.2f}) and spatial mismatch ({spatial:.2f})."
    )
    r=Reading(
        station_id=reading.station_id,timestamp=ts,temperature=reading.temperature,
        pressure=reading.pressure,humidity=reading.humidity,anomaly=anomaly,
        score=score,confidence=confidence,severity=severity,root_cause=root,
        explanation=explanation,
        corrected_temperature=corr["temperature"] if corr else None,
        corrected_pressure=corr["pressure"] if corr else None,
        corrected_humidity=corr["humidity"] if corr else None
    )
    db.add(r)
    st=db.query(Station).filter_by(station_id=reading.station_id).first()
    if st:
        st.last_seen=ts
        # Health decreases with persistent anomaly severity, but is bounded.
        st.health=float(np.clip(st.health - (score*4 if anomaly else -0.15),0,100))
        st.status=severity
    if anomaly:
        parameter=max(
            [("Temperature",components["Temperature jump"]),
             ("Pressure",components["Pressure deviation"]),
             ("Humidity",components["Humidity inconsistency"])],
            key=lambda x:x[1]
        )[0]
        db.add(Alert(
            station_id=reading.station_id,timestamp=ts,parameter=parameter,
            severity=severity,score=score,status="Active",
            root_cause=root,explanation=explanation
        ))
    db.commit()
    db.refresh(r)
    health=st.health if st else 100
    db.close()
    return {
        "station_id":reading.station_id,"timestamp":ts,
        "temperature":reading.temperature,"pressure":reading.pressure,"humidity":reading.humidity,
        "anomaly":anomaly,"anomaly_score":round(score,3),"confidence":round(confidence,3),
        "severity":severity,"root_cause":root,"corrected_values":corr,
        "explanation":explanation,"feature_contributions":{k:round(float(v),3) for k,v in components.items()},
        "sensor_health":round(float(health),1)
    }
