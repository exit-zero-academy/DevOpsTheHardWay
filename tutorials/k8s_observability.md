# Kubernetes Cluster Observability 

## Motivation and challenges 

Kubernetes cluster is great, but what about monitoring the cluster applications?

By monitoring we mean collecting **logs** and **metrics** from our containers and nodes. 

- Logs are chronological records of events that occur within the app, typically in a semi-structured textual form.
- Metrics, on the other hand, are quantitative measurements (numbers) that represent the state or performance of a system (e.g. CPU usage, network incoming traffic).
  Since metrics are values that might change very rapidly, they often collected at regular intervals (e.g. every 15 seconds). 

Collecting logs and metrics from applications is important for investigate issues and bugs, analyse app performance, auditing security events, etc...

Monitoring clusters presents unique challenges stemming from the distributed nature of its components and the dynamic, ephemeral environment it operates in. 

- Pods are distributed across dozen of Nodes.
- Pods are launched and terminated throughout the cluster's lifecycle, which lead to loss of critical logs from pods that was terminated.

In this tutorial we will set up a robust monitoring system for our cluster.

## Logs collection using FluentBit 

[FluentBit](https://docs.fluentbit.io/manual/installation/kubernetes) is an open source Log Processor. Using FluentBit you can:

- Collect Kubernetes containers logs
- Enrich logs with Kubernetes Metadata (e.g. Pod name, namespace, labels).
- Centralize your logs in third party storage services like Elasticsearch, InfluxDB, etc.

It is important to understand how FluentBit will be deployed.
Kubernetes manages a cluster of **nodes**, so our log agent tool will need to run on **every** node to collect logs from every pod, hence FluentBit is deployed as a [DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/) (exactly one Pod that runs on every Node of the cluster).

Here is the architecture:

![][k8s_observability_fluent]

1. [Pods in k8s cluster write logs](https://kubernetes.io/docs/concepts/cluster-administration/logging/) to `stdout` as well as to a log file located in `/var/log/containers/` in the node. 

> #### Try it yourself
> 
> SSH into one of your cluster's node, take a look on `/var/log/containers` dir.

2. As said, FluentBit will be deployed as a **DaemonSet**. 

   Since logs collection involving reading log files from every Node, we want an instance of FluentBit in each Node, otherwise we deal with cumbersome inter-node communication, increase traffic load, and potential data loss.
   When FluentBit is deployed as a DaemonSet, each node has its own FluentBit instance responsible for collecting logs from the containers running on that node. 

3. Each FluentBit Pod is collecting logs into a local buffer, and every interval, sends the collected data into Elasticsearch (also will be deployed in the cluster).
   
> [!NOTE]
> Elasticsearch is a No-SQL database. It is designed to handle large volumes of data and provides near real-time search and analytics capabilities. Elasticsearch is often used as the underlying engine for applications that require full-text search, log and event data analysis.

4. The Grafana/Kibana server will visualize logs stored in Elasticsearch. 


### Deploying FluentBit in Kubernetes

The recommended way to deploy FluentBit is with the official Helm Chart: https://docs.fluentbit.io/manual/installation/kubernetes#installing-with-helm-chart

Let's get started. Here are general guidelines, try to handle the deployment details yourself 💪:

1. Deploy Elasticsearch and Kibana from https://www.elastic.co/guide/en/cloud-on-k8s/2.13/k8s-deploy-eck.html.
2. Deploy FluentBit from https://docs.fluentbit.io/manual/installation/kubernetes#installing-with-helm-chart.
3. Upgrade the chart according to the values files in `k8s/fluent-values.yaml`: 

```bash
helm upgrade --install fluent-bit fluent/fluent-bit -f k8s/fluent-values.yaml 
```

4. Visit your grafana server and explore logs.

## Collect metrics using Prometheus

[Prometheus](https://prometheus.io/docs/introduction/overview/) is a monitoring platform that collects metrics from [different platforms](https://prometheus.io/docs/instrumenting/exporters/) (such as databases, cloud providers, and k8s clusters).

Prometheus collects and stores its metrics as **time series** data, i.e. metrics information is stored with the timestamp at which it was recorded, alongside optional key-value pairs called **labels**.
Prometheus monitors its targets by using a **pull-based model**, where Prometheus periodically fetches metrics from the HTTP endpoints exposed by the targets.

![][k8s_prom-architecture]

1. Deploy Prometheus using the [community Helm chart](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus). The Chart is already configured with the exporters needed to collect metrics from Pods and Nodes in your cluster. Use `k8s/prometheus-values.yaml` as the values override file. 
1. Integrate Prometheus into Grafana as a datasource.
1. In your Grafana, import one of the following dashboards to get some insights about your cluster:
    - https://grafana.com/grafana/dashboards/6417-kubernetes-cluster-prometheus/
    - https://grafana.com/grafana/dashboards/315-kubernetes-cluster-monitoring-via-prometheus/
    - https://grafana.com/grafana/dashboards/12740-kubernetes-monitoring/


[k8s_observability_fluent]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/k8s_observability_fluent.png
[k8s_prom-architecture]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/k8s_prom-architecture.png