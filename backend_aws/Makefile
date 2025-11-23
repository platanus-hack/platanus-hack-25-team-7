
STACK_NAME ?= pvhack-backend
REGION ?= us-east-1
API_URL ?= $(shell aws cloudformation describe-stacks --stack-name $(STACK_NAME) --region $(REGION) --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text)
BUCKET_NAME ?= $(shell aws cloudformation describe-stacks --stack-name $(STACK_NAME) --region $(REGION) --query "Stacks[0].Outputs[?OutputKey=='MediaBucketName'].OutputValue" --output text)

.PHONY: build deploy validate upload-test-video test-upload test-split test-analysis

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
	@echo '    }' >> env.json
	@echo '}' >> env.json
	@echo "env.json created successfully"


set_credentials:
	@echo "Setting AWS credentials ..."
	aws configure set aws_access_key_id $(AWS_ACCESS_KEY_ID)
	aws configure set aws_secret_access_key $(AWS_SECRETS_ACCESS_KEY)
	aws configure set region $(AWS_REGION)
	cat ~/.aws/credentials

get_api_url:
	@echo "Getting API URL for stack $(STACK_NAME) in region $(REGION)..."
	@echo "API URL: $(API_URL)"

build:
	sam build

deploy:
	sam build
	sam deploy --stack-name $(STACK_NAME) --resolve-s3 --capabilities CAPABILITY_IAM --region $(REGION) --resolve-image-repos

validate:
	sam validate --template template.yaml

upload-test-video:
	@echo "Getting Bucket Name..."
	@echo "Bucket: $(BUCKET_NAME)"
	@echo "Uploading test video..."
	aws s3 cp ../backend/media/round_chimaev.mp4 s3://$(BUCKET_NAME)/uploads/test_video.mp4 --region $(REGION)
	@echo "Video uploaded to s3://$(BUCKET_NAME)/uploads/test_video.mp4"

test-upload:
	@echo "Testing /upload endpoint at $(API_URL)..."
	@curl -s -X POST "$(API_URL)/upload" \
		-H "Content-Type: application/json" \
		-d '{"s3_key": "uploads/test_video.mp4"}' | tee last_upload.json
	@echo "\n\nJob ID saved to last_upload.json"

test-split:
	@if [ -z "$(JOB_ID)" ]; then \
		if [ -f last_upload.json ]; then \
			JOB_ID=$$(cat last_upload.json | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])"); \
			echo "Using Job ID from last_upload.json: $$JOB_ID"; \
			curl -s "$(API_URL)/split/$$JOB_ID" | jq; \
		else \
			echo "Error: JOB_ID is missing and last_upload.json not found. Usage: make test-split JOB_ID=<your_job_id>"; \
		fi \
	else \
		echo "Checking status for Job ID: $(JOB_ID)"; \
		curl -s "$(API_URL)/split/$(JOB_ID)" | jq; \
	fi

test-analysis:
	@if [ -z "$(JOB_ID)" ]; then \
		if [ -f last_upload.json ]; then \
			JOB_ID=$$(cat last_upload.json | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])"); \
			echo "Using Job ID from last_upload.json: $$JOB_ID"; \
			curl -s "$(API_URL)/analysis/$$JOB_ID" | jq; \
		else \
			echo "Error: JOB_ID is missing and last_upload.json not found. Usage: make test-analysis JOB_ID=<your_job_id>"; \
		fi \
	else \
		echo "Checking analysis status for Job ID: $(JOB_ID)"; \
		curl -s "$(API_URL)/analysis/$(JOB_ID)" | jq; \
	fi
