#!/bin/python3
from typing import Dict
from util import auth
from util import manga
from util import chapter
from util import filename
from util import util
import json
import time
import os
from pprint import pprint

config = json.load(open("settings.json",))
last_session_refresh = config["auth"]["token"]["last_refresh"]



def update_config():
  util.write_json_to_file("settings.json", config)

def check_token_local(silent = True):
  if config["auth"]["token"]["refresh"] is None:
    if not silent:
      print("[Auth] Refresh token does not exist, requesting new with given login data")
    tokens = auth.authenticate(config["auth"]["username"], config["auth"]["password"])
    config["auth"]["token"]["refresh"] = tokens.refresh
    config["auth"]["token"]["session"] = tokens.session
    config["auth"]["token"]["last_refresh"] = int(time.time())
    if not silent:
      print("[Auth] login successful, using new session and refresh tokens")
    update_config()
    return
  if config["auth"]["token"]["session"] is not None:
    if (last_session_refresh + config["jwt_session_time"]) < time.time():
      valid = auth.check_session_token(config["auth"]["token"]["session"])
      if not valid:
        tokens = auth.refresh_token(config["auth"]["token"]["refresh"])
        config["auth"]["token"]["refresh"] = tokens.refresh
        config["auth"]["token"]["session"] = tokens.session
        config["auth"]["token"]["last_refresh"] = int(time.time())
        update_config()
      else:
        if not silent:
          print("[Auth] Session token still valid, using it for a while")
    else:
      if not silent:
        print("[Auth] Session token still valid, using it for a while")

def gather_manga_in_list():
  existing_mangalist = {}

  if os.path.exists("%s/mangalist.json" % config["downloads_folder"]):
    existing_mangalist = json.load(open("%s/mangalist.json" % config["downloads_folder"],))

  print("[Manga] Getting all manga reading status...")
  new_mangalist = manga.get_all_reading_manga(config["auth"]["token"]["session"])

  print("[Manga] Got %d manga, getting metadata for all manga..." % len(new_mangalist))
  i = 0
  for manga_id, reading_status in new_mangalist.items():
    i += 1
    if manga_id not in existing_mangalist:
      manga_info = manga.get_manga_info(manga_id)

      manganame = None
      if "en" in manga_info["attributes"]["title"]:
        manganame = manga_info["attributes"]["title"]["en"]
      if "jp" in manga_info["attributes"]["title"]:
        manganame = manga_info["attributes"]["title"]["jp"]
        print("Manga with id '%s' has no english title, defaulting to japanese.")
      elif len(manga_info["attributes"]["title"]) > 0:
        manganame = list(manga_info["attributes"]["title"].values[0])
        print("Title in english for manga with id '%s' not found, defaulting to first item in list." % manga_id)
      else:
        manganame = manga_id
        print("Manga with id '%s' has no title in any language, defaulting to manga-id instead.")


      entry = {
        "reading_status": reading_status,
        "friendly_name": filename.clean_filename(manganame).rstrip(' .')
      }
      existing_mangalist[manga_id] = entry

      mangafolder = "%s/%s" % (config["downloads_folder"], entry["friendly_name"])
      if not os.path.exists("%s/manga_info.json" % (mangafolder)):
        os.mkdir("%s" % (mangafolder))
        util.write_json_to_file("%s/manga_info.json" % (mangafolder), manga_info)

      print("[%d / %d] %s" % (i, len(new_mangalist), entry["friendly_name"]))

      util.write_json_to_file("%s/mangalist.json" % config["downloads_folder"], existing_mangalist)
      time.sleep(config["delay"]["manga_info"])
  return existing_mangalist

def download_all_manga(mangalist):
  manga = 0
  for manga_id, data in mangalist.items():
    manga += 1
    folder_name = data["friendly_name"]
    path = "%s/%s" % (config["downloads_folder"], folder_name)
    chapters = chapter.get_all_chapters(manga_id, config["delay"]["chapter"], lang=config["lang"])
    util.write_json_to_file("%s/chapters.json" % path, chapters)

    print("\n[Manga (%d/%d)] Downloading %s, got %d chapters" % (manga, len(mangalist), data["friendly_name"], len(chapters)))

    i = 1
    for chap, data in chapters.items():
      chapter_folder_name = "Chapter %s" % data["chapter"]
      if data["title"] is not None and data["title"] is not "" and data["title"].strip():
        chapter_folder_name += " - %s" % filename.clean_filename(data["title"]).rstrip('. ')
      
      util.printProgressBar(i, len(chapters), chapter_folder_name, length=50)
      if not os.path.exists("%s/%s" % (path, chapter_folder_name)):
        baseurl = chapter.get_base_url_for_chapter(data["data"]["id"])
        images = chapter.get_chapter_images(baseurl, data)
        chapter.download_chapter_images(path, chapter_folder_name, images, config["delay"]["chapter_image"])
        time.sleep(config["delay"]["chapter"])
      i += 1


if __name__ == "__main__":
  print("[Auth] Logging in using username: %s" % config["auth"]["username"])
  
  print("[Auth] Checking for present tokens...")
  check_token_local(False)

  if not os.path.exists(config["downloads_folder"]):
    os.mkdir(config["downloads_folder"])
    print("[Manga] Downloads folder created")
  
  mangalist = gather_manga_in_list()

  print("[Manga] Downloading all manga...")
  download_all_manga(mangalist)
  #chapter.get_all_chapters("d0c60a11-0106-45cf-abfc-d131cb49868f", config["delay"]["chapter"], lang=config["lang"])


