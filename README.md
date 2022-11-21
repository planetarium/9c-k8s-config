# Kubernetes settings for Nine Chronicles 🐱

YAML files needed to setup kubernetes clusters for Nine Chronicles mainnet and internal testing. Repository contains:

- `9c-main`: configurations for deploying 9c main cluster
- `9c-internal`: configurations for deploy 9c internal cluster
- `9c-onboarding`: configurations for headless cluster deployment of onboarding.nine-chronicles.com
- `9c-test`: configurations for deploy 9c test cluster


Overview of k8s objects used in Nine Chronicles deployment:
- service
  - Used for deploying the overall [cluster service](https://github.com/planetarium/9c-k8s-config/blob/master/9c-main/service.yaml)
- deployment
  - Used for deploying [seed node](https://github.com/planetarium/9c-k8s-config/blob/master/9c-main/seed-deployment-1.yaml)
- statefulset
  - Used for deploying [miner node](https://github.com/planetarium/9c-k8s-config/blob/master/9c-main/miner-1.yaml) and [explorer node](https://github.com/planetarium/9c-k8s-config/blob/master/9c-main/explorer.yaml)
- cronjob
  - Used for deploying [snapshot node](https://github.com/planetarium/9c-k8s-config/blob/master/9c-main/snapshot.yaml)
- configmap
  - Used for deploying [scripts](https://github.com/planetarium/9c-k8s-config/blob/master/9c-main/configmap.yaml) used in various nodes
- persistentvolumeclaim
  - Used for deploying persistent storage used in various nodes
  - Persistent volume will be created automatically when you deploy any statefulset.

[]
