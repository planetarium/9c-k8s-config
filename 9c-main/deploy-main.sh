#!/usr/bin/env bash
set -ex

BASEDIR=$(dirname "$0")
echo "$BASEDIR"

checkout_k8s_main_branch() {
  git checkout main
  git pull https://github.com/planetarium/9c-k8s-config.git main
}

# kubectl configuration must be already set on your environment
checkout_main_cluster() {
  aws eks update-kubeconfig --name 9c-main --region us-east-2 --role-arn arn:aws:iam::319679068466:role/EKS
  kubectl config set current-context arn:aws:eks:us-east-2:319679068466:cluster/9c-main
}

clear_cluster() {
  kubectl delete sts \
    main-full-state \
    main-miner-2 \
    explorer \
    main-data-provider \
    main-data-provider-db \
    remote-headless-1 \
    remote-headless-2 \
    remote-headless-3 \
    remote-headless-4 \
    remote-headless-5 \
    remote-headless-6 \
    remote-headless-7 \
    remote-headless-8 \
    remote-headless-9 \
    remote-headless-10 \
    remote-headless-31 \
    remote-headless-99

    # Provide ample time so that the nodes can be fully terminated before a new deployment
    echo "Provide ample time so that the nodes can be fully terminated before a new deployment"
    sleep 60
}

deploy_cluster() {
  kubectl apply \
    -f $BASEDIR/tcp-seed-deployment-1.yaml \
    -f $BASEDIR/tcp-seed-deployment-2.yaml \
    -f $BASEDIR/tcp-seed-deployment-3.yaml \
    -f $BASEDIR/configmap-full.yaml \
    -f $BASEDIR/configmap-partition-reset.yaml \
    -f $BASEDIR/configmap-partition.yaml \
    -f $BASEDIR/configmap-probe.yaml \
    -f $BASEDIR/snapshot-partition.yaml \
    -f $BASEDIR/snapshot-partition-reset.yaml \
    -f $BASEDIR/snapshot-full.yaml \
    -f $BASEDIR/miner-3.yaml

  # Wait for seed nodes to be fully deployed
  echo "Wait for seed nodes to be fully deployed"
  sleep 30

  # Restart miner first
  kubectl delete pod main-miner-3-0

  # Wait for miner to start
  echo "Wait for miner to start"
  sleep 30

  # Start remaining services
  echo "Start remaining services"
  kubectl apply  \
    -f $BASEDIR/full-state.yaml \
    -f $BASEDIR/miner-2.yaml \
    -f $BASEDIR/explorer.yaml \
    -f $BASEDIR/data-provider.yaml \
    -f $BASEDIR/data-provider-db.yaml \
    -f $BASEDIR/remote-headless-1.yaml \
    -f $BASEDIR/remote-headless-2.yaml \
    -f $BASEDIR/remote-headless-3.yaml \
    -f $BASEDIR/remote-headless-4.yaml \
    -f $BASEDIR/remote-headless-5.yaml \
    -f $BASEDIR/remote-headless-6.yaml \
    -f $BASEDIR/remote-headless-7.yaml \
    -f $BASEDIR/remote-headless-8.yaml \
    -f $BASEDIR/remote-headless-9.yaml \
    -f $BASEDIR/remote-headless-10.yaml \
    -f $BASEDIR/remote-headless-31.yaml \
    -f $BASEDIR/remote-headless-99.yaml
}

echo "Checkout k8s main branch."
checkout_k8s_main_branch || true
slack_token=$(kubectl get secrets/slack-token  --template='{{.data.token | base64decode}}')

curl --data "[K8S] Mainnet deployment start." "https://planetariumhq.slack.com/services/hooks/slackbot?token=$slack_token&channel=%239c-mainnet"
echo "Checkout 9c-main cluster."
checkout_main_cluster || true

echo "Clear 9c-main cluster."
clear_cluster || true

echo "Deploy 9c-main cluster."
deploy_cluster || true
curl --data "[K8S] Mainnet deployment complete." "https://planetariumhq.slack.com/services/hooks/slackbot?token=$slack_token&channel=%239c-mainnet"

echo "Deploy 9c-onboarding cluster."
$BASEDIR/../9c-onboarding/deploy-headless.sh

kubectl config set current-context arn:aws:eks:us-east-2:319679068466:cluster/9c-main
kubectl get pod --watch
