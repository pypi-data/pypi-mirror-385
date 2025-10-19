"""
Proto Generation Information

This file contains information about when and how the proto bindings were generated.
Generated automatically by scripts/generate_proto.py
"""

import subprocess

# Source repository information
PROTO_REPOSITORY = "https://github.com/ehsaniara/joblet-proto"
PROTO_COMMIT_HASH = "02ea2bb95d51fa3b17b63e23600d57a8f68cba33"
PROTO_TAG = "v2.3.0"
GENERATION_TIMESTAMP = (
    "Sat Oct 18 05:24:38 PM UTC 2025"
)

# Protocol buffer compiler version
try:
    PROTOC_VERSION = subprocess.run(
        ["protoc", "--version"], capture_output=True, text=True
    ).stdout.strip()
except Exception:
    PROTOC_VERSION = "unknown"

# Python grpcio-tools version
GRPCIO_TOOLS_VERSION = "1.75.1"
