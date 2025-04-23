#!/bin/bash

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create log directory if it doesn't exist
mkdir -p "${DIR}/../../../logs/mechanic_tests/status_effects"

# Run the status effects test
echo "Running status effects tests..."
python3 "${DIR}/test_status_effects.py"

# Check if test was successful
if [ $? -eq 0 ]; then
    echo "Status effects tests completed successfully!"
    echo "Logs available at: ${DIR}/../../../logs/mechanic_tests/status_effects/"
else
    echo "Status effects tests failed!"
    exit 1
fi 