# AWS Elastic Kubernetes Service (EKS) 

Kubernetes is shipped by [many different distributions](https://nubenetes.com/matrix-table/#), each aimed for a specific purpose.
Throughout this tutorial we will be working with Elastic Kubernetes Service (EKS), which is a Kubernetes cluster managed by AWS.  

## Elastic Kubernetes Service (EKS)

> [!IMPORTANT]
> This tutorial let you feel how a production ready Kubernetes cluster can be easily provisioned using EKS, but since this resource is quite expensive, **you should delete your EKS clusters after creation**. 


To provision an EKS cluster using the AWS Management Console:

1. Open the Amazon EKS console at https://console.aws.amazon.com/eks/home#/clusters
2. Choose **Add cluster** and then choose **Create**.
3. On the Configure cluster page, enter the following fields:
    - **Name** - A name for your cluster. E.g. `john-k8s`.
    - Choose your **Kubernetes version**.  
    - For **Cluster service role**, create an IAM role as [described here](https://docs.aws.amazon.com/eks/latest/userguide/service_IAM_role.html#create-service-role). The EKS cluster IAM role allows the Kubernetes control plane to manage AWS resources on your behalf.  
    - Leave other default definitions.
4. On the **Specify networking** page, select values for the following fields:
    - **VPC** - Choose your VPC. 
    - **Subnets** - choose your public subnets. 
    - **Security groups** - leave empty.
    - For **Cluster endpoint access**, select **Public**.
5. Leave the **Configure observability** page like that.
6. Leave the **Select add-ons** page and the **Configure selected add-ons settings** page like that.
7. On the **Review and create** page, review your  cluster information and create. 

Cluster provisioning takes several minutes.

## Controlling the cluster

> [!IMPORTANT]
> Before executing the below command, make sure the [`aws` CLI version 2 is installed](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). 


Let's authenticate `kubectl` with your EKS cluster:

```shell
aws eks --region <your-region> update-kubeconfig --name <cluster_name>
```

Change `<your-region>` and `<cluster_name>` accordingly. 

Make sure `kubectl` successfully communicates with your cluster:

```console
$ kubectl get pods -A
NAMESPACE     NAME                      READY   STATUS    RESTARTS   AGE
kube-system   coredns-58488c5db-g89gc   0/1     Pending   0          152m
kube-system   coredns-58488c5db-z4f67   0/1     Pending   0          152m
```

## Manage Nodes

A fresh EKS cluster doesn't have Nodes, but only the **Control Plane** server.

EKS cluster offer different approaches to create and manage Nodes:

1. **EKS managed node groups**: EKS create and manage the cluster EC2 instances for you. Just choose an instance type, minimum and maximum number of Nodes. 
2. **Self-managed nodes**: you manually add EC2 instances to the cluster. You have to create the instances yourself, configure them and connect them to the cluster Control Plane.  
3. **AWS Fargate**: a technology that provides on-demand, right-sized compute capacity without even seeing the EC2 instances. You don't have to provision, configure, or scale groups of virtual machines on your own. Just schedule a Pod and AWS will take control on compute themselves (feels like "serverless" cluster). 

We will use the **EKS manage node groups** approach.

To create a managed node group using the AWS Management Console:

1. Wait for your cluster status to show as `ACTIVE`.
2. Open the Amazon EKS console at https://console.aws.amazon.com/eks/home#/clusters.
3. Choose the name of the cluster that you want to create a managed node group in.
4. Select the **Compute** tab.
5. Choose **Add node group**.
6. On the **Configure node group** page, fill out the parameters accordingly. 
   - **Name** - To your choice. E.g. `default-ng`.
   - **Node IAM role** - create a node IAM role as [described here](https://docs.aws.amazon.com/eks/latest/userguide/create-node-role.html#create-worker-node-role).
7. On the **Set compute and scaling configuration** page, keep all the default configurations.
8. On the **Specify networking** page, keep all the default configurations.
9. Review and create.
    
## Install k8s dashboard 

Install the dashboard as described here: 

https://github.com/kubernetes/dashboard

When opening the dashboard UI, you are asked to provide the service account token with which you can access the dashboard.

Let's generate an admin service account and retrieve its secret access token:

```yaml
# k8s/k8s-dashboard-user.yaml

apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
---
apiVersion: v1
kind: Secret
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
  annotations:
    kubernetes.io/service-account.name: "admin-user"
type: kubernetes.io/service-account-token
```

And appy it:

```bash
kubectl apply -f k8s/k8s-dashboard-user.yaml
```

You can retrieve the secret by: 

```bash
kubectl get secret admin-user -n kubernetes-dashboard -o jsonpath={".data.token"} | base64 -d
```

## Install EBS CSI driver

The [EBS CSI driver](https://github.com/kubernetes-sigs/aws-ebs-csi-driver) allows you to create and manage EBS volumes as storage for the Kubernetes Volumes that you create. 

The Amazon EBS CSI plugin requires IAM permissions to make calls to AWS APIs on your behalf. For more information, see [Creating the Amazon EBS CSI driver IAM role](https://docs.aws.amazon.com/eks/latest/userguide/csi-iam-role.html).

1. Open the Amazon EKS console at https://console.aws.amazon.com/eks/home#/clusters
2. In the left navigation pane, choose **Clusters**.
3. Choose the name of the cluster that you want to configure the Amazon EBS CSI add-on for.
4. Choose the **Add-ons** tab.
5. Choose **Get more add-ons**.
6. On the **Select add-ons** page, do the following:

    - In the **Amazon EKS-addons** section, select the **Amazon EBS CSI Driver** check box.
    - Choose **Next**.
7. On the **Configure selected add-ons settings** page, select the name of an **IAM role** that you attached the Amazon EBS CSI driver IAM policy.
8. On the **Review and add** page, choose **Create**. 

## Nodes autoscaling 

So far, we've seen Pod horizontal autoscaling (HPA). 
But Kubernetes clusters have actually two levels of scaling - Pod level scaling (done using **Horizontal Pod Autoscaler HPA**), and Node level scaling (done using a tool called [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master)).

https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/aws/README.md

Cluster Autoscaler requires the ability to examine and modify Auto Scaling Groups (ASG), assign the following permission to your node IAM role:

```json 
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "autoscaling:DescribeAutoScalingGroups",
        "autoscaling:DescribeAutoScalingInstances",
        "autoscaling:DescribeLaunchConfigurations",
        "autoscaling:DescribeScalingActivities",
        "autoscaling:DescribeTags",
        "ec2:DescribeImages",
        "ec2:DescribeInstanceTypes",
        "ec2:DescribeLaunchTemplateVersions",
        "ec2:GetInstanceTypesFromInstanceRequirements",
        "eks:DescribeNodegroup"
      ],
      "Resource": ["*"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "autoscaling:SetDesiredCapacity",
        "autoscaling:TerminateInstanceInAutoScalingGroup"
      ],
      "Resource": ["*"]
    }
  ]
}
```

The Kubernetes cluster autoscaler should automatically discover the ASG associated with your node groups. 
It's done by a specific tagging or the ASG resource: `k8s.io/cluster-autoscaler/<cluster-name>` and `k8s.io/cluster-autoscaler/enabled`.
But no further action is required here as EKS automatically tagged the node group's ASG for auto-discovery by the Kubernetes cluster autoscaler.

Download the example YAML manifest from [Autoscaler official source code](https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml): 

```bash
wget https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml
```

Edit the line specifying your node group tags (`--node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/<YOUR CLUSTER NAME>`), and apply:

```bash
kubectl apply -f cluster-autoscaler-autodiscover.yaml
```

# Exercises 

### :pencil2: Deploy the Netflix stack

Deploy your Netflix YAML manifests in the new EKS cluster.

### :pencil2: EKS Pod Identities

EKS Pod Identities provide the ability to manage credentials for your applications, similar to the way that you assign IAM role to EC2 instances.
Instead of creating and distributing your AWS credentials to the containers or using the Node's role, you associate an IAM role with a Kubernetes service account and configure your Pods to use the service account.

Follow:    
https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html
