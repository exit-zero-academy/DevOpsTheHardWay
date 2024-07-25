# Docker compose brief

Are you tired by executing `docker run`, `docker build`? so are we.

[Docker Compose](https://docs.docker.com/compose/) is a tool for defining and running multi-container Docker applications.
With Compose, you use a YAML file to configure your application's services. 
Then, with a single command, you create and start all the services from your configuration.

Using Compose is essentially a three-step process:

1. Define your app's environment with a `Dockerfile` so it can be reproduced anywhere.
2. Define the services that make up your app in `docker-compose.yml` so they can be run together in an isolated environment.
3. Run `docker compose up` and the Docker compose command starts and runs your entire app.

A `docker-compose.yml` looks like this:

```yaml
version: "3.9"
services:
  web:
    build: docker-containers
    ports:
      - "8000:5000"
    volumes:
      - .:/code
      - logvolume01:/var/log
    depends_on:
      - redis
  redis:
    image: redis
volumes:
  logvolume01: { }
```

The given Docker Compose file describes a multi-service application with two services: `web` and `redis`. 
Here's a breakdown of some components:

1. `version: "3.9"` specifies the version of the Docker Compose syntax being used.
2. `services:` begins the services section, where you define the containers for your application.
3. `web:` defines a service named `web`. This service is built from the current directory (`build: .`) using a Dockerfile.
4. `volumes:` defines volume mappings between the host and container.
5. `redis:` defines a service named `redis`. This service uses the official Redis image.

## Compose benefits 

Using Docker Compose offers several benefits:

- **Simplified Container Orchestration**: Docker Compose allows for the definition and management of multi-container applications as a single unit.
- **Reproducible Environments**: Since compose is defined in a YAML file, it's easy to deploy the same environment in different machine without missing any `docker run` command. This ensures that the application runs consistently across different machines.
- **Automate Volumes and Networking**: Docker Compose automatically creates a network for the application and assigns a unique DNS name to each service. No need to create networks and volumes. 

## Introducing YAML

YAML (YAML Ain't Markup Language) is a human-readable data format commonly used for configuration files and data exchange between systems.
YAMl is the cousin of JSON, by means that it uses indentation and key-value pairs to represent structured data, very similarly to JSON, by in a more clean syntax.

To prepare for working with Docker Compose, and later with Kubernetes, it is important to familiarize yourself with YAML syntax, which is the preferred syntax for writing Docker Compose files.

Find your favorite tutorial (there are hundreds YouTube videos and written tutorials) to see some YAML basic syntax (it takes no more than 20 minutes).

## Try compose 

In this course we will briefly introduce Docker Compose only as a stepping stone towards learning Kubernetes.
Docker Compose is nice tool to get yourself familiar with the concept of container orchestration and deployment.
However, Kubernetes (k8s) is way more powerful orchestration platform, which will be learnt later on in the course.

The official Docker Compose website provides good getting started tutorial with Docker Compose, explaining key concepts and demonstrating how to write a Compose file.
Complete the tutorial:      
https://docs.docker.com/compose/gettingstarted/


# Exercises

### :pencil2: Nginx, NetflixFrontend, NetflixMovieCatalog

Create a `docker-compose.yaml` file for the following:

![][docker_nginx_frontend_catalog]


[docker_nginx-flask-mongo]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/docker_nginx-flask-mongo.png
[docker_nginx_frontend_catalog]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/docker_nginx_frontend_catalog.png


