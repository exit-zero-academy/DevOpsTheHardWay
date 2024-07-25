# Kubernetes Networking

The Kubernetes networking model facilitates communication between pods within a cluster, and from the outside world into the cluster.

- Pods can communicate with each other using their internal IP addresses. 
  Every pod in a cluster can reach every other pod without NAT.
- **Services** provide a stable endpoint that abstracts the underlying pod instances. Services enable load balancing and automatic discovery of pod changes.
  Pods can use the service name as a DNS entry to connect to other services.

So far, we've seen how to use Services to publish services only for consumption **inside your cluster**.

## Expose applications outside the cluster using a Service of type `LoadBalancer`

Kubernetes allows you to create a Service of `type=LoadBalancer` (no need to apply the below example):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: LoadBalancer
  selector:
    app.kubernetes.io/name: MyApp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
  clusterIP: 10.0.171.239
```

This Service takes effect only on cloud providers which support external load balancers (like AWS ELB). 
Applying this Service will **provision a Elastic Load Balancer (ELB) for your Service**.

![][k8s_networking_lb_service]

Traffic from the Elastic Load Balancer is directed to the backend Pods by the Service. The cloud provider decides how it is load balanced across different cluster's Nodes.

Note than the actual creation of the load balancer happens asynchronously, and information about the provisioned balancer is published in the Service's `.status.loadBalancer` field.

## Ingress and Ingress controller 

A Service of type `LoadBalancer` is the core mechanism that allows you to expose application to clients outside the cluster. 

What now? should we set up a separate Elastic Load Balancer for each Service we wish to make accessible from outside the cluster?
Doesn't this approach seem inefficient and overly complex in terms of resource utilization and cost?

It is. Let's introduce an **Ingress** and **Ingress Controller**.

Ingress Controller is an application that runs in the Kubernetes cluster that manage external access to services within the cluster. 
There are [many Ingress Controller implementations](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/) for different usages and clusters. 

[Nginx ingress controller](https://github.com/kubernetes/ingress-nginx) is one of the popular used one. 
Essentially, it's the same old good Nginx webserver app, exposed to be available outside the cluster (using Service of type `LoadBalancer`), and configured to route incoming traffic to different Services in the cluster (a.k.a. reverse proxy). 

![][k8s_networking_nginx_ic]

**Ingress** is another Kubernetes object, that defines the **routing rules** for the Ingress Controller (so you don't need to edit Nginx `.conf` configuration files yourself).

Let's deploy an Ingress Controller and apply an Ingress with routing rules. 

## Deploy the Nginx Ingress Controller

Ingress controllers are not started automatically with a cluster, you have to deploy it manually. 
We'll deploy the Nginx Ingress Controller behind an AWS Network Load Balancer (NLB).
Just apply the manifest as described in the [Network Load Balancer (NLB)](https://kubernetes.github.io/ingress-nginx/deploy/#network-load-balancer-nlb) section.

The above manifest mainly creates:

- Deployment `ingress-nginx-controller` of the Nginx webserver.
- Srvice `ingress-nginx-controller` of type `LoadBalancer`. 
- IngressClass `nginx` to be used in the Ingress objects (see `ingressClassName` below).
- RBAC related resources. 

To route traffic to the NetflixFrontend service, apply the below `Ingress` (change values according to your configurations): 

```yaml
# k8s/ingress-demo.yaml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: netflix-frontend
spec:
  rules:
  - host: YOUR_ELB_or_ROUTE53_DOMAIN_HERE 
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: YOUR_NETFLIX_FRONTEND_SERVICE_HERE
            port:
              number: YOUR_SERVICE_PORT_HERE
  ingressClassName: nginx
```

Nginx is configured to automatically discover all ingress where `ingressClassName: nginx` is present, like yours.

Visit the application using the ELB or Route53 domain name. 

> [!NOTE]
> #### The relation between **Ingress** and **Ingress Controller**:
> 
> **Ingress** only defines the *routing rules*, it is not responsible for the actual routing mechanism.  
> An Ingress controller is responsible for fulfilling the Ingress routing rules. 
> In order for the Ingress resource to work, the cluster must have an Ingress Controller running.

# Exercises 

### :pencil2: Terminate HTTPS traffic in the Nginx Ingress controller 

Follow the below docs to configure your Nginx Ingress Controller to listen to HTTPS connectionS:

https://kubernetes.github.io/ingress-nginx/examples/tls-termination/#tls-termination

You can also **force** your incoming traffic to use HTTPS by adding the following annotation to the `Ingress` object:

```text
nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
```

### :pencil2: Canary using Nginx 

You can add [nginx annotations](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/) to specific `Ingress` objects to customize their behavior.

In some cases, you may want to "canary" a new set of changes by sending a small number of requests to a different service than the production service. 
The [canary annotation](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/#canary) enables the Ingress spec to act as an alternative service for requests to route to depending on the rules applied.

In this exercise we'll deploy a canary for the NetflixFrontend service. 

- Deploy the NetflixFrontend service in a version which is not your most up-to-date (e.g. `0.8.0` instead of `0.9.0`). 
- Now you want to deploy the newer app version (e.g. `0.9.0`) but you don't confident with this deployment.
  Create other (separated) YAML manifests for the new version of the service, call then `netflix-frontend-canary`. 
- Create another `Ingress` pointing to your canary Deployment, as follows: 

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: canary
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "5"
spec:
  ingressClassName: nginx
  rules:
     # TODO ... Make sure the `host` entry is the same as the existed netflix-frontend Ingress. 
```

This Ingress routes 5% of the traffic to the canary deployment. 

Test your configurations by periodically access the application:

```bash
/bin/sh -c "while sleep 0.05; do (wget -q -O- http://LOAD_BALANCER_DOMAIN &); done"
```

**Bonus**: Use [different annotations](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/) to perform a canary deployment which routes users based on a request header `FOO=bar`, instead of specific percentage.


[k8s_networking_lb_service]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/k8s_networking_lb_service.png
[k8s_networking_nginx_ic]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/k8s_networking_nginx_ic.png
