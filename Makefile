# Everything is started from here, by hand. Nothing runs on a timer.
#
#   make check      read every article and say what is wrong with any of them
#   make publish    check, then publish the articles to the portal (Firestore)
#   make preview    check, then write them where a local portal reads them

SHELL := /bin/bash
.DEFAULT_GOAL := help
.PHONY: help install test check publish preview

# The Google Cloud project of the portal, and where a local portal keeps its data.
GCP_PROJECT ?= $(shell gcloud config get-value project 2>/dev/null)
PORTAL_DATA ?= ../market-hub-landing/data/opinion
export UV_LINK_MODE ?= copy

help: ## List the targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  make %-9s %s\n", $$1, $$2}'

install: ## Install the dependencies
	uv sync

test: ## Run the tests
	uv run pytest

check: ## Read every article and say what is wrong with any of them
	uv run python -m marketopinion check

publish: ## Check the articles and publish them to the portal (needs gcloud signed in)
	GOOGLE_CLOUD_PROJECT=$(GCP_PROJECT) uv run python -m marketopinion publish

preview: ## Check the articles and write them where a local portal reads them
	uv run python -m marketopinion publish --to $(PORTAL_DATA)
