import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT_DIR / "var" / "log"
LOG_DIR.mkdir(parents=True, exist_ok=True)

bind = f"127.0.0.1:{os.getenv('EMMIE_PORT', '8001')}"
workers = int(os.getenv("EMMIE_GUNICORN_WORKERS", "2"))
threads = int(os.getenv("EMMIE_GUNICORN_THREADS", "2"))
timeout = 60
graceful_timeout = 20
accesslog = str(LOG_DIR / "gunicorn-access.log")
errorlog = str(LOG_DIR / "gunicorn-error.log")
capture_output = True

