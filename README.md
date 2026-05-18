# Elevator Dwell Analytics

Estudo de caso público de um serviço de video analytics para permanência em elevadores.

Este repositório é uma versão sanitizada e segura para portfólio de um fluxo que envolve streams VMS, detecção de pessoas, regras de permanência, cooldown de alertas, contexto operacional Dahua/Intelbras e health checks para operadores. Não é uma cópia de código de produção. O objetivo é mostrar decisões de engenharia sem expor clientes, endpoints de câmeras, gravações, SDKs proprietários, credenciais ou integrações privadas.

## Problema Operacional

Em ambientes residenciais monitorados, uma câmera de elevador pode parecer normal enquanto o sinal operacional está errado: uma pessoa permanece na cabine, o stream congela, o endpoint de alerta deixa de receber eventos ou o mesmo evento se repete em excesso. O sistema precisa detectar tempo de permanência, manter contexto suficiente para suporte e produzir um payload compreensível para ferramentas de monitoramento.

## O Que Este Projeto Demonstra

- Serviço FastAPI para workers de video analytics em uma família operacional Dahua/Intelbras.
- Estado por câmera com ROI, limite de tempo, cooldown, idade do último frame e tracks.
- Ingestão sintética de tracks de pessoa, criando evento apenas após o limite configurado.
- Endpoint de saúde que separa falhas técnicas de eventos operacionais.
- Payload público e seguro para encaminhamento de alerta.

## Arquitetura

```text
worker de stream VMS -> payload de detecção -> motor de permanência -> payload de evento
                                             -> snapshot de runtime -> endpoint de saúde
```

Em produção, o sistema receberia frames de um worker VMS/SDK e executaria detecção/tracking antes de chamar a camada de analytics. Esta versão pública começa na fronteira do payload de detecção para poder ser testada em qualquer ambiente.

## Rodar Localmente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8011
```

Abra:

- `http://127.0.0.1:8011/`
- `http://127.0.0.1:8011/api/cameras`
- `http://127.0.0.1:8011/api/system/health`

Crie um evento sintético de permanência:

```bash
curl -X POST http://127.0.0.1:8011/api/demo/elevator-dwell
curl http://127.0.0.1:8011/api/events
```

## Escopo Público e Seguro

O repositório usa sites, IDs de câmera, bounding boxes e payloads sintéticos. Ele trata Dahua/Intelbras como uma única família operacional e não inclui IPs reais, nomes de clientes, gravações, SDKs proprietários, URLs de alerta ou credenciais.

## Competências Representadas

Python, FastAPI, arquitetura de video analytics, health checks, modelagem de eventos, operações VMS, API design e sanitização de projetos para portfólio público.
