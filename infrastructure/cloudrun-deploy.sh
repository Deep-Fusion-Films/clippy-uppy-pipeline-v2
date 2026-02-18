#!/bin/bash
set -e

PROJECT_ID="deepfusion-clippyuppy-pipeline"
REGION="europe-west2"
REPO="pipeline"

# -------------------------------
# Topic routing per service
# -------------------------------
get_next_topic () {
    case "$1" in
        source-adapters-getty-fetch-service) echo "ingest" ;;
        source-adapters-newsflare-transfer-service) echo "ingest" ;;
        source-adapters-direct-upload-trigger) echo "ingest" ;;

        batching-batch-window-service) echo "ingest" ;;

        ingestion-ingest-service) echo "video-split" ;;

        processing-video-split-service) echo "audio-transcribe" ;;
        processing-audio-transcribe-service) echo "enrich-vision" ;;
        processing-enrich-vision-service) echo "segment-merge" ;;
        processing-segment-merger-service) echo "store-metadata" ;;

        storage-store-service) echo "" ;;  # final stage
    esac
}

# -------------------------------
# Deploy function
# -------------------------------
deploy_service () {
    SERVICE_PATH=$1
    SERVICE_NAME=$(echo "$SERVICE_PATH" | tr '/' '-')
    IMAGE="europe-west2-docker.pkg.dev/$PROJECT_ID/$REPO/$SERVICE_PATH:latest"

    NEXT_TOPIC=$(get_next_topic "$SERVICE_NAME")

    echo "----------------------------------------"
    echo "Building $SERVICE_NAME from $SERVICE_PATH"
    echo "----------------------------------------"
    docker build -t $IMAGE "./$SERVICE_PATH"

    echo "Pushing $SERVICE_NAME..."
    docker push $IMAGE

    echo "Deploying $SERVICE_NAME..."
    if [ -z "$NEXT_TOPIC" ]; then
        # Final service has no NEXT_TOPIC
        gcloud run deploy $SERVICE_NAME \
            --image $IMAGE \
            --region $REGION \
            --platform managed \
            --allow-unauthenticated \
            --set-env-vars PROJECT_ID=$PROJECT_ID
    else
        gcloud run deploy $SERVICE_NAME \
            --image $IMAGE \
            --region $REGION \
            --platform managed \
            --allow-unauthenticated \
            --set-env-vars PROJECT_ID=$PROJECT_ID \
            --set-env-vars NEXT_TOPIC=$NEXT_TOPIC
    fi
}

# -------------------------------
# Deploy all services
# -------------------------------

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

echo "----------------------------------------"
echo "All services deployed successfully."
echo "----------------------------------------"
