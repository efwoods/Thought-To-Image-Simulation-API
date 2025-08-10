import os
import re
import json
import pickle
import base64
from io import BytesIO
from contextlib import asynccontextmanager
from pydantic import BaseModel
import datetime
from fastapi import FastAPI, APIRouter
from PIL import Image
import websockets
from dotenv import load_dotenv
from torchvision import transforms
from torchvision.transforms.functional import to_pil_image

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

import uvicorn
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from fastapi import Request
from core.logging import logger
from core.config import settings

from contextlib import asynccontextmanager
import requests
from PIL import Image
from io import BytesIO
import base64

from models.SimulationRequest import SimulationRequest
from service.webcam_to_websocket_service import (
    encode_image_to_base64,
    pil_image_to_base64,
    send_image,
    simulate_all_images,
)
import pickle
import os
from glob import glob
import random

RANDOM_SEED = 42

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_STIMULUS_IMAGE_DIR = "/app/data/test_stimulus_images/"

random.seed(RANDOM_SEED)

router = APIRouter()


@router.post("/enable-thought-to-image")
async def process_thought_to_image(payload: SimulationRequest):
    """
    Every time this endpoint is called, sample images will be synthesized into waveforms and reconstructed into images.
    The return is the original image, the synthesized neural waveform, and the reconstructed image.
    """
    # Simulate Test Images
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    # logger.info(f"CWD: {os.getcwd()}")
    # logger.info(f"BASE_DIR: {BASE_DIR}")
    # logger.info(f"TEST_INDICES: {TEST_STIMULUS_IMAGE_DIR}")

    stimulus_images_l = glob(TEST_STIMULUS_IMAGE_DIR + "*.jpeg")
    logger.info(f"stimulus_images_l: {stimulus_images_l}")

    random_stimulus_image_path = random.choice(stimulus_images_l)
    random_stimulus_image_name = os.path.basename(random_stimulus_image_path)

    logger.info(f"random_stimulus_image_path: {random_stimulus_image_path}")
    logger.info(f"random_stimulus_image_name: {random_stimulus_image_name}")

    image_base64 = encode_image_to_base64(random_stimulus_image_path)

    message = {
        "payload": {
            "image_base64": image_base64,
        },
        "metadata": {
            "type": "test",
            "initial_timestamp": timestamp,
            "origin": "webcam-to-websocket-simulation",
            "image_type": "jpeg",
            "processing_image_path": random_stimulus_image_path,
            "processing_image_name": random_stimulus_image_name,
            "user_id": payload.user_id,
            "avatar_id": payload.avatar_id,
        },
    }
    logger.info(
        f"settings.WS_ROOT_URI + /simulate/ws/simulate-image-to-waveform-latent: {settings.WS_ROOT_URI}"
        + "/simulate/ws/simulate-image-to-waveform-latent"
    )

    try:
        async with websockets.connect(
            settings.WS_ROOT_URI + "/simulate/ws/simulate-image-to-waveform-latent"
        ) as websocket:
            await websocket.send(json.dumps(message))
            response = await websocket.recv()
            logger.info(f"[{timestamp}] Response: {response}")
            return response
    except Exception as e:
        logger.error(f"[ERROR] {timestamp}: {e}")
        return json.dumps({"error": str(e)})
