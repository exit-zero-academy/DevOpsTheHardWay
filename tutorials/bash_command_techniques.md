# Bash Command Techniques

## Exit status and `$?`

In Unix-like operating systems, every command that is executed returns an exit status to the shell that invoked it. The exit status is a numeric value that indicates the success or failure of the command. A value of 0 indicates success, while a non-zero value indicates failure.

The exit status of the most recently executed command can be accessed via the `$?` variable in Bash.

```console
[myuser@hostname]~$ ls /non-existing-dir
ls: cannot access '/non-existing-dir': No such file or directory
[myuser@hostname]~$ echo $?
2
```

In the above example, if you run a command like `ls /non-existing-dir`, you will receive an error message saying that the directory does not exist, and the exit status will be non-zero. You can access the exit status of this command by typing `echo $?`. The output will be the exit status of the previous command (in this case, the value is 2).
Some common non-zero exit status values include:

- `1`: General catch-all error code
- `2`: Misuse of shell built-ins (e.g. incorrect number of arguments)
- `126`: Command found but not executable
- `127`: Command not found
- `128`+: Exit status of a program that was terminated due to a signal


Explore the man page of the `grep` command. List all possible exit codes, and specify the reason for every exit code.

## Running Multiple Commands (Conditionally)

The bash shell allows users to join multiple commands on a single command line by separating the commands with a `;` (semicolon).

```console
[myuser@hostname]~$ cd /etc/ssh; ls
moduli  	ssh_config.d  sshd_config.d   	ssh_host_ecdsa_key.pub  ssh_host_ed25519_key.pub  ssh_host_rsa_key.pub
ssh_config  sshd_config   ssh_host_ecdsa_key  ssh_host_ed25519_key	ssh_host_rsa_key      	ssh_import_id
[myuser@hostname]/etc/ssh$
```

Nothing special in the above example… just two commands that were executed one after the other. 

The bash shell uses `&&` and `||` to join two commands conditionally. When commands are conditionally joined, the first will always execute. The second command may execute or not, depending on the return value (exit code) of the first command. For example, a user may want to create a directory, and then move a new file into that directory. If the creation of the directory fails, then there is no reason to move the file. The two commands can be coupled as follows:

```console
[myuser@hostname]~$ echo "one two three" > numbers.txt
[myuser@hostname]~$ mkdir /tmp/boring && mv numbers.txt /tmp/boring
```

By coupling two commands with `&&`, the second command will only run if the first command succeeded (i.e., had a return value of 0).

What if the `mkdir` command failed?

Similarly, multiple commands can be combined with `||`. In this case, bash will execute the second command only if the first command "fails" (has a non zero exit code). This is similar to the "or" operator found in programming languages. In the following example, myuser attempts to change the permissions on a file. If the command fails, a message to that effect is echoed to the screen.

```console
[myuser@hostname]~$ chmod 600 /tmp/boring/numbers.txt || echo "chmod failed."
[myuser@hostname]~$ chmod 600 /tmp/mostly/boring/primes.txt || echo "chmod failed"
chmod: failed to get attributes of /tmp/mostly/boring/primes.txt': No such file or directory
chmod failed
```

It’s common in bash scripts to create a directory and immediately `cd` to the directory, if the creations succeeded. Use conditional the `&&` operator to create the dir and cd into it only if the creation succeeded. 

<details>
  <summary>
     Solution
  </summary>

```bash
mkdir newdir && cd newdir
```

</details>

## Command Substitution

Command substitution allows users to run arbitrary commands in a subshell and incorporate the results into the command line. The modern syntax supported by the bash shell is: 

```bash
$(subcommand)
```

As an example of command substitution, `myuser` would like to create a directory that contains the date in its name. After examining the `date(1)` man page, he devises a format string to generate the date in a compact format.

```bash
[prince@station prince]$ date +%d%b%Y
04May2023
```

He now runs the mkdir command, using command substitution.

```bash
[prince@station prince]$ mkdir reports.$(date +%d%b%Y)
[prince@station prince]$ ls
reports.04May2003
```

The bash shell implements command substitution by spawning a new subshell, running the command, recording the output, and exiting the subshell. The text used to invoke the command substitution is then replaced with the recorded output from the command.

# Exercises 

### :pencil2: Code simplification using logical operators

```bash
ls -l /home/user/mydir
if [ $? -eq 0 ]; then
    echo "Directory exists."
else
    echo "Directory does not exist."
fi
```

The above code executes the `ls` command, then uses the `$?` variable along with [if statement](https://tldp.org/LDP/abs/html/fto.html) to test if the directory exists and prints corresponding messages.  
Use `&&` and `||` operators to simplify the script. The simplified code should achieve the same functionality in **one command**!
