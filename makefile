# Makefile for code formatting using Black
# -------- Global target --------
format-all:
	@echo "Formatting all source files..."
	@black .
	@echo "Formatting complete."

check-formatting-all:
	@echo "Checking code format..."
	@black --check . || true
	@echo "Format check complete."

get-formatting-status-all:
	@echo "Getting formatting status..."
	@black --diff --color .
	@echo "Formatting status complete."
	
# -------- Clean all --------
clean-code: check-formatting-all get-formatting-status-all format-all
	@echo "Code cleaned and formatted, you can commit the changes now."

# --------- Run bot ---------
# Usage: make run-bot reset-log=true (to clear logs before starting)
reset-log ?= false

run-bot:
	@clear
	@if [ "$(reset-log)" = "true" ]; then \
		echo "Resetting bot.log..."; \
		> bot.log; \
		echo "Logs cleared."; \
	fi
	@echo "Starting EpsilonAI bot..."
	@python3 main.py

#---Delete container and image and create new one---
delete-container-and-image:
	@echo "Deleting existing Docker container and image if they exist..."
	@sudo docker stop bot_container || true
	@sudo docker rm bot_container || true
	@docker rmi bot || true
	@echo "Deletion complete."

#---Build docker image---
build-docker-image:
	@echo "Building Docker image..."
	@sudo docker build -t bot .
	@echo "Docker image built successfully."

#---Run docker container---
run-docker-container:
	@echo "Running Docker container..."
	@sudo docker run --name bot_container --env-file .env bot
	@echo "Docker container is running."

#---Build and run docker container---
container: delete-container-and-image build-docker-image run-docker-container