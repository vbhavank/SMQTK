#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Use the repository root directory as the docker context
CONTEXT_DIR="${SCRIPT_DIR}/../../../"

IMAGE_VERSION="$(date +%Y%m%d)"
CPU_SUFFIX=-cpu
GPU_SUFFIX=-gpu-cuda8-cudnn6

docker build \
  -t kitware/smqtk/iqr_playground:${IMAGE_VERSION}${CPU_SUFFIX} \
  -f "${SCRIPT_DIR}/Dockerfile.cpu.df" \
  "${CONTEXT_DIR}"

if [ -x "$(which nvidia-docker 2>/dev/null)" ]
then
  nvidia-docker build \
    -t kitware/smqtk/iqr_playground:${IMAGE_VERSION}${GPU_SUFFIX} \
    -f "${SCRIPT_DIR}/Dockerfile.gpu-cuda8.0-cudnn6.df" \
    "${CONTEXT_DIR}"
fi
