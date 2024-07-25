# Terraform Modules

## Modules

Modules help you to package and reuse Terraform resources and configurations.
A modules is a collection of `.tf` files, kept together in a folder to be used for multiple resources.


## Example: using the AWS VPC module

Let's say you want to provision a VPC in your AWS account.

A complete VPC requires provisioning of many different resources (VPC, subnet, route table, gateways, etc..). 
But someone already done it before, why not using her work? 

To use a [VPC module](https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws), add the below block into your `main.tf` file to use the VPC module:

```terraform
module "netflix_app_vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.1"

  name = "<your-vpc-name>"
  cidr = "10.0.0.0/16"

  azs             = ["<az1>", "<az2>", "..."]
  private_subnets = ["<pr-subnet-CIDR-1>", "<pr-subnet-CIDR-2>"]
  public_subnets  = ["<pub-subnet-CIDR-1>", "<pub-subnet-CIDR-2>"]

  enable_nat_gateway = false

  tags = {
    Env         = var.env
  }
}
```

Make sure you specify a list of `azs` (availability zones), VPC name `<your-vpc-name>`, and subnets CIDRs (`<pr-subnet-CIDR-1>`...) according to your region.

Before you apply, you have to `terraform init` your workspace first in order to download the module files. 

Apply and inspect your VPC in AWS Console.

How does it work? 

A module is essentially a folder containing Terraform configuration files (after `terraform init` you'll find the files under `.terraform/modules/netflix_app_vpc`).
The module used in this example, contains configuration files to build a generic VPC in AWS.

By using the `module` block (as you've done), your provide your own values to the module's configuration files, like CIDRs, number of subnets, etc.
Every entry in the `module.netflix_app_vpc` block (e.g. `name`, `cidr`, `azs` etc...) is actually **defined as a variable** in the module directory (can be found under `.terraform/modules/netflix_app_vpc/variables.tf`).
So, when you apply, Terraform actually taking the entries from the `module` block and assign the values to the corresponding variables in the module files. 

To review the full list of possible input entries, visit the [Terraform Registry page for the VPC module](https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws).

### Outputs

The next obvious step is to migrate our `aws_instance.netflix_app` instance within the created VPC. 

To do so, add the following property to the `aws_instance.netflix_app` resource:

```diff
+ subnet_id   = module.netflix_app_vpc.public_subnets[0]
```

As can be seen, we used `module.netflix_app_vpc.vpc_id` is a reference the VPC id created by our module. 

The `module.netflix_app_vpc.vpc_id` attribute is known as a module **output**. 
After Terraform applies the configuration, the outputs from the module can be used in other resources in your configuration files.

In you take a closed look in `.terraform/modules/netflix_app_vpc/outputs.tf`, you'll see how outputs are defined:

```terraform 
output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.this[0].id
}
```

To create your security group within your VPC, add the following property to the `aws_security_group.netflix_app_sg` resource:

```diff
+ vpc_id      = module.netflix_app_vpc.vpc_id
```

[Terraform Output](https://developer.hashicorp.com/terraform/language/values/variables) allows you to export structured data about your resources,
Either to share data from a child module to your root module (as in our case), or to be used in other parts of your system. 


> [!NOTE] 
> Every Terraform project has at least one module, known as its **root module**, which consists of the resources defined in the `.tf` files in the main working directory.


### Data Sources

Data sources allow Terraform to use information defined outside your configuration files.
A data sources fetches information from cloud provider APIs, such as disk image IDs, availability zones etc...

You will use the [`aws_availability_zones`](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/availability_zones) data source (which is part of the AWS provider) to configure your VPC's Availability Zones (AZs) dynamically according to the region you work on.
That way you can make your configuration files more modular, since AZs values would not be hard-coded, but fetched dynamically. 

List the AZs which can be accessed by an AWS account within the region configured in the provider.

```terraform
data "aws_availability_zones" "available_azs" {
  state = "available"
}
```

Change the following attribute in `netflix_app_vpc` module:

```text
- azs             = ["<az1>", "<az2>", ...]
+ azs             =data.aws_availability_zones.available_azs.names
```

Plan and apply.


The `aws_instance.netflix_app` configuration also uses a hard-coded AMI ID, which is only valid for the specific region. 
Use an `aws_ami` data source to load the correct AMI ID for the current region.

Add the following `aws_ami` data source to fetch AMIs from AWS API:

```terraform
data "aws_ami" "ubuntu_ami" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical owner ID for Ubuntu AMIs

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}
```

Replace the hard-coded AMI ID with the one loaded from the new data source.

```text
-  ami = "<your-hard-coded-ami>"
+  ami = data.aws_ami.ubuntu_ami.id
```

Add the following output in `outputs.tf`:

```text
output "netflix_app_ami" {
  description = "ID of the EC2 instance AMI"
  value       = data.aws_ami.amazon_linux_ami
}
```

Plan and apply.


# Exercises 

### :pencil2: Build the Netflix app module

In this exercise, you will create a Terraform module to provision the infrastructure required to deploy the Netflix app. (EC2 instances, security groups, VPCs, S3 buckets, and key pairs)

In the root directory of your Terraform project create the following file structure: 

```text
modules/
└── netflix-app/
     ├── main.tf
     ├── variables.tf
     ├── outputs.tf
     └── deploy.sh
```

The module should receive the following inputs:

- `aws_region`
- `vpc_cidr`
- `subnet_cidr`
- `availability_zone`
- `ami_id`
- `instance_type`
- `key_name`
- `public_key_path`
- `bucket_name`

The module should provide the following outputs: 

- `instance_id`
- `bucket_name`

Example for usage from `main.tf` of the root module:

```terraform
module "netflix_app" {
  source = "./modules/netflix-app"

  aws_region         = "us-west-2"
  vpc_cidr           = "10.0.0.0/16"
  subnet_cidr        = "10.0.1.0/24"
  availability_zone  = "us-west-2a"
  ami_id             = "ami-0123456789abcdef0"
  instance_type      = "t2.micro"
  key_name           = "my-key-pair"
  public_key_path    = "~/.ssh/id_rsa.pub"
  bucket_name        = "my-netflix-app-bucket"
}
```

### :pencil2: Build cloud agnostic app 

Let's say you have to be able to launch your app in **different clouds** (AWS, Azure, GCP). 
For simplicity, assume that all your cloud infrastructure is a single VM.  
How can you utilize Terraform modules to create cloud-agnostic configurations? 

Here's an example that demonstrates how to achieve this.

Create the following dir structure:

```text
cloud-vm/
├── modules/
│   ├── aws/
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   ├── variables.tf
│   ├── gcp/
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   ├── variables.tf
├── main.tf
├── outputs.tf
├── providers.tf
├── variables.tf
```

The `main.tf` and `providers.tf` **skeletons** may look like:

```terraform
# main.tf

module "vm" {
  source = "./modules/${var.cloud_provider}"
  
  vm_name = var.vm_name
  vm_size = var.vm_size
  region  = var.region
}
```

And 

```terraform
# providers.tf

provider "aws" {
  region = var.region
}

provider "google" {
  project = var.project_id
  region  = var.region
}
```

And applying the infrastructure is a certain cloud cab ne done by: 

```bash
terraform init
terraform apply -var="cloud_provider=aws" -var="region=us-east-1"
```

Complete the remaining configuration files and make it work (since we don't have a GCP account, no need to apply there).

