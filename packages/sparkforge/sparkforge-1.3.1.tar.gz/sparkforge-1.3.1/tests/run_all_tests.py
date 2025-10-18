#!/usr/bin/env python3
"""
Complete test runner for SparkForge.

This script runs all tests (unit, integration, system) with proper configuration and reporting.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_all_tests():
    """Run all tests with mypy type checking."""
    print("🚀 Running SparkForge Complete Test Suite")
    print("🔧 Using Mock Spark (faster, more reliable testing)")
    print("=" * 50)

    # Set up environment
    env = os.environ.copy()
    env["JAVA_HOME"] = "/opt/homebrew/Cellar/openjdk@11/11.0.28"
    env["PATH"] = f"{env['JAVA_HOME']}/bin:{env['PATH']}"
    # Default to mock mode for faster, more reliable testing
    env["SPARK_MODE"] = "mock"

    start_time = time.time()

    # Run main tests (excluding performance tests)
    print("📊 Running main tests (unit, integration, system)...")
    main_test_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "--ignore=tests/performance",
        "-v",
        "--tb=short",
        "--durations=10",
        "--cov=sparkforge",
        "--cov-report=term",
        "--cov-report=html:htmlcov_all",
    ]

    main_result = subprocess.run(main_test_cmd, env=env, capture_output=True, text=True)

    # Run performance tests separately
    print("⚡ Running performance tests...")
    perf_test_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/performance/",
        "-v",
        "--tb=short",
    ]

    perf_result = subprocess.run(perf_test_cmd, env=env, capture_output=True, text=True)

    # Skip mypy type checking on tests (not needed)
    # Only run mypy on source code
    print("🔍 Running mypy on source code...")
    mypy_source_cmd = [
        sys.executable,
        "-m",
        "mypy",
        "sparkforge/",
        "--config-file=mypy.ini",
    ]

    mypy_source_result = subprocess.run(
        mypy_source_cmd, env=env, capture_output=True, text=True
    )

    end_time = time.time()
    duration = end_time - start_time

    # Print results
    print("\n" + "=" * 50)
    print("📊 COMPLETE TEST SUITE RESULTS")
    print("=" * 50)

    if main_result.returncode == 0:
        print("✅ Main tests: PASSED")
    else:
        print("❌ Main tests: FAILED")
        print(main_result.stdout)
        print(main_result.stderr)

    if perf_result.returncode == 0:
        print("✅ Performance tests: PASSED")
    else:
        print("❌ Performance tests: FAILED")
        print(perf_result.stdout)
        print(perf_result.stderr)

    if mypy_source_result.returncode == 0:
        print("✅ Source code mypy: PASSED")
    else:
        print("❌ Source code mypy: FAILED")
        print(mypy_source_result.stdout)
        print(mypy_source_result.stderr)

    print(f"⏱️  Total duration: {duration:.2f}s")

    # Return success if all checks passed
    return main_result.returncode == 0 and perf_result.returncode == 0 and mypy_source_result.returncode == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
