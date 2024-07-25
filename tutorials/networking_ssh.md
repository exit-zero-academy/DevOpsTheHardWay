# SSH Protocol 

The SSH protocol (Secure Shell) is a widely used protocol for secure remote access to systems and devices.
It provides strong encryption and authentication mechanisms, allowing users to securely log in to a remote machines and execute commands or transfer files.

In addition to traditional password authentication, the Secure Shell application can use public key cryptography to authenticate users.

## Basic usage

The basic usage of the `ssh` command is as follows:

```shell
ssh [user@]hostname [command]
```

- `user`: The username to use for the remote connection (optional).
- `hostname`: The hostname or IP address of the remote system.
- `command`: The command to execute on the remote system (optional). If you omit the command, ssh will open a shell session on the remote system, allowing you to interact with it as if you were physically sitting in front of it.

If you are connecting to the system for the first time, ssh will ask you to verify the authenticity of the remote host by displaying the fingerprint of the remote system's public key.

```console
[myuser@hostname]$ ssh ec2-user@server1
The authenticity of host 'server1 (192.168.0.254)' can't be established.
RSA key fingerprint is fc:c8:87:90:f0:39:af:4f:de:99:cc:30:ce:64:b2:8e.
Are you sure you want to continue connecting (yes/no)?
```

Once you have verified the fingerprint, ssh will establish a secure connection to the remote system and open a shell session.
Verified server's fingerprint are stored in the clients machine under `~/.ssh/known_hosts`.

On subsequent connections to the same server, the SSH client will check the fingerprint of the server's public key against the fingerprints stored in the `known_hosts` file.
If the fingerprint of the server's public key has changed, the SSH client will display a warning message and refuse to connect to the server.
This helps to protect against man-in-the-middle attacks.


## Generating a public-private key-pair locally

When using ssh, a user's public-private key pair can be generated with the `ssh-keygen` command.

```console
[myuser@station myuser]$ ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/home/myuser/.ssh/id_rsa): ENTER
Enter passphrase (empty for no passphrase): ENTER
Enter same passphrase again: ENTER
Your identification has been saved in /home/myuser/.ssh/id_rsa.
Your public key has been saved in /home/myuser/.ssh/id_rsa.pub.
The key fingerprint is:
e0:71:43:df:ed:40:01:0b:44:54:db:c2:80:f2:33:aa myuser@station
```

The user `myuser` was first prompted for the new (private) key's filename, to which `myuser` simply hit ENTER to accept the default filename: `~/.ssh/id_rsa`. 
**Make sure that you don't override important existed key when you are playing with `ssh-keygen`.**

Next, `myuser` was given the opportunity to attach a passphrase to his private key.
By hitting ENTER again (twice), `myuser` chose not to. 

The private key was generated under `/home/myuser/.ssh/id_rsa`,
while the public key under `/home/myuser/.ssh/id_rsa.pub`.

You should **NEVER** send your private key, not even on a secure channel. 

## Allowing account access: `~/.ssh/authorized_keys`

SSH access to a server is granted by obtaining a copy of the public key of the person who is to be granted access, and storing it in the server's `~/.ssh/authorized_keys` file.
More people can be granted access to an account by simply appending their public keys to the `~/.ssh/authorized_keys` files, one public key per line.

The `~/.ssh/authorized_keys` file, and the whole `~/.ssh` directory, must only be readable by the user.
How the copy of the public key is obtained does not matter. It could be emailed, scped (as discussed in a moment), or transferred from one terminal to another using the mouse's cut and paste buffer.


## Transferring files securely and easily: `scp`

The `scp` command uses a syntax almost identical to the `cp` command, but either the source file(s) or the
destination file can be on a remote machine. 

When referring to a file on a remote machine, the following syntax is used:

```shell
user@host:path
```

As an example, the following command line would transfer the `/etc/services` file from `server1` into the `~/cfg/server1/etc/` directory in `myuser`'s home directory:

```console
[myuser@hostname]$ scp ec2-user@server1:/etc/services cfg/server1/etc/
services    100% |*****************************| 19936      00:00
```

The `-r` command line switch (for "recursive") must be specified when copying an entire directory (and its subdirectories).
In the following, `myuser` recursively copies the `/etc/sysconfig` directory from his local machine to the machine `server1`'s `/tmp` directory:

