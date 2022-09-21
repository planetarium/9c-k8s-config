# RELEASE

## 사전 작업이 끝난 사람들을 위한 요약

1. `configmap-versions.yaml` 에서 새로운 APV 버전으로 바꾼다.
2. `kustomization.yaml` 에서 새로운 git hash 버전으로 바꾼다.
3. `deploy-previewnet.sh` 을 실행시킨다.
    - 윈도우의 경우 `git bash` 혹은 `wsl` 을 사용한다.

## 사전 작업
### 의존성
- aws cli version 2
- eksctl
- kubectl

### 사전 작업 시작하기
1. `aws configure` 을 이용하여 자신의 aws 계정을 등록한다. (region은 `us-east-2` 로 하면 좋다.)
2. `aws eks update-kubeconfig --name 9c-preview-net --region us-east-2 --role-arn arn:aws:iam::319679068466:role/EKS` 로 설정이 바뀌는지 본다.
3. `kubectl get pod` 으로 pod 들이 정상적으로 뜬다면 이 글의 첫 번째 항목인 **사전 작업이 끝난 사람들을 위한 요약**으로 돌아간다.
