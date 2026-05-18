from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.analytics import ElevatorAnalyticsEngine


app = FastAPI(
    title='Análise de Permanência em Elevadores',
    version='2.0.0',
    description='Módulo público para análise de permanência em elevadores, VMS (Sistema de Gerenciamento de Vídeo), streaming e alertas operacionais.',
)


CAMERAS = [
    {
        'id': 'elev-social-a01',
        'name': 'Cabine do elevador social',
        'site': 'Torre residencial A',
        'platform_family': 'hikvision',
        'threshold_s': 120.0,
        'cooldown_s': 60.0,
        'analysis_enabled': True,
        'roi': [
            {'x': 0.18, 'y': 0.12},
            {'x': 0.86, 'y': 0.12},
            {'x': 0.86, 'y': 0.95},
            {'x': 0.18, 'y': 0.95},
        ],
        'forbidden_zone': [],
    },
    {
        'id': 'elev-service-b02',
        'name': 'Cabine do elevador de serviço',
        'site': 'Torre residencial B',
        'platform_family': 'hikvision',
        'threshold_s': 150.0,
        'cooldown_s': 90.0,
        'analysis_enabled': True,
        'roi': [
            {'x': 0.16, 'y': 0.10},
            {'x': 0.84, 'y': 0.10},
            {'x': 0.84, 'y': 0.94},
            {'x': 0.16, 'y': 0.94},
        ],
        'forbidden_zone': [
            {'x': 0.00, 'y': 0.00},
            {'x': 0.16, 'y': 0.00},
            {'x': 0.16, 'y': 1.00},
            {'x': 0.00, 'y': 1.00},
        ],
    },
]

engine = ElevatorAnalyticsEngine()
for camera in CAMERAS:
    engine.register_camera(camera)


class DetectionIn(BaseModel):
    track_id: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: list[float] = Field(min_length=4, max_length=4)
    observed_for_s: float = Field(ge=0.0)
    counter_paused: bool = False


@app.get('/', response_class=HTMLResponse)
def index() -> str:
    return '''
    <main style="font-family:system-ui;max-width:920px;margin:40px auto;line-height:1.5">
      <p style="text-transform:uppercase;font-size:12px;letter-spacing:.08em;color:#476582">módulo público</p>
      <h1>Análise de Permanência em Elevadores</h1>
      <p>
        Módulo FastAPI para runtime de câmera, ROI, track de pessoa, limite de permanência,
        evento operacional e health check. Representa um worker de analytics conectado a stream VMS em tempo real.
        VMS significa Sistema de Gerenciamento de Vídeo, a camada que centraliza câmeras, streams, eventos e alertas.
      </p>
      <ul>
        <li><a href="/api/system/health">Saúde do sistema</a></li>
        <li><a href="/api/cameras">Câmeras com runtime</a></li>
        <li><a href="/api/events">Eventos</a></li>
      </ul>
      <p>Use <code>POST /api/demo/elevator-dwell</code> para criar um evento sintético de permanência.</p>
    </main>
    '''


@app.get('/api/cameras')
def list_cameras() -> list[dict]:
    return [{**camera, 'runtime': engine.runtime_snapshot(camera['id'])} for camera in CAMERAS]


@app.get('/api/cameras/{camera_id}')
def get_camera(camera_id: str) -> dict:
    camera = _camera_by_id(camera_id)
    return {**camera, 'runtime': engine.runtime_snapshot(camera_id)}


@app.post('/api/cameras/{camera_id}/detections')
def ingest_detection(camera_id: str, payload: DetectionIn) -> dict:
    _camera_by_id(camera_id)
    return engine.ingest_detection(
        camera_id=camera_id,
        track_id=payload.track_id,
        confidence=payload.confidence,
        bbox=payload.bbox,
        observed_for_s=payload.observed_for_s,
        counter_paused=payload.counter_paused,
    )


@app.post('/api/demo/elevator-dwell')
def demo_elevator_dwell() -> dict:
    return engine.ingest_detection(
        camera_id='elev-social-a01',
        track_id='person-017',
        confidence=0.88,
        bbox=[0.34, 0.18, 0.58, 0.92],
        observed_for_s=138.4,
    )


@app.get('/api/events')
def list_events() -> list[dict]:
    return engine.list_events()


@app.get('/api/system/health')
def system_health() -> dict:
    return engine.system_health()


def _camera_by_id(camera_id: str) -> dict:
    for camera in CAMERAS:
        if camera['id'] == camera_id:
            return camera
    raise HTTPException(status_code=404, detail='Camera not found')
