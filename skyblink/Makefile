.PHONY: setup data pipeline test lint web api demo verify

setup:
	@echo "Setting up project..."
	python -m pip install -r pipeline/requirements.txt
	python -m pip install -r api/requirements.txt
	cd web && npm install

data:
	@echo "Generating simulated data..."
	python -m pipeline.skyblink_pipeline.synth.generate

pipeline:
	@echo "Running processing pipeline..."
	python -m pipeline.skyblink_pipeline.core.run

test:
	pytest pipeline/tests
	pytest api/tests
	cd web && npm run test

lint:
	ruff check pipeline
	ruff check api
	cd web && npm run lint

web:
	cd web && npm run build
	cd web && npm start

api:
	cd api && uvicorn app.main:app --reload

demo: setup data pipeline
	@echo "Starting API and Web..."
	start cmd /c "cd api && uvicorn app.main:app --port 8000"
	cd web && npm run dev

verify: lint test
	bash scripts/verify.sh
