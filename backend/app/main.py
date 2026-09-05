from datetime import datetime, timedelta
from pathlib import Path
import csv, io, asyncio, random
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from app.database import init_db, SessionLocal, Station, Reading, Alert
from app.schemas import SensorReading, AlertUpdate, StationCreate, SimulationRequest, AdminLogin, MonitorConfig
from app.services.anomaly_service import process
from app.auth import login as admin_login, require_admin
from app.report import build_readings_pdf
from app.services import monitor

app=FastAPI(title='SkyGuard AI API', version='2.0.0', description='Real-time AI/ML anomaly detection backend for Automatic Weather Stations.')
app.add_middleware(CORSMiddleware, allow_origin_regex='.*', allow_credentials=False, allow_methods=['*'], allow_headers=['*'])

@app.on_event('startup')
def startup():
    init_db()

def db():
    s=SessionLocal()
    try: yield s
    finally: s.close()

def _reading(r):
    return {'id':r.id,'station_id':r.station_id,'timestamp':r.timestamp,'temperature':r.temperature,'pressure':r.pressure,'humidity':r.humidity,'anomaly':r.anomaly,'anomaly_score':r.score,'confidence':r.confidence,'severity':r.severity,'root_cause':r.root_cause,'explanation':r.explanation,'corrected_values':({'temperature':r.corrected_temperature,'pressure':r.corrected_pressure,'humidity':r.corrected_humidity} if r.corrected_temperature is not None else None)}

def _alert(a):
    return {'id':a.id,'station_id':a.station_id,'timestamp':a.timestamp,'parameter':a.parameter,'severity':a.severity,'score':a.score,'status':a.status,'root_cause':a.root_cause,'explanation':a.explanation}

def _station(x):
    return {'station_id':x.station_id,'name':x.name,'latitude':x.latitude,'longitude':x.longitude,'health':round(x.health,1),'status':x.status,'last_seen':x.last_seen}

@app.get('/api/health')
def health(): return {'status':'ok','service':'SkyGuard AI','model':'Hybrid IsolationForest','time':datetime.utcnow(),'monitor':monitor.status()}

@app.post('/api/auth/login')
def login(payload: AdminLogin): return {'token':admin_login(payload.username,payload.password),'username':payload.username}
@app.post('/api/auth/logout')
def logout(_: bool=Depends(require_admin)): return {'message':'Logged out'}

@app.get('/api/stations')
def stations(db:Session=Depends(db)): return [_station(x) for x in db.query(Station).order_by(Station.station_id).all()]

@app.post('/api/stations')
def add_station(payload:StationCreate,db:Session=Depends(db),_:bool=Depends(require_admin)):
    if db.query(Station).filter_by(station_id=payload.station_id).first(): raise HTTPException(409,'Station already exists')
    x=Station(**payload.model_dump()); db.add(x); db.commit(); db.refresh(x); return _station(x)

@app.delete('/api/stations/{station_id}')
def delete_station(station_id:str,db:Session=Depends(db),_:bool=Depends(require_admin)):
    x=db.query(Station).filter_by(station_id=station_id).first()
    if not x: raise HTTPException(404,'Station not found')
    db.query(Alert).filter_by(station_id=station_id).delete(); db.query(Reading).filter_by(station_id=station_id).delete(); db.delete(x); db.commit()
    return {'message':'Station deleted','station_id':station_id}

@app.post('/api/readings')
def ingest(payload:SensorReading):
    return process(payload)

@app.get('/api/stations/{station_id}/latest')
def latest(station_id:str,db:Session=Depends(db)):
    r=db.query(Reading).filter_by(station_id=station_id).order_by(Reading.timestamp.desc()).first()
    if not r: raise HTTPException(404,'No readings for station')
    return _reading(r)

@app.get('/api/stations/{station_id}/trend')
def trend(station_id:str,hours:int=Query(1,ge=1,le=168),db:Session=Depends(db)):
    since=datetime.utcnow()-timedelta(hours=hours)
    return [_reading(r) for r in db.query(Reading).filter(Reading.station_id==station_id,Reading.timestamp>=since).order_by(Reading.timestamp.asc()).all()]

@app.get('/api/alerts')
def alerts(limit:int=Query(50,ge=1,le=500),status:str|None=None,db:Session=Depends(db)):
    q=db.query(Alert).order_by(Alert.timestamp.desc())
    if status: q=q.filter(Alert.status==status)
    return [_alert(a) for a in q.limit(limit).all()]

