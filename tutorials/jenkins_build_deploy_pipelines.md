# Jenkins Pipelines

Jenkins Pipelines enable teams to automate repetitive tasks, and ensure consistent and reliable software releases.

## The `Jenkinsfile`

A Jenkins pipeline is defined in a file usually called `Jenkinsfile`, stored as part of the code repository.
In this file you instruct Jenkins on how to build, test and deploy your application by specifying a series of stages, steps, and configurations.  

There are two main types of syntax for defining Jenkins pipelines in a Jenkinsfile: [Declarative Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/#declarative-pipeline) and [Scripted Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/#scripted-pipeline).

- Declarative syntax is a more structured and easy. It uses a predefined set of functions (a.k.a [directives](https://www.jenkins.io/doc/book/pipeline/syntax/#declarative-directives)) to define the pipeline's structure.
- Scripted syntax provides a more flexible and powerful way to define pipelines. It allows you to use Groovy scripting to customize and control every aspect of the pipeline. This pipelines won't be covered in this course.

The `Jenkinsfile` typically consists of multiple **Stages**, each of which performs a specific **Steps**, such as building the code as a Docker image, running tests, or deploying the software to Kubernetes cluster, etc...

Let's recall the pipeline you've created in the previous exercise (the pipeline will be used to build docker image for the [NetflixFrontend][NetflixFrontend] app).  

```text
// pipelines/build.Jenkinsfile

pipeline {
    agent any
    
    triggers {
        githubPush()
    }

    stages {
        stage('Build app container') {
            steps {
                sh '''
                    # your pipeline commands here....
                    
                    # for example list the files in the pipeline workdir
                    ls 
                    
                    # build an image
                    docker build -t netflix-front .
                '''
            }
        }
    }
}
```

The `Jenkinsfile` is written in a Declarative Pipeline syntax. Let's break down each part of the code:

- `pipeline`: This is the outermost block that encapsulates the entire pipeline definition.
- `agent any`: This directive specifies the [agent](https://www.jenkins.io/doc/book/using/using-agents/) where the pipeline stages will run. The `any` keyword indicates that the pipeline can run on any available agent.
- `stages`: The [stages block](https://www.jenkins.io/doc/book/pipeline/syntax/#stages) contains a series of stages that define the major steps in the pipeline. 
- `stage('Build app container')`: This directive defines a specific stage named "Build app container". Each stage represents a logical phase of your pipeline, such as building, testing, deploying, etc.
- `steps`: Inside the stage block, the [steps block](https://www.jenkins.io/doc/book/pipeline/syntax/#steps) contains the individual steps or tasks to be executed within that stage.
- `sh`: This [sh step](https://www.jenkins.io/doc/pipeline/tour/running-multiple-steps/#linux-bsd-and-mac-os) executes a shell command. 
- `triggers`: specifies the conditions that trigger the pipeline. `githubPush()` triggers the pipeline whenever there is a push to the associated GitHub repository.

## Pipeline execution

This is what happen when your pipeline in being executed:

1. Jenkins schedules the job on one of its available **agents** (also known as nodes). 
2. Jenkins creates a **workspace directory** on the agent's file system. This directory serves as the working area for the pipeline job.
3. Jenkins checks out the source code into the workspace. 
4. Jenkins executes your pipeline script step-by-step. 

## Jenkins credentials 

Jenkins should be provided with different credentials in order to integrate with external systems. 
For example, credentials to push built Docker images to DockerHub, credentials to provision or describe infrastructure in AWS, or credentials to push to GitHub repo. 

Jenkins has a standard place to store credentials which is called the **System Credentials Provider**.  
Credentials stored under this provider usually available at the system level and are not restricted to a specific pipeline, folder, or user.

> [!IMPORTANT]
> Jenkins, as your main CI/CD server, can potentially hold **VERY** sensitive credentials. 
> Not everyone (including myself) will be exposing high value credentials to Jenkins, as the way the data is stored may not meet your organization's security policies.
> 
> Instead of using the **System Credentials Provider**, you can use another provider to connect Jenkins to an external source, e.g. [AWS Secret Manager credentials provider](https://plugins.jenkins.io/aws-secrets-manager-credentials-provider/), or [Kubernetes](https://plugins.jenkins.io/kubernetes-credentials-provider/).

### Create credentials for DockerHub (or ECR)

1. In your Jenkins server main dashboard page, choose **Manage Jenkins**.
2. Choose **Credentials**.
3. Under **Stores scoped to Jenkins**, choose the **System** store (the standard provider discussed above).
4. Under **System**, click the **Global credentials (unrestricted)** domain, then choose **Add credentials**.
5. From the [**Kind** field](https://www.jenkins.io/doc/book/using/using-credentials/#types-of-credentials), choose the **Username and password** type.
6. From the **Scope** field, choose the **Global** scope since this credentials should be used from within a pipeline. 
7. Add the credentials themselves:
   - Your DockerHub username (or your AWS access key id if using ECR)
   - Your DockerHub password or token (or your AWS secret access key if using ECR)
   - Provide a unique ID for the credentials (e.g., `dockerhub`).
8. Click **Create** to save the credentials.

> [!NOTE]
> You might want to install the [AWS Credentials Plugin](https://plugins.jenkins.io/aws-credentials/), which adds support for storing and using AWS credentials in Jenkins.

### Create credentials for GitHub 

Repeat the above steps to create a GitHub credentials: 

- The **Kind** must be **Username and password**.
- Choose **Username** to your choice (it'll not be used...). The **Password** should be a GitHub Personal Access Token with the following scope:
  ```text
  repo,read:user,user:email,write:repo_hook
  ```
  [Click here](https://github.com/settings/tokens/new?scopes=repo,read:user,user:email,write:repo_hook) to create a token with this scope.


## The "Build" pipeline

The process of transforming the app source code into a runnable application is called "Build".
The byproduct of build process is usually known as **Artifact**. 

In our case, the build artifacts are Docker images, ready to be deployed in anywhere. 

> [!NOTE]
> There are many other build tools used in different programming languages and contexts, e.g. [maven](https://www.jenkins.io/doc/tutorials/build-a-java-app-with-maven/#fork-and-clone-the-sample-repository-on-github), `npm`, `gradle`, etc...

We now want to complete the `build.Jenkinsfile` pipeline, such that on every run of this job,
a new docker image of the app will be built and stored in container registry (either DockerHub or ECR).


Here is a skeleton for the `build.Jenkinsfile`. **Carefully** review it, feel free to change according to your needs:  

```text
pipeline {
    agent any
    
    triggers {
        githubPush()   // trigger the pipeline upon push event in github
    }
    
    options { 
        timeout(time: 10, unit: 'MINUTES')  // discard the build after 10 minutes of running
        timestamps()  // display timestamp in console output 
    }
    
    environment { 
        // GIT_COMMIT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        // TIMESTAMP = new Date().format("yyyyMMdd-HHmmss")
        
        IMAGE_TAG = "v1.0.$BUILD_NUMBER"
        IMAGE_BASE_NAME = "netflix-app"
        
        DOCKER_CREDS = credentials('dockerhub')
        DOCKER_USERNAME = "${DOCKER_CREDS_USR}"  // The _USR suffix added to access the username value 
        DOCKER_PASS = "${DOCKER_CREDS_PSW}"      // The _PSW suffix added to access the password value
    } 

    stages {
        stage('Docker setup') {
            steps {             
                sh '''
                  docker login -u $DOCKER_USERNAME -p $DOCKER_PASS
                '''
            }
        }
        
        stage('Build & Push') {
            steps {             
                sh '''
                  IMAGE_FULL_NAME=$DOCKER_USERNAME/$IMAGE_BASE_NAME:$IMAGE_TAG
                
                  docker build -t $IMAGE_FULL_NAME .
                  docker push $IMAGE_FULL_NAME
                '''
            }
        }
    }
}
```

Test your pipeline by commit & push changes and expect a new Docker image to be stored in your container registry. 

### Notes

- We used the `BUILD_NUMBER` [environment variable](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#using-environment-variables) to tag the images, but you can also use the `GIT_COMMIT` or the `TIMESTAMP` env vars for more meaningful tagging. Anyway never use the `latest` tag.
- We added some useful [options](https://www.jenkins.io/doc/book/pipeline/syntax/#options).

## The "Deploy" pipeline

The deploy pipeline deploys the new app version we've just built in the Build pipeline, into your environment. 
There are many ways to implement deployment pipelines, depending on your system (e.g. Kubernetes, AWS Lambda, EC2 instance, etc...).

In our case, we want to deploy our newly created Docker image into our Kubernetes cluster using [ArgoCD](https://argo-cd.readthedocs.io/en/stable/).

In the **NetflixInfra** repo (the dedicated repo you've created for the Kubernetes YAML manifests for the Netflix stack), create another `Jenkinsfile` under `pipelines/deploy.Jenkinsfile`, as follows:

```text
pipeline {
    agent any
    
    parameters { 
        string(name: 'SERVICE_NAME', defaultValue: '', description: '')
        string(name: 'IMAGE_FULL_NAME_PARAM', defaultValue: '', description: '')
    }

    stages {
        stage('Git setup') {
            steps {
                /* 
                Jenkins checks out a specific commit, rather than HEAD of the repo.
                This puts the repo in a "detached" state, which doesn't allow committing and pushing. 
                Thus you have to checkout out the branch explicitly, as below.
                */
                
                sh 'git checkout -b main || git checkout main'
            }
        }
        stage('update YAML manifest') {
            steps {
                /*
                
                Now your turn! implement the pipeline steps ...
                
                - `cd` into the directory corresponding to the SERVICE_NAME variable. 
                - Change the YAML manifests according to the new $IMAGE_FULL_NAME_PARAM parameter.
                  You can do so using `yq` or `sed` command, by a simple Python script, or any other method.
                - Commit the changes 
                   * Setting global Git user.name and user.email in 'Manage Jenkins > System' is recommended.
                   * Setting Shell executable to `/bin/bash` in 'Manage Jenkins > System' is recommended.
                */ 
            }
        }
        stage('Git push') {
            steps {
               // Change `credentialsId` according to the Id you've configured your GitHub token
               withCredentials([
                usernamePassword(credentialsId: 'github', usernameVariable: 'GITHUB_USERNAME', passwordVariable: 'GITHUB_TOKEN')
               ]) {
               
                 sh 'git push https://$GITHUB_TOKEN@github.com/alonitac/NetflixInfra2.git main'
               
               }
            }
        }
        post {
            cleanup {
                cleanWs()
            }
        }
    }
}
``` 

Carefully review the pipeline and complete the step yourself. 

In the Jenkins dashboard, create another Jenkins **Pipeline** (e.g. named `NetflixFrontendDeploy`). Configure it similarly to the Build pipeline - choose **Pipeline script from SCM**, and specify the Git URL, branch, path to the Jenkinsfile, **as well as your created GitHub credentials** (as this pipeline has to push commit on your behalf).  

As can be seen, unlike the Build pipeline, the Deploy pipeline is not triggered automatically upon a push event in GitHub (there is no `githubPush()`...)
but is instead initiated by providing a parameter called `IMAGE_FULL_NAME_PARAM`, which represents the new Docker image to deploy to your Kubernetes cluster. 

Now to complete the Build-Deploy flow, configure the Build pipeline to trigger the Deploy pipeline and provide it with the `IMAGE_FULL_NAME_PARAM` parameter by adding the following stage after a successful Docker image build: 

```diff
stages {

  ...

+ stage('Trigger Deploy') {
+     steps {
+         build job: '<deploy-pipeline-name-here>', wait: false, parameters: [
+             string(name: 'SERVICE_NAME', value: "NetflixFrontend"),
+             string(name: 'IMAGE_FULL_NAME_PARAM', value: "$DOCKER_USERNAME/$IMAGE_BASE_NAME:$IMAGE_TAG")
+         ]
+     }
+ }

}
```

Where `<deploy-pipeline-name-here>` is the name of your Deploy pipeline (should be `NetflixFrontendDeploy` if you followed our example).

Test your simple CI/CD pipeline end-to-end.

## The Build and Deploy phases - overview

![][jenkins_build_deploy]


# Exercises 

### :pencil2: Clean the build artifacts from Jenkins server

Use the [`post` directive](https://www.jenkins.io/doc/book/pipeline/syntax/#post) and the [`docker system prune -a --force --filter "until=24h"` command](https://docs.docker.com/config/pruning) to cleanup the built Docker images and containers from the disk. 

### :pencil2: Clean the workspace after every build 

Jenkins does not clean the workspace by default after a build. 
Jenkins retains the contents of the workspace between builds to improve performance by avoiding the need to re-fetch and recreate the entire workspace each time a build runs.

Cleaning the workspace can help ensure that no artifacts from previous builds interfere with the current build.

Configure `stage('Clean Workspace')` stage to [clean the workspace](https://www.jenkins.io/doc/pipeline/steps/ws-cleanup/) before or after a build. 



[jenkins_build_deploy]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/jenkins_build_deploy.png

