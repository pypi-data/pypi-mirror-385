#!/bin/bash
# Basic happy path tests for edgarcli

set -e  # Exit on first error

echo "Running edgarcli basic tests..."
echo

# Set up test identity
export EDGAR_IDENTITY="Test User test@example.com"

# Test 1: Company lookup
echo "Test 1: Company lookup (AAPL)"
uv run edgarcli company AAPL > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ Company lookup successful"
else
    echo "✗ Company lookup failed"
    exit 1
fi
echo

# Test 2: Get filings list
echo "Test 2: Get filings list (AAPL 10-K)"
uv run edgarcli filings AAPL --form 10-K --limit 3 > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ Filings list successful"
else
    echo "✗ Filings list failed"
    exit 1
fi
echo

# Test 3: Get latest filing
echo "Test 3: Get latest filing (AAPL 10-K)"
uv run edgarcli filing AAPL --form 10-K --latest > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ Latest filing retrieval successful"
else
    echo "✗ Latest filing retrieval failed"
    exit 1
fi
echo

# Test 4: Configuration commands
echo "Test 4: Configuration commands"
uv run edgarcli config get-identity > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ Config get-identity successful"
else
    echo "✗ Config get-identity failed"
    exit 1
fi
echo

echo "All tests passed! ✓"
