from typing import Dict
from . import util
from . import chapter
import requests

def get_all_reading_manga(session_token: str) -> Dict[str, str]:
  return requests.get("https://api.mangadex.org/manga/status", headers=util.gen_session_header(session_token)).json()["statuses"]

def get_manga_info(manga_id: str):
  return requests.get("https://api.mangadex.org/manga/%s" % manga_id).json()["data"]

def download_manga(manga_id: str, basepath: str):
  pass