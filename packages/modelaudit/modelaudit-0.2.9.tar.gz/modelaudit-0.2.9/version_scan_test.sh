#!/bin/bash
set -e

# Script to scan sentence-transformers/all-MiniLM-L6-v2 across all ModelAudit versions
# From v0.1.5 (when model was added) to v0.2.8 (current)

MODEL="hf://sentence-transformers/all-MiniLM-L6-v2"
VERSIONS=("0.1.5" "0.2.0" "0.2.1" "0.2.2" "0.2.3" "0.2.4" "0.2.5" "0.2.6" "0.2.7" "0.2.8")
RESULTS_DIR="version_scan_results"

mkdir -p "$RESULTS_DIR"

echo "========================================="
echo "ModelAudit Version Comparison Test"
echo "Model: $MODEL"
echo "Versions: ${VERSIONS[@]}"
echo "========================================="
echo ""

for VERSION in "${VERSIONS[@]}"; do
    echo "----------------------------------------"
    echo "Testing version $VERSION"
    echo "----------------------------------------"

    # Create temporary venv for this version
    VENV_DIR="/tmp/modelaudit_test_${VERSION}"
    rm -rf "$VENV_DIR"
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"

    # Install specific version
    echo "Installing modelaudit==$VERSION..."
    pip install -q "modelaudit==$VERSION" 2>&1 | grep -v "already satisfied" || true

    # Run scan with JSON output
    OUTPUT_FILE="$RESULTS_DIR/scan_${VERSION}.json"
    echo "Scanning model..."

    # Run scan - some versions might fail, that's OK
    if modelaudit "$MODEL" --format json --output "$OUTPUT_FILE" 2>&1 | tee "$RESULTS_DIR/scan_${VERSION}.log"; then
        echo "✓ Scan completed successfully"
    else
        EXIT_CODE=$?
        echo "✗ Scan failed with exit code $EXIT_CODE"
        echo "$EXIT_CODE" > "$RESULTS_DIR/scan_${VERSION}.exitcode"
    fi

    # Clean up venv
    deactivate
    rm -rf "$VENV_DIR"

    echo ""
done

echo "========================================="
echo "All scans complete!"
echo "Results saved to $RESULTS_DIR/"
echo "========================================="
