# backend/app.py
from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from services.rppg_detector import extract_rppg
from services.frame_analyzer import analyze_frame_variance
from services.zkp_engine import generate_zkp_proof
import jwt, hashlib, time

app = FastAPI()

@app.post("/analyze")
async def analyze(payload: FramePayload, token=Depends(verify_jwt)):
    results = {
        "rppg_bpm": extract_rppg(payload.frames),
        "frame_variance": analyze_frame_variance(payload.frames),
        "lipsync_lag_ms": detect_lipsync(payload.audio, payload.frames),
        "micro_jitter_um": measure_jitter(payload.frames),
    }
    score = compute_humanity_score(results)
    return {"score": score, "signals": results, "timestamp": time.time()}

@app.post("/verify")
async def verify(session_id: str, score: float):
    if score >= 70:
        proof = generate_zkp_proof(session_id)  # No biometrics stored
        token = jwt.encode({"sid": session_id, "verified": True,
                           "zkp_hash": proof}, SECRET_KEY)
        return {"verified": True, "token": token, "zkp_badge": proof}
    return {"verified": False, "reason": "Deepfake signature detected"}

def compute_humanity_score(signals):
    weights = {"rppg": 0.35, "variance": 0.25, 
               "jitter": 0.20, "lipsync": 0.20}
    # Weighted scoring with normalization per signal
    rppg_score  = 100 if 55 <= signals["rppg_bpm"] <= 100 else 20
    var_score   = 100 - (signals["frame_variance"] * 80)  # low σ = human
    jitter_score= 100 if signals["micro_jitter_um"] < 15 else 25
    sync_score  = 100 if signals["lipsync_lag_ms"] < 60 else 10
    return (rppg_score*weights["rppg"] + var_score*weights["variance"] +
            jitter_score*weights["jitter"] + sync_score*weights["lipsync"])