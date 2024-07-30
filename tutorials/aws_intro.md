# Amazon Web Services (AWS) - Intro to Cloud Computing

Cloud computing is a technology that allows businesses and individuals to access and use computing resources over the internet, without the need for owning or maintaining physical hardware. 
Amazon Web Services (AWS) is a leading provider of cloud computing services, offering a wide range of tools and platforms that enable businesses to deploy, scale, and manage their applications and data in the cloud.
With AWS, organizations can benefit from the flexibility, scalability, and cost-effectiveness of cloud computing, while focusing on their core business objectives.

## Region and Zones

AWS operates state-of-the-art, highly available data centers. Although rare, failures can occur that affect the availability of instances that are in the same location. If you host all of your instances in a single location that is affected by a failure, none of your instances would be available.

Each **Region** is designed to be isolated from the other Regions. This achieves the greatest possible **fault tolerance** and **stability**.

Here are a few available regions of AWS:

| Code           | Name                    |
|----------------|-------------------------|
| `us-east-2`    | US East (Ohio)          |
| `us-east-1`    | US East (N. Virginia)   |
| `us-west-1`    | US West (N. California) |
| `us-west-2`    | US West (Oregon)        |
| `eu-west-1`    | 	Europe (Ireland)       |
| `eu-central-1` | 	Europe (Frankfurt)     |
| `eu-north-1`   | 	Europe (Stockholm)     |

Each Region has multiple, isolated locations known as **Availability Zones**. The code for Availability Zone is its Region code followed by a letter identifier. For example, `us-east-1a`.

## SLA

AWS Service Level Agreements (**SLA**) are commitments made by AWS to its customers regarding the availability and performance of its cloud services.
SLAs specify the percentage of uptime that customers can expect from AWS services and the compensation they can receive if AWS fails to meet these commitments.
AWS offers different SLAs for different services, and the SLAs can vary based on the region and the type of service used. AWS SLAs provide customers with a level of assurance and confidence in the reliability and availability of the cloud services they use.

For more information, [here](https://aws.amazon.com/legal/service-level-agreements/?aws-sla-cards.sort-by=item.additionalFields.serviceNameLower&aws-sla-cards.sort-order=asc&awsf.tech-category-filter=*all).

## Launch a virtual machine (EC2 instance) 

Amazon EC2 (Elastic Compute Cloud) is a web service that provides resizable compute capacity in the cloud. 
It allows users to create and manage virtual machines, commonly referred to as "instances", which can be launched in a matter of minutes and configured with custom hardware, network settings, and operating systems.

![][networking_project_stop]

1. Open the Amazon EC2 console at [https://console\.aws\.amazon\.com/ec2/](https://console.aws.amazon.com/ec2/).

2. From the EC2 console dashboard, in the **Launch instance** box, choose **Launch instance**, and then choose **Launch instance** from the options that appear\.

3. Under **Name and tags**, for **Name**, enter a descriptive name for your instance\.

4. Under **Application and OS Images \(Amazon Machine Image\)**, do the following:

   1. Choose **Quick Start**, and then choose **Ubuntu**\. This is the operating system \(OS\) for your instance\.
   
5. Under **Instance type**, from the **Instance type** list, you can select the hardware configuration for your instance\. Choose the `t2.nano` instance type (the cheapest one). In Regions where `t2.nano` is unavailable, you can use a `t3.nano` instance.

6. Under **Key pair \(login\)**, choose **create new key pair** the key pair that you created when getting set up\.

   1. For **Name**, enter a descriptive name for the key pair\. Amazon EC2 associates the public key with the name that you specify as the key name\.

   2. For **Key pair type**, choose either **RSA**.

   3. For **Private key file format**, choose the format in which to save the private key\. Since we will use `ssh` to connect to the machine, choose **pem**.

   4. Choose **Create key pair**\.
   
     **Important**  
     This step should be done once! once you've created a key-pair, use it for every EC2 instance you are launching. 

   5. The private key file is automatically downloaded by your browser\. The base file name is the name you specified as the name of your key pair, and the file name extension is determined by the file format you chose\. Save the private key file in a **safe place**\.
      
      **Important**  
      This is the only chance for you to save the private key file\.

   6. Your private key file has to have permission of `400`, `chmod` it if needed.

7. Next to **Network settings**, choose **Edit**\. 

   1. For **VPC** choose the default VPC fo your region.
   2. For **Subnet** choose any subnet you want. 
   3. Choose **Create security group** while providing a name other than `launch-wizard-x`. 

8. Keep the default selections for the other configuration settings for your instance\.

9. Review a summary of your instance configuration in the **Summary** panel, and when you're ready, choose **Launch instance**\.

10. A confirmation page lets you know that your instance is launching\. Choose **View all instances** to close the confirmation page and return to the console\.

11. On the **Instances** screen, you can view the status of the launch\. It takes a short time for an instance to launch\. When you launch an instance, its initial state is `pending`\. After the instance starts, its state changes to `running` and it receives a public DNS name\.

12. It can take a few minutes for the instance to be ready for you to connect to it\. Check that your instance has passed its status checks; you can view this information in the **Status check** column\.

> [!NOTE]
> When stopping the instance, please note that the public IP address may change, while the private IP address remains unchanged


To connect to your instance, open the terminal in your local machine, and connect to your instance by: 

```shell
ssh -i "</path/key-pair-name.pem>" ubuntu@<instance-public-dns-name-or-ip>
```

Try to `ping` the instance from your local machine. Having troubles?
Note that by default, the only allowed inbound traffic to an EC2 instance is port 22 (why?).
[Take a look here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/authorizing-access-to-an-instance.html#add-rule-authorize-access) to know how to allow inbound traffic for different ports. 


[networking_project_stop]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/networking_project_stop.gif