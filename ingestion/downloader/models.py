from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class DownloadTask:
    url: str
    download_dir: Optional[str] = None
    filename: Optional[str] = None
    file_type: Optional[str] = None  
    list_name: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry: int = 3