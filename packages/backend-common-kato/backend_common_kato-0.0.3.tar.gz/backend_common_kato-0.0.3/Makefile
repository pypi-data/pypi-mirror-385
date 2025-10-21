# Backend Common Package Makefile
# Simple deployment commands

.PHONY: help clean build test version publish

# Default target
help: ## Show available commands
	@echo "Backend Common Package - Available Commands:"
	@echo ""
	@echo "  clean     - Clean build artifacts"
	@echo "  build     - Build package"
	@echo "  test      - Run tests"
	@echo "  version   - Show current version"
	@echo "  publish   - Publish package (includes test + build + deploy)"
	@echo ""

# Clean build artifacts
clean: ## Clean build artifacts
	chmod +x scripts/clean.sh
	./scripts/clean.sh

# Build package
build: ## Build package
	chmod +x scripts/build.sh
	./scripts/build.sh

# Run tests
test: ## Run tests
	chmod +x scripts/test.sh
	./scripts/test.sh

# Show current version
version: ## Show current version
	chmod +x scripts/version.sh
	./scripts/version.sh

# Publish package (full pipeline)
publish: ## Publish package (check version, test, build, deploy)
	chmod +x scripts/publish.sh
	./scripts/publish.sh
