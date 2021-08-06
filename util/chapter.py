import time
from . import util
import requests
import collections
import os
import urllib.request

def get_all_chapters(manga_id: str, sleep: int, silent=True, lang="en"):
  offset = 0
  nochapterid = 1
  chapters = dict()
  print("Getting Chapters for %s" % manga_id)
  while True:
    to_add = get_chapters(manga_id, offset=offset, limit=100)
    offset += 100
    for chapter in to_add:
      chapter_chapter = chapter["data"]["attributes"]["chapter"]
      if chapter_chapter is None:
        chapter_chapter = 0 + (nochapterid / 10)
        nochapterid += 1

      chapter_title = chapter["data"]["attributes"]["title"]
      chapter_volume = chapter["data"]["attributes"]["volume"]
      if not silent:
        print("Got Chapter metadata for %s - %s" % (chapter_chapter, chapter_title))
      
      data = {
        "chapter": chapter_chapter,
        "volume": chapter_volume,
        "title": chapter_title,
        "data": chapter["data"]
      }
      chapters[chapter_chapter] = data

    time.sleep(sleep)
    if len(to_add) is not 100:
      break
  return util.sort_dict(chapters)

def get_chapters(manga_id: str, limit=10, offset=0, lang="en"):
  params = {
    "limit": limit,
    "offset": offset,
    "translatedLanguage[]": lang
  }
  request = requests.get("https://api.mangadex.org/manga/%s/feed" % (manga_id), params=params)
  json = request.json()
  return json["results"]

def get_base_url_for_chapter(chapter_id: str):
  return requests.get("https://api.mangadex.org/at-home/server/%s" % chapter_id).json()["baseUrl"]

def construct_image_url(base_url_with_token: str, chapter_hash: str, filename: str, quality_mode = "data"):
  return "%s/%s/%s/%s" % (base_url_with_token, quality_mode, chapter_hash, filename)

def get_chapter_images(base_url_with_token: str, chapter_data):
  images = []
  for image in chapter_data["data"]["attributes"]["data"]:
    images.append(construct_image_url(base_url_with_token, chapter_data["data"]["attributes"]["hash"], image))
  return images

def download_chapter_images(manga_path: str, chapter_path: str, images, sleep: float):
  basepath = "%s/%s" % (manga_path, chapter_path)
  if not os.path.exists(basepath):
    os.mkdir(basepath)
    i = 0
    try:
      for image in images:
        i += 1
        filename, extension = os.path.splitext(image)
        urllib.request.urlretrieve(image, "%s/%03d%s" % (basepath, i, extension))
        time.sleep(sleep)
    except:
      time.sleep(5)
      download_chapter_images(manga_path, chapter_path, images, sleep)