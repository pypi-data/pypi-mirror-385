#!/bin/bash
run_and_check() {
    "$@"
    status=$?
    if [ $status -ne 0 ]; then
        echo "Error with \"$@\": Exited with status $status"
        exit $status
    fi
    return $status
}

echo "I: Creating and activating virtual environment for pre-commit..."
python3 -m venv "$(dirname "$0")/../.venv"
source "$(dirname "$0")/../.venv/bin/activate"

echo "I: Installing tools required for pre-commit checks..."
run_and_check pip install dos2unix
run_and_check pip install clang-format==18.1.3
echo "I: Installing pre-commit in virtual environment..."
run_and_check pip install pre-commit
run_and_check pre-commit install

echo "I: Installation successful."
