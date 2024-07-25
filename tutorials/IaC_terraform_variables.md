# Terraform variables

## Backend configurations

Let's store the `terraform.state` file in an appropriate place: a dedicated S3 bucket.

A **Backend** defines where Terraform stores its [state](https://www.terraform.io/language/state) data files.
This lets multiple people access the state data and work together on that collection of infrastructure resources.
When changing backends, Terraform will give you the option to **migrate** your state to the new backend. 
This lets you adopt backends without losing any existing state.

Always backup your state by enable bucket versioning!

1. Create a dedicated S3 bucket to store your state files. 
2. To configure a backend, add a nested `backend` block within the top-level `terraform` block. The following example configures the `s3_backend` backend:
   ```terraform
   terraform {
   
     ...
    
     backend "s3" {
       bucket = "<bucket-name>"
       key    = "tfstate.json"
       region = "<bucket-region>"
       # optional: dynamodb_table = "<table-name>"
     }
   
     ...
   
   }
   ```
2. Apply the changes and make sure the state is stored in S3.

This backend also supports state locking and consistency checking via Dynamo DB, which can be enabled by setting the `dynamodb_table` field to an existing DynamoDB table name.
The table must have a partition key named `LockID` with type of `String`.

## Variables

So far, the `main.tf` configuration file included some hard-coded values.
[Terraform variables](https://developer.hashicorp.com/terraform/language/values/variables) allow you to write configuration that is flexible and easier to re-use for different environments and potentially different regions.

Our goal is to provision our EC2 instance (and the other resources you've created last tutorial) for different environments and AWS regions. 

1. In the workspace repo, create a new file called `variables.tf` with blocks defining the following variables: 
   ```terraform
   variable "env" {
      description = "Deployment environment"
      type        = string
   }

   variable "region" {
      description = "AWS region"
      type        = string
   }
   
   variable "ami_id" {
      description = "EC2 Ubuntu AMI"
      type        = string
   }
   ```
2. In `main.tf`, update the `aws_instance.netflix_app` resource block to use the new variable.
   ```diff
   resource "aws_instance" "netflix_app" {
   -  ami           = "<ec2-ami>"
   +  ami           = var.ami_id
     instance_type = "t2.micro"
   
     tags = {
   -    Name = "<instance-name>"
   +    Name = "<instance-name>-${var.env}"
     }
   }
   ```
   
   In addition, update the `provider` block, as follows:

   ```diff
   provider "aws" {
   -  region  = "<aws-region>"
   +  region  = var.region
   }   
   ```

3. Plan and apply the configurations by:

   ```bash
   terraform apply -var region=<your-region-code-value> -var ami_id=<your-ubuntu-ami-id> -var env=dev
   ```
   
   While changing `<your-region-code-value>` and `<your-ubuntu-ami-id>` according to your values.

## The `tfvars` file

As you can imagine, a typical Terraform project has many variables.
Should we use the `-var` flag in the `terraform apply` command to set each one of the variable values? 
No, that's where the `.tfvars` file comes in. 

This file holds the **values** for the variables, while `variables.tf` **defines** what the variables are.

1. Create the `region.<aws-region-code>.dev.tfvars` (while changing `<aws-region-code>` to your current AWS region. E.g. `region.us-east-1.dev.tfvars`), as follows:

   ```text
   env = dev
   region = <aws-region-code>
   ami_id = <your-ubuntu-ami-id>
   ```
2. Now you can apply the configurations by:
   ```bash
   terraform apply -var-file region.<aws-region-code>.dev.tfvars
   ```
   
3. Now create `.tfvars` file with corresponding values per environment, per region. For example: 

   ```text
   my_tf_repo/
   ├── main.tf                         # Main configuration file
   ├── variables.tf
   ├── region.us-east-1.dev.tfvars         # Values related for us-east-1 region
   └── region.eu-central-1.prod.tfvars      # Values related for eu-central-1 region
   ```

Soon you'll see how to use it properly.

## Terraform workspaces 

How can the same configuration files be applied for multiple AWS regions?
Obviously, each region or environment should have a separate `.tfstate` file for storing state data (why???).

[Terraform workspaces](https://developer.hashicorp.com/terraform/cli/workspaces) can help you to easily manage multiple sets of resources, originated from the same `.tf` configuration files.

All you have to do it to create a workspace per region, per env. For example:

```bash
terraform workspace new us-east-1.dev
```

And once you want to apply the configuration in us-east-1, dev, perform:

```bash
terraform workspace select us-east-1.dev
terraform apply -var-file region.us-east-1.dev.tfvars
```

**Note**: The `tfstate` files of all regions will be stored in the same S3 bucket.

1. Create a dedicated workspace per region-env.
2. Apply the configurations. 
3. Take a look on the separated `.tfstate` files in the S3 bucket.


## Secrets and sensitive data

How can Terraform handle sensitive data? 

Let's say you want to create a secret in [AWS Secret Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html):

```terraform 
resource "aws_secretsmanager_secret" "bot_token" {
  name = "<my-secret-name>"
}

resource "aws_secretsmanager_secret_version" "bot_token" {
  secret_id     = aws_secretsmanager_secret.example.id
  secret_string = "1234528664:AAEUHt47XsoPkQRqIBA0EYxaEGQdKtGoLtM"
}
```

Obviously, this above configurations can't be committed as part of your source code. 
For that, you'll utilize [Sensitive variables](https://developer.hashicorp.com/terraform/tutorials/configuration-language/sensitive-variables)


```terraform 
variable "secret_name" {
  description = "The name of the secret"
  type        = string
  default     = "<my-secret-name>"
}

variable "secret_value" {
  description = "The value of the secret"
  type        = string
  sensitive   = true
}


resource "aws_secretsmanager_secret" "bot_token" {
  name = var.secret_name
}

resource "aws_secretsmanager_secret_version" "bot_token" {
  secret_id     = aws_secretsmanager_secret.example.id
  secret_string = var.secret_value
}
```

If you were to run terraform apply now, Terraform would prompt you for value for the `aws_secretsmanager_secret_version.bot_token` variable since you haven't assigned any value.

But sometimes you can't enter the value manually (E.g. as part of a CI/CD automation). 
So you use the `-var` flag: `terraform apply -var="secret_value=1234528664:AAEUHt47XsoPkQRqIBA0EYxaEGQdKtGoLtM"`.

# Exercises 

### :pencil2: Simple CI/CD pipeline for Terraform 

1. In your repo, under `.github/workflows/infra.yaml`, create a simple GitHub Actions workflow YAML. 
2. Configure the pipeline to provision the infrastructure in different regions and environments upon every commit and push of changes to the configuration files. 
3. Test your pipelines. 


