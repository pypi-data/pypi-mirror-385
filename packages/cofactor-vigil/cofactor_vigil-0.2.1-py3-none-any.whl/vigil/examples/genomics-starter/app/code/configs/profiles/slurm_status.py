#!/usr/bin/env python3
"""SLURM job status checker for Snakemake."""

import subprocess
import sys

jobid = sys.argv[1]

try:
    # Check job status with sacct
    result = subprocess.run(
        ["sacct", "-j", jobid, "--format=State", "--noheader", "--parsable2"],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )

    status = result.stdout.strip().split("|")[0]

    # Map SLURM states to Snakemake expectations
    if status in ["COMPLETED"]:
        print("success")
    elif status in ["RUNNING", "PENDING", "COMPLETING"]:
        print("running")
    else:
        # FAILED, CANCELLED, TIMEOUT, NODE_FAIL, PREEMPTED, OUT_OF_MEMORY
        print("failed")

except subprocess.TimeoutExpired:
    print("running")  # Assume still running if sacct times out
except subprocess.CalledProcessError:
    print("failed")
except Exception:
    print("failed")
