#!/bin/bash
set -e

PROJECT_ID="deepfusion-clippyuppy-pipeline"
REGION="europe-west2"
REPO="pipeline"

deploy_service () {
    SERVICE=$1
    IMAGE="europe-west2-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE:latest"

    echo "Building $SERVICE..."
    docker build -t $IMAGE "./$SERVICE"

    echo "Pushing $SERVICE..."
    docker push $IMAGE

    echo "Deploying $SERVICE..."
    gcloud run deploy $SERVICE \
        --image $IMAGE \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated
}

# Source adapters
deploy_service "source-adapters/getty-fetch-service"
deploy_service "source-adapters/newsflare-transfer-service"
deploy_service "source-adapters/direct-upload-trigger"

# Batching
deploy_service "batching/batch-window-service"

# Ingestion
deploy_service "ingestion/ingest-service"

# Processing
deploy_service "processing/video-split-service"
deploy_service "processing/audio-transcribe-service"
deploy_service "processing/enrich-vision-service"
deploy_service "processing/segment-merger-service"

# Storage
deploy_service "storage/store-service"

echo "All services deployed."

