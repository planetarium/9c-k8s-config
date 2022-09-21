#!/usr/bin/env bash
set -ex

BASEDIR=$(dirname "$0")
echo "$BASEDIR"

# kubectl configuration must be already set on your environment
checkout_main_cluster() {
  aws eks update-kubeconfig --name 9c-previewnet --region us-east-2 --role-arn arn:aws:iam::319679068466:role/EKS
  kubectl config set current-context arn:aws:eks:us-east-2:319679068466:cluster/9c-previewnet
}

clear_cluster() {
  kubectl scale --replicas=0 \
    sts/explorer \
    sts/previewnet-auth-miner \
    sts/previewnet-miner-1 \
    sts/remote-headless-1 \
    
  kubectl delete -k $BASEDIR
  # Provide ample time so that the nodes can be fully terminated before a new deployment 
  echo "Provide ample time so that the nodes can be fully terminated before a new deployment"
  sleep 20
}

deploy_cluster() {
  kubectl apply -f $BASEDIR/configmap-versions.yaml
  kubectl apply -k $BASEDIR
}

slack_token=$(kubectl get secrets/slack-token  --template='{{.data.token | base64decode}}')
curl --data "[K8S] PreviewNet deployment start." "https://planetariumhq.slack.com/services/hooks/slackbot?token=$slack_token&channel=%239c-previewnet"
echo "Checkout 9c-previewnet cluster."
checkout_main_cluster || true

echo "Clear 9c-previewnet cluster."
clear_cluster || true

echo "Deploy 9c-previewnet cluster."
deploy_cluster || true
curl --data "[K8S] PreviewNet deployment complete." "https://planetariumhq.slack.com/services/hooks/slackbot?token=$slack_token&channel=%239c-previewnet"

kubectl get pod --watch
