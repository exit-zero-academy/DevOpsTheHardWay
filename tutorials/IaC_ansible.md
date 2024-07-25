# IaC with Ansible

Ansible is an open-source automation tool that simplifies the process of configuring and managing remote servers.

Main features:

- Declarative language described in YAMLs.
- Automate repetitive tasks such as software installation, configuration management, and application deployment across multiple servers or workstations.
- Works over SSH, allowing it to manage both Linux and Windows machines.
- Large and active community.
- Ships with a [comprehensive documentation](https://docs.ansible.com/ansible/latest/getting_started/index.html#getting-started-with-ansible). 

## Installation

https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-and-upgrading-ansible-with-pip

**Note**: While Ansible as a tool can connect and manage remote Windows servers, installing and using Ansible **from** Windows is not supported, only Linux here. 

## Choosing the right tool (Terraform vs Ansible)

![](../.img/IaC_ansible_tf.png)

## Build a simple Inventory and use ad-hoc commands

> [!TIP]
> 
> During the tutorial you'll modify and create files. Since we work on our shared git repo, you can work on your own branch and commit changes to save your work. 


Ansible works against multiple nodes or "hosts" using a list or group of lists known as [Inventory](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html).

An **ad-hoc command** is a single, one-time command that you run against your inventory, without actually specifying the command or the configuration "as code".
Ad-hoc commands are useful for performing quick and simple tasks, such as checking the uptime of a server or installing a package.

Before starting, make sure you **two** up and running Ubuntu instances.

1. In our course repo, under `ansible_workdir`, create a simple `hosts` Inventory file as follows:

```ini
<host-1-ip>
<host-2-ip>
```

Change `<host-1-ip>` and `<host-2-ip>` to your instances public IP addresses.

We will use the [`ping` module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/ping_module.html) to ping our hosts.

> [!NOTE]
> **Ansible modules** are small units of code (written in Python) that perform specific tasks on target systems.
> Examples of modules include those for executing commands, copying files, managing packages, and configuring services.
> Ansible is shipped with hundreds of [built-in modules](https://docs.ansible.com/ansible/latest/modules/list_of_all_modules.html) available for usage.


2. Run the below command from the `ansible_workdir` dir. Investigate the returned error and use the `--user` option to fix it.

```shell
ansible -i hosts --private-key /path/to/private-key-pem-file all -m ping
```

As you may see, under the hood, ansible is trying to connect to the machines via SSH connection. 

To disable the SSH authenticity checking, you can configure the following env var:

```bash
export ANSIBLE_HOST_KEY_CHECKING=False
```

3. Let's say the hosts are running a frontend app, we can arrange hosts under groups, and automate tasks for specific group:

```ini
[frontend]
web1 ansible_host=<host-ip-1> ansible_user=<host-ssh-user>
web2 ansible_host=<host-ip-2> ansible_user=<host-ssh-user>
```

There are two more default groups: `all` and `ungrouped`. 
The `all` group contains every host. 
The `ungrouped` group contains all hosts that don’t have another group aside from `all`.

Ansible support many more [behavioral inventory parameters](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html#connecting-to-hosts-behavioral-inventory-parameters). 

4. Let's check the uptime of all servers listed under the `frontend` group:

```shell
ansible -i hosts --private-key /path/to/private-key-pem-file frontend -m command -a "uptime"
```

## Working with Playbooks

If you need to execute a task more than once, you should write a **Playbook** and put it under some source control (e.g. Git repo).
Ansible Playbooks offer a repeatable, re-usable and simple configuration management.

Playbooks are expressed in YAML format, composed of one or more "plays" in an **ordered** list.
A playbook "play" runs one or more tasks.

Let's create a task that verifies the installation of `nginx` (and install it if needed).

1. Create the following `site.yaml` file, representing an Ansible playbook:
2. 
```yaml
- name: Frontend servers
  hosts: frontend
  tasks:
    - name: Ensure nginx is at the latest version
      ansible.builtin.apt:
        name: nginx
        state: latest
```

In the above example, [`ansible.builtin.apt`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_module.html) is the module being used, `name` and `state` are module's parameters. 

2. Apply your playbook using the following `ansible-playbook` command.

```shell
ansible-playbook -i hosts --private-key /path/to/private-key-pem-file site.yaml
```

As the tasks in this playbook require `root` privileges, we add the `become: yes` to enable execute tasks as a different Linux user. We also use [variables](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html#using-variables) to make the playbook more modular:

```yaml
- name: Frontend servers
  hosts: frontend
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

We now want to modify our Nginx server configurations.

3. Add the following task to your playbook:

```yaml
- name: Frontend servers
  hosts: frontend
  become: yes
  vars:
    nginx_major_version: 1
  vars_files:
    - vars/nginx-custom-vars.yaml
  tasks:
    - name: Ensure nginx is installed
      ansible.builtin.apt:
        name: "nginx={{ nginx_major_version }}.*"
        state: present
        update_cache: yes
          
    - name: Create a the server static files directory if it does not exist
      ansible.builtin.file:
        path: "{{ document_root }}"
        state: directory
        mode: '0755'
       
    - name: Copy custom index.html file
      ansible.builtin.template:
        src: index.html.j2
        dest: "{{ document_root }}/index.html"

    - name: Copy Nginx server template
      ansible.builtin.template:
        src: custom.conf.j2
        dest: /etc/nginx/conf.d/custom.conf
```

Ansible uses [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) templating tool to copy files to hosts, while enable dynamic expressions according to the defined [variables](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#playbooks-variables).
The `templates/custom.conf.j2` and its corresponding variable file `vars/nginx-custom-vars.yaml` can be found in our course repo.

4. Run the playbook. Connect to one of the hosts and make sure the configurations has been applied. Try to visit the server using one of the machine's public IP (don't forget to open the relevant port in the instance's security group).
5. For the new Nginx configs to be applied, it's required to restart the `nginx` service. Let's add a [Handler](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_handlers.html#handlers) that restarts the daemon after a successful configuration change:

```yaml
- name: Frontend servers
  hosts: frontend
  become: yes
  vars:
    nginx_major_version: 1
  vars_files:
    - vars/nginx-custom-vars.yaml
  tasks:
    - name: Ensure nginx is installed
      ansible.builtin.apt:
        name: "nginx={{ nginx_major_version }}.*"
        state: present
        update_cache: yes
          
    - name: Create a the server static files directory if it does not exist
      ansible.builtin.file:
        path: "{{ document_root }}"
        state: directory
        mode: '0755'
       
    - name: Copy custom index.html file
      ansible.builtin.template:
        src: index.html.j2
        dest: "{{ document_root }}/index.html"

    - name: Copy Nginx server template
      ansible.builtin.template:
        src: custom.conf.j2
        dest: /etc/nginx/conf.d/custom.conf
        
      notify:
        - Restart Nginx

  handlers:
    - name: Restart Nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
```

7. Run the playbook and manually check the status of the `nginx` service in one of the hosts.

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
ansible-playbook -i hosts --private-key /path/to/private-key-pem-file site.yaml --check --diff 
```

## Ansible Facts

You can retrieve or discover information (known as **Facts**) about your remote systems. 

For example, with facts variables you can use the IP address of a machine as a configuration value on another system. 
Or you can perform tasks based on the specific host OS.

Let's run the `setup` ad-hoc command to print all facts ansible collects on a given host:

```shell
ansible -i hosts --private-key /path/to/private-key-pem-file frontend -m setup
```

Let's assume your `frontend` group contains both Ubuntu and RedHat servers. 
In such case, the usage of `ansible.builtin.apt` module doesn't fit the RedHat family servers.

We would like to add a condition for this task to use the appropriate package manager based on the OS:

```yaml
- name: Frontend servers
  hosts: frontend
  become: yes
  vars:
    nginx_major_version: 1
  vars_files:
    - vars/nginx-custom-vars.yaml
  tasks:
    - name: Ensure nginx is installed
      ansible.builtin.apt:
        name: "nginx={{ nginx_major_version }}.*"
        state: present
        update_cache: yes
      when: ansible_facts['pkg_mgr'] == 'apt'
        
    - name: Ensure nginx is installed
      ansible.builtin.yum:
        name: "nginx={{ nginx_major_version }}.*"
        state: present
      when: ansible_facts['pkg_mgr'] == 'yum'
          
    - name: Create a the server static files directory if it does not exist
      ansible.builtin.file:
        path: "{{ document_root }}"
        state: directory
        mode: '0755'
       
    - name: Copy custom index.html file
      ansible.builtin.template:
        src: index.html.j2
        dest: "{{ document_root }}/index.html"

    - name: Copy Nginx server template
      ansible.builtin.template:
        src: custom.conf.j2
        dest: /etc/nginx/conf.d/custom.conf
        
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
        │   ├── custom.conf.j2
        │   └── index.html.j2
        └── vars/
            └── main.yaml
```

- In `tasks/main.yaml`, copy the tasks (the content under the `tasks:` entry in the original `site.yaml` file).
- In `handlers/main.yaml` copy the handlers.
- Copy the content of `vars/nginx-custom-vars.yaml` into `vars/main.yaml`.

By default, Ansible will look in each directory within a role for a `main.yaml` file for configurations to apply.

Create a `site.yaml` file with the following content:

```yaml
---
- name: Frontend servers
  hosts: frontend
  become: yes
  roles:
    - nginx
  tasks:
    # ...
```

Ansible will execute roles first, then other tasks in the play.

Apply your playbook. Make sure it works properly. 

# Exercises 

### :pencil2: Deploy the 2048 game

The 2048 game is a web-based game in which you have to join numbers and reach an 2048 tile. 
The source code can be found [here](https://github.com/gabrielecirulli/2048). 

Your goal is to serve this game behind the nginx webserver.
Create a deployment playbook with task that clones the repo files into the directory that nginx uses to serve static content.

Notes:

- Make sure you can play the game using the IP address of one of your hosts (please **don't** start playing it during class).
- Don't serve the `README.md` file, existed in a fresh clone of the 2048 game repo.
- You should be able to execute the playbook again and again.

### :pencil2: Backup Nginx conf files

Create a task that copies all nginx conf files into `/nginx_backups` dir into an [epoch-timestamped](https://www.epochconverter.com/) `tag.gz` file. For example:

```bash
nginx_backups/1579076412.tar.gz
nginx_backups/1705306827.tar.gz
...
```

Depending on your Nginx version, `.conf` files can be found at:

- `/etc/nginx/nginx.conf`.
- `/etc/nginx/conf.d/`.
- `/etc/nginx/sites-available/` (usually a symlink to `/etc/nginx/sites-enabled/`).

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
    create 0640 www-data adm  # Changes NGINX log permissions
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

### :pencil2: Use nginx role 

(or any different other role)

https://github.com/geerlingguy/ansible-role-nginx

