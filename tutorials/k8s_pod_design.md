# Pods and containers design

In this tutorial we will take a closer look on Pods and containers characteristics, and how they are designed and scheduled on nodes properly.

Throughout this tutorial, we will work again with the `nginx` service.

Let's apply the following `nginx` Deployment (delete any previous Deployments if exist):

```yaml
# k8s/resources-demo.yaml 

apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
        labels:
          app: nginx
    spec:
      containers:
      - name: server
        image: nginx:1.26.0
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
          limits:
            cpu: 200m
            memory: 200Mi
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - name: http
    port: 80
    targetPort: 80
```

## Describe Pod

The `kubectl describe` command displays a comprehensive set of information about pods. 
This command is very useful for diagnosing issues, understanding the current [state of a pod](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase) and [containers](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#container-states), and gathering information for debugging purposes, [Pod conditions](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-conditions), Volumes, Network and Events.

## Resource management for Pods and containers

As can be seen from the above YAML manifest, when you specify a Pod, you can optionally specify how much of each resource (CPU and memory) a container needs: 

```text 
Limits:
  cpu:     200m
  memory:  200Mi
Requests:
  cpu:     100m
  memory:  100Mi
```

What do the **Limits** and **Requests** mean? 

### Resource limits

When you specify a resource **Limits** for a container, the **kubelet** enforces those limits, as follows:

- If the container tries to consume more than the allowed amount of memory, the system kernel terminates the process that attempted the allocation, with an out of memory (OOM) error.
- If the container tries to consume more than the allowed amount of CPU, it is just not allowed to do it.

Let's connect to the Pod and create an artificial CPU load, using he `stress` command:

> [!NOTE]
> Before starting, make sure the `metrics-server` is installed in your cluster. 
> 
> - If working on Minikube: `minikube addons enable metrics-server`.
> - If working on another k8s cluster, [read here](https://github.com/kubernetes-sigs/metrics-server?tab=readme-ov-file#installation). 


```console 
$ kubectl exec -it <nginx-pod-name> -- /bin/bash
root@nginx-698dcc74b9-7d56w:/ # apt update
...

root@nginx-698dcc74b9-7d56w:/ # apt install stress-ng
...

root@nginx-698dcc74b9-7d56w:/ # stress-ng --cpu 2 --vm 1 --vm-bytes 50M -v
stress-ng: info:  [723] defaulting to a 86400 second (1 day, 0.00 secs) run per stressor
stress-ng: info:  [723] dispatching hogs: 2 cpu, 1 vm
```

Watch the Pod's CPU and memory metrics in the Kubernetes UI Dashboard. Although the stress test tries to use 2 cpus, it's limited to 200m (200 mili-cpu, which is equivalent to 0.2 cpu), as specified in the `.resources.limits.cpu` entry.
In addition, the Pod **is** able to use a `50M` of memory as it's below the specified limit (200 megabytes). 

Let's try to use more than the memory limit:

```console
/src # stress-ng --cpu 2 --vm 1 --vm-bytes 500M -v
stress-ng: info:  [723] defaulting to a 86400 second (1 day, 0.00 secs) run per stressor
stress-ng: info:  [723] dispatching hogs: 2 cpu, 1 vm
```

Watch how the processed is killed by the kernel using a `SIGKILL` signal. 

### Resources requests 

While resources limits is quite straight forward, resources request has a completely different purpose. 

When you specify the resource **Requests** for containers in a Pod, the **kube-scheduler** uses this information to decide which node to place the Pod on. How?   

When a Pod is created, the kube-scheduler should select a Node for the Pod to run on. Each node has a maximum capacity for CPU and RAM. 
The scheduler ensures that the resource CPU and memory requests of the scheduled containers is less than the capacity of the node.

```console
$ kubectl get nodes
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   15d   v1.27.4

$ kubectl describe nodes minikube
Name:               minikube
[ ... lines removed for clarity ...]
Capacity:
  cpu:                2
  ephemeral-storage:  30297152Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             3956276Ki
  pods:               110
Allocatable:
  cpu:                2
  ephemeral-storage:  30297152Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             3956276Ki
  pods:               110
[ ... lines removed for clarity ...]
Non-terminated Pods:          (23 in total)
  Namespace                   Name                                          CPU Requests  CPU Limits  Memory Requests  Memory Limits  Age
  ---------                   ----                                          ------------  ----------  ---------------  -------------  ---
  default                     adservice-746b758986-vh7zt                    100m (5%)     300m (15%)  180Mi (4%)       300Mi (7%)     15d
  default                     cartservice-5d844fc8b7-rl7fp                  200m (10%)    300m (15%)  64Mi (1%)        128Mi (3%)     15d
  default                     checkoutservice-5b8645f5f4-gbpwn              50m (2%)      200m (10%)  64Mi (1%)        128Mi (3%)     15d
  default                     currencyservice-79b446569d-dqq7l              50m (2%)      200m (10%)  64Mi (1%)        128Mi (3%)     15d
  default                     emailservice-55df5dcf48-5ksdz                 50m (2%)      200m (10%)  64Mi (1%)        128Mi (3%)     15d
  default                     frontend-66b6775756-bxhbq                     50m (2%)      200m (10%)  64Mi (1%)        128Mi (3%)     15d
  default                     frontend-pod                                  50m (2%)      100m (5%)   5Mi (0%)         128Mi (3%)     50m
  default                     loadgenerator-78964b9495-rphvs                50m (2%)      500m (25%)  256Mi (6%)       512Mi (13%)    15d
  default                     paymentservice-8f98685c6-cjcmx                50m (2%)      200m (10%)  64Mi (1%)        128Mi (3%)     15d
  default                     productcatalogservice-5b9df8d49b-ng6pz        100m (5%)     200m (10%)  64Mi (1%)        128Mi (3%)     15d
  default                     recommendationservice-5b4bbc7cd4-rkdft        50m (2%)      200m (10%)  220Mi (5%)       450Mi (11%)    15d
  default                     redis-cart-76b9545755-nr785                   70m (3%)      125m (6%)   200Mi (5%)       256Mi (6%)     15d
  default                     shippingservice-648c56798-m8vjh               100m (5%)     200m (10%)  64Mi (1%)        128Mi (3%)     15d
  kube-system                 coredns-5d78c9869d-jkx8m                      100m (5%)     0 (0%)      70Mi (1%)        170Mi (4%)     15d
  kube-system                 etcd-minikube                                 100m (5%)     0 (0%)      100Mi (2%)       0 (0%)         15d
  kube-system                 kube-apiserver-minikube                       250m (12%)    0 (0%)      0 (0%)           0 (0%)         15d
  kube-system                 kube-controller-manager-minikube              200m (10%)    0 (0%)      0 (0%)           0 (0%)         15d
  kube-system                 kube-proxy-kv6m6                              0 (0%)        0 (0%)      0 (0%)           0 (0%)         15d
  kube-system                 kube-scheduler-minikube                       100m (5%)     0 (0%)      0 (0%)           0 (0%)         15d
  kube-system                 metrics-server-7746886d4f-t5btd               100m (5%)     0 (0%)      200Mi (5%)       0 (0%)         15d
  kube-system                 storage-provisioner                           0 (0%)        0 (0%)      0 (0%)           0 (0%)         15d
  kubernetes-dashboard        dashboard-metrics-scraper-5dd9cbfd69-lm4s2    0 (0%)        0 (0%)      0 (0%)           0 (0%)         15d
  kubernetes-dashboard        kubernetes-dashboard-5c5cfc8747-86kzb         0 (0%)        0 (0%)      0 (0%)           0 (0%)         15d
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests      Limits
  --------           --------      ------
  cpu                1820m (91%)   2925m (146%)
  memory             1743Mi (45%)  2840Mi (73%)
```

By looking at the “Pods” section, you can see which Pods are taking up space on the node.

Note that although actual memory resource usage on nodes is low (`45%`), the scheduler still refuses to place a Pod on a node if the memory request is more than the available capacity of the node. 
This protects against a resource shortage on a node when resource usage later increases, for example, during a daily peak in request rate.

Test it yourself! Try to change the `.resources.request.cpu` to a larger value (e.g. `3000m` instead of `100m`), and re-apply the Pod. What happened? 

Since the total CPU requests on that node is `91%` (`1820m` out of `2000m` CPU), you can see that if a new Pod requests more than `180m` or more than `1.2Gi` of memory, that Pod will not fit on that node.

> [!NOTE]
> In Production, always specify resource request and limit. It allows an efficient resource utilization and ensures that containers have the necessary resources to run effectively and scale as needed within the cluster.

## Configure quality of service for Pods

What happened if a container exceeds its memory request and the node that it runs on becomes short of memory overall? it is likely that the Pod the container belongs to will be **evicted**.

When you create a Pod, Kubernetes assigns a **Quality of Service (QoS) class** to each Pod as a consequence of the resource constraints that you specify for the containers in that Pod.
QoS classes are used by Kubernetes to decide which Pods to evict from a Node experiencing [Node Pressure](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/). 

1. [Guaranteed](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/#guaranteed) - The Pod specifies resources request and limit. CPU and Memory requests and limit are equal.
2. [Burstable](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/#burstable) - The Pod specifies resources request and limit. But CPU and Memory requests and limit are not equal.
3. [BestEffort](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/#besteffort) - The Pod does not specify resources request or limit for some of its containers.


When a Node runs out of resources, Kubernetes will first evict `BestEffort` Pods running on that Node, followed by `Burstable` and finally `Guaranteed` Pods.
When this eviction is due to resource pressure, **only Pods exceeding resource requests are candidates** for eviction.

Try to simulate Node pressure by overloading the node from a `Guaranteed` Pod, `Burstable` Pod and `BestEffort` Pod, and see the behaviour. 

## Container probes - Liveness and Readiness probes

A **probe** is a diagnostic performed periodically by the **kubelet** on a container, usually by an HTTP request, to check the container status. 

- **Liveness probes** are used to determine the health of a container (a.k.a. health check), by a periodic checks. The container is restarting if the probe fails.
- **Readiness probes** are used to determine whether a Pod is ready to receive traffic (when it is prepared to accept requests, preventing traffic from being sent to Pods that are not fully operational, mostly because the pod is still initializing, or is about to terminate as part of a rolling update).

> [!NOTE]
> In Production, always specify Liveness and Readiness probes, they are essential to ensure the availability and proper functioning of applications within Pods.

### Define a Liveness probe

The `nginx` service, as you may know, exposes an default endpoint: `/`. Upon an HTTP request, if the endpoint returns a `200` status code, it means "the server is alive".

In the below example, the `livenessProbe` entry defines a liveness probe for our Pod: 

```yaml
# k8s/liveness-demo.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
        labels:
          app: nginx
    spec:
      containers:
      - name: server
        image: nginx:1.26.0
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
          limits:
            cpu: 200m
            memory: 200Mi
        livenessProbe:
          initialDelaySeconds: 10
          httpGet:
            path: "/"
            port: 80
```

Let's make the liveness probe fail by connecting to the nginx pod and changing the listening port number of the server:

```console
$ kubectl exec -it <nginx-pod> -- /bin/bash

root@nginx-678b7f6564-wzwrq:/# sed -i 's/80/8080/g' /etc/nginx/conf.d/default.conf
root@nginx-678b7f6564-wzwrq:/# nginx -s reload
```

The prob HTTP requests to `/` will fail, thus, the **kubelet** will restart the container.

This restarting mechanism helps the application to be more available.
For example, when the server is entering a deadlock (the application is running, but unable to make progress),
restarting the container in such a state can help to make the application more available despite bugs.

By default, the HTTP probe is done every **10 seconds**, and should be low-cost, it shouldn't affect the application performance. 

### Define a Readiness probe

Sometimes, applications are temporarily unable to serve traffic.
For example, an application might need to load large data or configuration files during startup, or depend on external services after startup. 
In such cases, you don't want to kill the application, but you don't want to send it requests either.

Kubernetes provides readiness probes to detect and mitigate these situations. 
A pod with containers reporting that they are not ready does not receive traffic through Kubernetes Services.

Readiness probes are configured similarly to liveness probes:

```yaml
# k8s/readiness-demo.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
        labels:
          app: nginx
    spec:
      containers:
      - name: server
        image: nginx:1.26.0
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
          limits:
            cpu: 200m
            memory: 200Mi
        livenessProbe:
          initialDelaySeconds: 10
          httpGet:
            path: "/"
            port: 80
        readinessProbe:
          initialDelaySeconds: 10
          httpGet:
            path: "/readiness"
            port: 80
```

In the above example, we use the `/readiness` endpoint to perform the readiness probe HTTP request.
Since the endpoint does not exist in the `nginx` image by default, the probe will fail at the beginning, and traffic from the Service wouldn't be routed to this Pod. 

Deploy the above manifest, you'll see that the `nginx` Deployment does not complete the rolling update since the new replicaset container is not ready. 

Let's connect to the nginx container and configure the `/readiness` endpoint: 

```bash 
kubectl exec -it <nginx-pod> -- /bin/bash
```

Install `nano` or your favorite editor:

```bash
apt update && apt install nano -y
```

Add the following `location{}` directive into `server{}` under `/etc/nginx/conf.d/default.conf`:

```text
location /readiness {
 return 200 'Ready';
}
```

Finally, reload the server:

```bash
nginx -s reload
```

Check that your container pass the readiness probes properly. 


#### Readiness probes are critical to perform a successful Rolling Update 

In the context of a rolling update, readiness probes play a crucial role in ensuring a seamless transition.
When old replicaset Pods receive the SIGTERM signal from the kubelet, the Pod should start a graceful termination process. First of all it should stop receiving new requests.
By failing the readiness probes, the Pod indicates that it's not ready to receive new traffic. 

## Assign Pods to Nodes

There are some circumstances where you may want to control which Node the Pod is deployed on.
For example, we probably want to ensure that our `nginx` Pods are scheduled on nodes with SSD disk (as a webserver frequently access the disk to serve content). 

There are [several ways](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/) to allow the Node selection, [nodeSelector](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector) is the simplest recommended form. 
You can add the `nodeSelector` field to your Pod specification and specify the desirable target node.

```yaml
# k8s/node-selector-demo.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  nodeSelector:
    disk: ssd     # <------ Kubernetes only schedules the Pod onto nodes that have the label you specify.
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
        labels:
          app: nginx
    spec:
      containers:
      - name: server
        image: nginx:1.26.0
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
          limits:
            cpu: 200m
            memory: 200Mi
        livenessProbe:
          initialDelaySeconds: 10
          httpGet:
            path: "/"
            port: 80
        readinessProbe:
          initialDelaySeconds: 10
          httpGet:
            path: "/"
            port: 80
```

When apply the above manifest, you'll discover that the Pod cannot be schedule on any of the cluster's nodes. 
This because the **kube-scheduler** didn't find any Node with the `disk=ssd` label. 

Like many other Kubernetes objects, Nodes have **labels**:

```console
$ kubectl get nodes --show-labels
minikube       Ready    control-plane   22d   v1.27.4   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=minikube,kubernetes.io/os=linux,minikube.k8s.io/commit=fd7ecd9c4599bef9f04c0986c4a0187f98a4396e,minikube.k8s.io/name=minikube,minikube.k8s.io/primary=true,minikube.k8s.io/updated_at=2023_10_11T07_10_41_0700,minikube.k8s.io/version=v1.31.2,node-role.kubernetes.io/control-plane=,node.kubernetes.io/exclude-from-external-load-balancers=
```

Let's manually attach the label `disk=ssd` to your cluster's single existed node:

```console
$ kubectl label nodes minikube disk=ssd
node/minikube labeled
```

Make sure the Pod has been successfully scheduled on the labelled Node.

### Taints and Tolerations

We've seen that Node Selector is a simple mechanism to attract a Pod on specific Node (or group of nodes) by a label.
This technique is useful, for example, to schedule Pods on Nodes with specific hardware specification.

But what if we want to ensure that **only** those specific Pods use the dedicated Node?
For example, Nodes with an expensive GPU, it is desirable to keep pods that don't need the GPU off of those nodes, thus leaving room for later-arriving pods that do need the GPU. 

**Taints and Tolerations** can help us. [Taints](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) allow a node to **repel** a set of pods.

Let's add a **taint** to a node using `kubectl taint`:

```bash 
kubectl taint nodes minikube gpu=true:NoSchedule
```

The taint has key `gpu`, value `true`, and taint effect `NoSchedule`.
This means that **no pod will be able to schedule** onto the `minikube` node, unless it has a matching **toleration**.

A **Tolerations** allow the scheduler to schedule pods with matching taints.
To tolerate the above taint, you can specify toleration in the pod specification.

```yaml
# k8s/taint-toleration-demo.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  tolerations:
    - key: "gpu"
      operator: "Equal"
      value: "true"
      effect: "NoSchedule"
  nodeSelector:
    disk: ssd
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
        labels:
          app: nginx
    spec:
      containers:
      - name: server
        image: nginx:1.26.0
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
          limits:
            cpu: 200m
            memory: 200Mi
        livenessProbe:
          initialDelaySeconds: 10
          httpGet:
            path: "/"
            port: 80
        readinessProbe:
          initialDelaySeconds: 10
          httpGet:
            path: "/"
            port: 80
```

The above defined toleration would allow to schedule the Pod onto `minikube`.

**Note**: Taints and Tolerations **do not** guarantee that the pods only prefer these nodes. 
So the pods may be scheduled on the other untainted nodes. 
To guarantee that group of pods would be scheduled on a node, and **only** them, both **node selector** and **taint and tolerations** should be used.

To remove the taint: 

```bash 
kubectl taint nodes minikube gpu=true:NoSchedule-
```

## Horizontal Pod Autoscaling

> [!NOTE]
> Before starting, make sure the `metrics-server` is installed in your cluster. 
> 
> - If working on Minikube: `minikube addons enable metrics-server`.
> - If working on another k8s cluster, [read here](https://github.com/kubernetes-sigs/metrics-server?tab=readme-ov-file#installation). 

A **HorizontalPodAutoscaler** (HPA for short) automatically updates the number of Pods to match demand, usually in a Deployment or StatefulSet.

The HorizontalPodAutoscaler controller periodically (by default every 15 seconds) adjusts the desired scale of its target (for example, a Deployment) to match observed metrics such as average CPU utilization, average memory utilization, or any other custom metric you specify.
The common use for HPA is to configure it to fetch metrics from a [Metrics Server](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/#metrics-server) API (should be installed as an add-on). 
Every 15 seconds, the HPA controller queries the Metric Server and fetches resource utilization metrics (e.g. CPU, Memory) for each Pod that are part of the HPA. 
The controller then calculates the desired replicas, and scale in/out based on the current replicas.

Let's create an autoscaler object for the `nginx` Deployment:

```yaml
# k8s/hpa-autoscaler-demo.yaml

apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa-demo
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 50
```

When defining the pod specification, the resource **Requests**, like CPU and memory must be specified.
This is used to determine the resource utilization and used by the HPA controller to scale the target up or down.
In the above example, the HPA will scale up once the Pod is reaching 50% of the `.resources.requests.cpu`. 

Next, let's see how the autoscaler reacts to increased load. 
To do this, you'll start a different Pod to act as a client. 
The container within the client Pod runs in an infinite loop, sending queries to the `nginx-service` service.

```bash 
kubectl run -it load-generator --rm --image=busybox:1.28 --restart=Never -- /bin/sh -c "while sleep 0.001; do (wget -q -O- http://nginx-service &); done"
```


## Multiple containers pod

As you may know, a Pod is a group of one or more containers.
The containers in a Pod are automatically co-located and co-scheduled on the same physical or virtual machine in the cluster.

Grouping containers in a single Pod is a relatively advanced and **uncommon** use case. 
You should use this pattern only in specific cases in which your containers are tightly coupled.

For example, you might have an `nginx` container that acts as a web server for files in a shared volume, and a separate "helper" container that updates those files from a remote source:

![k8s_multicontainer_pod][k8s_multicontainer_pod]

This pattern is called a **Sidecar**:

```yaml
# k8s/sidecar-demo.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
        labels:
          app: nginx
    spec:
      containers:
        - name: webserver
          image: nginx
          volumeMounts:
          - name: html
            mountPath: /usr/share/nginx/html
        - name: helper
          image: debian
          volumeMounts:
          - name: html
            mountPath: /html
          command: ["/bin/sh", "-c"]
          args:
            - while true; do
                date >> /html/index.html;
                sleep 1;
              done
      volumes:
        - name: html
          emptyDir: { }
```

Apply the above manifest and observe the server behaviour. 

Other multi-container Pod patterns are **Proxies** and **Adapters**:

- **Proxies:** Acts as a proxy to the mian container. For example, an Nginx container that pass the traffic to a Flask backend server.
- **Adapter:** Used to standardize and normalize application input and output. For example, integrating a legacy system with a new framework by introducing an adapter container that translates calls between the two interfaces.


# Exercises 

### :pencil2: Readiness and Liveness to the Netflix stack 

1. Define a `livenessProbe` and a `readinessProbe` for the Netflix stack services:

   - NetflixFrontend
   - NetflixMovieCatalog
   - Grafana
   - InfluxDB
   - Redis

2. In the **NetflixMovieCatalog** service's source code, define a `SIGTERM` signal handler.
   The handler should indicate that the server is not ready by setting a **global variable** from `True` to `False`.
   When the server is not ready, you should fail the readiness probes, so the server will stop receiving traffic after a while.


### :pencil2: Zero downtime during scale

Your goal in this exercise is to achieve zero downtime during scale up/down events of a simple webserver.

The code can be found in `k8s/zero_downtime_node` (a simple Nodejs webserver).

1. Build the image and push it to a dedicated DockerHub or ECR repo.
2. Deploy the app as a simple `Deployment` (with the corresponding `Service`). 
3. Generate some incoming traffic (20 requests per second) from a dedicated pod: 
   ```bash
   kubectl run -i --tty load-generator --rm --image=busybox:1.28 --restart=Never -- /bin/sh -c "while sleep 0.05; do (wget -q -O- http://SERVICE_URL &); done"
   ```
   Chane `SERVICE_URL` accordingly.    

4. Increase the webserver's Deployment replicas while watching the `load-generator` pod logs. Did you lose requests for a short moment? Why?
5. Decrease the number of replicas, lost requests again? Why? 
6. Define a `liveness` and `readiness` probes in your Deployment. Change the server code in the `/ready` endpoint, and the `SIGTERM` handler to support zero down-time during scale up/down. You may also want to specify the `terminationGracePeriodSeconds` entry for the container.
8. Create a horizontal pod autoscaler (HPA) for the deployment. Base your HPA on CPU utilization, set the `resources.requests.cpu` and `resources.limits.cpu` entries `300m`. Maximum number of pods to 10.
7. Generate some load as described in step 3. Let the HPA to increase and decrease the number of pods. Make sure you don't lose even a single requests during **scale up and scale down** events.

**Bonus**: Make sure you are able to perform a rolling update with zero downtime, during traffic load. 

### :pencil2: Pod troubleshoot

In the file `k8s/pod-troubleshoot.yaml`, a PostgreSQL database Deployment is provided with intentionally injected issues for troubleshooting purposes.

Fix the issues while complying with the below requirements: 

- You should be able to communicate with the DB by (the command creates a temporary Pod that lists the existed databases in your Postgresserver ):

  ```bash
  kubectl run -i --tty --rm postgres-client --image=postgres:11.22-bullseye --restart=Never -- /bin/sh -c "PGPASSWORD=<your-pg-pass> psql -h postgres-service -U postgres -c '\list'"
  ```
  
  While `<your-pg-pass>` is your postgres DB password.

- The DB must be running on a node labeled `disktype=ssd`.
- The `postgres:11.22-bullseye` container must be scheduled on a node with at least 50 milli-cpu.
- The `postgres:11.22-bullseye` container must have liveness and readiness probed configured and working properly. 



[k8s_multicontainer_pod]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/k8s_multicontainer_pod.png
