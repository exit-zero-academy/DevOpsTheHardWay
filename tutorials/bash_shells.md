# Shells

## Motivation for bash scripting

Bash, or the Bourne-Again SHell, is a widely-used Unix shell and command language that provides a powerful command-line interface for interacting with the operating system.

Learning Bash can help you:

-  Make life easier on UNIX or UNIX-like system
-  Ease execution of daily tasks
-  Automate important operation tasks

Overall, learning Bash can help you to become a more efficient and effective system administrator, developer, or data analyst.

The UNIX shell program interprets user commands to the kernel, which are either directly entered by the user, or which can be read from a file called the **shell script**. Apart from passing commands to the kernel, the main task of a shell is providing a **user environment**, which can be configured individually using shell resource configuration files.

The example below shows the evolution of a bash program, just take a look, you don't need to execute it. It starts simply by grouping a few commands into a file, without any error handling and flow control... until it forms a well written professional script.

### From commands to Bash program

Consider the below script to clean up log files (`messages`, `wtmp`) in `/var/log`. 

```bash
# Run as root, of course.
cd /var/log
cat /dev/null > messages
cat /dev/null > wtmp
echo "Log files cleaned up."
```

There is nothing unusual here, only a set of commands that could just as easily have been invoked one by one. Is this a script? Maybe...Is this a program? Not yet...

Let's try again...

```bash
# Proper header for a Bash script.
#!/bin/bash

# Run as root, of course.
LOG_DIR=/var/log   # Variables are better than hard-coded values.

cd $LOG_DIR
cat /dev/null > messages
cat /dev/null > wtmp
echo "Logs cleaned up."

exit # The right and proper method of "exiting" from a script.
# A bare "exit" (no parameter) returns the exit status of the preceding command.
```

Now that's beginning to look like a real script. But we can go even farther...

The following script uses quite a number of features that will be explained later on.

```bash
#!/bin/bash
LOG_DIR=/var/log
ROOT_UID=0 	# Only users with $UID 0 have root privileges.
LINES=50   	# Default number of lines saved.

E_XCD=86   	# Can't change directory?
E_NOTROOT=87   # Non-root exit error.


# Run as root, of course.
if [ "$UID" -ne "$ROOT_UID" ]
then
  echo "Must be root to run this script."
  exit $E_NOTROOT
fi

if [ -n "$1" ]  # Test whether command-line argument is present (non-empty).
then
  lines=$1
else
  lines=$LINES  # Default, if not specified on command-line.
fi

cd $LOG_DIR
if [ `pwd` != "$LOG_DIR" ] # or if [ "$PWD" != "$LOG_DIR" ]
                       	# Not in /var/log?
then
  echo "Can't change to $LOG_DIR."
  exit $E_XCD
fi # Doublecheck if in right directory before messing with log file.


tail -n $lines messages > mesg.temp  # Save last section of message log file.
mv mesg.temp messages            	# Rename it as system log file.
cat /dev/null > wtmp

echo "Log files cleaned up."
exit 0
```

## Shell types 

Let's recall the 2 main shells we usually work with in Linux system:

- `sh` or Bourne Shell: the original shell still used on UNIX systems.
- `bash` or Bourne Again shell: the standard GNU shell, intuitive and flexible. Probably most advisable for beginner users, while at the same time a powerful tool for the advanced and professional user. On Linux, bash is the standard shell for common users.

The file `/etc/shells` gives an overview of known shells on a Linux system:

```bash
cat /etc/shells
```

