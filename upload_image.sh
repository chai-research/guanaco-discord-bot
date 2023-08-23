#!/bin/bash

set -e

IMAGE="gcr.io/chai-959f8/guanaco-discord-bot:latest"
echo "Building image '$IMAGE'"

docker build -t "$IMAGE" --platform linux/amd64 .
docker push "$IMAGE"
