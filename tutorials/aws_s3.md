# Simple Storage Service (S3)

In this tutorial, you'll store the movies thumbnails in an S3 bucket and configure the service to serve the content from your bucket. 

To store your data in Amazon S3, you first create a **bucket** and specify a bucket name and AWS Region.
Then, you upload your data to that bucket as **objects** in Amazon S3. 
Each object has a **key** (or key name), which is the unique identifier for the object within the bucket.

2. upload images from cli
3. make it public static
4. change netflix to this source test


In the below example, you create a bucket to store user analytics data for the NetflixFrontend app. 

## Create a Bucket

1. Open the Amazon S3 console at https://console.aws.amazon.com/s3/.
2. In the left navigation pane, choose **Buckets**\.
3. Choose **Create bucket**.

   The **Create bucket** wizard opens.

4. In **Bucket name**, enter a DNS-compliant name for your bucket.

   The bucket name must:
   + Be unique across **all of Amazon S3**.
   + Be between 3 and 63 characters long.
   + Not contain uppercase characters.
   + Start with a lowercase letter or number.

5. In **Region**, choose the AWS Region where you want the bucket to reside.

   Choose the Region where you provisioned your EC2 instance.

6. Under **Object Ownership**, leave ACLs disabled. By default, ACLs are disabled\. A majority of modern use cases in Amazon S3 no longer require the use of ACLs\. We recommend that you keep ACLs disabled, except in unusual circumstances where you must control access for each object individually\.

8. Enable Default encryption with `SSE-S3` encryption type.

9. Choose **Create bucket**.

## Upload objects to S3 bucket from an EC2 instance

In the NetflixFrontend app, whenever a user opens the details window for a specific movie, an HTTP request is sent to the server containing the activity information.
This activity if turn is stored as an object in an S3 bucket for later usage (for example by user analytics or recommendation teams).

You can review the code that upload object to S3 under `pages/api/analytics.ts` in the NetflixFrontend repo..

In your EC2 instance where the NetflixFrontend container is running, re-run the container while providing the following environment variables to the container: 

- `AWS_REGION` - Your region code (e.g. `us-east-1`).
- `AWS_S3_BUCKET` - The name of your bucket.

Visit the Netflix app, expand one of the movies information window, this activity should trigger an HTTP request to the app, which is turn will save the activity object in S3 bucket.

**Disclaimer:** This is not going to work. You should see an error like "Error updating user session" in the console logs of the NetflixFrontend logs. 
Since the identity who writes the data to the S3 bucket is your EC2 instance, it has to have permissions to operate in S3.

![][ec2-s3]

Keep reading....

### Attach IAM role to your EC2 Instance with permissions over S3

To access an S3 bucket from an EC2 instance, you need to create an IAM role with the appropriate permissions and attach it to the EC2 instance.
The role should have policies that grant the necessary permissions to read from and write to the S3 bucket, and the EC2 instance needs to be launched with this IAM role.
IAM role will be taught soon. But for now, just follow the instructions below.

1. Open the IAM console at [https://console\.aws\.amazon\.com/iam/](https://console.aws.amazon.com/iam/)\.

1. In the navigation pane, choose **Roles**, **Create role**\.

1. On the **Trusted entity type** page, choose **AWS service** and the **EC2** use case\. Choose **Next: Permissions**\.

1. On the **Attach permissions policy** page, search for **AmazonS3FullAccess** AWS managed policy\.

1. On the **Review** page, enter a name for the role and choose **Create role**\.


**To replace an IAM role for an instance**

1. In EC2 navigation pane, choose **Instances**.

1. Select the instance, choose **Actions**, **Security**, **Modify IAM role**.

1. Choose your created IAM role, click **Save**.

After assigning the role, check that app stores user activity in your S3 bucket. 

## Enable versioning on your bucket

What happen if you upload an object name that already exists? 

You'll notice that the new object overrides the old one, without any option to restore the older version. 
If this happens unintentionally or due to a bug in the application code, it can result in the permanent loss of data.

The risk of data loss can be mitigated by implementing **versioning** in S3. 
When versioning is enabled, each object uploaded to S3 is assigned a unique version ID, which can be used to retrieve previous versions of the object. 
This allows you to recover data that was accidentally overwritten or deleted, and provides a safety net in case of data corruption or other issues.

1. Open the Amazon S3 console at [https://console\.aws\.amazon\.com/s3/](https://console.aws.amazon.com/s3/)\.

2. In the **Buckets** list, choose the name of the bucket that you want to enable versioning for\.

3. Choose **Properties**\.

4. Under **Bucket Versioning**, choose **Edit**\.

5. Choose **Enable**, and then choose **Save changes**\.

6. Upload multiple object with the same key, make sure versioning is working.

## Create lifecycle rule to manage non-current versions

When versioning is enabled in S3, every time an object is overwritten or deleted, a new version of that object is created. Over time, this can lead to a large number of versions for a given object, many of which may no longer be needed for business or compliance reasons.

By creating lifecycle rules, you can define actions to automatically transition non-current versions of objects to a lower-cost storage class or delete them altogether. This can help you reduce storage costs and improve the efficiency of your S3 usage, while also ensuring that you are in compliance with data retention policies and regulations.

For example, you might create a lifecycle rule to transition all non-current versions of objects to `Standard-IA` storage after 30 days, and then delete them after 365 days. This would allow you to retain current versions of objects in S3 for fast access, while still meeting your data retention requirements and reducing storage costs for non-current versions.


1. Choose the **Management** tab, and choose **Create lifecycle rule**\.

1. In **Lifecycle rule name**, enter a name for your rule\.

1. Choose the scope of the lifecycle rule (in this demo we will apply this lifecycle rule to all objects in the bucket).

1. Under **Lifecycle rule actions**, choose the actions that you want your lifecycle rule to perform:
   + Transition *noncurrent* versions of objects between storage classes
   + Permanently delete *noncurrent* versions of objects

1. Under **Transition non\-current versions of objects between storage classes**:

   1. In **Storage class transitions**, choose **Standard\-IA**.

   1. In **Days after object becomes non\-current**, enter 30.

1. Under **Permanently delete previous versions of objects**, in **Number of days after objects become previous versions**, enter 90 days.

1. Choose **Create rule**\.

   If the rule does not contain any errors, Amazon S3 enables it, and you can see it on the **Management** tab under **Lifecycle rules**\.

# Exercises

### :pencil2: S3 pricing

Explore the [S3 pricing page](https://aws.amazon.com/s3/pricing/).

Compute the monthly cost of the below bucket characteristics:

1. us-east-1
2. S3 Standard
3. 4TB stored data
4. 40 million PUT requests.
5. 10 million GET requests.
6. 5TB inbound traffic
7. 10TB outbound traffic


[ec2-s3]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/ec2-s3.png