Here is an example of a shell called [Restricted Bash](https://tldp.org/LDP/abs/html/restricted-sh.html):

```bash
rbash 	# this command creates a new terminal session of restricted bash which may be looked exactly like bash terminal
cd /var
```

Was the last command successful? What can you conclude about `rbash`?

Your default shell is set in the `/etc/passwd` file for each user.

```bash
# to know your current Linux user, echo the following environment variable
echo $USER
cat /etc/passwd | grep $USER
```

## Which shell should execute the script?

When running a script in a subshell, you should define which shell should run the script. The shell type in which you wrote the script might not be the default on your system, so commands you entered might result in errors when executed by the wrong shell.

The **sha-bang (#!)** at the head of a script tells your system that this file is a set of commands to be fed to the command interpreter indicated.

Note that the path given at the "sha-bang" must be correct, otherwise an error message -- usually "Command not found." -- will be the only result of running the script.

Copy and execute the following snippet to a `myscript.sh` file in your local Linux machine.

```bash
#!/bin/bash

ls
cd /var
```

Test the above script with `/bin/sh` as the sha-bang shell. Add an `echo` command to print some environment variable that will indicate the shell that is currently running the program.

## Run bash programs 

Having written a bash script, you can invoke it in two ways:

- `./myscript.sh` - This is the method we’ve seen so far. It runs the script as an executable file, using the interpreter specified in the shebang line. If the script is not marked as executable, you will get a "Permission denied" error.
- `bash myscript.sh` - This explicitly runs the script using the bash shell, regardless of the shebang line (`#!/bin/bash`) at the beginning of the script. This means that even if the script is not marked as executable (`chmod +x myscript.sh`), you can still run it.


## Bash system-wide configuration files

Before we begin, it is important to distinguish between subtly different types of shells: login and non-login shells, and interactive and non-interactive shells.

- A **login shell** is executed only after a user logs into the system.
- A **non-login shell** is started within a user's current session (shells that are spawned from within an existing shell session).
- An **interactive shell** allows the user to interact with the system through a command-line interface.
- A **non-interactive shell** is not designed for user interaction and is typically used for running scripts or commands in the background.

> #### 🧐 Test yourself
> 
> Consider the below terminal session:
> 
> ```bash
> 1 myuser@hostname:~$ su -l john
>   Password: [PASSWORD ENTERED] 
>   john@hostname:~$ echo $USER
>   john
> 2 john@hostname:~$ rbash
> 3 john@hostname:~$ sh -c 'echo hi'
> ```
> 
> For each of lines 1, 2, and 3, determine the shell type: login/non-login, and interactive/non-interactive. 

Bash configuration files are scripts that are executed when a Bash shell is started (or ends). These scripts define the initial **environment and behavior of the shell**. There are several Bash startup scripts that can be used to configure the Bash shell. Here are some of the most commonly used Bash startup scripts:

1. `/etc/profile`: This script is executed by all login shells (sh, bash etc..) when a user logs in to the system. It sets environment variables, adds directories to the PATH, and performs other **system-wide** configuration tasks.
1. `/etc/profile.d/*.sh`: This directory contains additional shell scripts that are `source`d by `/etc/profile` if they exist. These scripts can be used to add environment variables, aliases, or other settings that are specific to a particular application or package.
1. `/etc/bash.bashrc`: This script is executed by all Bash shells that are not login shells. It sets system-wide Bash settings.
1. `/etc/bash_profile`: This script is executed by login shells after `/etc/profile`. It can be used to override or extend the settings in `/etc/profile`, or to perform user-specific configuration tasks.

## Bash user-wide configuration files

Bash user-wide configuration files are scripts that are executed by Bash each time a user logs in. These files are located in the user's home directory and are used to customize the user's shell environment. Here are some common Bash user-wide configuration files:\

1. `~/.bash_profile`: This is the primary Bash user configuration file. It is executed when the user logs in and sets up the user's environment.
1. `~/.bashrc`: This file is executed by Bash for each interactive non-login shell. It is used to set up aliases, functions, and other settings for the user's shell.
1. `~/.bash_login`: This file is executed after `~/.bash_profile` if it exists. It is used to provide additional configuration settings.
1. `~/.profile`: This file is executed by the command interpreter for login shells. It is used to set environment variables and to execute commands that should be run for login shells.

These configuration files allow users to customize their shell environment to their specific needs, including setting aliases, modifying the prompt, and configuring other settings.

> #### 🧐 Test yourself 
> 
> The `ll` command is a commonly used alias for  `ls -l`. Try it yourself…
> 
> Open the `~/.bashrc` file using your favorite  text editor (e.g. `nano`) and search this alias definition. Add another alias of your own. 


# Exercises 

### :pencil2: Read-only Environment Variable for all Shells

Create a read-only environment variable that is accessible to all users and all shells on the system. Under `/etc/profile.d` dir, create your script that defines the variable (any var name and value you wish). Then, use the `readonly` command to make the variable read-only so that it cannot be modified by any user or process on the system. Finally, verify that the variable is read-only by attempting to modify its value from your user shell (re-login is needed).

### :pencil2: Connect to user-friendly users

Attempt to log in to the `nobody` user on an **Ubuntu system** (the root account is able to connect to every user without providing the users’ password). 
Observe the message that is displayed and identify the reason for it.
Which shell does the `nobody` user use?

### :pencil2: The root user command prompt in the `sh` shell

1. Open a terminal and start a `sh` session as the root user:  `sudo sh`.
1. Note that the prompt is “#”. Exit the session.
1. Open a terminal and start a `sh` session as your user (assuming you are not root): `sh`.
1. How does the prompt look like? It should be different from the root’s prompt. 

Take a look in the content of `/etc/profile` and search (even if you’re still not familiar with all the code elements there) for the code that defines the shell prompt for root and non-root users. 

Which env var defines the shell prompt? Try to change this variable in your current terminal session and see what happens.


