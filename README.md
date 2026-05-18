# Elevator Dwell Analytics

Módulo FastAPI que representa a análise de permanência em câmeras de elevador dentro de uma operação VMS integrada.

## O Que o Sistema Faz

- Recebe payloads sintéticos de detecção vindos de um worker de stream VMS em tempo real.
- Mantém runtime por câmera: ROI, último frame, tracks ativos, limite de permanência e cooldown.
- Gera evento quando uma pessoa permanece no elevador acima do tempo configurado.
- Expõe health check para diferenciar falha técnica de ausência real de evento.
- Modela payload de integração para camada de alertas sem expor endpoints reais.

## Contexto Representado

- Câmeras Hikvision em ambiente VMS.
- Workers de vídeo consumindo stream em tempo real.
- Módulo de analytics separado da camada de visualização.
- Integração com operação por eventos e health checks.

## Endpoints

- `GET /` - página simples com links do módulo.
- `GET /api/cameras` - câmeras e runtime atual.
- `GET /api/cameras/{camera_id}` - runtime de uma câmera.
- `POST /api/cameras/{camera_id}/detections` - ingere uma detecção sintética.
- `POST /api/demo/elevator-dwell` - cria um evento sintético de permanência.
- `GET /api/events` - lista eventos gerados.
- `GET /api/system/health` - saúde do módulo.

## Rodar Localmente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8011
```

## Testar

```bash
curl http://127.0.0.1:8011/api/cameras
curl -X POST http://127.0.0.1:8011/api/demo/elevator-dwell
curl http://127.0.0.1:8011/api/events
curl http://127.0.0.1:8011/api/system/health
```

## Escopo Público

Este repositório usa dados sintéticos. Não inclui IPs reais, nomes de clientes, gravações, SDKs proprietários, credenciais, URLs de alerta ou regras internas de produção.