```console 
[myuser@hostname]$ scp -r /etc/sysconfig ec2-user@server1:/tmp
ifup-aliases    100% |*****************************| 13137  00:00
ifcfg-lo        100% |*****************************| 254    00:00
ifdown          100% |*****************************| 3676   00:00
ifdown-ippp     100% |*****************************| 820    00:00
ifdown-ipv6     100% |*****************************| 4076   00:00
```

# Exercises

Since the essence of SSH is communication between two machines, you will be running a Docker container on your local machine, and communicating with this container from your local machine. If you are not familiar with containers, don't worry, they will be taught later on. For now, think about Docker containers as a small, lightweight OS running within your real OS  (we don't believe we say that… Docker containers are **far away** from being small OS!).

Pre-requisites:

1. Install Docker on your machine if you don't have it yet.
2. Generate RSA key pair using the `ssh-keygen` command.

> [!IMPORTANT]
> Usually the default directory to store keys is the `~/.ssh`. But in this exercise set, you must store the generated key **outside** the `~/.ssh` directory.

3. Run the container by:

```bash
docker run --rm --name=ssh-server -p 2222:2222 -e PASSWORD_ACCESS=true -e USER_PASSWORD=$((RANDOM % 9999)) -e USER_NAME=elvis -e PUBLIC_KEY="$(cat /path/to/your/public-key-file)" -e SUDO_ACCESS=ture lscr.io/linuxserver/openssh-server:latest bash -c "sed -i 's/AllowTcpForwarding no/AllowTcpForwarding yes/g' /etc/ssh/sshd_config &&  nc -l -k 8087"
```

Change `/path/to/your/public-key-file` to the path of your public key.

4. In another terminal session, execute the below command to extract the IP address of your container:

```bash
docker inspect ssh-server | jq -r '.[0].NetworkSettings.IPAddress'
```

Solve the below exercises while the container is running. The IP address you just extracted is the “remote” machine IP that should be used to connect to the machine, the port is 2222, the user is `elvis`.

### :pencil2: Simple connection

Use the `ssh` command to  connect to your machine.

### :pencil2: Port forward

SSH port forwarding allows you to securely tunnel traffic between a local and a remote machine over an encrypted SSH connection, enabling access to remote services as if they were running on the local machine.

Connect to the remote server while forwarding port 8087 from the remote into port 8085 in the local machine.

You can check if the forwarding works properly by running `nc localhost 8085` from your local machine and sending some data to the server (take a look on the server's console output to make sure the data was sent).  


### :pencil2: Add new keys

Generate another RSA key-pair. Allow ssh connection using this new key-pair. The `authorized_keys` file is located in the remote machine under `/config/.ssh/` .

### :pencil2: Change fingerprint

Stop the docker container process (you can do it by CTRL+c), and start again, try to connect again to the remote machine using the ssh command from the previous exercise. What happened, why? How can you fix it?


### :pencil2: Password auth

Password authentication in SSH is the ability to authenticate with a username and password pair. It is not recommended to use password authentication because it is vulnerable to brute-force attacks, where an attacker can repeatedly guess passwords until they gain access to the system. It is safer to use key-based authentication, which is more secure and allows for automated access without exposing passwords.

You know that the password for elvis username is a 4 digit number. Simpliy trying all possible passwords (1000-9999) is the sure way to discover elvis' password. It will take no more than 10 minutes.

1. Try to authenticate without your key-pair. You should see the Password prompt, asking you to insert the password. Try your luck...
2. Install `sshpass` if you don't have one.
3. Execute the below bash script until you find the correct password.

```bash
for i in $(seq 1000 9999); do
  echo trying $i
  sshpass -p $i ssh -o StrictHostKeyChecking=no -p 2222 elvis@<machine-ip>
done
```

While changing `<machine-ip>` to your ip. 

### :pencil2: Change the ssh daemon

To change the SSH daemon configuration, you can modify the `sshd_config` file on the server. This file typically resides in the `/etc/ssh/` directory. 
You can edit this file with `nano` to change various settings such as the port number, authentication methods, and allowed users/groups. 
After making changes to the `sshd_config` file, you'll need to restart the SSH daemon for the changes to take effect. 
Usually it's done by `systemctl restart sshd`, but since you are working on a Docker container, it's done by running the following command **from within the machine**:

```bash
kill -HUP $(cat /config/sshd.pid)
```

Your goal is to configure the `sshd` to not allow password authentication at all!
