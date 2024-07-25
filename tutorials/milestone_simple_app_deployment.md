# Deploy the NetflixMovieCatalog in virtual machine in AWS

1. In our shared AWS account, create an EC2 instance.
2. Run the `netflixmoviecatalog` within your instance (install dependencies if needed).
3. [Register a real domain using Route53](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/domain-register.html) (choose `.click` which is the cheapest). After registering your domain, in the domain's **Hosted Zone** (which represents your authoritative server), create an A record to your instance IP.
4. Make your server accessible via **HTTPS only** by using **self-signed certificate**.
5. as a service, venv.
