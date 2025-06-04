#!/usr/bin/env bash
set -eo pipefail

env=$1
tag=$2

echo "uninstall github-webhook-receiver:$tag from demo-$env"
helm uninstall github-webhook-receiver --namespace "demo-$env"
