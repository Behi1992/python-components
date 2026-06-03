from .models import DownloadTask
from .structured_downloader import download_file

def download(task: DownloadTask) -> str:
    return download_file(task)