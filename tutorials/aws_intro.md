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

