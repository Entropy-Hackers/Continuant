# Copyright Entropy Hackers. Licensed under the Apache License, Version 2.0.
"""Continuant instance dashboard (v2, FastAPI + Vue 3 + SQLite).

Runs ALONGSIDE a single Continuant instance — one dashboard deployment per
instance, colocated with it (not a cross-instance/multi-server aggregator,
see docs/adr/0002).

Reads this instance's own `audit/` (produced by tools/audit-tap) and,
read-only, its `workspace/`. Writes exactly one thing: `control/command.json`
— a request that a host-side executor (tools/control-exec) picks up and
acts on; this container never gets `docker.sock`. See docs/adr/0004.
"""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from fastapi import Cookie, Depends, FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import auth
import control
import db
import reading

INSTANCE_NAME = os.environ["DASHBOARD_INSTANCE_NAME"]
AUDIT_DIR = Path(os.environ.get("DASHBOARD_AUDIT_DIR", "/data/audit"))
WORKSPACE_DIR = Path(os.environ.get("DASHBOARD_WORKSPACE_DIR", "/data/workspace"))
CONTROL_DIR = Path(os.environ.get("DASHBOARD_CONTROL_DIR", "/data/control"))
DB_PATH = Path(os.environ.get("DASHBOARD_DB_PATH", "/data/db/dashboard.sqlite3"))
ADMIN_PASSWORD_HASH = os.environ["DASHBOARD_ADMIN_PASSWORD_HASH"].encode("utf-8")
SECRET_KEY = os.environ["DASHBOARD_SECRET_KEY"]
POLL_INTERVAL_MINUTES = int(os.environ.get("DASHBOARD_POLL_INTERVAL_MINUTES", "5"))
STALE_AFTER = timedelta(minutes=POLL_INTERVAL_MINUTES * 2)

serializer = auth.make_serializer(SECRET_KEY)
db.init_db(DB_PATH)

app = FastAPI(title=f"Continuant Dashboard — {INSTANCE_NAME}")


def require_auth(dashboard_session: str | None = Cookie(default=None)) -> None:
    if not auth.verify_session_cookie(serializer, dashboard_session):
        raise HTTPException(status_code=401, detail="not authenticated")


class LoginRequest(BaseModel):
    password: str


class StopResumeRequest(BaseModel):
    channel: str


class CronRequest(BaseModel):
    job_id: str
    enabled: bool


class PhaseRequest(BaseModel):
    phase: str
    notes: str = ""


@app.post("/api/login")
def login(body: LoginRequest, response: Response):
    if not auth.check_password(body.password, ADMIN_PASSWORD_HASH):
        raise HTTPException(status_code=401, detail="Falsches Passwort.")
    cookie_value = auth.make_session_cookie(serializer)
    response.set_cookie(
        auth.COOKIE_NAME, cookie_value,
        max_age=auth.MAX_AGE_SECONDS, httponly=True, samesite="lax",
    )
    return {"ok": True}


@app.post("/api/logout")
def logout(response: Response):
    response.delete_cookie(auth.COOKIE_NAME)
    return {"ok": True}


@app.get("/api/status", dependencies=[Depends(require_auth)])
def status():
    summary = reading.read_instance_summary(AUDIT_DIR, STALE_AFTER)
    life = reading.read_instance_life(WORKSPACE_DIR)
    phase = control.read_phase(CONTROL_DIR)
    return {
        "instance": INSTANCE_NAME,
        **summary,
        **life,
        "phase": phase,
    }


@app.get("/api/control/log", dependencies=[Depends(require_auth)])
def control_log():
    return {"entries": control.tail_log(CONTROL_DIR)}


@app.post("/api/control/stop", dependencies=[Depends(require_auth)])
def control_stop(body: StopResumeRequest):
    try:
        control.request_stop_channel(CONTROL_DIR, body.channel, requested_by="dashboard")
    except control.ControlQueueBusy as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "queued": "stop_channel"}


@app.post("/api/control/resume", dependencies=[Depends(require_auth)])
def control_resume(body: StopResumeRequest):
    try:
        control.request_resume_channel(CONTROL_DIR, body.channel, requested_by="dashboard")
    except control.ControlQueueBusy as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "queued": "resume_channel"}


@app.post("/api/control/cron", dependencies=[Depends(require_auth)])
def control_cron(body: CronRequest):
    try:
        control.request_set_cron_enabled(CONTROL_DIR, body.job_id, body.enabled, requested_by="dashboard")
    except control.ControlQueueBusy as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "queued": "set_cron_enabled"}


@app.get("/api/phase", dependencies=[Depends(require_auth)])
def get_phase():
    return {
        "current": control.read_phase(CONTROL_DIR),
        "history": db.recent_phase_history(DB_PATH),
    }


@app.put("/api/phase", dependencies=[Depends(require_auth)])
def put_phase(body: PhaseRequest):
    if body.phase not in ("unmuendig", "muendig"):
        raise HTTPException(status_code=400, detail="phase must be 'unmuendig' or 'muendig'")
    doc = control.write_phase(CONTROL_DIR, body.phase, body.notes)
    db.record_phase_change(DB_PATH, doc["since"], body.phase, body.notes, changed_by="dashboard")
    return doc


# Static frontend (Vite build output) — mounted last so /api/* above takes
# precedence. Single-page app, no client-side router, so plain StaticFiles
# with html=True (serves index.html for /) is enough.
FRONTEND_DIST = Path(os.environ.get("DASHBOARD_FRONTEND_DIST", "/app/frontend_dist"))
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
