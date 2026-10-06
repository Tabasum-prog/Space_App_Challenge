from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="SkyBlink API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Vote(BaseModel):
    candidate_id: str
    vote: str # "confirm" or "reject"

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/fields")
def get_fields():
    return [{"id": "F03", "name": "Ecliptic plane field A"}]

@app.get("/fields/{field_id}")
def get_field(field_id: str):
    if field_id != "F03":
        raise HTTPException(status_code=404, detail="Field not found")
    
    return {
        "id": "F03",
        "name": "Ecliptic plane field A",
        "center": {"ra_deg": 164.28, "dec_deg": 41.28},
        "size_deg": 0.2,
        "bands_um": [1.25, 2.20, 3.30, 4.27],
        "passes_available": ["2025-pass1", "2025-pass2", "2026-pass3"],
        "pair_status": "ok",
        "delta_lambda_um": 0.02,
        "story_id": "S2",
        "candidates": ["F03-C001", "F03-C012"],
        "data_release": "QR2",
        "simulated": True,
        "acknowledgement": True
    }

@app.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: str):
    if candidate_id != "F03-C012":
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    return {
        "id": "F03-C012",
        "field_id": "F03",
        "ra_deg": 164.2800,
        "dec_deg": 41.2800,
        "band_um": 3.30,
        "epochs": ["2025-pass1", "2026-pass3"],
        "snr": 6.4,
        "p_local": 8.1e-11,
        "p_trials_adjusted": 3.2e-5,
        "kind": "dipole",
        "dipole_separation_arcsec": 11.2,
        "sharpness": 1.05,
        "chi2_psf": 1.2,
        "persistent_in_other_pass": True,
        "type_label": "unidentified",
        "crossmatch": { "catalog": None, "id": None, "sep_arcsec": None },
        "status": "candidate",
        "tiles": { 
            "epoch_a": "F03/a.webp", 
            "epoch_b": "F03/b.webp",
            "diff": "F03/d.webp", 
            "snr": "F03/s.webp" 
        },
        "notes": ""
    }

@app.post("/live/pair")
def live_pair():
    return JSONResponse(
        status_code=501, 
        content={"message": "Live connection to IRSA is not implemented yet. The real provider must be plugged in."}
    )

import sqlite3

conn = sqlite3.connect('votes.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS votes (candidate_id TEXT, vote TEXT)''')
conn.commit()

@app.post("/votes")
def vote(vote: Vote):
    c.execute("INSERT INTO votes VALUES (?, ?)", (vote.candidate_id, vote.vote))
    conn.commit()
    return {"status": "ok", "recorded": vote.model_dump()}
