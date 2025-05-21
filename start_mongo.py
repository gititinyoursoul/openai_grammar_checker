# start_mongo.py
import os
import time
import socket
import subprocess
from pathlib import Path
from grammar_checker.logger import get_logger

logger = get_logger(__name__)

# Load environment variables from .env file
MONGO_BIN_PATH = os.getenv("MONGO_BIN_PATH")
MONGO_CONFIG_PATH = os.getenv("MONGO_CONFIG_PATH")

# Resolve relative paths
exe = Path(MONGO_BIN_PATH).expanduser().resolve() if MONGO_BIN_PATH else None
cfg = Path(MONGO_CONFIG_PATH).expanduser().resolve() if MONGO_CONFIG_PATH else None


def is_mongodb_running(host="127.0.0.1", port=27017, timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def start_mongo():
    if not exe or not cfg:
        logger.error(
            "Missing MONGO_BIN_PATH or MONGO_CONFIG_PATH is invalid or missing."
        )
        return False

    try:
        logger.info(f"Starting MongoDB...")
        logger.info(f"MongoDB Binary: '{exe}'")
        logger.info(f"MongoDB Config: '{cfg}'")

        # Start MongoDB as a non-blocking subprocess
        subprocess.Popen(
            [str(exe), "--config", str(cfg)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=(
                subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            ),  # Windows: prevent opening a new window
        )

        if is_mongodb_running():
            logger.info("MongoDB is live and accepting connections.")
            return True
        else:
            logger.warning(
                "MongoDB process started, but it's not responding on port 27017."
            )
            return False

    except FileNotFoundError:
        logger.error("mongod.exe not found. Check MONGO_BIN_PATH.")
    except subprocess.CalledProcessError as e:
        logger.error(f"MongoDB failed to start: {e}")

    return False


# def stop_mongo():
#     if not MONGO_BIN_PATH or not MONGO_CONFIG_PATH:
#         logger.error("Missing MONGO_BIN_PATH or MONGO_CONFIG_PATH in .env")
#         return

#     try:
#         logger.info("Shutting down MongoDB...")
#         subprocess.run(
#             [str(exe), "--config", str(cfg), "--shutdown"],
#             check=True,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#         )
#         logger.info("MongoDB shut down successfully.")
#     except subprocess.CalledProcessError as e:
#         logger.error(f"Failed to shut down MongoDB: {e}")
#     except FileNotFoundError:
#         logger.error("mongod.exe not found. Check your path in .env.")


if __name__ == "__main__":
    is_running = start_mongo()
    print("MongoDB started" if is_running else "Failed to start MongoDB")
