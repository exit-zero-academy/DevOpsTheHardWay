# IaC with Ansible

So far, you’ve managed servers manually. Now imagine you have 3000 servers, how can you install and configure Nginx on each one of them? 

The naive approach might be to write a bash script that iterates over the 3000 machines and performs the installation and configuration. 
However, we can do it much better!

- **Imperative vs. Declarative**: In a Bash script, obviously, you need to write command for every step needed to reach your desired state. 
  This is known as the **imperative** approach. 
  In contrast, in the **declarative** approach you only have to specify what the final state should look like (e.g., "Nginx should be installed and configured"), and the there is a tool (you guess right, Ansible) that **figures out how to achieve that state**, automatically. 
- **Parallelism**: Bash script typically handles servers sequentially, which can be time-consuming.
  We want a tool that can manage hundreds of servers in parallel.


Ansible is an open-source automation tool that simplifies the process of configuring and managing remote servers.

Main features:

- Automate repetitive tasks such as software installation, configuration management, and application deployment across multiple servers or workstations.
- Works over SSH, allowing it to manage both Linux and Windows machines.
- Large and active community.
- Ships with a [comprehensive documentation](https://docs.ansible.com/ansible/latest/getting_started/index.html#getting-started-with-ansible). 

## Installation

https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-and-upgrading-ansible-with-pip

**Note**: While Ansible as a tool can connect and manage remote Windows servers, installing and using Ansible **from** Windows is not supported, only Linux here. 

## Build a simple Inventory and use ad-hoc commands

> [!TIP]
> 
> During the tutorial you'll modify and create files under the `ansible_workdir` dir in our course repo.
> You can create and work on your own branch, then commit changes to save your work without changing the main branch. 

1. Before starting, make sure you have some **three** up and running `*.nano` Ubuntu instances.


Ansible works against multiple machines (also **nodes** or **hosts**) using a file known as an [Inventory](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html). In this tutorial, the inventory file will be stored under `ansible_workdir/hosts`.

2. In our course repo, under `ansible_workdir`, fill in the `hosts` inventory file as follows:

```ini
<host-1-ip>
<host-2-ip>
<host-3-ip>
```

Change `<host-1-ip>`, `<host-2-ip>` and `<host-3-ip>` to your instance public IP addresses.

An **ad-hoc command** is a single, one-time command that you run against your inventory.
Ad-hoc commands are useful for performing quick and simple tasks, such as checking the status of each server.

We will use the [`ping` module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/ping_module.html) to ping our hosts.

> [!NOTE]
> **Ansible modules** are small units of code (written in Python) that perform specific tasks on target systems.
> Examples of modules include those for executing commands, copying files, managing packages, and configuring services.
> Ansible is shipped with hundreds of [built-in modules](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/index.html) available for usage.


3. Run the below command from the `ansible_workdir` dir. 

```shell
ansible -i hosts --ssh-common-args='-o StrictHostKeyChecking=no' --user ubuntu --private-key /path/to/private-key-pem-file all -m ping
```

As you may see, under the hood, ansible is trying to connect to the machines via SSH connection. 

Here's a breakdown of the above command:

- `-i hosts`: Specifies the inventory file.
- `--ssh-common-args='-o StrictHostKeyChecking=no'`: Passes additional SSH options to disable host key checking, preventing SSH from asking whether to trust the host's key.
- `--user ubuntu`: Specifies the SSH user as ubuntu.
- `--private-key /path/to/private-key-pem-file`: Uses the specified private key file for authentication.
- `all`: Targets all hosts in the inventory file.
- `-m ping`: Uses the ping module to check the connectivity of the target hosts.

4. Let's say the 2 hosts are running the [NetflixMovieCatalog][NetflixMovieCatalog][^1] app, and the 3rd host is your Nginx webserver. We can arrange our hosts under groups, and automate tasks for specific group:

```ini
[catalog]
catalog1 ansible_host=<host-ip-1>
catalog2 ansible_host=<host-ip-2>

[webserver]
nginx ansible_host=<host-ip-3>
```

There are two more default groups: `all` and `ungrouped`: 
- The `all` group contains every host. 
- The `ungrouped` group contains all hosts that don’t have another group aside from `all`.

Ansible support many more [behavioral inventory parameters](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html#connecting-to-hosts-behavioral-inventory-parameters).

5.  Let's check the uptime of all servers listed under the `catalog` group:

```shell
ansible -i hosts --ssh-common-args='-o StrictHostKeyChecking=no' --user ubuntu --private-key /path/to/private-key-pem-file catalog -m command -a "uptime"
```

## Working with Playbooks

If you need to execute complex tasks, run them more than once, and document your tasks - ad-hoc command are not convenient enough.
You should write a **Playbook** and put it under your Git repo.

Ansible Playbooks offer a repeatable, re-usable and simple configuration management.

Playbooks are expressed in YAML format, composed of one or more "plays" in an **ordered** list.
A playbook "play" runs one or more tasks.

Let's create a task that verifies the installation of `nginx` (and install it if needed).

1. Under `ansible_workdir`, take a look on the following `site.yaml` file, representing an Ansible playbook:

```yaml
- name: Nginx webserver
  hosts: webserver
  tasks:
    - name: Ensure nginx is at the latest version
      ansible.builtin.apt:
        name: nginx
        state: latest
```

In the above example, [`ansible.builtin.apt`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_module.html) is the module being used, `name` and `state` are module's parameters. 

2. Apply your playbook using the following `ansible-playbook` command (it may not work, keep reading to resolve the issue).

```shell
ansible-playbook -i hosts --ssh-common-args='-o StrictHostKeyChecking=no' --user ubuntu --private-key /path/to/private-key-pem-file site.yaml
```

As the tasks in this playbook require `root` privileges, we add the `become: yes` to enable execute tasks as a different Linux user. We also use [variables](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html#using-variables) to make the playbook more modular:

```yaml
- name: Nginx webserver
  hosts: webserver
  become: yes
  vars:
    nginx_major_version: 1
  tasks:
    - name: Ensure nginx is installed
      ansible.builtin.apt:
        name: "nginx={{ nginx_major_version }}.*"
        state: present
        update_cache: yes
```

Run the playbook again and make sure the task has been completed successfully.

> [!NOTE]
> If you run again the same playbook, what happen? why? 

We now want to modify our Nginx server configurations.

3. Add the following task to your playbook, so Nginx serves movies posters as static content:

```yaml
- name: Nginx webserver
  hosts: webserver
  become: yes
  vars:
    nginx_major_version: 1
  vars_files:
    - vars/nginx-vars.yaml
  tasks:
    - name: Ensure nginx is installed
      ansible.builtin.apt:
        name: "nginx={{ nginx_major_version }}.*"
        state: present
        update_cache: yes
    
    - name: Create the poster static files directory
      ansible.builtin.file:
        path: "{{ poster_root }}"
        state: directory
        mode: '0775'

    - name: Download the movies posters images.tar.gz file
      ansible.builtin.get_url:
        url: "{{ posters_data_url }}"
        dest: "{{ poster_root }}/images.tar.gz"
        mode: '0644'

    - name: Extract images.tar.gz to /usr/share/nginx/poster
      ansible.builtin.unarchive:
        src: "{{ poster_root }}/images.tar.gz"
        dest: "{{ poster_root }}"
        remote_src: yes

    - name: Copy the default.conf server template
      ansible.builtin.template:
        src: default.conf.j2
        dest: /etc/nginx/conf.d/default.conf
```

Ansible uses [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) templating tool to copy files to hosts, while enable dynamic expressions according to the defined [variables](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#playbooks-variables).
The `templates/default.conf.j2` and its corresponding variable file `vars/nginx-vars.yaml` can be found in our course repo.

4. Run the playbook. Connect to the Nginx host and make sure the configurations has been applied. Try to request the server for a poster image content (don't forget to open the relevant port in the instance's security group).
5. For the new Nginx configs to be applied, it's required to restart (or reload) the `nginx` service. Let's add a [Handler](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_handlers.html#handlers) that restarts the daemon after a successful configuration change:

```yaml
- name: Nginx webserver
  hosts: webserver
  become: yes
  vars:
    nginx_major_version: 1
  vars_files:
    - vars/nginx-vars.yaml
  tasks:
    - name: Ensure nginx is installed
      ansible.builtin.apt:
        name: "nginx={{ nginx_major_version }}.*"
        state: present
        update_cache: yes
    
    - name: Create the poster static files directory
      ansible.builtin.file:
        path: "{{ poster_root }}"
        state: directory
        mode: '0775'

    - name: Download the movies posters images.tar.gz file
      ansible.builtin.get_url:
        url: "{{ posters_data_url }}"
        dest: "{{ poster_root }}/images.tar.gz"
        mode: '0644'

    - name: Extract images.tar.gz to /usr/share/nginx/poster
      ansible.builtin.unarchive:
        src: "{{ poster_root }}/images.tar.gz"
        dest: "{{ poster_root }}"
        remote_src: yes

    - name: Copy the default.conf server template
      ansible.builtin.template:
        src: default.conf.j2
        dest: /etc/nginx/conf.d/default.conf  
      notify:
        - Restart Nginx

  handlers:
    - name: Restart Nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
```

7. Run the playbook and manually check the status of the `nginx` service in the hosts.

> #### Try it yourself
> 
> Change the server's port number to a value other than `8080`, apply the playbook and make sure the configurations have been applied. 

### Validating playbook tasks: `check` mode and `diff` mode

Ansible provides two modes of execution that validate tasks: **check** mode and **diff** mode.
They are useful when you are creating or editing a playbook, and you want to know what it will do.

- In `check` mode, Ansible runs without making any changes on remote systems, and report the changes that would have made.
- In `diff` mode, Ansible provides before-and-after comparisons.

Simply add the `--check` or `--diff` options (both or separated) to the `ansible-playbook` command:

```shell
ansible-playbook -i hosts --ssh-common-args='-o StrictHostKeyChecking=no' --user ubuntu --private-key /path/to/private-key-pem-file site.yaml --check --diff 
```

## Ansible Facts

You can retrieve or discover information (known as **Facts**) about your remote systems. 

For example, with facts variables you can use the IP address of a machine as a configuration value on another system. 
Or you can perform tasks based on the specific host OS.

Let's run the `setup` ad-hoc command to print all facts ansible collects on a given host:

```shell
ansible -i hosts --ssh-common-args='-o StrictHostKeyChecking=no' --user ubuntu --private-key /path/to/private-key-pem-file webserver -m setup
```

Let's assume your `webserver` group contains both Ubuntu and CentOS servers. 
In such case, the usage of `ansible.builtin.apt` module doesn't fit the RedHat family servers.

We would like to add a condition for this task to use the appropriate package manager based on the OS:

```yaml
- name: Nginx webserver
  hosts: webserver
  become: yes
  vars:
    nginx_major_version: 1
  vars_files:
    - vars/nginx-vars.yaml
  tasks:
    - name: Ubuntu - Ensure nginx is installed
      ansible.builtin.apt:
        name: "nginx={{ nginx_major_version }}.*"
        state: present
        update_cache: yes
      when: ansible_facts['pkg_mgr'] == 'apt'
        
    - name: CentOS - Ensure nginx is installed
      ansible.builtin.yum:
        name: "nginx={{ nginx_major_version }}.*"
        state: present
      when: ansible_facts['pkg_mgr'] == 'yum'

    - name: Create the poster static files directory
      ansible.builtin.file:
        path: "{{ poster_root }}"
        state: directory
        mode: '0775'

    - name: Download the movies posters images.tar.gz file
      ansible.builtin.get_url:
        url: "{{ posters_data_url }}"
        dest: "{{ poster_root }}/images.tar.gz"
        mode: '0644'

    - name: Extract images.tar.gz to /usr/share/nginx/poster
      ansible.builtin.unarchive:
        src: "{{ poster_root }}/images.tar.gz"
        dest: "{{ poster_root }}"
        remote_src: yes

    - name: Copy the default.conf server template
      ansible.builtin.template:
        src: default.conf.j2
        dest: /etc/nginx/conf.d/default.conf  
      notify:
        - Restart Nginx

  handlers:
    - name: Restart Nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
```

## Organize the playbook using Roles

[Roles](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html) are collection of tasks, files, templates, variables and other Ansible artifacts that are organized in a structured way to perform a specific function.
Roles are used to create reusable and modular code, making it easier to manage complex configurations and deployments.

Rearrange your `ansible_workdir` dir according to the following files structure:

```text
ansible_workdir/
└── roles/
    └── nginx/
        ├── tasks/
        │   └── main.yaml
        ├── handlers/
        │   └── main.yaml
        ├── templates/
        │   └── default.conf.j2
        └── vars/
            └── main.yaml
```

- In `tasks/main.yaml`, copy the tasks (the content under the `tasks:` entry in the original `site.yaml` file).
- In `handlers/main.yaml` copy the handlers.
- Copy the content of `vars/nginx-vars.yaml` into `vars/main.yaml`.

By default, Ansible will look in each directory within a role for a `main.yaml` file for configurations to apply.

Create a `site.yaml` file with the following content:

```yaml
---
- name: Nginx webserver
  hosts: webserver
  become: yes
  vars:
    nginx_major_version: 1   # now better to take this var into roles/nginx/vars/main.yaml 
  roles:
    - nginx
  tasks:
    # ...
```

Ansible will execute roles first, then other tasks in the play.

Apply your playbook. Make sure it works properly. 

# Exercises 

### :pencil2: Deploy the NetflixMovieCatalog in the `catalog` instances group

Create a role that deploys the [NetflixMovieCatalog][NetflixMovieCatalog] as a Linux service in the instances under the `catalog` group. 
Modify the `nginx` role to be functioning as a load balancer and route the traffic across the two catalog instances. 

Your roles layout should look as follows:

```text 
ansible_workdir/
├── site.yaml
└── roles/
    ├── nginx/
    │   ├── tasks/
    │   │   └── main.yaml
    │   ├── handlers/
    │   │   └── main.yaml
    │   ├── templates/
    │   │   └── default.conf.j2
    │   └── vars/
    │       └── main.yaml
    └── catalog/
        ├── tasks/
        │   └── main.yaml
        ├── handlers/
        │   └── main.yaml
        ├── templates/
        └── vars/
            └── main.yaml
```

Your `site.yaml` might look like:

```yaml
---
- name: Catalog servers
  hosts: catalog
  become: yes
  roles:
    - catalog

- name: Nginx web server
  hosts: webserver
  become: yes
  roles:
    - nginx
```

> [!TIP]
> You can use Ansible facts to retrieve the private IP of the `catalog` instances to be used in the Nginx `default.conf` server's configuration file. 

### :pencil2: Serve the 2048 game from you Nginx webserver

Under `roles/nginx/templates/game2048.conf.j2` create another Nginx server (a `server{...}` directive) that serves the [2048 game](https://github.com/gabrielecirulli/2048).

The 2048 game is a web-based game in which you have to join numbers and reach an 2048 tile. 
The source code can be found [here](https://github.com/gabrielecirulli/2048). 

Create a playbook with task that clones the repo files into the directory that nginx uses to serve static content.

Notes:

- The server should lister on port `8083`.
- Make sure you can play the game using the IP address of one of your hosts (please **don't** start playing it during class).
- Don't serve the `README.md` file (which exists in a fresh clone of the 2048 game repo).
- Try to apply the playbook again and again, what happen? Is your playbook declarative?

### :pencil2: Nginx Logs rotation 

In this exercise, we perform logs rotation for Nginx using the `logrotate` tool.

- Add task that installs the latest version of `logrotate` on your hosts.
- Using the `ansible.builtin.template` module, create a task that copies the below template file into `/etc/logrotate.d/nginx`:

```text
/var/log/nginx/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
{% if ansible_facts['os_family'] == "Debian" %}
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 $(cat /var/run/nginx.pid)
        fi
{% else %}
        nginx -s reopen
{% endif %}
    endscript
}
```

- You can start the log rotation job by `logrotate -f /etc/logrotate.d/nginx`. Use the `ansible.builtin.command` module to execute this command on your hosts (once the configuration file has been copied).

Apply the playbook, make sure Nginx rotates logs file properly. 


[NetflixMovieCatalog]: https://github.com/exit-zero-academy/NetflixMovieCatalog.git

[^1]: Please complete the [Simple app deployment](milestone_simple_app_deployment.md) to get yourself familiar with the NetflixMovieCatalog app.