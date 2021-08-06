import requests
from dataclasses import dataclass

from requests.api import head
from . import util

@dataclass
class AuthResponse:
  session: str
  refresh: str

  def __init__(self, session: str, refresh: str):
      self.session = session
      self.refresh = refresh

def authenticate(username: str, password: str) -> AuthResponse:
  endpoint = "https://api.mangadex.org/auth/login"

  data = {
    "username": username,
    "password": password
  }
  result = requests.post(url=endpoint, json=data)
  if result.status_code is not 200:
    return ValueError(result)
  
  json = result.json()
  return AuthResponse(json["token"]["session"], json["token"]["refresh"])

def check_session_token(session_token: str) -> bool:
  endpoint = "https://api.mangadex.org/auth/check"
  data = requests.get(url=endpoint, headers=util.gen_session_header(session_token)).json()
  return data["isAuthenticated"]

def refresh_token(refresh_token: str) -> AuthResponse:
  endpoint = "https://api.mangadex.org/auth/refresh"
  json = {
    "token": refresh_token
  }
  data = requests.post(url=endpoint, json=json).json()
  return AuthResponse(data["token"]["session"], data["token"]["refresh"])

