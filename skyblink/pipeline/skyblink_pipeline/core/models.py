from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class CrossMatch(BaseModel):
    catalog: Optional[str]
    id: Optional[str]
    sep_arcsec: Optional[float]

class Tiles(BaseModel):
    epoch_a: str
    epoch_b: str
    diff: str
    snr: str

class CandidateRecord(BaseModel):
    id: str
    field_id: str
    ra_deg: float
    dec_deg: float
    band_um: float
    epochs: List[str]
    snr: float
    p_local: float
    p_trials_adjusted: float
    kind: Literal["dipole", "pair", "appeared", "disappeared"]
    dipole_separation_arcsec: float
    sharpness: float
    chi2_psf: float
    persistent_in_other_pass: bool
    type_label: Literal["known_asteroid", "known_comet", "hpm_star", "known_variable", "unidentified"]
    crossmatch: CrossMatch
    status: Literal["candidate", "known", "rejected"]
    tiles: Tiles
    notes: str

class Center(BaseModel):
    ra_deg: float
    dec_deg: float

class FieldManifest(BaseModel):
    id: str
    name: str
    center: Center
    size_deg: float
    bands_um: List[float]
    passes_available: List[str]
    pair_status: Literal["ok", "not_enough_epochs"]
    delta_lambda_um: float
    story_id: str
    candidates: List[str]
    data_release: str
    simulated: bool
    acknowledgement: bool
