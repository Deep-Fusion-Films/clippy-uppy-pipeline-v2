# clippy-uppy-pipeline-v2
Cost-effective version of Clippy-Uppy-V1

Layout:

/pipeline
│
├── /source-adapters
│   ├── /getty-fetch-service
│   │   ├── main.py
│   │   ├── getty_api.py
│   │   ├── downloader.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── /newsflare-transfer-service
│   │   ├── main.py
│   │   ├── newsflare_api.py
│   │   ├── cross_cloud_transfer.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── /direct-upload-trigger
│       ├── main.py
│       ├── gcs_event_handler.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── /batching
│   └── /batch-window-service
│       ├── main.py
│       ├── window_manager.py
│       ├── gcs_scanner.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── /ingestion
│   └── /ingest-service
│       ├── main.py
│       ├── asset_registry.py
│       ├── validator.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── /processing
│   ├── /video-split-service
│   │   ├── main.py
│   │   ├── ffmpeg_splitter.py
│   │   ├── segment_manifest.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── /audio-transcribe-service
│   │   ├── main.py
│   │   ├── gemini_audio.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── /enrich-vision-service
│   │   ├── main.py
│   │   ├── gemini_video.py
│   │   ├── prompt.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── /segment-merger-service
│       ├── main.py
│       ├── merge_logic.py
│       ├── timeline_builder.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── /storage
│   └── /store-service
│       ├── main.py
│       ├── gcs_writer.py
│       ├── retention_tags.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── /infrastructure
│   ├── cloudrun-deploy.sh
│   ├── pubsub-topics.yaml
│   ├── gcs-lifecycle-raw.json
│   ├── gcs-lifecycle-metadata.json
│   ├── iam-roles.yaml
│   └── /terraform   (optional)
│
└── README.md
