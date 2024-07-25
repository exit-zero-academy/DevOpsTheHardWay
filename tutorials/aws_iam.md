# Identity and Access Management (IAM)

### Create IAM role with permissions over S3 and attach it to an EC2 instance

If you haven't created a role yet, here is a short recap:

1. Open the IAM console at [https://console\.aws\.amazon\.com/iam/](https://console.aws.amazon.com/iam/)\.

2. In the navigation pane, choose **Roles**, **Create role**\.

3. On the **Trusted entity type** page, choose **AWS service** and the **EC2** use case\. Choose **Next: Permissions**\.

4. On the **Attach permissions policy** page, search for **AmazonS3FullAccess** AWS managed policy\.

5. On the **Review** page, enter a name for the role and choose **Create role**\.
6. Attach the role to your EC2 instance. 
7. Test your policy.

Let's review the created permission JSON:

```json
    {
  "Version" : "2012-10-17",
  "Statement" : [
    {
      "Effect" : "Allow",
      "Action" : [
        "s3:*",  // Allowed actions on Amazon S3 resources
        "s3-object-lambda:*"  // Allowed actions on S3 Object Lambda resources
      ],
      "Resource" : "*"  // Allowed resource - in this case, all resources
    }
  ]
}
```

- `Version`: Denotes the version of the policy language being used.
- `Statement`: An array of policy statements, each defining a permission rule.
- `Effect`: Specifies whether the statement allows or denies access ("Allow" in this case).
- `Action`: Lists the actions allowed ("s3:" for all S3 actions, "s3-object-lambda:" for all S3 Object Lambda  actions).
- `Resource`: Specifies the resource to which the actions apply ("*" signifies all resources).

This policy allows any action (`s3:*`) and any action on S3 Object Lambda (`s3-object-lambda:*`) for any resource (`*`) because of the `Allow` effect.


## The Principle of Least Privilege

**The Principle of Least Privilege (PoLP)** is a security best practice that involves giving users and systems only the minimum permissions necessary to perform their tasks or functions, and no more. 
This helps to reduce the risk of accidental or intentional damage or data loss, and limit the potential impact of security breaches or vulnerabilities.

## Design a policy according to the PoLP

Let's modify the above created policy to follow the PolP. 

### Custom `Action`s and `Resource`s 

1. Inspired by [Allows read and write access to objects in an S3 Bucket](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html), allow your IAM role an access only to the specific bucket you use to store data.
2. **Validate your changes** either by trying to upload to another bucket, or using the [IAM Policy Simulator](https://policysim.aws.amazon.com/).

### Use `Condition`s 

1. Inspired by [Restricting access policy permissions to a specific storage class](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security_iam_service-with-iam.html#example-storage-class-condition-key).
   Create a policy to restrict objects uploads to the `STANDARD` storage class only.  
2. Validate your policy.

### Restrict access to specific IAM roles (even from different AWS accounts!)

Let's say the Netflix analytics team need an access to your bucket, but their platform are provisioned in another AWS account. 
How can the analytics team access a resource from another AWS account? 

So far, you've created an **Identity-based polices** - a policy which was assigned to some given **identity** (your IAM role in our example). 
Your EC2 instance which holds this role can say: "I'm an EC2! I have permissions to write objects to ABC bucket". 

In the other hand, **Resource -based policies** are policies that we assign to **resources** (our S3 bucket in our example).
The S3 bucket which holds the policy can say: "I'm an S3 bucket! I allow only for A and B IAM roles to talk with me".

In order for the analytics team to have access, we need to create a **Resource-based** policy on the S3 bucket that grants the specific IAM role from the analytics team account the necessary permissions.
This involves specifying the ARN of the IAM role from the external account in the bucket policy.

Here is an example of how to set this up:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                  "arn:aws:iam::019273951234:role/netflix-analytics-team-role"
                ]
            },
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::<your-bucket-name>",
                "arn:aws:s3:::<your-bucket-name>/*"
            ]
        }
    ]
}
```

Change `<your-bucket-name>` accordingly. 

Let's create the policy: 

1. In your bucket, choose the **Permissions** tab.
2. Under **Bucket policy**, choose **Edit**.
3. In the **Edit bucket policy** page, edit the JSON in the Policy section.
4. Inspired by [restrict access to specific VPC](https://repost.aws/knowledge-center/block-s3-traffic-vpc-ip), add another statement that blocks traffic to the bucket unless it's originated from your VPC, and the analytics team VPC, which is `vpc-1a2b3c4d`.
5. Validate your policy (only that you have access from within your VPC but not outside of it). 

> [!NOTE] 
> Resource based policy are mainly use to grant access to identities outside the current AWS account.


# Exercises

### :pencil2: Use `Condition` to enforce resource tagging policy

Inspired by [Tagging and access control policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/tagging-and-policies.html),
create a policy that enforces each uploaded object to be tagged by `Env=prod` or `Env=dev`.

In order to comply with the policy, you'll have to change some code (Node.js app) in the [NetflixFrontend][NetflixFrontend] repo, under `pages/api/analytics.ts`.


### :pencil2: Allow only HTTPS only

As you may know, Amazon S3 offers encryption in **transit** (data is encrypted when traveling between machines - HTTPS) and encryption **at rest** (data is encrypted when stored in the disk). 
But S3 allows also communication over HTTP, so encryption in transit may be violated.

Inspired by [this AWS blog post](https://repost.aws/knowledge-center/s3-bucket-policy-for-config-rule),
create a resource-based policy which enforces the user to access the bucket over HTTPS only. 


[NetflixFrontend]: https://github.com/exit-zero-academy/NetflixFrontend