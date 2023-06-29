#!/bin/sh

set -euxo pipefail

cd /

python -m "$@"
