#!/usr/bin/env bash
set -ex

BASEDIR=$(dirname "$0")
echo "$BASEDIR"

checkout_k8s_main_branch() {
  git checkout main
  git pull https://github.com/planetarium/9c-k8s-config.git main
}

# kubectl configuration must be already set on your environment
checkout_test_cluster() {
  aws eks update-kubeconfig --name 9c-test --region us-east-2 --profile planetarium-dev
}

deploy_cluster() {
  kubectl apply \
    -f $BASEDIR/tcp-seed-deployment-1.yaml \
    -f $BASEDIR/tcp-seed-deployment-2.yaml \
    -f $BASEDIR/configmap-probe.yaml \
	  -f $BASEDIR/configmap-data-provider.yaml \
    -f $BASEDIR/miner-1.yaml

  # Wait for seed nodes to be fully deployed
  echo "Wait for seed nodes to be fully deployed"
  sleep 30

  # Restart miner first
  kubectl delete pod test-miner-1-0

  # Wait for miner to start
  echo "Wait for miner to start"
  sleep 30

  # Start remaining services
  echo "Start remaining services"
  kubectl apply  \
    -f $BASEDIR/miner-1.yaml \
    -f $BASEDIR/data-provider.yaml \
    -f $BASEDIR/remote-headless-1.yaml \
    -f $BASEDIR/remote-headless-2.yaml
}

echo "Checkout 9c-main cluster."
checkout_test_cluster || true

echo "Deploy 9c-main cluster."
deploy_cluster || true

kubectl config set current-context arn:aws:eks:us-east-2:838612679705:cluster/9c-test
kubectl get pod --watch
