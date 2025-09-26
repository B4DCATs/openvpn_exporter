# OpenVPN Prometheus Exporter v2.0 - Makefile

.PHONY: help build run test clean lint format docker-build docker-run docker-compose-up docker-compose-down

# Default target
help:
	@echo "OpenVPN Prometheus Exporter v2.0"
	@echo ""
	@echo "Available targets:"
	@echo "  build          - Install Python dependencies"
	@echo "  run            - Run the exporter locally"
	@echo "  test           - Run tests"
	@echo "  lint           - Run linter"
	@echo "  format         - Format code with black"
	@echo "  clean          - Clean up generated files"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run Docker container"
	@echo "  docker-compose-up   - Start with docker-compose"
	@echo "  docker-compose-down - Stop docker-compose"

# Python targets
build:
	pip install -r requirements.txt

run:
	python openvpn_exporter.py --openvpn.status_paths examples/client.status,examples/server2.status,examples/server3.status

test:
	pytest tests/ -v

lint:
	flake8 openvpn_exporter.py
	mypy openvpn_exporter.py

format:
	black openvpn_exporter.py

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache

# Docker targets
docker-build:
	docker build -t openvpn-exporter:v2.0 .

docker-run:
	docker run -d \
		--name openvpn-exporter-v2 \
		-p 9176:9176 \
		-v $(PWD)/examples:/app/examples:ro \
		openvpn-exporter:v2.0 \
		--openvpn.status_paths /app/examples/client.status,/app/examples/server2.status,/app/examples/server3.status

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

# Development targets
dev-setup: build
	@echo "Development environment setup complete"
	@echo "Run 'make run' to start the exporter"

# Production targets
prod-build: docker-build
	@echo "Production image built: openvpn-exporter:v2.0"

# Security targets
security-check:
	@echo "Running security checks..."
	bandit -r openvpn_exporter.py
	safety check

# All-in-one targets
setup: build
	@echo "Setup complete. Run 'make run' to start."

full-test: lint test
	@echo "All tests passed!"

# Help for specific targets
help-build:
	@echo "Build: Install Python dependencies from requirements.txt"

help-run:
	@echo "Run: Start the exporter with example status files"

help-docker:
	@echo "Docker: Build and run the exporter in a container"
