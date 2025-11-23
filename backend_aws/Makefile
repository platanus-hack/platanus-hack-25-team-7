
PORT ?= 3000

.PHONY: copy_env export_env env_to_json set_credentials build deploy fd validate install-nodemon run_local local-api test-upload test-split test-analysis

copy_env:
	cp ../backend/.env .env

export_env:
	@echo "Exporting vars..."
	@set -a; . ./.env; set +a; \
		echo "All variables exported."; \
		bash
		
env_to_json:
	@echo "Converting .env to env.json..."
	@echo '{' > env.json
	@echo '    "Parameters": {' >> env.json
	@awk -F '=' 'NF==2 && !/^#/ && $$1 !~ /^[[:space:]]*$$/ { \
		gsub(/^[[:space:]]+|[[:space:]]+$$/, "", $$1); \
		gsub(/^[[:space:]]+|[[:space:]]+$$/, "", $$2); \
		gsub(/"/, "", $$2); \
		if (NR > 1 && prev) print "        \"" prev_key "\": \"" prev_val "\","; \
		prev=1; prev_key=$$1; prev_val=$$2; \
	} END { \
		if (prev) print "        \"" prev_key "\": \"" prev_val "\""; \
	}' .env >> env.json
	@echo ',' >> env.json
	@echo '        "AWS_ENDPOINT_URL": "http://host.docker.internal:4566",' >> env.json
	@echo '        "DYNAMODB_ENDPOINT": "http://host.docker.internal:8001",' >> env.json
	@echo '        "SPLIT_QUEUE_URL": "http://host.docker.internal:4566/000000000000/SplitQueue.fifo",' >> env.json
	@echo '        "ANALYSIS_QUEUE_URL": "http://host.docker.internal:4566/000000000000/AnalysisQueue.fifo"' >> env.json
	@echo '    }' >> env.json
	@echo '}' >> env.json
	@echo "env.json created successfully"

set_credentials:
	@echo "Setting AWS credentials ..."
	aws configure set aws_access_key_id $(AWS_ACCESS_KEY_ID)
	aws configure set aws_secret_access_key $(AWS_SECRETS_ACCESS_KEY)
	aws configure set region $(AWS_REGION)
	cat ~/.aws/credentials

build:
	sam build

deploy:
	sam build --debug
	sam deploy --guided \
		--no-confirm-changeset \
        --capabilities CAPABILITY_IAM \
		--resolve-image-repos

fd:
	sam deploy

validate:
	sam validate --template template.yaml

install-nodemon:
	@echo "Installing nodemon globally..."
	npm install -g nodemon


run_local:
	clear
	docker image prune -f
	docker container prune -f
	docker stop $$(docker ps -q) || true
	docker rm $$(docker ps -a -q) || true
	-sudo kill -9 $$(lsof -t -i :3000) 2>/dev/null || true
	@echo "Starting SAM local API server with auto-reload..."
	@echo "Console logs will appear below:"
	@echo "================================"
	nodemon --watch ./ --ext js,py,json,yml,yaml --ignore logs/ --exec "sam build && sam local start-api --env-vars ./env.json --warm-containers EAGER --host 0.0.0.0 --container-host-interface 0.0.0.0 --add-host=host.docker.internal:host-gateway 2>&1 | tee -a logs/local-api.log"

local-api:
	sam build && sam local start-api --env-vars ./env.json --warm-containers EAGER --host 0.0.0.0 --port $(PORT)

setup-local:
	@echo "Starting local AWS services..."
	docker run -d --name dynamodb-local -p 8001:8000 amazon/dynamodb-local
	docker run -d --name localstack -p 4566:4566 -e SERVICES=s3,sqs -e DEBUG=1 localstack/localstack
	@echo "Waiting for services..."
	@sleep 10
	@echo "Creating resources..."
	aws dynamodb create-table --table-name pvhack-jobs \
		--attribute-definitions AttributeName=job_id,AttributeType=S AttributeName=split_status,AttributeType=S AttributeName=analysis_status,AttributeType=S \
		--key-schema AttributeName=job_id,KeyType=HASH \
		--global-secondary-indexes 'IndexName=SplitStatusIndex,KeySchema=[{AttributeName=split_status,KeyType=HASH}],Projection={ProjectionType=ALL}' 'IndexName=AnalysisStatusIndex,KeySchema=[{AttributeName=analysis_status,KeyType=HASH}],Projection={ProjectionType=ALL}' \
		--billing-mode PAY_PER_REQUEST \
		--endpoint-url http://localhost:8001
	aws s3 mb s3://pvhack-media --endpoint-url http://localhost:4566
	aws sqs create-queue --queue-name SplitQueue.fifo --attributes FifoQueue=true,ContentBasedDeduplication=true --endpoint-url http://localhost:4566
	aws sqs create-queue --queue-name AnalysisQueue.fifo --attributes FifoQueue=true,ContentBasedDeduplication=true --endpoint-url http://localhost:4566

stop-local:
	@echo "Stopping local services..."
	-docker stop dynamodb-local localstack
	-docker rm dynamodb-local localstack

seed-test-data:
	@echo "Uploading test video..."
	aws s3 cp ../backend/media/round_chimaev.mp4 s3://pvhack-media/uploads/test_video.mp4 --endpoint-url http://localhost:4566
	@echo "Video uploaded to s3://pvhack-media/uploads/test_video.mp4"

test-upload-local:
	@echo "Testing /upload endpoint..."
	@curl -X POST "http://localhost:$(PORT)/upload" \
		-H "Content-Type: application/json" \
		-d '{"s3_key": "uploads/test_video.mp4"}'

invoke-splitter:
	@echo "Invoking SplitterFunction..."
	@# Create event file if needed, or pass inline
	sam local invoke SplitterFunction --event events/split_event.json --env-vars env.json --docker-network host

invoke-analyzer:
	@echo "Invoking AnalyzerFunction..."
	sam local invoke AnalyzerFunction --event events/analysis_event.json --env-vars env.json --docker-network host


test-split:
	@if [ -z "$(JOB_ID)" ]; then \
		echo "Error: JOB_ID is missing. Usage: make test-split JOB_ID=<your_job_id>"; \
	else \
		echo "Checking status for Job ID: $(JOB_ID)"; \
		curl "http://localhost:$(PORT)/split/$(JOB_ID)"; \
		echo ""; \
	fi

test-analysis:
	@if [ -z "$(JOB_ID)" ]; then \
		echo "Error: JOB_ID is missing. Usage: make test-analysis JOB_ID=<your_job_id>"; \
	else \
		echo "Checking analysis status for Job ID: $(JOB_ID)"; \
		curl "http://localhost:$(PORT)/analysis/$(JOB_ID)" | python3 -m json.tool; \
		echo ""; \
	fi
