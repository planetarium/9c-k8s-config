# Monitoring

<img width="1679" alt="monitoring.libplanet.io RPC page picture." src="https://user-images.githubusercontent.com/26626194/145417776-52710bb4-c00e-4196-ac89-5d40a24ca111.png">

This directory consists of elements to monitor the 9c-main network's status. You can access it at [monitoring.libplanet.io](https://monitoring.libplanet.io).

## Installation

There are two types of elements. One is [Helm] chart and another one is Kubernetes Pod.

### [Helm]

At first, you should install Helm CLI. Please see https://helm.sh/docs/intro/install/#through-package-managers.

As shortcut:

```
# macOS
brew install helm

# Windows
choco install kubernetes-helm

# With Snap
sudo snap install helm --classic
```

### [Helm] Charts, [Prometheus] and [Grafana]

To install helm charts, [Prometheus] and [Grafana], follow the below commands.

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/prometheus --namespace monitoring --values prometheus-values.yaml
helm install grafana grafana/grafana --namespace monitoring --values grafana-values.yaml
```

### [9c-headless-metrics-aggregator]

There is a metrics provider which aggregates metrics of RPC nodes like RPC clients or tip index.

```
kubectl apply -f 9c-headless-metrics-aggregator.yaml
```

## Update

### Helm Charts, [Prometheus] and [Grafana]

To upgrade helm charts, edit the `*-values.yaml` file and run `helm upgrade` like below

```
# For Grafana
helm upgrade -f grafana-values.yaml grafana grafana/grafana

# For Prometheus
helm upgrade -f prometheus-values.yaml prometheus prometheus-community/prometheus
```

### [9c-headless-metrics-aggregator]

It is stateless application and pod. So you can delete it anytime and recreate.

```
kubectl delete pod ninechronicles-headleses-metrics-aggregator
kubectl apply -f 9c-headless-metrics-aggregator.yaml
```


[Helm]: https://helm.sh/
[Prometheus]: https://prometheus.io/
[Grafana]: https://grafana.com/
[9c-headless-metrics-aggregator]: https://github.com/planetarium/9c-headless-metrics-aggregator