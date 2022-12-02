#!/usr/bin/env bash
set -ex

BASEDIR=$(dirname "$0")
QUITE=$(echo $1 | awk '{print tolower($0)}')

echo "$BASEDIR"

# kubectl configuration must be already set on your environment
checkout_internal_cluster() {
  aws eks update-kubeconfig --name 9c-pbft-internal --role-arn arn:aws:iam::838612679705:role/EKS
  kubectl config set current-context arn:aws:eks:us-east-2:838612679705:cluster/9c-pbft-internal
}

clear_cluster() {
  if [[ "$QUITE" != "--quite" ]]; then
    curl --data "[K8S] Clearing 9c-pbft-internal cluster." "https://planetariumhq.slack.com/services/hooks/slackbot?token=$1&channel=%23tf-9c-pbft-2022"
  fi
  kubectl delete -k $BASEDIR
}

deploy_cluster() {
  if [[ "$QUITE" != "--quite" ]]; then
    curl --data "[K8S] Deploying 9c-pbft-internal cluster." "https://planetariumhq.slack.com/services/hooks/slackbot?token=$1&channel=%23tf-9c-pbft-2022"
  fi
  kubectl apply -f $BASEDIR/configmap-versions.yaml
  kubectl apply -f $BASEDIR/configmap-snapshot-script.yaml
  kubectl apply -f $BASEDIR/configmap-data-provider.yaml
  kubectl apply -k $BASEDIR
}

# Type "y" to reset the cluster with a new snapshot and "n" to just deploy the cluster.
echo "Do you want to reset the cluster with a snapshot(y/n)?"
read response

checkout_internal_cluster || true
slack_token=$(kubectl get secrets/slack  --template='{{.data.token | base64decode}}')
echo $slack_token

clear_cluster $slack_token || true

if [ $response = y ]
then
  echo "Reset cluster with snapshot."
  if [[ "$QUITE" != "--quite" ]]; then
    curl --data "[K8S] Reset cluster with a snapshot." "https://planetariumhq.slack.com/services/hooks/slackbot?token=$slack_token&channel=%23tf-9c-pbft-2022"
  fi
else
  echo "Reset cluster without snapshot."
  if [[ "$QUITE" != "--quite" ]]; then
    curl --data "[K8S] Reset cluster without a snapshot." "https://planetariumhq.slack.com/services/hooks/slackbot?token=$slack_token&channel=%23tf-9c-pbft-2022"
  fi
fi

kubectl delete configmap reset-snapshot-option --ignore-not-found=true
kubectl create configmap reset-snapshot-option --from-literal=RESET_SNAPSHOT_OPTION=$response

deploy_cluster $slack_token || true

kubectl get pod