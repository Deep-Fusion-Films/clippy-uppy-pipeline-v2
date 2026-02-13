import json
import logging
from google.cloud import firestore, storage

logger = logging.getLogger("store-service")
logger.setLevel(logging.INFO)

firestore_client = firestore.Client()
storage_client = storage.Client()


def log(message: str, **kwargs):
    logger.info(json.dumps({"message": message, **kwargs}))

