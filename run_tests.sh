#!/bin/bash

# Run pytest with coverage report
pytest tests/ -v --cov=app --cov-report=term-missing 