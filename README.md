Clippy Uppy Pipeline v2
AI‑powered, event‑driven video ingestion and enrichment pipeline
Clippy Uppy Pipeline v2 is a modular, serverless, microservice‑based system for ingesting, processing, analysing, and enriching video content using Google Cloud and Gemini models.

It is designed for:

High‑volume ingestion

Real‑time and batch enrichment

Multi‑provider support (Getty, Newsflare, direct uploads)

Scalable, fault‑tolerant processing

Deep metadata extraction using Gemini Flash and Pro Vision

Durable storage in Firestore + GCS

This repository contains all microservices, shared utilities, orchestrators, and documentation for the full pipeline.

🧱 Architecture Overview
Code
GCS Upload / Provider Event
          │
          ▼
   ingest-service
          │
          ▼
 audio-extract-service
          │
          ▼
audio-transcribe-service
          │
          ▼
 frame-sample-service
          │
          ▼
 ┌──────────────────────────────────────────┐
 │ enrich-service (Flash)                   │
 │ enrich-pro-service (Pro Vision)          │
 │ batch-enrich-service (Gemini Batch API)  │
 └──────────────────────────────────────────┘
          │
          ▼
      store-service
          │
          ▼
   Firestore + GCS JSON
Orchestration is handled by:

orchestrator → real‑time Flash pipeline

batch-orchestrator → Batch API + Pro Vision pipelines

📦 Repository Structure
Code
clippy-uppy-pipeline-v2/
│
├── ingest-service/              # Normalises ingest events and starts pipeline
├── audio-extract-service/       # Extracts audio using FFmpeg
├── audio-transcribe-service/    # Transcribes audio using Gemini Audio
├── frame-sample-service/        # Extracts frames (1 FPS, max 50)
│
├── enrich-service/              # Gemini Flash enrichment
├── enrich-pro-service/          # Gemini Pro Vision enrichment
├── batch-enrich-service/        # Gemini Batch API enrichment (backfills)
│
├── store-service/               # Writes metadata to Firestore + GCS
│
├── orchestrator/                # Real-time Flash pipeline controller
├── batch-orchestrator/          # Batch + Pro Vision pipeline controller
│
├── shared/                      # Shared utilities (GCS, FFmpeg, Gemini, Pub/Sub)
│
└── documentation/               # Architecture, message contracts, service docs
Each service is a standalone Cloud Run microservice with:

main.py (FastAPI entrypoint)

Dockerfile

requirements.txt

utils.py

Service‑specific logic

🔄 Pipeline Flow (High-Level)
1. Ingest
ingest-service receives GCS events or provider metadata, normalises them into a Unified Ingest Format, and publishes to:

Code
pipeline.v2.start
2. Audio Extraction
audio-extract-service:

Downloads video

Extracts audio via FFmpeg

Uploads audio

Publishes to pipeline.v2.audio.transcribe

3. Transcription
audio-transcribe-service:

Downloads audio

Sends to Gemini Audio

Uploads transcript

Publishes to pipeline.v2.frame.sample

4. Frame Sampling
frame-sample-service:

Extracts 1 FPS frames (max 50)

Uploads frames

Publishes to pipeline.v2.enrich

5. Enrichment
Three possible paths:

Flash (real‑time)
enrich-service → Gemini Flash
Produces lightweight metadata.

Pro Vision (deep analysis)
enrich-pro-service → Gemini 1.5 Pro Vision
Produces richer metadata (timeline, transitions, weather, etc.)

Batch API (bulk backfills)
batch-enrich-service → Gemini Batch API
Processes large volumes cheaply.

6. Storage
store-service writes:

Structured metadata → Firestore

Full JSON payload → GCS

🧠 Orchestration
Real‑time Flash pipeline
Handled by orchestrator:

Code
pipeline.v2.start → audio.extract → audio.transcribe → frame.sample → enrich → store
Batch + Pro Vision pipeline
Handled by batch-orchestrator:

Code
pipeline.v2.start → enrich.pro OR batch.enrich → store
Routing rules can be extended (e.g., “send Newsflare to Pro Vision”).

🧪 Local Development
Run any service locally:
bash
cd ingest-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
Build Docker image:
bash
docker build -t ingest-service .
Run with Docker:
bash
docker run -p 8080:8080 ingest-service
☁️ Deployment (Cloud Run)
Deploy any service:

bash
gcloud run deploy ingest-service \
  --source ingest-service \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated
Repeat for each service.

🔧 Environment Variables
Each service uses a subset of:

Variable	Description
GCP_PROJECT	GCP project ID
PIPELINE_START_TOPIC	Ingest → Orchestrator
AUDIO_EXTRACT_TOPIC	Orchestrator → Audio Extract
AUDIO_TRANSCRIBE_TOPIC	Audio Extract → Transcribe
FRAME_SAMPLE_TOPIC	Transcribe → Frame Sample
ENRICH_TOPIC	Frame Sample → Flash
PRO_ENRICH_TOPIC	Frame Sample → Pro Vision
BATCH_ENRICH_TOPIC	Batch API jobs
STORE_TOPIC	Enrich → Store
METADATA_BUCKET	GCS bucket for metadata JSON
🧩 Shared Utilities
The shared/ directory contains:

ffmpeg.py — audio + frame extraction helpers

gcs.py — GCS download/upload utilities

gemini.py — Gemini Flash, Pro Vision, Audio, Batch wrappers

pubsub.py — Pub/Sub publish + decode helpers

schemas.py — shared Pydantic models

utils.py — logging, ID generation, helpers

This prevents duplication across services.

🗺️ Documentation
See the documentation/ folder for:

Architecture overview

Pipeline flow

Per‑service documentation

Message contracts

Deployment guide

Error handling

Scaling and performance

Roadmap
