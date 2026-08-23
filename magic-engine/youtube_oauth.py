#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, json, os, secrets, urllib.parse, urllib.request
from pathlib import Path

SCOPE = "https://www.googleapis.com/auth/youtube.upload"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def _post(url: str, form: dict) -> dict:
    data = urllib.parse.urlencode(form).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def generate_authorization(client_id: str, redirect_uri: str) -> dict:
    verifier = secrets.token_urlsafe(64)[:96]
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    state = secrets.token_urlsafe(24)
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
    }
    return {
        "authorization_url": AUTH_URL + "?" + urllib.parse.urlencode(params),
        "code_verifier": verifier,
        "state": state,
        "redirect_uri": redirect_uri,
    }


def exchange_code(client_id: str, client_secret: str, code: str, redirect_uri: str, code_verifier: str) -> dict:
    return _post(TOKEN_URL, {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "code_verifier": code_verifier,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    })


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    payload = _post(TOKEN_URL, {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    })
    token = str(payload.get("access_token") or "").strip()
    if not token:
        raise RuntimeError(f"Google token refresh failed: {payload}")
    return token


if __name__ == "__main__":
    client_id = (os.getenv("YOUTUBE_CLIENT_ID") or "").strip()
    redirect_uri = (os.getenv("YOUTUBE_REDIRECT_URI") or "http://127.0.0.1:8765").strip()
    if not client_id:
        raise SystemExit("YOUTUBE_CLIENT_ID missing")
    out = generate_authorization(client_id, redirect_uri)
    Path("magic-engine/output").mkdir(parents=True, exist_ok=True)
    Path("magic-engine/output/youtube-oauth-request.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(out["authorization_url"])
