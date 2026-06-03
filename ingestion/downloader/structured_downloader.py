import hashlib
from pathlib import Path
from datetime import datetime
import requests

from .models import DownloadTask

DOWNLOAD_DIR = Path("data/downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _generate_filename(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _get_original_filename(task: DownloadTask) -> str:
    if task.filename:
        return task.filename

    name = task.url.split("/")[-1]
    if name:
        return name

    return _generate_filename(task.url)


def _build_final_filename(task: DownloadTask, original_name: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    list_part = task.list_name or "default"

    return f"{list_part}_{timestamp}_{original_name}"


def download_file(task: DownloadTask) -> str:
    original_name = _get_original_filename(task)
    final_filename = _build_final_filename(task, original_name)

    file_path = DOWNLOAD_DIR / final_filename

    headers = task.headers or {
        "User-Agent": "Mozilla/5.0"
    }

    for attempt in range(task.retry):
        try:
            response = requests.get(
                task.url,
                headers=headers,
                timeout=task.timeout,
                stream=True,
                allow_redirects=True
            )

            response.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"Downloaded: {final_filename}")
            return str(file_path)

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")

    raise Exception(f"Failed after {task.retry} attempts: {task.url}")