@app.patch('/api/alerts/{alert_id}')
def update_alert(alert_id:int,payload:AlertUpdate,db:Session=Depends(db),_:bool=Depends(require_admin)):
    a=db.query(Alert).filter_by(id=alert_id).first()
    if not a: raise HTTPException(404,'Alert not found')
    a.status=payload.status; db.commit(); db.refresh(a); return _alert(a)

@app.post('/api/simulate')
def simulate(payload:SimulationRequest, _:bool=Depends(require_admin)):
    patterns={
      'normal':{'temperature':29.5,'pressure':1008,'humidity':70},
      'temperature_spike':{'temperature':55,'pressure':1007,'humidity':72},
      'pressure_shift':{'temperature':30,'pressure':960,'humidity':70},
      'humidity_spike':{'temperature':31,'pressure':1008,'humidity':99},
      'multi_parameter_spike':{'temperature':55,'pressure':975,'humidity':99},
      'frozen_value':{'temperature':44,'pressure':985,'humidity':20},
      'communication_error':{'temperature':-80,'pressure':850,'humidity':0},
    }
    base=patterns[payload.anomaly_type]; results=[]
    runs = max(payload.count, 6) if payload.anomaly_type == 'frozen_value' else payload.count
    for i in range(runs):
        jitter=0 if payload.anomaly_type != 'normal' else random.uniform(-1,1)
        r=SensorReading(station_id=payload.station_id,temperature=base['temperature']+jitter,pressure=base['pressure']+jitter,humidity=max(0,min(100,base['humidity']+jitter)),timestamp=datetime.utcnow()+timedelta(milliseconds=i))
        results.append(process(r))
    return {'count':len(results),'results':results}

@app.get('/api/monitor')
def get_monitor(): return monitor.status()

@app.post('/api/monitor')
async def set_monitor(payload:MonitorConfig,_:bool=Depends(require_admin)):
    monitor.configure(payload.enabled,payload.interval_seconds)
    if payload.enabled:
        # This endpoint is async so the background task is created on
        # FastAPI's running event loop (the previous sync endpoint ran in
        # a worker thread, where no asyncio loop was available).
        monitor.start_background()
    return monitor.status()

@app.get('/api/dashboard/{station_id}')
def dashboard(station_id:str,db:Session=Depends(db)):
    s=db.query(Station).filter_by(station_id=station_id).first()
    if not s: raise HTTPException(404,'Station not found')
    latest_r=db.query(Reading).filter_by(station_id=station_id).order_by(Reading.timestamp.desc()).first()
    recent=db.query(Reading).filter_by(station_id=station_id).order_by(Reading.timestamp.desc()).limit(240).all()
    active=db.query(Alert).filter(Alert.station_id==station_id,Alert.status=='Active').order_by(Alert.timestamp.desc()).first()
    return {'station':_station(s),'latest':_reading(latest_r) if latest_r else None,'trend':[ _reading(x) for x in reversed(recent)],'latest_alert':_alert(active) if active else None}

@app.get('/api/export/report.pdf')
def export_pdf(station_id:str|None=None,db:Session=Depends(db),_:bool=Depends(require_admin)):
    q=db.query(Reading).order_by(Reading.timestamp.asc())
    if station_id:q=q.filter(Reading.station_id==station_id)
    rows=q.limit(2000).all(); pdf=build_readings_pdf(rows,station_id)
    return Response(content=pdf.getvalue(),media_type='application/pdf',headers={'Content-Disposition':'attachment; filename=skyguard-anomaly-report.pdf'})

@app.get('/api/export/readings')
def export_readings(station_id:str|None=None,db:Session=Depends(db)):
    q=db.query(Reading).order_by(Reading.timestamp.asc())
    if station_id:q=q.filter(Reading.station_id==station_id)
    rows=q.limit(5000).all(); out=io.StringIO(); w=csv.writer(out)
    w.writerow(['timestamp','station_id','temperature','pressure','humidity','anomaly','score','confidence','severity','root_cause'])
    for r in rows:w.writerow([r.timestamp,r.station_id,r.temperature,r.pressure,r.humidity,r.anomaly,r.score,r.confidence,r.severity,r.root_cause])
    return StreamingResponse(iter([out.getvalue()]),media_type='text/csv',headers={'Content-Disposition':'attachment; filename=skyguard-readings.csv'})

@app.post('/api/model/retrain')
def retrain(_:bool=Depends(require_admin)):
    return {'message':'Model retraining endpoint ready; baseline model is generated on startup.'}
