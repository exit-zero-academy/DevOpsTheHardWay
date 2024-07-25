# Docker containers storage

## Docker data persistence

By default, all files created inside a container are stored on a writable container layer.
This means that the data doesn't persist when that container no longer exists.

Docker has two options for containers to store files on the host machine, so that the files are persisted even after the container stops: **volumes**, and **bind mounts**.

## Bind mounts 

**Bind mounts** provide a way to mount a directory or file **from the host machine into a container**.
Bind mounts directly map a directory or file on the host machine to a directory in the container. 

Let's take the old good `nginx` image:

```bash
docker run --rm -p 8080:80 -v /path/on/host:/usr/share/nginx/html --name my-nginx nginx:latest
```

In this example, we're running an Nginx container while the `-v /path/on/host:/usr/share/nginx/html` flag specifies the bind mount.
It maps the directory `/path/on/host` on the host machine to the `/usr/share/nginx/html` directory inside the container.

Whenever the `my-nginx` container is accessing `/usr/share/nginx/html` path, the directory it actually sees is `/path/on/host` on the host machine.
More than that, every change the container does to the `/usr/share/nginx/html` directory will reflect in the corresponding location on the host machine, `/path/on/host`, due to the bind mount.
The other way also applies, changes made on the host machine in `/path/on/host` will be visible inside the container under `/usr/share/nginx/html`.

As you may know, `/usr/share/nginx/html` is the location from which Nginx serves static content files.
In that way, files you'll place in `/path/on/host` on your host machine, will be served by the running nginx container, without the need to copy those files to the container during build time.

Bind mounts are commonly used for development workflows, where file changes on the host are immediately reflected in the container without the need to rebuild or restart the container. 
They also allow for easy access to files on the host machine, making it convenient to provide configuration files, logs, or other resources to the container.

### Try it yourself - Persist nginx 

1. In you host machine, create a directory and put some sample `index.html` file in it (search for sample file in the internet).
2. Run an nginx container while mapping the path `/usr/share/nginx/html` within the container, to your created directory.
3. Open up your browser and visit the nginx webserver: `http://localhost:8080`. Make sure the nginx serves your file.
4. On your host machine, delete `index.hmtl`.
5. Refresh the server and make sure the nginx is responding with `404` page not found error. 

## Volumes 

**Docker volumes** is another way to persist data in containers. 
While bind mounts are dependent on the directory structure and OS of the host machine, volumes are logical space that completely managed by Docker.
Volumes offer a higher level of abstraction, allow us to work with different kind of storages, e.g. volumes stored on remote hosts or cloud providers.
Volumes can be shared among multiple containers.

### Create and manage volumes

Unlike a bind mount, you can create and manage volumes outside the scope of any container.

```bash 
docker volume create my-vol
```

Let's inspect the created volume:

```bash
$ docker volume inspect my-vol
[
    {
        "CreatedAt": "2023-05-10T14:28:15+03:00",
        "Driver": "local",
        "Labels": {},
        "Mountpoint": "/var/lib/docker/volumes/my-vol/_data",
        "Name": "my-vol",
        "Options": {},
        "Scope": "local"
    }
]
```

Inspecting the volume discovers the real location that the data will be stored on the host machine: `/var/lib/docker/volumes/my-vol/_data`.

