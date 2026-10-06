#!/bin/bash
set -e

echo "Running Verification Script..."

echo "Testing Python..."
python -m pytest -v

echo "Generating data..."
python -m pipeline.skyblink_pipeline.synth.generate

echo "Testing Web..."
cd web
npm test
npm run build
cd ..

echo "============================"
echo "Verify OK"
echo "============================"
