#!/bin/bash
# Run Django tests with coverage

echo "🧪 Running Django Tests with Coverage..."
echo "========================================"

# Install test dependencies if not installed
pip install -q pytest pytest-django pytest-cov coverage factory-boy

# Run tests with coverage
pytest --cov=. \
       --cov-report=html \
       --cov-report=term-missing \
       --cov-report=xml \
       --verbose \
       --tb=short

# Show coverage summary
echo ""
echo "📊 Coverage Summary:"
echo "==================="
coverage report

echo ""
echo "✅ Tests completed!"
echo "📄 HTML Report: htmlcov/index.html"
echo "📄 XML Report: coverage.xml"