The `local` volume driver is the default built-in driver that stores data on the local host machine.
But docker offers [many more](https://docs.docker.com/engine/extend/legacy_plugins/#volume-plugins) drivers that allow you to create different types of volumes that can be mapped to your container.
For example, the [Azure File Storage plugin](https://github.com/Azure/azurefile-dockervolumedriver) lets you mount Microsoft Azure File Storage shares to Docker containers as volumes.

The following example mounts the volume `my-vol` into `/usr/share/nginx/html` in the container.

```bash
docker run --rm --name my-nginx -v my-vol:/usr/share/nginx/html nginx:latest
```

Essentially we've got the same effect as the above example, but now the mounted volume is not just a directory in the OS, 
but logically managed by docker. 

Can you see how elegant is it? volumes provide a seamless abstraction layer for persisting data within containers.
The container believe it reads and writes data from some location in his file system (`/usr/share/nginx/html`), without any knowledge of the underlying storage details (of the `my-vol` volume). 
If we would have used the Azure File Storage plugin, the data would be actually stored in the cloud.

Remove a volume:

```bash
docker volume rm my-vol
```

### More about volumes

- A given volume can be mounted into multiple containers simultaneously. 
- When no running container is using a volume, the volume is still available to Docker and is not removed automatically.
- If you mount an **empty volume** into a directory in the container in which files or directories exist, these files or directories are **propagated (copied)** into the volume. 
- Similarly, if you start a container and specify a volume which does not already exist, an empty volume is created for you. This is a good way to pre-populate data that another container needs.
- If you mount a **bind mount** or **non-empty volume** into a directory in the container in which some files or directories exist, these files or directories are **obscured by the mount**.

### Read-only volumes 

Sometimes, the container only needs read access to the data, is such way multiple containers can safely mount the same volume without write race condition. 
You can simultaneously mount a single volume as read-write for some containers and as read-only for others.

The following example mounts the directory as a read-only volume, by adding `ro` to the `-v` flag:

```bash 
docker run -d \
  --name=nginxtest \
  -v nginx-vol:/usr/share/nginx/html:ro \
  nginx:latest
```

Other possible options are:

1. `ro` (Read-Only): Mounts the volume in read-only mode, allowing only read operations.
2. `rw` (Read-Write): Mounts the volume in read-write mode, allowing both read and write operations (the default).
4. `Z` (Shared): Marks the volume as shared, allowing it to be **safely** shared between multiple containers.
5. `nocopy` (No Copy): Indicates that the volume should not be copied from the container image but instead be created as an empty volume.
6. `delegated` (Delegated Copy): Specifies that the volume should be created as an empty volume but be populated with data from the container image on-demand.

Where multiple options are present, you can separate them using commas.

## `tmpfs` mounts

Volumes and bind mounts let you share files between the host machine and container so that you can persist data even after the container is stopped.

As opposed to volumes and bind mounts, a **tmpfs mount** is temporary file system, and only persisted in the host memory (RAM). 
When the container **stops**, the tmpfs mount is removed, and files written there won't be persisted.

This is useful to temporarily store sensitive files that you don't want to persist in either the host or the container writable layer.

To use a tmpfs mount in a container, use the `--tmpfs` flag.
There is no source for tmpfs mounts. The following example creates a tmpfs mount at `/ap`p in a Nginx container. 

```bash
docker run -d \
  -it \
  --name tmptest \
  --tmpfs /app \
  nginx:latest
```

## Summary 

No matter which type of mount you choose to use, the data looks the same **from within the container**. 
It is exposed as either a directory or an individual file in the container's filesystem.

An easy way to visualize the difference among volumes, bind mounts, and tmpfs mounts is to think about where the data lives on the host machine.

![][docker_volumes]

- **Volumes** are stored in a part of the host filesystem which is **managed by
  Docker** (`/var/lib/docker/volumes/` on Linux). Non-Docker processes should not
  modify this part of the filesystem.

- **Bind mounts** may be stored *anywhere* on the host system. They may even be
  important system files or directories. Non-Docker processes on the host machine
  or a Docker container can modify them at any time.

- **`tmpfs` mounts** are stored in the host system's memory only, and are never
  written to the host system's filesystem.

# Exercises

### :pencil2: Mount the Nginx conf file 

1. Run your NetflixMovieCatalog container.
2. Create an Nginx container which routes the traffic to your NetflixMovieCatalog container. 
   For simplicity, you don't need to wrap the Flask app with uWSGI. Instead, your Nginx communicates directly with Flask using a simple `proxy_pass` directive over HTTP protocol:
   ```text
   server {
     listen 80;
     server_name  localhost;
     location / {
       proxy_pass http://<netflix_movie_catalog>:8080;
      }
   } 
   ```
   
   While `<netflix_movie_catalog>` is the container IP of your NetflixMovieCatalog container.
3. Persist the `.conf` file of Nginx so you can kill the container and start a fresh one, and still the Nginx custom server configuration would be applied. 
4. Visit the app via Nginx. 

### :pencil2: Persist InfluxDB database

Your goal is to run InfluxDB container from the [previous exercise](docker_containers.md#pencil2-availability-test-system) while the data is stored persistently.

Make sure the data is persistent by `docker kill` the container and create a new container one.  

### :pencil2: Understanding user file ownership in docker

When running a container, the default user inside the container is often set to the `root` user, and this user has full control of the container's processes.
Since containers are isolated process in general, we don't really care that `root` is the user operating within the container.

But, when mounting directories from the host machine using the `-v` command, it is important to be cautious when using the root user in a container. Why?

We will investigate this case in this exercise...

1. On your host machine, create a directory under `~/test_docker`.
2. Run the `ubuntu` container while mounting `/test` within the container, into `~/test_docker` in the host machine:

```bash
docker run -it -v ~/test_docker:/test ubuntu /bin/bash
```

3. From your host machine, create a file within `~/test_docker` directory.
4. From the `ubuntu` container, list the mounted directory (`/test`), can you see the file you've created from your host machine?
   Who are the UID (user ID) and GID (group ID) owning the file?
5. From within the container, create a file within `/test`.
6. List `~/test_docker` from your host machine. Who are user and group owning the file created from the container?
7. Try to indicate the potential vulnerability: "If an attacker gains control of the container, they may be able to..."
8. Repeat the above scenario, but instead of using `-v`, use docker volumes. Starts by creating a new volume by: `docker create volume testvol`. Describe how using docker managed volume can reduce the potential risk.


### :pencil2: Investigate volume mounting

Use the `ubuntu` container to experiment with volume mounting and answer the following questions:

1. What happens when you mount an **empty docker volume** into a directory in the container in which files or directories exist?
2. What happens when you start a container and specify a docker volume name that does not exist?
3. What happens when you mount a path using **bind mount** of non-empty directory in the container?
4. What happens when you start a container and specify paths (both in the host machine and the container) that does not exist?

[docker_volumes]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/docker_volumes.png