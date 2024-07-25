## Secured Lambda based API using CloudFront, WAF and Cognito

This tutorial was inspired by [AWS Well-Architected Labs - Multilayered API Security with Cognito and WAF ](https://www.wellarchitectedlabs.com/security/300_labs/300_multilayered_api_security_with_cognito_and_waf/).
To get some background and context about this tutorial, please enter the link and read the introduction section.  

![][aws_api-lambda-1]

## Create the DB 

If you've already created the "tweets" DB from the previous demo, you are allowed to skip this section. Otherwise, before you move on, please [create the tweets DB](aws_rds.md#provision-postgres-using-rds) and fill it with the tables and data.  

## Create the Lambda Functions

Create a **Container image** Lambda function, from the code under the `lambda-api` directory. 
Make sure your Lambda function has the following env vars:
 - `DB_HOST` - with a value as your DB host.
 - `DB_USER` - with a value as your DB username.
 - `DB_PASSWORD` - with a value as your DB password.
 - `DATABASE_NAME` - with a value as your database name you've created.

## Create the API gateway with Lambda proxy integration 

[Lambda proxy integration](https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html) is a lightweight, flexible API Gateway API integration type that allows you to integrate an API method – or an entire API – with a Lambda function.
The Lambda function can be written in any language that Lambda supports.
Because it's a proxy integration, you can change the Lambda function implementation at any time without needing to redeploy your API.

1. Sign in to the API Gateway console at [https://console\.aws\.amazon\.com/apigateway](https://console.aws.amazon.com/apigateway).

2. Choose **Create API**\. Under **REST API**, choose **Build**\.

3. Create an empty API as follows:

   1. Under **Create new API**, choose **New API**\.

   1. Under **Settings**:
      + For **API name**, enter your API name\.
      + Leave **Endpoint Type** set to **Regional**\.

   1. Choose **Create API**\.

4. Create the `tweets` resource as follows:

   1. Choose the root resource \(**/**\) in the **Resources** tree\.

   1. Choose **Create Resource** from the **Actions** dropdown menu\.

   1. Leave **Configure as proxy resource** unchecked\.

   1. For **Resource Name**, enter **tweets**\.

   1. Leave **Resource Path** set to **/tweets**\.

   1. Choose **Create Resource**\.

5. In a proxy integration, the entire request is sent to the backend Lambda function as-is.

   To set up the `GET` method, do the following:

   1. In the **Resources** list, choose **/tweets**\.

   2. In the **Actions** menu, choose **Create method**\.

   3. Choose **GET** from the dropdown menu, and choose the checkmark icon.

   4. Leave the **Integration type** set to **Lambda Function**\.

   5. Choose **Use Lambda Proxy integration**\.

   6. From the **Lambda Region** dropdown menu, choose the region where you created the Lambda function.

   7. In the **Lambda Function** field, choose your Lambda from the dropdown menu\.

   8. Leave **Use Default Timeout** checked\.

   9. Choose **Save**\.

   10. Choose **OK** when prompted with **Add Permission to Lambda Function**\.

### Deploy and test the API

1. Choose **Deploy API** from the **Actions** dropdown menu\.

2. For **Deployment stage**, choose **\[new stage\]**\.

3. For **Stage name**, enter **prod**\.

6. Choose **Deploy**\.

7. Note the API's **Invoke URL**\.

### Test the API gateway

1. Open a terminal window\.

1. Copy the following cURL command and paste it into the terminal window, replacing `<InvokeURL>` with your API's URL.

   ```
   curl -H 'content-type: application/json' <InvokeURL>/tweets?username=MetiersInternet
   ```

You should get a successful response with a payload similar to the following:

```json
[
   ["Bill Gates Talks Databases, Free Software on Reddit http://t.co/ShX4hZlA #billgates #databases"],
   ["http://t.co/D3KOJIvF article about Madden 2013 using AI to prodict the super bowl #databases #bus311"]
]
``` 

## Integrate CloudFront for regional API endpoints

CloudFront delivers your content through a worldwide network of data centers (a.k.a. CDN) called edge locations.
We will distribute our API through CloudFront not only to improve performance, but also to supports geoblocking, which you can use to help block requests from particular geographic locations from being served.
Furthermore, CloudFront can automatically close connections from slow reading or slow writing attackers.

The API Gateway will be configured to accept requests only from CloudFront (by custom header secret). This helps prevent anyone from accessing your API Gateway deployment directly.
Additionally, we will integrate AWS WAF to protect the API from SQL injection attack.

We will build out the architecture as follows:

![][aws_api-lambda-2]


### Create CloudFront distribution

1. In the [CloudFront console](https://console.aws.amazon.com/cloudfront/), choose **Create Distribution**.
2. On the **Create Distribution** page, for **Origin Domain Name**, paste your API's invoke URL (**excluding** the stage name). e.g.:
   ```text
   https://2chayswz52.execute-api.us-east-1.amazonaws.com
   ```
3. For **Origin Path**, enter your API's stage name with a slash in front of it (/prod). Or, if you want to enter the stage name yourself when invoking the URL, don't enter an Origin Path.
4. For **Viewer protocol policy**, choose **HTTPS Only** (API Gateway doesn't support unencrypted endpoints).
5. Under **Cache key and origin requests** choose **Legacy cache settings** and select **All** for **Query strings**. We do it so CloudFront will forward users query parameters to the API gateway.
6. Choose **Create Distribution**.
7. Wait for your distribution to deploy. This takes 15-20 minutes. When its **Status** appears as **Deployed** in the console, the distribution is ready.

### Create WAF

1. Sign in to the AWS Management Console and open the AWS WAF console at [https://console\.aws\.amazon\.com/wafv2/](https://console.aws.amazon.com/wafv2/).

2. Choose **Web ACLs** in the navigation pane, and then choose **Create web ACL**\.

3. For **Name**, enter your Web ACL name.

4. For **Resource type**, choose **Regional resources** as the category of AWS resource that you want to associate with this web ACL.

5. Choose the **region** of your API gateway.

6. For **Associated AWS resources \- optional**, choose **Add AWS resources**\. In the dialog box, choose your API gateway, and then choose **Add**.

7. Choose **Next**\.

We would like now to create a rule that deny all access to the API gateway except requests originated from CloudFront. We achieve that by defining a custom `X-Origin-Verify` header containing a secret value.

8. On the **Add rules and rule groups** page, choose **Add rules**, and then choose **Add my own rules and rule groups**\.

   1. Choose the **Rule builder** rule type.

   2. For **Name**, enter a name such `verify-origin` or something similar.
   3. For **Statement** choose the **Single header** inspection component.
   4. **Header field name** will be `X-Origin-Verify` and define exactly match criteria to some secret value, e.g. `BYKSBttvxM0BM4m5yXYk9iyDvfEU9kHI`.
   5. In **Action** choose **Allow** to allow only requests with the appropriate `X-Origin-Verify` header and value.
   6. Choose **Add rule**\.

9. Choose **Block** as the default action for the web ACL.

10. For all next steps, choose **Next**, check over your definitions, and choose **Create web ACL**\.

### Add the `X-Origin-Verify` header to CloudFront

You can configure CloudFront to add custom headers to the requests that it sends to your origin.

1. In the [CloudFront console](https://console.aws.amazon.com/cloudfront/).
2. Choose your distribution.
3. On the **Origin** tab, choose the single existed origin and click **Edit**.
4. Under **Add custom header** and the header corresponding to the header WAF expected: `X-Origin-Verify: BYKSBttvxM0BM4m5yXYk9iyDvfEU9kHI`
5. Click **Save changes**.


### Associate the WAF with the API gateway

1. Sign in to the API Gateway console at [https://console\.aws\.amazon\.com/apigateway](https://console.aws.amazon.com/apigateway)\.

2. In the **APIs** navigation pane, choose the API, and then choose **Stages**\.

3. In the **Stages** pane, choose the name of the stage (prod).

4. In the **Stage Editor** pane, choose the **Settings** tab\.

5. To associate a Regional web ACL with the API stage:

   1. In the AWS WAF web ACL dropdown list, choose the Regional web ACL that you want to associate with this stage\.

6. Choose **Save Changes**\.

## Testing the API

Test that your API is accessible through CloudFront but not directly through its endpoint.

## SQL-injection prevention using WAF

AWS WAF can be used to mitigate the risk of vulnerabilities such as SQL Injection, Distributed denial of service (DDoS) and other common attacks.
An SQL Injection attack consists of insertion of an SQL query via the input data to the application. A successful SQL injection exploit can be capable or reading sensitive data from a database, or in extreme cases data modification/deletion.

Our current API retrieves data from RDS for MySQL and relies on the user interacting via CloudFront.
However, it is still possible for malicious SQL code to be injected into a web request, which could result in unwanted data extraction.

As a simple example, simply add `or 1=1` at the end of your CloudFront domain name as shown:

`curl -H 'content-type: application/json' <CloudFrontURL>/tweets?username=bla%27%20or%20username%21%3D%27`


### Protect the API gateway from SQL injection using WAF

1. Sign in to the AWS Management Console and open the AWS WAF console at [https://console\.aws\.amazon\.com/wafv2/](https://console.aws.amazon.com/wafv2/).

2. Choose **Web ACLs** in the navigation pane, and then choose **Create web ACL** (a new WAF!).

3. For **Name**, enter your Web ACL name.

5. For **Resource type**, choose **CloudFront distributions** as the category of AWS resource that you want to associate with this web ACL.

6. For **Associated AWS resources \- optional**, choose **Add AWS resources**\. In the dialog box, choose your CloudFront distribution, and then choose **Add**.

7. Choose **Next**\.

8. add managed rule groups, on the **Add rules and rule groups** page, choose **Add rules**, and then choose **Add managed rule groups**\. Do the following for each managed rule group that you want to add:

   1. On the **Add managed rule groups** page, expand the **AWS managed rule groups**.

   2. Turn on the **SQL database** toggle in the **Action** column\.

   3. Choose **Add rules** to finish adding managed rules and return to the **Add rules and rule groups** page\.

11. Choose **Allow** as the default action for the web ACL.
10. For all next steps, choose **Next**, check over your definitions, and choose **Create web ACL**\.

### Associate the WAF with your CloudFront distribution

1. In the [CloudFront console](https://console.aws.amazon.com/cloudfront/), choose your distribution.
2. Under **General** tab, click the **Edit** button in **Settings** section.
3. Under **AWS WAF web ACL - optional** choose the WAF you've just created.
4. Choose **Save changes**.

[aws_api-lambda-1]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/aws_api-lambda-1.png
[aws_api-lambda-2]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/aws_api-lambda-2.png