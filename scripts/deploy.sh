#!/usr/bin/env bash
set -eo pipefail

env=$1
tag=$2

echo "set webhook-secret-value.yaml"
op inject -i tpl/webhook-secret-value.yaml.tpl -o charts/github-webhook-receiver/webhook-secret-value.yaml

echo "deploy github-webhook-receiver:$tag to demo-$env"
helm upgrade github-webhook-receiver charts/github-webhook-receiver \
      --install --atomic --timeout 120s \
      --namespace "demo-$env" \
      --values "charts/github-webhook-receiver/values.yaml" \
      --values "charts/github-webhook-receiver/values-$env.yaml" \
      --values "charts/github-webhook-receiver/webhook-secret-value.yaml" \
      --set image.tag="$tag"
