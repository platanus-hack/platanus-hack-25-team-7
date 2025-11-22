
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

