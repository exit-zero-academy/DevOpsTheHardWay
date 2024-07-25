# Kubernetes StatefulSet and Storage

In this tutorial, we will deploy a MongoDB cluster, and integrate it with the [NetflixMovieCatalog][NetflixMovieCatalog] service.

Currently, the NetflixMovieCatalog service stores movies data in a simple JSON files under the `data/` dir. 
We want this service to dynamically read movies from a MongoDB cluster, deployed in Kubernetes.

The MongoDB cluster consists by 3 Pods: One primary replica and two secondary replicas.

![][k8s_storage_and_statefulset_mongo]

## Deploy MongoDB as a StatefulSet

Due to the stateful nature of databases, we need a mechanism to persist data in Kubernetes.
So far, Pods in the cluster were ephemeral resources, Pod's container state was not saved, so all of the files that were created or modified during the lifetime of the container were lost.

Kubernetes allows you to bind a [Persistent Volume](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) to a Pod, so the data stored in that volume exist beyond the lifetime of a pod. 
An example for a persistent volume can be an external AWS EBS, Azure disks, or a "logical volume" that mounts a file or directory from the host node's filesystem into your Pod.

One more problem that arise here is the **"identity"** of Pods. 
The MongoDB cluster consists by 3 Pods, although all of them have the same container spec (based on the [mongo image](https://hub.docker.com/_/mongo)), one Pod is functioning as a **primary**, while the others are **secondaries** replicas. 

Obviously we cannot use Deployment here. In a Deployment, which manage an identical set of Pods, we can not prefer "this pod" over "that pod", each pod is interchangeable with any other pod. 
In the MongoDB case, we should remember that "pod number 1" is the primary, while "pods 2 and 3" are secondaries replicas. 
In that sense, Pod has an "identity". 

Here **StatefulSet** comes in.

A [StatefulSet](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) is the workload resource for **stateful** applications deployed in Kubernetes.
Similarly to Deployment, StatefulSet manages the deployment and scaling of a set of Pods, but provides **guarantees about the ordering and uniqueness of these Pods**.

Like a Deployment, a StatefulSet manages Pods that are based on an identical container spec. 
Unlike a Deployment, a StatefulSet maintains a **sticky identity** for each of its Pods. 

We'll explain these concepts using the below example:

```yaml
# k8s/mongo-statefulset.yaml

apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongo
spec:
  serviceName: "mongo-service"
  replicas: 3
  selector:
    matchLabels:
      app: mongo
  template:
    metadata:
      labels:
        app: mongo
    spec:
      containers:
        - name: mongo
          image: mongo:5
          command:
            - mongod
            - "--replSet"
            - myReplicaSet
            - "--bind_ip_all"
          ports:
            - containerPort: 27017
          volumeMounts:
            - name: mongo-persistent-storage
              mountPath: /data/db
  volumeClaimTemplates:
  - metadata:
      name: mongo-persistent-storage
    spec:
      storageClassName: standard
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 2Gi
---
apiVersion: v1
kind: Service
metadata:
  name: mongo-service
  labels:
    app: mongo
spec:
  clusterIP: None
  selector:
    app: mongo
  ports:
  - port: 27017
    targetPort: 27017
```

Now we need to initiate the mongo cluster. In order to do so, get a Mongo shell access to the first Pod of the StatefulSet, denoted by `mongo-0`.

```console
$ kubectl exec -ti mongo-0 -- mongosh
Current Mongosh Log ID:	654f5d7fbe499b77952befe7
Connecting to:		mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.0.1
Using MongoDB:		7.0.2
Using Mongosh:		2.0.1
...
```

From the opened Mongo Shell, initialize the Mongo cluster:

```javascript
rs.initiate()
rs.add("mongo-1.mongo-service:27017")
rs.add("mongo-2.mongo-service:27017")
```

The address of the primary replica from within the cluster is: `mongo-0.mongo-service:27017`. 

## StatefulSet and Volumes characteristics

```console 
$ kubectl get pods -l app=mongo
NAME      READY   STATUS    RESTARTS   AGE
mongo-0   1/1     Running   0          12m
mongo-1   1/1     Running   0          12m
mongo-2   1/1     Running   0          12m
```

As can be seen, the StatefulSet assigns each Pod a unique, stable name of the form `<statefulset-name>-<ordinal-index>`, which results in Pods named `mongo-0`, `mongo-1`, and `mongo-2` (as opposed to Deployments, in which Pods got a random name). 

Each Pod in the Mongo cluster has its own volume to store data: 

```console
$ kubectl get persistentvolumeclaim
NAME                               STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
mongo-persistent-storage-mongo-0   Bound    pvc-d45d676d-abff-4d0c-89ac-545a29f3d339   2Gi        RWO            standard       26m
mongo-persistent-storage-mongo-1   Bound    pvc-7b35b117-5ad4-433d-82a7-99968d89615c   2Gi        RWO            standard       26m
mongo-persistent-storage-mongo-2   Bound    pvc-0d5b76ce-e5aa-44a8-bc16-21070e0a5e45   2Gi        RWO            standard       26m
```

Did I create those volumes myself? 🤔 No... The volumes were created **dynamically** as part of the StatefulSet creation. 

How? In the `mongo` example above, the `VolumeClaimTemplate` entry defined in a StatefulSet creates a **PersistentVolumeClaim (PVC)** for each Pod. 
Then for each **PersistentVolumeClaim (PVC)**, a single **PersistentVolume (PV)** is created with a **StorageClass** of `standard` and 2 GiB of provisioned storage.

Let us explain:

- **PersistentVolume (PV)** is a piece of storage in the cluster. PV can represent a physical disk connected to your cluster's Nodes, or an existed EBS in AWS.
  But Pods can not use a PV directly, instead, they do it by another object called PersistentVolumeClaim (PVC).
- **PersistentVolumeClaim (PVC)** is a **request** for volume, a **claim** for an existed PV. Pods are bound to PVC, which bound to PV resources.
  The reason for having a PVC is to **decouple** storage management from pod spec. Pods can request storage without needing to know the specifics of the underlying storage infrastructure.
- **Storage Class (SC)** provides a way to describe the "classes" of storage that the cluster can provision.
  For example, we can have one SC to provision volumes in AWS of type `gp3`, and another SC to provision `gp2` volumes.  
  Obviously, there should be a well-defined **interface** between the storage system of the cloud provider, and Kubernetes. The most commonly used interface today is the [Container Storage Interface (CSI)](https://github.com/container-storage-interface/spec).
  Usually, Kubernetes clusters have default storage class to be used if the `storageClassName` field was not specified. 
  
  In Minikube clusters, the `standard` Storage Class has the `k8s.io/minikube-hostpath` provisioner, which mount a directory in the node's file system as a "storage". This Storage Class should be used for development only, it is not useful for real data persistence. 
  
![k8s_statefulset_and_storage_summary][k8s_statefulset_and_storage_summary]

When a Pod is (re)scheduled onto a node, for example as a result of a rolling update, its knows the PVC associated with it. That way Pods can be failed or replaced, and returned to the same volume the previous Pod has.
In our example, Pod `mongo-0` will always be mounted to `pvc-d45d676d-abff-4d0c-89ac-545a29f3d339` volume.

What else should we say about the `mongo` StatefulSet? 

Pods also have a **stable network identity**. 
Talking with the primary replica can be done via `mongo-0.mongo-service:27017`.

The domain takes the form: `<pod-name>.<service-name>`.

Note that the `mongo-service` Service created for the StatefulSet, has an entry `ClusterIP: none`. This is known as a [Headless Service](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services). 
**Headless Service** doesn't have Cluster IP and no load-balancing mechanism for the different Pods, instead, it is used for **discovery mechanisms**.
When resolving the DNS name `mongo-service`, you don't get an IP address of **one** of the Pods this service is pointing to (as done in a regular service), but you get the IP addresses of **all** the Pods this service is pointing to. 

```bash 
kubectl run -i --tty --rm headless-test --image=alpine --restart=Never -- nslookup mongo-service
```

We use the Service just to group the Pods together under domain name, but the actual communication is done against a particular Pod. 

In our case, if you want to perform read/write to the MongoDB, talk with `mongo-0.mongo-service`, if you want to read only, talk with either `mongo-1.mongo-service`, or `mongo-2.mongo-service`.


## Deployment and scaling guarantees in StatefulSet

When your `mongo` StatefulSet was created, the 3 Pods have been deployed **in order** - `mongo-0`, `mongo-1`, then `mongo-2`.
`mongo-1` will not be deployed before `mongo-0` is **Running** and **Ready**, the same goes for `mongo-2`. 

If you were to scale the StatefulSet such that `replicas=1` (only 1 replica of Mongo), `mongo-2` would be terminated first, then `mongo-1`.
`mongo-1` would not be terminated until `mongo-2` is fully shutdown and deleted.

A StatefulSet's `.spec.updateStrategy` field allows you to configure and disable automated rolling updates.
When a StatefulSet's `.spec.updateStrategy.type` is set to `RollingUpdate`, the StatefulSet will delete and recreate each Pod in the StatefulSet.
It will proceed in the same order as Pod termination (from the largest ordinal to the smallest), updating each Pod one at a time.

### Volumes and data protection

PersistentVolumeClaims (PVCs) and PersistentVolumes (PVs) are not a joke, guys. 
These are the objects in the cluster representing real infrastructure containing an important data that you cannot allow yourself to lose.  

You don't want to delete a PVC or PV by mistake, and lose your data as a result. 

Kubernetes is shipped with a **Storage Object in Use Protection feature** to deal with such kind of risks. 

PVC in an **active use** by a Pod and PV that are bound to it are not removed immediately from the system:

- PVC removal is postponed until the PVC is no longer actively used by any Pods.
- PV removal is postponed until the PV is no longer bound to a PVC.

And what about the underlying infrastructure that the PV in bound to (such as an AWS EBS or GCE PD volume)? 

Kubernetes allows reclamation of the PersistentVolume resource by another PersistentVolumeClaim.
The **Reclaim Policy** for a PV tells the cluster what to do with the volume after it has been released of its claim. 

Volumes reclaim policy can either be `Retained` or `Deleted`.

- `Retain` - When the PV is deleted, the associated external infrastructure still exists. 
- `Delete` - When the PV is deleted, the associated external infrastructure is removed as well.


# Exercises

### :pencil2: Integrate the MongoDB cluster into the `NetflixMovieCatalog` service.

Modify the Python code in your [NetflixMovieCatalog][NetflixMovieCatalog] service to serve data retrieved from the above deployed MongoDB cluster. 

### :pencil2: Persist Grafana data using StatefulSet

**Before starting, delete any existed Grafana server from previous exercises**.

Provision a Grafana server using a StatefulSet with `2GB` volume to persist the server's data and configurations.
All Grafana data is stored under `/var/lib/grafana`. The server should run using 1 replica.

Make sure the StatefulSet was created successfully, and that Grafana data is persistent.


### :pencil2: Increase volumes capacity

Assume your MongoDB cluster is monitored by Grafana, and you see that the disk capacity is about to be out of space.    

This exercise guides you how to properly increase the Kubernetes volume size.  

Resizing an existing volume is done by editing the **PersistentVolumeClaim** object.

Never interact manually with the storage backend, nor delete and recreate PV and PVC objects to increase the size of a volume. 

The StorageClass that your PVC is based on, must have the `allowVolumeExpansion` field set to `true`: 

```bash
kubectl describe storageclass <storage-class-name>
```

To add the `allowVolumeExpansion: true` field, or can edit the resource manually via the Kubernetes Dashboard, or perform:

```bash
# Using nano 
KUBE_EDITOR="nano" kubectl edit storageclass <storage-class-name>

# Or VIM
kubectl edit storageclass <storage-class-name>
```

Now just increase the volume size in your PVC, again either by editing it manually via the Kubernetes Dashboard, or by:

```bash
kubectl edit pvc <pvc-name>
```

Kubernetes will interpret a change to the storage field as a request for more space, and will trigger automatic volume resizing.

Once the PVC has the condition `FileSystemResizePending` then pod that uses the PVC can be restarted to finish file system resizing on the node. 
Restart can be achieved by deleting and recreating the pod or by scaling down the StatefulSet and then scaling it up again.

Once file system resizing is done, the PVC will automatically be updated to reflect new size.

Any errors encountered while expanding file system should be available as events on pod



[NetflixMovieCatalog]: https://github.com/exit-zero-academy/NetflixMovieCatalog
[k8s_statefulset_and_storage_summary]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/k8s_statefulset_and_storage_summary.png
[k8s_storage_and_statefulset_mongo]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/k8s_storage_and_statefulset_mongo.png

