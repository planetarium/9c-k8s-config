#!/usr/bin/env bash
set -ex

BASEDIR=$(dirname "$0")
echo "$BASEDIR"

# kubectl configuration must be already set on your environment
checkout_internal_cluster() {
  aws eks update-kubeconfig --name 9c-pbft-internal --role-arn arn:aws:iam::838612679705:role/EKS
  kubectl config set current-context arn:aws:eks:us-east-2:838612679705:cluster/9c-pbft-internal
}

clear_cluster() {
  kubectl delete -k $BASEDIR --dry-run=client
}

clean_db() {
  kubectl delete pvc internal-data-provider-db-data-internal-data-provider-db-0 internal-onboarding-db-data-internal-onboarding-db-0 --dry-run=client
}

deploy_cluster() {
  kubectl apply -f $BASEDIR/configmap-versions.yaml --dry-run=client
  kubectl apply -f $BASEDIR/configmap-snapshot-script.yaml --dry-run=client
  kubectl apply -f $BASEDIR/configmap-data-provider.yaml --dry-run=client
  kubectl apply -k $BASEDIR --dry-run=client
}

# Type "y" to reset the cluster with a new snapshot and "n" to just deploy the cluster.
echo "Do you want to reset the cluster with a new snapshot(y/n)?"
read response

checkout_internal_cluster || true
slack_token=$(kubectl get secrets/slack  --template='{{.data.token | base64decode}}')
echo $slack_token

clear_cluster $slack_token || true

clean_db $slack_token || true

if [ $response = y ]
then
  echo "Reset cluster with snapshot."
else
  echo "Reset cluster without snapshot."
fi

kubectl delete configmap reset-snapshot-option --dry-run=client
kubectl create configmap reset-snapshot-option --from-literal=RESET_SNAPSHOT_OPTION=$response --dry-run=client

deploy_cluster $slack_token || true

kubectl get pod
