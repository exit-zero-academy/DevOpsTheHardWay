# Artifact manager 

## Motivation

When committing and pushing changes regularly by a large development team, Jenkins can execute hundreds of pipelines jobs every day. 
Every pipeline can potentially download or create some **Artifacts**, i.e. a python package, docker image, AI model binaries, auto-generated configuration files, executable binaries, etc..

Artifact (or **Binary**) is a file, which is downloaded or created during the CI pipeline. 

![][artifacts_nexus2]

We can divide artifacts into two groups - artifacts that you own (e.g. a Docker image you build), and artifacts that you don't own, but your app relies on (e.g. a Docker **base** image that your image rely on).

There are several problems that arise with artifacts you don't own:

- Large artifacts (like Docker base image) should be downloaded from the internet, hence can significantly slowing down the build time.
- Artifacts that we don't own are rich ground for vulnerabilities, which can propagate to production. 
- You can innocently violate software licensing by using artifact that is protected by restricted license.

There are several problems with artifacts that you own:

- How to test and promote an artifact all the way from dev to deploy? 
- How can I control which artifact will be to allow different artifacts to be part lifecycle of 

# Nexus Repository Manager

[Nexus Artifact Manager](https://www.sonatype.com/products/sonatype-nexus-repository) is used to store and manage your artifacts. Here are its key features:

- Can store various types of artifacts, including Maven, PyPi packages, Docker images, Helm charts, and more.
- Acts as a proxy for remote repositories, fetching and caching artifacts from external sources like PyPI (see figure below). This helps improve build speed by reducing the need to download artifacts repeatedly.
- Single source of truth for all environments, including developer's local machine. This ensures that the correct versions of dependencies are used, leading to more reliable builds and deployments.
- Nexus can manage the lifecycle of artifacts, including promote and release versions of your artifacts.
- Nexus provides reporting and monitoring tools to track artifact usage, repository health, vulnerabilities and software licensing violation.

![][artifacts_nexus]

## Installation

We will deploy the Nexus server using a [pre-built Docker image](https://hub.docker.com/r/sonatype/nexus3/) as a Docker Compose project.

```shell
cd nexus_docker
docker compose up
```

## Repository Management

Nexus ships with a great [Official docs](https://help.sonatype.com/repomanager3/nexus-repository-administration/repository-management) and compatible with [many package managers](https://help.sonatype.com/repomanager3/nexus-repository-administration/formats): Java/Maven, npm, NuGet, PyPI, Docker, Helm, Yum, and APT.

### Repository Types

#### Proxy repo

Proxy repository is a repository that is linked to a remote repository. Any request for a component is verified against the local content of the proxy repository. If no local component is found, the request is forwarded to the remote repository.

#### Hosted repo

Hosted repository is a repository that stores components in the repository manager as the authoritative location for these components.

#### Group repo

Repository group allow you to combine multiple repositories and other repository groups in a single repository.
This in turn means that your users can rely on a single URL for their configuration needs, while the administrators can add more repositories and therefore components to the repository group.


## Create a PyPi proxy repo

1. After signing in to your Nexus server as an administrator, click on the **Server configuration** icon אo the left of the search bar.
2. Create a [PyPi proxy repo](https://help.sonatype.com/repomanager3/nexus-repository-administration/formats/pypi-repositories), call it `pypi.org-central`, as it proxies the official https://pypi.org packages index.
3. Open up the [NetflixMovieCatalog][NetflixMovieCatalog] repo, make sure the repo contains a Python virtual environment (a.k.a. venv), and [configure](https://help.sonatype.com/repomanager3/nexus-repository-administration/formats/pypi-repositories#PyPIRepositories-Download,searchandinstallpackagesusingpip) `pip` to download Python packages from your private artifact repository. To do so, create a file in `<venv-dir>/pip.conf` (while `<venv-dir>` is your venv) with the following content:
```text
[global]
trusted-host = localhost:8081
index-url = http://localhost:8081/repository/pypi.org-central/simple
```

5. Install `flask` by `pip install flask`.
6. Make sure you see the package when browsing the repo content by clicking on the **Browse (box)** icon to the left of the search bar. 


## Create a PyPi hosted repo, pack and upload a Python library

Let's say your team develop a Python SDK for the Netflix service, called `PyFlix`. 
The SDK can provide an easy-to-use interface for developers to integrate Netflix services into their Python applications.

Here is an example of how your customers might be using the SDK:

```bash
pip install pyflix
```

And

```python
import pyflix

api_key = 'your_netflix_api_key_here'
client = pyflix.Client(api_key)
search_results = client.search_movies('action')
```

### An overview of packaging for Python

The [PyFlixPythonSDK][PyFlixPythonSDK] repo contains a Python source code for a sample package called `pyflix`.
As you can see, in order to turn python files grouped under the same directory into a Python package, 
we need to add some necessary files and organize directory structure in a specific format.

### Hosted repositories

Staging allows your organization to have some sequence of hosted repositories and move or promote components through those repositories in accordance with your delivery or code promotion process. 
In modern software development, teams test the software before deploying it to a production system.


1. Create a `pypi (hosted)` repo, call it `py-dev` (later on we'll create hosted repositories for `test` and `prod` environments). Keep all default definitions. 

> [!NOTE]
> - Hosted repos which typically host stable and officially released versions of your Python packages known as **Releases** repo.
> - Hosted repos which typically used for hosting snapshots or development versions, called **Snapshots**.

Now let's build the package and publish it into the `py-dev` hosted repo.

2. Fork the [PyFlixPythonSDK][PyFlixPythonSDK] repo and clone it locally. 
3. In the PyFlixPythonSDK repo, install packages required to build and publish your package: `pip install build twine`.
   The [build](https://pypa-build.readthedocs.io/en/latest/) package is responsible to "pack" your Python code into distribution archives, which can then be uploaded to your PyPi hosted repository using the [twine](https://twine.readthedocs.io/en/stable/) tool.

4. Open a terminal in the library root directory, build the package by: `python -m build`.    
   This will build the package in an isolated environment, generating two formats under the `dist/` dir: a source-distribution (`.tar.gz`), and wheel (`.whl`).

   - **Source-distribution** (or `sdist` for short) is a format that contains the source code in pure Python files, along with setup and build scripts.
     When installed, these packages are **built and compiled** on the target system.
   
   - **Wheel** (of `whl` for short) is a binary distribution format that contains **pre-compiled**, platform-specific versions of a Python package.
     whl packages are typically faster to install because they don't require compilation on the target system. 
   
   `pip` always prefers wheels.

5. Upload all archives under `dist/` by (provide username and password, and change the `--repository-url` URL value if needed):
   ```bash
   python3 -m twine upload --repository-url http://localhost:8081/repository/py-dev/ -u <nexus-username> -p <nexus-password> dist/*
   ```
6. Observe the uploaded packages in Nexus server.

## Create group repo

1. Create a **PyPI group repo**, which contains both the proxy and hosted repo you've created in the previous sections. 

Note that the order of the repositories listed in **Ordered Group Repositories** is important. When the repository manager searches for a component in a group, it will return the first match. 
It's recommended placing hosted repositories higher in the list than proxy repositories within the list. 

2. Change the repo URL in `pip.conf` according to the new group repo URL.
3. Make sure you are able to install new packages after changing the repo URL.

> [!NOTE]
> Your packages still have to be uploaded directly to the hosted repository as groups won't proxy uploads to the hosted repository.


# Exercises 

## :pencil2: Repository Health Check

[Repository Health Check (RHC)](https://help.sonatype.com/repomanager3/nexus-repository-administration/repository-management/repository-health-check) allows Nexus Repository users to identify open source security risks in proxy repositories at the earliest stages of their DevOps pipeline.

New vulnerabilities report is updated every 24 hours.

If you’re running Nexus Repository **Pro**, you can see a detailed report.

1. Enable RHC by clicking the **Analyze** button on the relevant repository in **Repositories** page.
2. Try to install the `requests==2.2.1` package, which has several known security issues.

### :pencil2: CI pipeline for building the `pyflix` package 

In your [PyFlixPythonSDK][PyFlixPythonSDK] repo, create a `build.Jenkinsfile` that when pushing new code from branch `dev`, the pipeline tests, builds and publishes a new version of the package into the Nexus `pypi-dev` repo:

```text
pipeline {
    agent any
    environment {
        NEXUS_CREDENTIALS_ID = "..."  # TODO complete me 
        NEXUS_URL = "..."
        GROUP_REPO_NAME = "..."
        DEV_HOSTED_REPO_NAME = "..."
    }
    stages {
        stage('Install Dependencies') {
            steps {
                sh '''
                   python -m venv venv
                   . venv/bin/activate
                   
                   # now packages should be installed from your Nexus pypi.org-central, not from the original pypi.org!
                   NEXUS_PYPI_URL="${NEXUS_URL}/repository/${GROUP_REPO_NAME}/simple"
                   pip install --trusted-host ${NEXUS_URL} --index-url ${NEXUS_PYPI_URL}  -r requirements.txt   
                '''
            }
        }
        stage('Run Unittest') {
            steps {
                sh '''
                  . venv/bin/activate
                  python -m unittest discover -s tests
                '''
            }
        }
        stage('Upload to pypi dev') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${NEXUS_CREDENTIALS_ID}", passwordVariable: 'NEXUS_PASSWORD', usernameVariable: 'NEXUS_USERNAME')]) {
                    sh """
                        . venv/bin/activate
                        twine upload --repository-url ${NEXUS_URL}/repository/${DEV_HOSTED_REPO_NAME}/ -u $NEXUS_USERNAME -p $NEXUS_PASSWORD dist/*
                    """
                }
            }
        }
    }
    post {
        cleanup {
            cleanWs()
        }
    }
}
```

## :pencil2: Artifact staging workflow

![][artifacts_nexus_staging]

For more information https://help.sonatype.com/en/staging.html

## :pencil2: Pipeline 

Create a Jenkins pipeline that downloads a Python package from your hosted repo and uploads it to PyPI. 

## :pencil2: Nexus Docker repo  

1. In your Nexus server, create `Docker(proxy)`, `Docker(hosted)` and `Docker(group)` which contains the two repos (the proxy and hosted).
2. From your local machine, pull an image from the created group repo.
4. From your local machine, push an image into the hosted repo.

## :pencil2: Policy to clean-up artifacts 

If you are not cleaning out old and unused components, your repositories will grow quickly. Over time, this will present risks to your deployment:

- Storage costs will increase
- Performance is impacted
- Artifact discovery will take longer
- Consuming all available storage will results in server failure

Create two clean-up policies as follows:

- `dev-cleanup` policy that cleans artifacts after 30 days.
- `prod-cleanup` policy that cleans artifact after 1 year (production artifacts should be stored for long time). 

Create associate the `dev-cleanup` policy with one of your repositories.


## :pencil2: Define s3 as an artifacts storage

Follow:  

https://help.sonatype.com/repomanager3/nexus-repository-administration/repository-management/configuring-blob-stores#ConfiguringBlobStores-AWSSimpleStorageService(S3)



[NetflixMovieCatalog]: https://github.com/exit-zero-academy/NetflixMovieCatalog.git
[PyFlixPythonSDK]: https://github.com/exit-zero-academy/PyFlixPythonSDK.git
[artifacts_nexus2]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/artifacts_nexus2.png
[artifacts_nexus]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/artifacts_nexus.png
[artifacts_nexus_staging]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/artifacts_nexus_staging.png

