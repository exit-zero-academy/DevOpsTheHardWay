# VPC Tutorial

#

2 public subnets in different az


## VPC with a 2 public and private subnet

![publicVPC][networking_project_vpc1]

The configuration for this network includes the following:
+ A virtual private cloud \(VPC\) with a size /16 IPv4 CIDR block: `10.2.0.0/16`. This provides 65,536 private IPv4 addresses\.
+ A subnet with a size /24 IPv4 CIDR block: `10.0.0.0/24`. This provides 256 private IPv4 addresses\.
+ An internet gateway\. This connects the VPC to the internet and to other AWS services\.
+ An instance with a private IPv4 address in the subnet range, which enables the instance to communicate with other instances in the VPC, and a public IPv4 address which enables the instance to connect to the internet and to be reached from the internet\.
+ A custom route table associated with the subnet\. The route table entries enable instances in the subnet to use IPv4 to communicate with other instances in the VPC, and to communicate directly over the internet\. A subnet that's associated with a route table that has a route to an internet gateway is known as a *public subnet*\.


### Create a VPC

1. Open the Amazon VPC console at [https://console\.aws\.amazon\.com/vpc/](https://console.aws.amazon.com/vpc).

2. In the navigation pane, choose **Your VPCs**, **Create VPC**\.

3. Under **Resources to create**, choose **VPC only**\.

4. Specify the following VPC details\.
    + **Name tag**: Provide a name for your VPC\. Doing so creates a tag with a key of `Name` and the value that you specify\.
    + **IPv4 CIDR block**: Specify an IPv4 CIDR block of `10.0.0.0/16` for your VPC\. The CIDR block size must have a size between /16 and /28\. More information can be found in [RFC 1918](http://www.faqs.org/rfcs/rfc1918.html).

    + **Tenancy**: Choose the default tenancy option for this VPC\.
        + **Default** ensures that EC2 instances launched in this VPC use the EC2 instance tenancy attribute specified when the EC2 instance is launched\.
        + **Dedicated** ensures that EC2 instances launched in this VPC are run on dedicated tenancy instances regardless of the tenancy attribute specified at launch\.

5. Choose **Create VPC**\.


### Create a subnet in your VPC

To add a new subnet to your VPC, you must specify an IPv4 CIDR block for the subnet from the range of your VPC\. You can specify the Availability Zone in which you want the subnet to reside\. You can have multiple subnets in the same Availability Zone\.

1. In the navigation pane, choose **Subnets**\.

2. Choose **Create subnet**\.

3. For **VPC ID**: Choose the VPC for the subnet\.

4. For **Subnet name**, enter a name for your subnet\. Doing so creates a tag with a key of `Name` and the value that you specify\.

5. For **Availability Zone**, you can choose a Zone for your subnet, or leave the default **No Preference** to let AWS choose one for you\.

6. For **IPv4 CIDR block**, enter an IPv4 CIDR block for your subnet\: `10.0.0.0/24`\.

7. Choose **Create subnet**\.

### Create a custom route table

1. In the navigation pane, choose **Route Tables**\.

2. Choose **Create route table**\.

3. For **Name tag**, enter a name for your route table\.

4. For **VPC**, choose your VPC\.

5. Choose **Create**\.


### Create and attach an internet gateway

After you create an internet gateway, attach it to your VPC\.

**To create an internet gateway and attach it to your VPC**

1. In the navigation pane, choose **Internet Gateways**, and then choose **Create internet gateway**\.

2. Name your internet gateway\.

3. Choose **Create internet gateway**\.

4. Select the internet gateway that you just created, and then choose **Actions, Attach to VPC**\.

5. Select your VPC from the list, and then choose **Attach internet gateway**\.


### Add Internet Gateway as a target in a custom route table

When you create a subnet, we automatically associate it with the main route table for the VPC\. By default, the main route table doesn't contain a route to an internet gateway\. The following procedure uses your custom route table and creates a route that sends traffic destined outside the VPC to the internet gateway, and then associates it with your subnet\.

1. Select the custom route table that you just created\. The details pane displays tabs for working with its routes, associations, and route propagation\.

2. On the **Routes** tab, choose **Edit routes**, **Add route**, and add the following routes as necessary\. Choose **Save changes** when you're done\.
    + For IPv4 traffic, specify `0.0.0.0/0` in the **Destination** box, and select the internet gateway ID in the **Target** list\.

3. On the **Subnet associations** tab, choose **Edit subnet associations**, select the check box for the subnet, and then choose **Save associations**\.


### Test your VPC

Create an EC2 instance within your VPC, connect to it and access the internet.


## VPC with public and private subnets with NAT gateway

![publicVPC][vpc2]


This architecture is suitable if you want to run a public-facing web application, while maintaining back-end servers that aren't publicly accessible.
A common example is web servers in a public subnet and the database in a private subnet.
You can set up security and routing so that the web servers can communicate with the database servers.

The instances in the public subnet can send outbound traffic directly to the internet, whereas the instances in the private subnet can't.
Instead, the instances in the private subnet can access the internet by using a network address translation (NAT) gateway that resides in the public subnet.
The database can connect to the internet for software updates using the NAT gateway, but the internet cannot establish connections to the database.


The configuration for this scenario includes the following:
+ A VPC with a size /16 IPv4 CIDR block: 10\.0\.0\.0/16\. This provides 65,536 private IPv4 addresses\.
+ A public subnet with a size /24 IPv4 CIDR block: 10\.0\.0\.0/24\. This provides 256 private IPv4 addresses\. A public subnet is a subnet that's associated with a route table that has a route to an internet gateway\.
+ A private subnet with a size /24 IPv4 CIDR block: 10\.0\.1\.0/24\. This provides 256 private IPv4 addresses\.
+ An internet gateway\. This connects the VPC to the internet and to other AWS services\.
+ A NAT gateway with its own Elastic IP address\. Instances in the private subnet can send requests to the internet through the NAT gateway over IPv4 \(for example, for software updates\)\.
+ A custom route table associated with the public subnet\. This route table contains an entry that enables instances in the subnet to communicate with other instances in the VPC, and an entry that enables instances in the subnet to communicate directly with the internet over IPv4\.
+ The main route table associated with the private subnet\. The route table contains an entry that enables instances in the subnet to communicate with other instances in the VPC, and an entry that enables instances in the subnet to communicate with the internet through the NAT gateway.


### Create another subnet

As per the above section, create another subnet within your VPC with CIDR block of `10\.0\.1\.0/24`. This subnet should be associated with the main route table.

### Create and attach a NAT gateway

NAT Gateway must be associated with an Elastic IP Address (static IP reservation service of AWS)

### Allocate an Elastic IP Address


1. Open the Amazon EC2 console at [https://console\.aws\.amazon\.com/ec2/](https://console.aws.amazon.com/ec2/)\.

2. In the navigation pane, choose **Network & Security**, **Elastic IPs**\.

3. Choose **Allocate Elastic IP address**\.

4. For **Public IPv4 address pool**, choose **Amazon's pool of IPv4 addresses**

5. Add a **Name** tag\.

6. Choose **Allocate**\.

### Create a NAT Gateway


1. Open the Amazon VPC console at [https://console\.aws\.amazon\.com/vpc/](https://console.aws.amazon.com/vpc/)\.

2. In the navigation pane, choose **NAT Gateways**\.

3. Choose **Create NAT Gateway** and do the following:

    1. Specify a name for the NAT gateway\. This creates a tag where the key is **Name** and the value is the name that you specify\.

    2. Select the subnet in which to create the NAT gateway\.

    3. For **Connectivity type**, select **Public** \(the default\) to create a public NAT gateway\.

    4. For **Elastic IP allocation ID**, select the Elastic IP address to associate with the NAT gateway\.

    5. Choose **Create a NAT Gateway**\.

### Add NAT Gateway as a target in the main route table

1. Select the main route table of your VPC\. The details pane displays tabs for working with its routes, associations, and route propagation\.

2. On the **Routes** tab, choose **Edit routes**, **Add route**, and add the following routes as necessary\. Choose **Save changes** when you're done\.
    + For IPv4 traffic, specify `0.0.0.0/0` in the **Destination** box, and select your NAT gateway ID in the **Target** list\.


**Please delete the NAT gateway when done**

# Exercises

### :pencil2: VPC peering 

Can be done in pairs.

A VPC peering connection is a networking connection between two VPCs that enables you to route traffic between them privately.
Resources in peered VPCs can communicate with each other as if they are within the same network. You can create a VPC peering connection between your own VPCs, with a VPC in another AWS account, or with a VPC in a different AWS Region. Traffic between peered VPCs never traverses the public internet.

![][vpc_peering]

Follow AWS documentation on VPC peering (https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) to create a simulated networking scenario. 

### :pencil2: Create a flow log that publishes to Amazon S3

VPC Flow Logs is a feature that enables you to capture information about the IP traffic going to and from network interfaces in your VPC. Flow log data can be published to the following locations: Amazon CloudWatch Logs, Amazon S3, or Amazon Kinesis Data Firehose. 

https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-s3.html
 

### :pencil2: Create a VPC endpoint to access CloudWatch

https://docs.aws.amazon.com/vpc/latest/privatelink/getting-started.html



[networking_project_vpc1]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/networking_project_vpc1.png
[vpc2]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/vpc2.png
[vpc_peering]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/vpc_peering.png