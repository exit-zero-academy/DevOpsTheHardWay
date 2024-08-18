# Nginx Webserver

Based on: https://nginx.org/en/docs/

## Motivation 

So far, we've seen how to deploy a simple web applications using Flask, but to be honest, by means of scalability, performance and security - the Flask app is very poor.

Nginx is powerful web server that can act as an intermediary between your Flask application and end-users. It is responsible for many aspects that every modern HTTP servers should take into account, aspects that our Flask app can not provide, or such that we don't want to deal with in our Python code.
 
Here is a short list of what Nginx can do for you: 

- Static content
- Scale (multiprocess)
- Rate limit
- Cache
- TLS termination
- Load balancing
- Security
- Multiple web applications
- Authentication

## Installation 

> [!NOTE]
> Throughout the tutorial you should work on Ubuntu public EC2 instance in AWS.

Follow the official installation guideline for Ubuntu:  
https://nginx.org/en/linux_packages.html#Ubuntu

Make sure the Nginx service is up and running:

```console
$ sudo systemctl status nginx
● nginx.service - nginx - high performance web server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2023-04-27 06:58:53 UTC; 3s ago
       Docs: https://nginx.org/en/docs/
    Process: 12326 ExecStart=/usr/sbin/nginx -c /etc/nginx/nginx.conf (code=exited, status=0/SUCCESS)
   Main PID: 12327 (nginx)
      Tasks: 3 (limit: 1111)
     Memory: 3.9M
        CPU: 11ms
     CGroup: /system.slice/nginx.service
             ├─12327 "nginx: master process /usr/sbin/nginx -c /etc/nginx/nginx.conf"
             ├─12328 "nginx: worker process" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" ""
             └─12329 "nginx: worker process" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" "" ""

```

The above output discovers that Nginx is operating in the so-called **master-workers** architecture.

## Nginx architecture

Nginx has one master process and several worker processes.

The main purpose of the master process is to read and evaluate configuration, and maintain worker processes.
Worker processes do actual processing of requests, which are efficiently distributed among worker processes.
The number of worker processes is defined in the configuration file and may be fixed, or automatically adjusted to the number of available CPU cores.

By default, the configuration file is named `nginx.conf` and placed in the directory `/etc/nginx`.

Changes made in the configuration file will not be applied until the command to reload configuration is sent to nginx or it is restarted. To reload configuration, execute:

```bash
sudo systemctl reload nginx
```

Once the master process receives the signal to reload configuration, it checks the syntax validity of the new configuration file and tries to apply the configuration provided in it. If this is a success, the master process starts new worker processes and sends messages to old worker processes, requesting them to shut down.
Old worker processes, receiving a command to shut down, stop accepting new connections and continue to service current requests until all such requests are serviced. After that, the old worker processes exit.

## Nginx config files

Let's take a look on the main configuration file of Nginx:


```console
$ cat /etc/nginx/nginx.conf
user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;

    include /etc/nginx/conf.d/*.conf;
}

```

