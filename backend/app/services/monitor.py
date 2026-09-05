import asyncio
import random
from datetime import datetime
from app.database import SessionLocal, Station
from app.schemas import SensorReading
from app.services.anomaly_service import process

_enabled = False
_interval = 5
_task = None


def status():
    return {'enabled': _enabled, 'interval_seconds': _interval}


def configure(enabled: bool, interval_seconds: int = 5):
    global _enabled, _interval
    _enabled = enabled
    _interval = interval_seconds


async def run_loop():
    global _task
    if _task and not _task.done():
        return
    _task = asyncio.current_task()
    try:
        while _enabled:
            db = SessionLocal()
            try:
                stations = db.query(Station).all()
            finally:
                db.close()
            for station in stations:
                # Real deployments call POST /api/readings from the AWS gateway.
                # Demo mode produces realistic baseline telemetry for continuous end-to-end monitoring.
                t = 29 + random.gauss(0, 1.3)
                p = 1008 + random.gauss(0, 1.8)
                h = max(15, min(98, 70 + random.gauss(0, 4)))
                process(SensorReading(station_id=station.station_id, temperature=t, pressure=p, humidity=h, timestamp=datetime.utcnow()))
            # Re-read _interval on every cycle so changing the UI interval takes effect.
            await asyncio.sleep(max(2, _interval))
    finally:
        _task = None


def start_background():
    try:
        loop = asyncio.get_running_loop()
        return loop.create_task(run_loop())
    except RuntimeError:
        return None
