#!/usr/bin/env bash
set -ex

BASEDIR=$(dirname "$0")
echo "$BASEDIR"

slack_token=$(kubectl get secrets/slack-token  --template='{{.data.token | base64decode}}')
curl --data "[K8S] Start headless deployment for onboarding." "https://planetariumhq.slack.com/services/hooks/slackbot?token=$slack_token&channel=%23onboarding-portal"
echo "Checkout 9c-onboarding cluster."
# kubectl configuration must be already set on your environment
aws eks update-kubeconfig --name 9c-onboarding --region us-east-2 --role-arn arn:aws:iam::319679068466:role/EKS
kubectl config set current-context arn:aws:eks:us-east-2:319679068466:cluster/9c-onboarding

kubectl delete -k $BASEDIR
# Provide ample time so that the nodes can be fully terminated before a new deployment 
echo "Provide ample time so that the nodes can be fully terminated before a new deployment"
sleep 30

echo "Deploy 9c-onboarding cluster."
kubectl apply -f $BASEDIR/configmap-versions.yaml
kubectl apply -k $BASEDIR
curl --data "[K8S] Complete headless deployment for onboarding." "https://planetariumhq.slack.com/services/hooks/slackbot?token=$slack_token&channel=%23onboarding-portal"