Every entry the `nginx.conf` file is called a **Directive**. There are simple directives, such `user` and `pid`, and block directives, such as `http {...}`. 
Block directives contain other directives within them, which are applied only in the context of the parent directive (e.g. the `keepalive_timeout` within the `http` directive applies only to the `http` context.).
Directives placed in the configuration file outside of any contexts are considered to be in the [main](https://nginx.org/en/docs/ngx_core_module.html) context.

Here are a few interesting directives explained: 

- The `events` directive specifies settings for the nginx **event loop** (the core engine of Nginx), which handles client connections. The `worker_connections` directive specifies the maximum number of client connections that a worker process can handle simultaneously.
- The `http` directive contains configuration settings for the HTTP server.
- The `sendfile` directive enables or disables serving static files
- The `include /etc/nginx/conf.d/*.conf;` directive includes any `.conf` files in the `/etc/nginx/conf.d/` directory. This is typically used to include additional configuration files that define virtual hosts or other server settings.

Now let's take a look on `/etc/nginx/conf.d/default.conf`:

```console
$ cat /etc/nginx/conf.d/default.conf
server {
    listen       80;
    server_name  localhost;

    #access_log  /var/log/nginx/host.access.log  main;

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }

    #error_page  404              /404.html;

    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }

    # proxy the PHP scripts to Apache listening on 127.0.0.1:80
    #
    #location ~ \.php$ {
    #    proxy_pass   http://127.0.0.1;
    #}

    # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
    #
    #location ~ \.php$ {
    #    root           html;
    #    fastcgi_pass   127.0.0.1:9000;
    #    fastcgi_index  index.php;
    #    fastcgi_param  SCRIPT_FILENAME  /scripts$fastcgi_script_name;
    #    include        fastcgi_params;
    #}

    # deny access to .htaccess files, if Apache's document root
    # concurs with nginx's one
    #
    #location ~ /\.ht {
    #    deny  all;
    #}
}
```

The `server` directive in Nginx is a fundamental configuration block used to define settings for virtual hosts. 
Each `server` block specifies how Nginx should handle requests for a specific domain or IP address, allowing you to host multiple websites on a single Nginx instance. 

As can be seen, the `server` block is configured to listen on port 80. 

Let's try it by visiting:

```text
http://<your-instance-ip>
```

The "Welcome to nginx!" page should be served by default. 


> [!NOTE]
> Your machine should accept incoming traffic on port `80`.

How does it work? 

The `location` block sets configuration depending on a request [URI](https://developer.mozilla.org/en-US/docs/Glossary/URI).
In out case, the `location /` block defines that every request URI that matches the `/` prefix, will be served according to the definitions of this block - 
all content is being served from `/usr/share/nginx/html`, and if otherwise not specified, the default served pages are `index.html` or `index.htm`.

If there are several matching location blocks nginx selects the one with the **longest prefix**.

## Serve static content 

An important web server task is serving out files (such as images or static HTML pages, images and media files).

Let's say we are Netflix, and we want to serve the poster image of movies to our website visitors.

1. Create a dir under `/usr/share/nginx/poster`, download and extract some images for example:
   ```bash
   cd /usr/share/nginx/poster
   wget https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/netflix_movies_poster_img/images.tar.gz
   tar -xzvf images.tar.gz
   ```
2. Under `/etc/nginx/conf.d/default.conf`, add another `location` directive that will be responsible for images serving, as follows:
```text
location /poster/ {
    root   /usr/share/nginx;
 }
```
3. To apply the new configurations: `sudo systemctl reload nginx`.
4. Try to serve some image by visit `http://<nginx-instance-ip>/poster/<some-image-path>`
5. Try to serve some image that doesn't exist. What happened?

In case something does not work as expected, you may try to find out the reason in `access.log` and `error.log` files in the directory `/usr/local/nginx/logs` or `/var/log/nginx`.

Remember our promise that Nginx can do a lot for you? Let's see some examples...

#### Caching

It's very reasonable to cache the served the images on the client side. 
Users visiting Netflix every day, why should we serve the same image if it was served a few hours ago? 

Here is how you can ask the browser to cache a served image for 30 days: 

```diff
location /poster/ {
    root   /usr/share/nginx;
+   expires 30d;
}
```

#### Missing files

Let's say we want to serve a default image in case the requested image was not found:

```diff
location /poster/ {
    root   /usr/share/nginx;
    expires 30d;
+    error_page 404 /poster/404.jpg;
}
```

Make sure the `/usr/share/nginx/poster/404.jpg` file exists.


## Reverse Proxy

### Forward (regular) proxy vs Reverse Proxy

A **forward proxy** (or just "proxy") is a server that sits between a client and a server and forwards requests from the client to the server **on behalf of the client**.
The client is **aware** of the proxy and sends its requests to the proxy, which then makes the request to the server and returns the response to the client.

![][webservers_proxy]

A **VPN** (Virtual Private Network) can be considered a type of forward proxy that encrypts and tunnels all traffic between a client and a server, allowing the client to securely access the server and bypass network restrictions.

A **reverse proxy**, on the other hand, sits between a client and a server and forwards requests from the client to one or more servers **on behalf of the server**. 
The client **is not aware** of the reverse proxy, it sends its requests to the server, and the server forwards the requests to the reverse proxy, which then forwards them to one or more backend servers.

![][webservers_reverse-proxy]

### Nginx Reverse Proxy

Nginx reverse proxy is a common technique used to evenly distribute traffic among multiple servers, seamlessly display content from various websites, or transfer requests for processing to **backend application** (E.g. our Flask app) through non-HTTP protocols.

We would like to serve the [NetflixMovieCatalog][NetflixMovieCatalog] app behind an Nginx reverse proxy. 

![][webserver_webapp]


> [!NOTE] 
> The terms **Web Application** and **Web Server** may confuse at first glance.
> 
> Nginx is a web server, by means that it is a general engine that serves HTTP requests and responses, for any application, regardless the content and that is being served, and the programing language.
> A web application, on the other hand, is responsible for the business logic and functionality, such as API logic implementation, form submission, data processing, and dynamic HTML rendering.
>
> Using web servers, web developers should not bother themselves with the overhead of handling security aspects, scalability, request rate limit, etc... they can focus of the app logic itself, save time and effort. 


As can be seen in the above figure, Nginx communicates with the Flask web applications using **UNIX sockets** (this is the most high-performed way), but Flask doesn't know how to work with sockets directly, but only with simple HTTP requests.
For that, there is even a well-defined interface between Python web applications to web server engines, called [WSGI](https://peps.python.org/pep-0333/) (Web Server Gateway Interface).  

[uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) is a tiny wrapper around Flask that implements the WSGI interface for running Python web applications that can serve HTTP requests from Nginx, Apache, and more common webservers...

![][webservers_uwsgi]

Let's serve the Flask app behind a uWsgi server.   

1. If haven't done yet, copy or clone the content of [NetflixMovieCatalog][NetflixMovieCatalog] into the Nginx machine, create Python virtual environment (venv) and install dependencies:
   
   ```bash
   python3 -m venv .venv
   source ./.venv/vin/activate
   pip install -r requirements.txt
   pip install uwsgi
   ```
   
2. To run the Flask app served by a uWSGI in the background, we'll configure it as a **Linux service** process. 
   The `.service` unit-file that specifies the service configurations is already given to you, you only have to change `<absolute-path-to-app-work-dir>` according to needs.  
   Take a look The `.ini` file instructs uwsgi how to run the Flask web application, the entrypoint file and the port the socket uses.

3. Copy `uwsgi-flask.service` to `/etc/systemd/system/uwsgi-flask.service`.
4. Enable and start the service with the following commands:

   ```bash
   sudo systemctl enable uwsgi-flask
   sudo systemctl start uwsgi-flask
   ```

5. Make sure it's running properly by: `sudo systemctl status uwsgi-flask`
6. Change the default configurations on your Nginx. Override the `location /` directive in `/etc/nginx/conf.d/default.conf` by the following:

```text
location / {
     include uwsgi_params;
     uwsgi_pass 127.0.0.1:3031;
}
```

7. Reload the Nginx server by `sudo systemctl reload nginx`. 
8. Visit the app in `http://<instance-public-ip>`.


## Multiple `server`s

Generally, the configuration file may include several `server` blocks distinguished by ports on which they listen to and by server names.

Nginx first decides which server should process the request. 
Let’s see a simple configuration with three virtual servers listen on port `80`, and another server listen on port `8080`:

```text
server {
    listen      80 default_server;
    server_name example.org www.example.org;
    ...
}

server {
    listen      80;
    server_name example.net www.example.net;
    ...
}

server {
    listen      80;
    server_name example.com www.example.com;
    ...
}

server {
    listen      8080;
    server_name example.com www.example.com;
    ...
}
```

In this configuration, in case that the webserver is accessed with port `80`, nginx tests the request’s header field `Host` to determine which server the request should be routed to.
In case the server is accessed with port `8080`, nginx route in request to the last server.  

If its value does not match any server name, or the request does not contain this header field at all, then nginx will route the request to the default server for this port.


# Exercises 

### :pencil2: Limit the static content serving functionality 

- Using Regular Expression, modify the `location /poster/` to serve only files ends with `.jpg`.
- Configure your `server` to block any requests without a `Host` header that match your website domain. The server should return a `400` status code (bad request).


### :pencil2: Nginx as a Load Balancer for the NetflixMovieCatalog app

1. Create 2 `*.nano` Ubuntu EC2 instance and deploy the [NetflixMovieCatalog][NetflixMovieCatalog] app within them, wrapped by a uWSGI server, as done in the tutorial.
2. Review the [upstream](https://nginx.org/en/docs/http/ngx_http_upstream_module.html#upstream) directive docs, and configure your Nginx server to be functioning as a Load Balancer which routes the traffic among your 2 instances. 
   Both the Nginx, and the 2 other instance should reside on the same network, and the communication has to be done using the instance's private IP. 
  
   You can utilize the below conf snippet:
   ```text
   # default.conf
   
   upstream backend {
   server <private-ip-1>:3031;
   server <private-ip-2>:3031;

   server {
   ...
   
       location / {
         include uwsgi_params;
         uwsgi_pass http://backend;
       }

   ...
   ```
3. Make sure the traffic is distributed over the two backends (almost) evenly. 

### :pencil2: Headers behind a reverse proxy

By default, Nginx redefines two header fields in proxied requests, `Host` (set to the `$proxy_host` [variable](https://nginx.org/en/docs/http/ngx_http_core_module.html#variables)) and `Connection` (set to `close`).
This behavior can cause issues by loosing information about the original client request, such as the client's IP address and the originally requested host.
To change these settings, as well as modifying other header fields, use the [`proxy_set_header`](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_set_header) directive.

```text
location / {
    ...
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    
    ...
}
```

Add these directive and make sure the correct information is available in your Flask app. 

### :pencil2: Caching 

Follow [Shesh's blog](https://www.sheshbabu.com/posts/nginx-caching-proxy/) to add caching functionality to your server.

### :pencil2: HTTPS in Nginx

Serve you Nginx server over HTTPS, and create another `server` which listens to HTTP (port 80) and redirect all traffic to the HTTPS `server`.

### :pencil2: Internal Nginx server

Sometimes you want to configure an Nginx `server` which accessible internally only from within your system. 

Review the [listen](https://nginx.org/en/docs/http/ngx_http_core_module.html#listen) directive and create a `server` that listens for requests originated from `127.0.0.1` only.
Test that the server is accessible only internally.

### :pencil2: CI/CD for the Nginx configuration files

In this exercise, you will set up a CI/CD pipeline to automate the deployment of Nginx configuration files to your EC2 instance.
The goal is to automatically update and reload Nginx whenever you make changes to its configuration files and push them to your repository.

- Create a new GitHub repo named **NetflixInfra** and clone it locally. 
  In your repository, create a folder named `nginx-config` and place your Nginx configuration files (`default.conf`, etc.) inside it.

- Create a new workflow file under `.github/workflows/nginx-deploy.yaml` in your repository. 
  
  In the `nginx-deploy.yaml` file, write a GitHub Actions workflow that:
     - Uses the SSH private key to connect to your EC2 instance.
     - Transfers the updated Nginx configuration files from the `nginx-config` folder to the appropriate directory on your EC2 instance.
     - Restarts the Nginx service on your EC2 instance to apply the changes.

- Test the CI/CD Pipeline by making a small change to your Nginx configuration files, commit and push the changes to your repository.
  Observe the GitHub Actions workflow being triggered and completing the deployment process.


[webservers_proxy]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/webservers_proxy.png
[webservers_reverse-proxy]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/webservers_reverse-proxy.png
[webserver_webapp]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/webserver_webapp.png
[webservers_uwsgi]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/webservers_uwsgi.png
[NetflixMovieCatalog]: https://github.com/exit-zero-academy/NetflixMovieCatalog

