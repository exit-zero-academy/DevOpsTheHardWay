# Route 53

Amazon Route 53 is a scalable and highly available DNS web service that serves as the authoritative DNS server for your domains, allowing you to manage DNS records. 
It also offers domain registration services, enabling you to purchase and manage domain names directly within AWS.

![][aws_route_53_dns]

## Registering a domain 

Throughout the course, you'll be using a real registered domain to manage and access the services that you'll deploy in the cloud.

> [!NOTE]
> If you already have a registered domain, read here how to [make Route 53 the DNS service for an existing domain](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/MigratingDNS.html) and skip the next section.

1. Sign in to the AWS Management Console and open the Route 53 console at https://console.aws.amazon.com/route53/
1. In the navigation pane, choose **Domains** and then **Registered domains**.
1. On the **Registered domains** page, choose **Register domains**.

   In the **Search for domain** section, enter the domain name that you want to register, and choose **Search** to find out whether the domain name is available.

   If you're using your domain just for learning and want to keep costs low, .click or .link are some of the cheapest TLDs, costing about $3-5 per year. [Take ta look here for a full pricing list](https://d32ze2gidvkk54.cloudfront.net/Amazon_Route_53_Domain_Registration_Pricing_20140731.pdf).
       
1. Choose **Proceed to checkout**.
1. On the **Pricing** page, choose the number of years that you want to register the domain for (1 year should be enough) and make sure the auto-renewal is disabled.
1. Choose **Next**.
1. On the **Contact information** page, enter contact information for the domain registrant, admin, tech, and billing contacts.
1. Choose **Next**.
1. On the **Review** page, review the information that you entered, and optionally correct it, read the terms of service, and select the check box to confirm that you've read the terms of service.
1. Choose **Submit**.
1. In the navigation pane, choose **Domains** and then **Requests**.
   - On this page you can view the status of domain. You need to respond to registrant contact verification email. You can also choose to resend the verification email.
   - When you receive the verification email, choose the link in the email that verifies that the email address is valid. If you don't receive the email immediately, check your junk email folder.

When domain registration is complete, go to next section. 

 

## Add records to registered domain

When registered your domain, Route 53 created a **Hosted Zone**. 

A hosted zone in Amazon Route 53 is a container for DNS records associated with a domain, effectively acting as the **authoritative server** for that domain.
It enables you to manage how traffic is routed to your resources by defining various record types, such as A and CNAME records.

1. In the navigation pane, choose **Hosted zones**\.

2. Choose the hosted zone associated with your domain.

3. Choose **Create record**\.

4. Define an A record for a custom sub-domain of yours (e.g. `my-name.mydomain.com`), the record value is an IP address of your EC2 instance created in a previous tutorial [^1]. 

5. Choose **Create records**\.   
   **Note**  
   Your new records take time to propagate to the Route 53 DNS servers



[aws_route_53_dns]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/aws_route_53_dns.png


[^1]: EC2 instance deployed in [Intro to cloud computing](aws_intro.md).