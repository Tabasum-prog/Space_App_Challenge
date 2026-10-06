# SkyBlink

A public-facing web tool that shows how the sky changes between SPHEREx survey passes, finds what moved or brightened using wavelength-matched difference imaging, and explains each object using astrophysics, quantum spectroscopy, radiation/particle physics, nuclear physics, and particle-physics-grade statistics.

## Architecture
- Pipeline (Python): Generates or fetches data, processes difference imaging, finds candidates, and exports everything as static files.
- Website (Next.js): Static site viewing pre-generated outputs, using a simulated backend or fallback API.
- Live API (FastAPI): Exposes real-time matching endpoints (fallback).

## Quick Start
```bash
make demo
```

## Testing
Run `make verify` to execute linting, unit tests, and pipeline generation.

## Data Acknowledgement
TODO: paste the official SPHEREx data acknowledgement from the IRSA SPHEREx page.
QR2 DOI 10.26131/IRSA652
