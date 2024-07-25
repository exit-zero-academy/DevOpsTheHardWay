# Helm - The Kubernetes Package Manager

## Motivation

**Helm** is a "package manager" for Kubernetes. Here are some of the main features of the tool:

- **Helm Charts**: Instead of dealing with numerous YAML manifests, which can be a complex task, Helm introduces the concept of a "Package" (known as **Chart**) – a cohesive group of related YAML manifests that collectively define a single application within the cluster.
  For example, an application might consist of a Deployment, Service, HorizontalPodAutoscaler, ConfigMap, and Secret. 
  These manifests are interdependent and essential for the seamless functioning of the application. 
  Helm encapsulates this collection, making it easier to manage, version, and deploy as a unit.

- **Sharing Charts**: Helm allows you to share your charts, or use other's charts. Want to deploy MongoDB server on your cluster? Someone already done it before, you can use her Helm Chart to with your own configuration values to deploy the MongoDB.  

- **Dynamic manifests**: Helm allows you to create reusable templates with placeholders for configuration values. For example:
  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: {{ .Values.serviceName }}   # the service value will be dynamically placed when applying the manifest
  spec:
    selector:
      app: {{ .Values.Name }}   # the selector value will be dynamically placed when applying the manifest
  ...
  ```
  
  This becomes very useful when dealing with multiple clusters that share similar configurations (Dev, Prod, Test clusters). 
  Instead of duplicating YAML files for each cluster, Helm enables the creation of parameterized templates.

## Install Helm

https://helm.sh/docs/intro/install/

## Helm Charts 

Helm uses a packaging format called charts. A chart is a collection of files that describe a related set of Kubernetes resources. 
A single chart might be used to deploy some single application in the cluster.

### Deploy Grafana using Helm

**Remove any existed grafana Deployment, StatefulSet or Service before you start.**

Like DockerHub, there is an open-source community Hub for Charts of famous applications.
It's called [Artifact Hub](https://artifacthub.io/packages/search?kind=0), check it out. 

Let's review and install the [official Helm Chart for Grafana](https://artifacthub.io/packages/helm/grafana/grafana).

To deploy the Grafana Chart, you first have to add the **Repository** in which this Chart exists. 
A Helm Repository is the place where Charts can be collected and shared.

```bash
helm repo add grafana-charts https://grafana.github.io/helm-charts
helm repo update
```

The `grafana-charts` Helm Repository contains many different Charts maintained by the Grafana organization. 
[Among the different Charts](https://artifacthub.io/packages/search?repo=grafana&sort=relevance&page=1) of this repo, there is a Chart used to deploy the Grafana server in Kubernetes. 

Deploy the `grafana` Chart by: 

```bash
helm install grafana grafana-charts/grafana 
```

The command syntax is as follows: `helm install <release-name> <helm-repo-name>/<chart-name>`.

Whenever you install a Chart, a new **Release** is created.   
In the above command, the Grafana server has been released under the name `grafana`, using the `grafana` Chart from the `grafana-charts` repo.

During installation, the Helm client will print useful information about which resources were created, what the state of the Release is, and also whether there are additional configuration steps you can or should take.

#### Try it yourself

Review the release's output. Then use `port-forward` to visit the Grafana server.

### Customize the Grafana release

When installed the Grafana Chart, the server has been release with default configurations that the Chart author decided for you. 

A typical Chart contains hundreds of different configurations, e.g. container's environment variables, custom secrets, etc..

Obviously, you want to customize the Grafana release according to your configurations.
Good Helm Chart should allow you to configure the Release according to your configurations. 

To see what options are configurable on a Chart, go to the [Chart's documentation page](https://artifacthub.io/packages/helm/grafana/grafana), or use the `helm show values grafana-charts/grafana` command. 

Let's override some of the default configurations by specifying them in a YAML file, and then pass that file during the Release upgrade:

```yaml
# k8s/grafana-values.yaml

persistence:
  enabled: true
  size: 2Gi

env:
  GF_DASHBOARDS_VERSIONS_TO_KEEP: 10

```

The above values configure the Grafana server data to be persistent, and define some Grafana related environment variable. 

To apply the new Chart values, `upgrade` the Release: 

```bash
helm upgrade -f grafana-values.yaml grafana grafana-charts/grafana
```

An `upgrade` takes an existing Release and upgrades it according to the information you provide. 
Because Kubernetes Charts can be large and complex, Helm tries to perform the least invasive upgrade. 
It will only update things that have changed since the last release.

#### Try it yourself

Review the [Official Grafana Helm values](https://artifacthub.io/packages/helm/grafana/grafana), and add more Chart values overrides in `grafana-values.yaml` to achieve following configurations: 

1. The deployed Grafana [image tag version](https://hub.docker.com/r/grafana/grafana/tags) is higher than `8.0.0`. 
2. The [`redis-datasource`](https://grafana.com/grafana/plugins/redis-datasource/?tab=overview) plugin is installed.
3. A redis datasource is configured to collect metrics from the `redis-cart` service.


If something does not go as planned during a release, it is easy to roll back to a previous release using `helm rollback [RELEASE] [REVISION]`:

```shell
helm rollback grafana 1
```

To uninstall the Chart release:

```shell
helm uninstall grafana
```


# Exercises 

### :pencil2: Redis cluster using Helm

Provision a Redis cluster with 1 master an 2 replicas using [Bitnami Helm Chart](https://artifacthub.io/packages/helm/bitnami/redis) 

Configure your NetflixFrontend to work with your Redis cluster instead of the existed `redis` Deployment as done in a previous exercise.  

### :pencil2: Create your own Helm chart for the NetflixFrontend service

In this exercise we will create a Chart for the [NetflixFrontend][NetflixFrontend].

Why is it good idea? For example, instead of maintaining two different sets of YAML manifests for both dev and prod environments, 
we will leverage the created Chart to deploy the application in two instances: first as `netflix-frontend-dev` for the Development environment, and as `netflix-frontend-prod` for Production env, each with his own values.

Helm can help you get started quickly by using the `helm create` command:

```bash
helm create netflix-frontend
```

Now there is a chart in `./netflix-frontend`. You can edit it and create your own templates.
The directory name is the name of the chart.

Inside of this directory, Helm will expect the following structure:

```text
netflix-frontend/
  Chart.yaml          # A YAML file containing information about the chart
  values.yaml         # The default configuration values for this chart
  charts/             # A directory containing any charts upon which this chart depends.
  templates/          # A directory of templates that, when combined with values, will generate valid Kubernetes manifest files.
```

For more information about Chart files structure, go to [Helm docs](https://helm.sh/docs/topics/charts/). 

Change the default Chart values in `values.yaml` to match the original `netflix-frontend` service.

As you edit your chart, you can validate that it is well-formed by running `helm lint`.

When it's time to package the chart up for deployment, you can run the `helm package` command:

```bash
helm package netflix-frontend
```

And that chart can now easily be installed by:

```bash
helm install netflix-frontend-dev ./netflix-frontend-0.1.0.tgz
```


[NetflixFrontend]: https://github.com/exit-zero-academy/NetflixFrontend.git
