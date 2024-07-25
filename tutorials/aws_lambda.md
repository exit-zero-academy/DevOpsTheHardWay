# Lambda Functions

## About serverless

Serverless architectures are a cloud computing paradigm that allows developers to build and deploy applications without the need to manage servers directly (PaaS).
In this model, the cloud provider takes care of server provisioning, scaling, and maintenance, enabling developers to focus solely on writing code and paying only for the actual resources consumed during execution. 

This approach offers reduced operational overhead, improved cost efficiency, and faster time-to-market for various types of applications and services.

## Email notification when new movie is released

Let's say Netflix wants to send an email to a group of customers when a new movie is released. 

In this tutorial we configure a Lambda function to be triggered whenever a new movie is added in the movies DynamoDB table. 
The Lambda function would send an email to those who have subscribed to receive notifications new movies.

### Create an SNS topic and subscribe an email 

1. Sign in to the [Amazon SNS console](https://console.aws.amazon.com/sns/home).
1. In the left navigation pane, choose **Topics**.
1. On the **Topics** page, choose **Create topic**.
1. By default, the console creates a FIFO topic. Choose **Standard**.
1. In the **Details** section, enter a **Name** for the topic.
1. Scroll to the end of the form and choose **Create topic**.
   The console opens the new topic's **Details** page.

1. In the left navigation pane, choose **Subscriptions**.
1. On the **Subscriptions** page, choose **Create subscription**.
1. On the **Create subscription** page, choose the **Topic ARN** field to see a list of the topics in your AWS account.
1. Choose the topic that you created in the previous step.
1. For **Protocol**, choose **Email**.
1. For **Endpoint**, enter an email address that can receive notifications.
1. Choose **Create subscription**.
1. The console opens the new subscription's **Details** page.
1. Check your email inbox and choose **Confirm subscription** in the email from AWS Notifications. The sender ID is usually `no-reply@sns.amazonaws.com`.
1. Amazon SNS opens your web browser and displays a subscription confirmation with your subscription ID.

### Enable Streams for your DynamoDB table

1. In the DynamoDB navigation pane on the left side, choose **Tables**.
2. Choose your table from the table list.
3. Choose the **Exports and streams** tab for your table.
4. Under **DynamoDB stream details** choose **Enable**.
5. Choose **New and old images** and click **Enable stream**.

### Create a Lambda Function

1. Open the [Functions page](https://console.aws.amazon.com/lambda/home#/functions) of the Lambda console\.

2. Choose **Create function**\.

3. Under **Basic information**, do the following:
    1. Enter **Function name**.
    2. For **Runtime**, confirm that **Python 3.x** is selected\.

4. Choose **Create function**\.
5. Enter your function, copy the content of `new_movie_lambda/app.py` and paste it in the **Code source**. 
6. Click the **Deploy** button.
7. On the same page, click **Add trigger** and choose your Dynamo table as a source trigger.
7. Configure an environment variable named `TOPIC_ARN` with the ARN of your topic. The lambda will send a notification to this topic.
8. In your Lambda IAM role, attach the `AWSLambdaInvocation-DynamoDB` and `AmazonSNSFullAccess` permissions to allow your Lambda read items from DynamoDB and publish messages to your SNS topic.  

Test your Lambda function by creating a new movie item in the Dynamo table and watch for new email in your inbox.


# Exercises

### :pencil2: Monitor your Lambda function

1. Access your Grafana instance (it must be running within an EC2 instance).
2. Add **CloudWatch** as a data source under Grafana's data source settings. To allow Grafana access CloudWatch, create a role with permission on CloudWatch and attach it to your EC2 instance. 
3. Create panels in Grafana to display the following Lambda metrics: invocation count, errors and running duration.


### :pencil2: Docker based Lambda

As DevOps engineers, we prefer deploying the Lambda function using Docker containers instead of directly copying the source code.

1. Under `new_movie_lambda/` create a `Dockerfile` to containerize your code:

```dockerfile
FROM public.ecr.aws/lambda/python:3.10

# TODO your instructions here....

CMD ["app.lambda_handler"]
```

2. Build the image and push it to an ECR repo:
   - Open the Amazon ECR console at [https://console\.aws\.amazon\.com/ecr/repositories](https://console.aws.amazon.com/ecr/repositories).
   - In the navigation pane, choose **Repositories**\.
   - On the **Repositories** page, choose **Create repository**\.
   - For **Repository name**, enter a unique name for your repository\. E.g. `john_new_movie_notify`
   - Choose **Create repository**\.
   - Select the repository that you created and choose **View push commands** to view the steps to build and push an image to your new repository\.

3. Create a new Lambda function based on your Docker image. 
4. Test it.


