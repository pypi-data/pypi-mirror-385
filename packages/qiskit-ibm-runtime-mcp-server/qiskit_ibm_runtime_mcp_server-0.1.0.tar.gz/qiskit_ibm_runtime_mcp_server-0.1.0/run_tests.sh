#!/bin/bash

# Qiskit IBM Runtime MCP Server - Test Runner Script

set -e

echo "🧪 Running Qiskit IBM Runtime MCP Server Tests"
echo "=============================================="

# Install test dependencies
echo "📦 Installing test dependencies..."
uv sync --group dev --group test

# Run linting
echo ""
echo "🔍 Running code linting..."
uv run ruff check src tests
uv run ruff format --check src tests

# Run type checking
echo ""
echo "🔬 Running type checking..."
uv run mypy src

# Run unit tests
echo ""
echo "🧪 Running unit tests..."
uv run pytest tests/ -v -m "not integration" --cov=src --cov-report=term-missing

# Run integration tests
echo ""
echo "🔗 Running integration tests..."
uv run pytest tests/ -v -m "integration" --cov=src --cov-append --cov-report=term-missing

# Generate coverage report
echo ""
echo "📊 Generating coverage report..."
uv run pytest tests/ --cov=src --cov-report=html --cov-report=xml

echo ""
echo "✅ All tests completed successfully!"
echo "📋 Coverage report generated in htmlcov/index.html"

# Assisted by watsonx Code Assistant