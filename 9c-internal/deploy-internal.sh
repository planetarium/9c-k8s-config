#!/usr/bin/env bash
set -ex

BASEDIR=$(dirname "$0")
echo "$BASEDIR"

# kubectl configuration must be already set on your environment
checkout_internal_cluster() {
  aws eks update-kubeconfig --name 9c-internal --region us-east-2 --role-arn arn:aws:iam::319679068466:role/EKS
  kubectl config set current-context arn:aws:eks:us-east-2:319679068466:cluster/9c-internal
}

clear_cluster() {
  curl --data "[K8S] Clearing 9c-internal cluster." 'https://planetariumhq.slack.com/services/hooks/slackbot?token=$1&channel=%239c-internal'
  kubectl delete -k $BASEDIR
}

clean_db() {
  curl --data "[K8S] Cleaning DP & Onboarding DB." 'https://planetariumhq.slack.com/services/hooks/slackbot?token=$1&channel=%239c-internal'
  kubectl delete pvc internal-data-provider-db-data-internal-data-provider-db-0 internal-onboarding-db-data-internal-onboarding-db-0
}

# AWS configuration must be already set on your environment
reset_snapshot() {
  curl --data "[K8S] Copying 9c-main snapshots to 9c-internal." 'https://planetariumhq.slack.com/services/hooks/slackbot?token=$3&channel=%239c-internal'
  ARCHIVE="archive_"$(date '+%Y%m%d%H')
  INTERNAL_PREFIX=$(echo $1 | awk '{gsub(/\//,"\\/");print}')
  ARCHIVE_PATH=$1$ARCHIVE/
  ARCHIVE_PREFIX=$(echo $ARCHIVE_PATH | awk '{gsub(/\//,"\\/");print}')
  MAIN_PREFIX=$(echo $2 | awk '{gsub(/\//,"\\/");print}')

  # archive internal cluster chain
  for f in $(aws s3 ls $1 | awk 'NF>1{print $4}' | grep "zip\|json"); do
    echo $f
    aws s3 mv $(echo $f | sed "s/.*/$INTERNAL_PREFIX&/") $(echo $f | sed "s/.*/$ARCHIVE_PREFIX&/")
  done

  # copy main cluster chain to internal
  for f in $(aws s3 ls $2 | awk 'NF>1{print $4}' | grep "zip\|json"); do
    echo $f
    aws s3 cp $(echo $f | sed "s/.*/$MAIN_PREFIX&/") $(echo $f | sed "s/.*/$INTERNAL_PREFIX&/")
  done

  aws s3 cp "s3://9c-snapshots/internal/latest.json" "s3://9c-snapshots/internal/mainnet_latest.json"

  BUCKET="s3://9c-snapshots"
  BUCKET_PREFIX=$(echo $BUCKET | awk '{gsub(/\//,"\\/");print}')
  CF_PATH=$(echo $1 | sed -e "s/^$BUCKET_PREFIX//" | sed "s/.*/&*/")

  # reset cf path
  CF_DISTRIBUTION_ID="EAU4XRUZSBUD5"
  aws cloudfront create-invalidation --distribution-id "$CF_DISTRIBUTION_ID" --paths "$CF_PATH"
}

deploy_cluster() {
  curl --data "[K8S] Deploying 9c-internal cluster." 'https://planetariumhq.slack.com/services/hooks/slackbot?token=$1&channel=%239c-internal'
  kubectl apply -f $BASEDIR/configmap-versions.yaml
  kubectl apply -f $BASEDIR/configmap-snapshot-script.yaml
  kubectl apply -f $BASEDIR/configmap-data-provider.yaml
  kubectl apply -k $BASEDIR
}

# Type "y" to reset the cluster with a new snapshot and "n" to just deploy the cluster.
echo "Do you want to reset the cluster with a new snapshot(y/n)?"
read response

checkout_internal_cluster || true
slack_token=$(kubectl get secrets/slack  --template='{{.data.token | base64decode}}')
echo $slack_token

clear_cluster $slack_token || true

# clean_db $slack_token || true

if [ $response = y ]
then
    echo "Reset cluster with a new snapshot"
    curl --data "[K8S] Reset cluster with a new snapshot" "https://planetariumhq.slack.com/services/hooks/slackbot?token=$slack_token&channel=%239c-internal"
    reset_snapshot "s3://9c-snapshots/internal/" "s3://9c-snapshots/main/partition/" $slack_token || true
else
    echo "Reset cluster without resetting snapshot."
    curl --data "[K8S] Reset cluster without resetting snapshot." "https://planetariumhq.slack.com/services/hooks/slackbot?token=$slack_token&channel=%239c-internal"
fi

kubectl delete configmap reset-snapshot-option
kubectl create configmap reset-snapshot-option --from-literal=RESET_SNAPSHOT_OPTION=$response

deploy_cluster $slack_token || true

kubectl get pod
