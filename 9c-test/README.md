
# Test network from zero
이 문서에서는 테스트용 네트워크를 구축하는 절차에 대해 다룹니다.

준비물
 - terraform
 - kubectl
 - awscli
## Setup EKS Cluster 
cluster를 dev계정에 구축하는 것을 기준으로 설명합니다.
### aws credential 설정
AWS dev 계정의 credential을 1password를 참조해서 `~/.aws/credential` 에 입력해줍니다. (1password의 `AWS(dev) Access Key`)
```
# ~/.aws/credentials
...
[planetarium-dev]
aws_access_key_id = <AWS_ACCESS_KEY_ID>
aws_secret_access_key = <AWS_SECRET_ACCESS_KEY>
region = us-east-2
...
```
혹은 aws cli의 `aws configure` 로 입력할 수 있습니다.

### network
본 문서는 cluster를 public network에 구축합니다. 따라서 cluster 및 node group이 통신할 public subnet이 존재해야 합니다.
private subnet을 사용할 경우 NAT gateway가 설정되어 있어야 합니다.
또한 각 subnet에 IP가 충분히 확보되어 있는 상황을 전제합니다.

### terraform
본 문서는 terraform을 이용해 cluster를 구축합니다. 관련 resource들은 전부 `terraform` 폴더에 있습니다.
1. provider.tf에서 profile을 `~/.aws/credentials` 에서 dev계정의 profile을 사용하도록 설정합니다. 
2. 해당 profile을 사용하도록 환경변수를 설정합니다.
     ````
     $ export AWS_PROFILE=planetarium-dev
     ````
3. backend.tf에서 state를 저장할 s3 경로를 지정합니다. 이때 bucket과 key에 해당하는 경로는 미리 존재해야 합니다.
4. variables.tf에서 cluster와 관련된 리소스들의 이름을 정해줍니다.
    ```
	variable "name" {
	  description = "general name for cluster related resources."
	> default     = "9c-test"
	}
     ```
     그 외 vpc나 subnet ID를 수정할 수 있습니다.
5. ```
   $ terraform init
   ```
   terraform state를 지정된 backend에 생성하고 provider를 내려받는 등 initialize작업을 수행합니다.
    ```  
   $ terraform plan
   ```
   plan은 현재 terraform state와 실제 리소스, 사용자의 코드를 비교해서 어떤 부분에 변경이 생길지 보여줍니다. 중요한 리소스가 삭제나 업데이트 되지는 않을지 한번 체크해봅시다.
6. ```
   $ terraform apply
   ```
   terraform plan의 변경사항들을 실제 리소스에 반영합니다. 해당 코드는 다음의 리소스들을 생성합니다.
    - EKS cluster
    - EKS Node Group
    - vpc, subnet tags
    - addons
    - cluster 운영에 필요한 각종 IAM role

## Setup Test Network
testnet 구축에 필요한 k8s manifest를 적용합니다. seed, miner, rpc 순서로 적용합니다.
### K8S
우선 kubectl context를 위에 생성한 cluster로 설정합니다.
```
$ aws eks update-kubeconfig --name <cluster name>
```
설정된 context는 `~/.kube/config` 에서 확인할 수 있습니다.

1. configMap
    node health check에 사용되는 script를 생성합니다.
    ```
    $ kubectl apply -f configmap-probe.yaml
    ```
2. storageClass
    node에서 사용할 볼륨을 확장가능한 형태로 생성하기 위해 storageClass를 새로 정의합니다. 또한 gp3 볼륨을 사용하기 위해 별도로 정의할 필요도 있습니다.
    ```
    $ kubectl apply -f gp2-extensible.yaml -f gp3-extensible.yaml
    ```
3. service
    각 node에서 사용할 service와 load balancer들을 미리 생성해줍니다.
    여기서 얻게되는 load balance의 domain을 각 node의 argument로 입력해야 하기 때문에 service를 먼저 생성하는 것을 권장합니다.
    ```
    $ kubectl apply -f service.yaml
    ```
