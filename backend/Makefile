.PHONY: run-backend stop-backend test-upload test-split ngrok help setup

# Variables
VENV = ./venv/bin
PYTHON = $(VENV)/python3
UVICORN = $(VENV)/uvicorn
LOG_FILE = ./server.log
PID_FILE = backend.pid

help:
	@echo "Available commands:"
	@echo "  make setup         - Create venv and install dependencies"
	@echo "  make run-backend   - Run FastAPI backend in background with reload"
	@echo "  make stop-backend  - Stop the background backend process"
	@echo "  make test-upload   - Test /upload endpoint with sample video"
	@echo "  make test-split    - Test /split endpoint (requires JOB_ID)"
	@echo "  make ngrok         - Start ngrok tunnel on port 8000"

setup:
	@echo "Creating virtual environment..."
	python3 -m venv venv
	@echo "Installing dependencies..."
	$(VENV)/pip install -r requirements.txt

run-backend:
	@echo "Starting backend in background with reload..."
	@rm -f $(LOG_FILE)
	@nohup $(UVICORN) main:app --reload --host 0.0.0.0 --port 8000 > $(LOG_FILE) 2>&1 & echo $$! > $(PID_FILE)
	@sleep 2
	@if [ -f $(PID_FILE) ]; then \
		echo "Backend started with PID $$(cat $(PID_FILE)). Logs are being written to $(LOG_FILE)"; \
	fi

stop-backend:
	@if [ -f $(PID_FILE) ]; then \
		echo "Stopping backend with PID $$(cat $(PID_FILE))..."; \
		kill $$(cat $(PID_FILE)) 2>/dev/null || true; \
		rm -f $(PID_FILE); \
		echo "Backend stopped."; \
	else \
		echo "No $(PID_FILE) found. Is the backend running?"; \
	fi

test-upload:
	@echo "Testing /upload endpoint..."
	@curl -X POST "http://localhost:8000/upload" -F "file=@media/round_chimaev.mp4"
	@echo "\n\nCopy the 'job_id' from the response above and run: make test-split JOB_ID=<job_id>"

test-split:
	@if [ -z "$(JOB_ID)" ]; then \
		echo "Error: JOB_ID is missing. Usage: make test-split JOB_ID=<your_job_id>"; \
	else \
		echo "Checking status for Job ID: $(JOB_ID)"; \
		curl "http://localhost:8000/split/$(JOB_ID)"; \
		echo ""; \
	fi

ngrok:
	@echo "Starting ngrok..."
	@ngrok http 8000

export_env:
	@echo "Exporting vars..."
	@set -a; . ./.env; set +a; \
		echo "All variables exported."; \
		bash

set_credentials:
	@echo "Setting AWS credentials ..."
	aws configure set aws_access_key_id $(AWS_ACCESS_KEY_ID)
	aws configure set aws_secret_access_key $(AWS_SECRETS_ACCESS_KEY)
	aws configure set region $(AWS_REGION)
	cat ~/.aws/credentials
