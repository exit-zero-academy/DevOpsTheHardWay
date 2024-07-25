# Bash Conditional Statement

## The if-else statement

Sometimes you need to specify different courses of action to be taken in a shell script, depending on the success or failure of a command. The if construction allows you to specify such conditions.

The most common syntax of the if command is:

```bash
if TEST-COMMAND
then
  POSITIVE-CONSEQUENT-COMMANDS
else
  NEGATIVE-CONSEQUENT-COMMANDS
fi
```

This is a conditional statement in Bash that consists of a `TEST-COMMAND`, followed by a positive consequent command block (`POSITIVE-CONSEQUENT-COMMANDS`), and an optional negative consequent command block (`NEGATIVE-CONSEQUENT-COMMANDS`). If the `TEST-COMMAND` is successful (returns an exit status of 0), then the positive consequent commands are executed, otherwise, the negative consequent commands (if provided) are executed. The `if` statement is terminated with the `fi` command.

### Testing files

**Before you start, review the man page of the `test` command.**

The first example checks for the existence of a file:

```bash
echo "This script checks the existence of the messages file."
echo "Checking..."
if [ -f /var/log/messages ]
then
  echo "/var/log/messages exists."
fi
echo
echo "...done."
```


> 🧐 What is the relation between the `test` command and `[`?

### Testing Exit Status

Recall that the $? variable holds the exit status of the previously executed command. The following example utilizes this variable to make a decision according to the success or failure of the previous command:

```bash
curl google.com &> /dev/null

if [ $? -eq 0 ]
then
  echo "Request succeeded"
else
  echo "Request failed, trying again..."
fi
```

### Numeric Comparisons

The below example demonstrates numeric comparison between a variable and 20. 
Don't worry is it doesn't work, you'll fix it soon 🙂

```bash
num=$(wc -l /etc/passwd)
echo $num

if [ "$num" -gt "20" ]; then
  echo "Too many users in the system."
fi
```

> #### 🧐 Test yourself
> 
> Copy the above script to a `.sh` file, and execute. Debug the script until you understand why the script fails. Use the `awk` command to fix the problem. Tip: using the `-x` flag can help you debug your bash run: `bash -x myscript.sh`
> 


### String Comparisons

```bash
if [[ "$(whoami)" != 'root' ]]; then
  echo "You have no permission to run $0 as non-root user."
  exit 1;
fi
```

### if-grep Construct

```bash
echo "Bash is ok" > file

if grep -q Bash file
then
  echo "File contains at least one occurrence of Bash."
fi
```

Another example:

```bash
word=Linux
letter_sequence=inu

if echo "$word" | grep -q "$letter_sequence"
# The "-q" option to grep suppresses output.
then
  echo "$letter_sequence found in $word"
else
  echo "$letter_sequence not found in $word"
fi
```

## `[...]` vs `[[...]]`

With version 2.02, Bash introduced the `[[ ... ]]` extended test command, which performs comparisons in a manner more familiar to programmers from other languages. The `[[...]]` construct is the more versatile Bash version of `[...]`. Using the `[[...]]` test construct, rather than `[...]` can prevent many logic errors in scripts.

# Exercises 

### :pencil2: Availability test script

The `curl` command can be used to perform a request to an external website and return the response's [status code](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status): 

```bash
curl -o /dev/null -s -w "%{http_code}" www.google.com
```

This `curl` command suppresses output (`-o /dev/null`), runs silently without printing the traffic progress (`-s`), and prints the HTTP status code (`-w "%{http_code}"`).

Create an `availability_test.sh` script that receives an address as the 1st (and only) argument, and perform the above `curl` command. 
The script should be completed successfully if the returned HTTP status code is `< 500`, 
or fail otherwise (you can exit the script with `exit 1` to indicate failure). 

Here is the expected behaviour:

```console
myuser@hostname:~$ ./availability_test.sh www.google.com
www.google.com is up!
myuser@hostname:~$ ./availability_test.sh http://cnn.com
http://cnn.com is up!
myuser@hostname:~$ ./availability_test.sh abcdefg
abcdefg is not available.
myuser@hostname:~$ echo $?
1
myuser@hostname:~$ ./availability_test.sh
A valid URL is required
myuser@hostname:~$ ./availability_test.sh google.com cnn.com
The script is expected a single argument only, but got 2.
myuser@hostname:~$ ./availability_test.sh httpbin.org/status/500   # this url should return a status code of 500
httpbin.org/status/500 is not available.
```

### :pencil2: Geo-location info

Write a bash script `geo_by_ip.sh` that, given an ip address, prints geo-location details, as follows:
1. The script first checks if `jq` cli is installed. If not installed, it prints a message to the user with a link to download the tool: https://stedolan.github.io/jq/download/
1. The script checks that **exactly one argument** was sent to it, which represents the ip address to check. Otherwise, an informative message is printed to stdout.
1. The script checks that the given IP argument is not equal to `127.0.0.1`.
1. The script performs an HTTP GET request to `http://ip-api.com/json/<ip>`, where `<ip>` is the IP argument. The results should be stored in a variable.
1. Using the jq tool and the variable containing the HTTP response, check that the request has succeeded by checking that the `status` key has a value of `success`. The command `jq -r '.<key>'` can extract a key from the json (e.g. `echo $RESPONSE | jq -r '.status'`)
1. If the request succeed, print the following information to the user:
    - country
    - city
    - regionName