4. secret
    miner가 사용할 private key를 kubernetes secret으로 미리 생성합니다. `secret-miner.yaml`에 private key를 **base64**로 인코딩하여 입력해줍니다.
    ```
	apiVersion: v1
	kind: Secret
	metadata:
	  name: miner-keys
	  namespace: default
	data:
	  miner1: <privateKey>         << base64 encoded private key 
    type: Opaque
    ```
    ```
    $ kubectl apply -f secret-miner.yaml
    ```
5. seed
    seed node를 생성합니다. `tcp-seed-deployment.yaml`를 적용하기 전에 apv, host, private key 등의 argument를 수정합니다.
    host는 서비스에서 생성한 seed service의 load balancer 주소가 되어야 합니다.
    load balancer의 주소는 `kubectl get svc <service name>`을 통해 확인할 수 있습니다.
    ```
    $ kubectl apply -f tcp-seed-deployment-1.yaml
    ```
6. miner
    miner node를 생성합니다. `miner-1.yaml`를 적용하기 전에 apv, genesis block, host, peer 등의 argument를 수정합니다.
    host는 서비스에서 생성한 miner-1 service의 load balancer 주소가 되어야 합니다.
    peer argument에는 위에서 생성한 seed node의 peerString를 입력해줍니다.
    또한 network-type이 default로 설정되어 있어야 합니다.
    ```
    $ kubectl apply -f miner-1.yaml
    ```
7. rpc
    rpc node를 생성합니다. `remote-headless-1.yaml`, `remote-headless-2.yaml`을 적용하기 전에 위 miner node와 같은 방식으로 argument를 수정합니다(apv, genesis block, host, peer, network type).
    ```
    $ kubectl apply -f remote-headless-1.yaml -f remote-headless-2.yaml
    ```
8. data-provider(optional, 이하 DP)
    DP node를 생성합니다. 우선 DP에서 사용할 database connection정보를 미리 secret으로 생성해 둡니다. `secret-data-provider.yaml`의 값들을 채워줍니다.(1password의 `AWS.RDS.DataProviderTest(Admin)` 참조)
    ```
	apiVersion: v1
	kind: Secret
	metadata:
	  name: data-provider-conn
	  namespace: default
	data:
	  database: <database-name>
	  host: >-
	    <host>
	  port: <port>
	  token: <password>
	  user: <user>
	  value: >-
	    <connect-string>
	type: Opaque
    ```
    testnet의 DP는 실행하기 전에 tip check하는 script를 수행합니다. 해당 script를 configmap으로 생성합니다.
    ```
    $ kubectl apply -f configmap-data-provider.yaml
    ```
    마지막으로 `data-provider.yaml`을 적용하여 DP node를 구축합니다. 다른 node들과 다르게 option들을 환경변수로 주입하고 있습니다. `NC_AppProtocolVersionToken`, `NC_PeerStrings__0`, `NC_GenesisBlockPath`, `NC_Host`, `NC_NetworkType`, `NC_Render`를 다른 node들처럼 필요한 값으로 설정합니다. testnet에서는 ice server를 사용하지 않기 때문에 host를 따로 입력해줘야 합니다. 따라서 `NC_IceServerString__0` 를 empty string으로 설정해주어야 합니다.

node 생성이 완료되면 graphql 쿼리를 통해 잘 구축되었는지 확인해봅니다.

**Request**
```
query
{
  peerChainState
  {
    state
  }
}
```

**Response**
```
{
  "data": {
    "peerChainState": {
      "state": [
        "0x6d50A754229354e7FB4B3741faE30F9016eCb5F2, 40643, 206274132390",
        "0xaB6F116B913E96C6796c98BD6e5B52B547fCE0De, 40643, 206274132390",
        "0x82b857D3fE3Bd09d778B40f0a8430B711b3525ED, -1, -1",
        "0xa76298c3d33D46E0B1544dD88f33B0aDfd404405, 40643, 206274132390",
        "0x81946E8Be12687F9e4c728f38BDF76598A11bE9B, 40643, 206274132390"
      ]
    }
  },
  "extensions": {}
}
```
위와 같이 모든 node에서 seed를 제외한 다른 node들이 표시되고 tip이 비슷한 수준이 되어야 합니다.
