# Bash Variables

Variables are how programming and scripting languages represent data. 
A variable is nothing more than a **label**, a name assigned to a location or set of locations in computer memory holding an item of data. As seen in previous examples, shell variables are in uppercase characters by convention.

Let us carefully distinguish between the name of a variable and its value.
If `variable1` is the name of a variable, then `$variable1` is a reference to its value, the data item it contains.

```bash
variable1=23
echo variable1
echo $variable1
```

No space permitted on either side of = sign when initializing variables. What happens if there is a space?

```bash
VARIABLE =value
VARIABLE= value
VARIABLE = value
```


## Assigning and referencing variables

Below are a few examples of variable referencing.
Try them out and make sure you understand each one of the cases.

```bash
A=375
HELLO=$A

echo HELLO      # HELLO
echo $HELLO     # 375
echo ${HELLO}   # 375
echo "$HELLO"   # 375
echo "${HELLO}" # 375
echo "Oh, I like them squishy" >> ode_to_$A.txt # ode_to_375.txt was created
              
# Variable referencing disabled (escaped) by single quotes
echo '$HELLO'
```

There are [MUCH more](https://tldp.org/LDP/abs/html/parameter-substitution.html#PARAMSUBREF) functionalities.

#### Bash variables are untyped

Unlike many other programming languages, Bash does not segregate its variables by "type." 
Essentially, Bash variables are character strings, but, depending on context, Bash permits arithmetic operations and comparisons on variables.
The determining factor is whether the value of a variable contains only digits.

```bash
a=879
echo "The value of \"a\" is $a."

a=16+5
echo "The value of \"a\" is now $a."
```

#### Assignment using `let`

```bash
let a=16+5
echo "The value of \"a\" is now $a."
```

#### Variable assignment using the commands substitution - `$(...)`

```bash
R=$(cat /etc/profile)
arch=$(uname -m)
echo $R
echo $arch
```

#### Variable reference using curly braces - `${...}`

Consider the below example:

```console
myuser@hostname:~$ ls
hello_world.txt
myuser@hostname:~$ echo $A
hola
myuser@hostname:~$ echo "filename language changed!" > $A_world.txt
myuser@hostname:~$ ls
hello_world.txt
myuser@hostname:~$ ls -a
hello_world.txt        .txt
```

Where is the file `hola_world.txt`? A couple of things have been mistakenly done by `myuser`! 
First, the bash shell dereferenced the correct variable name, but not the one that `myuser` intended. 
The bash shell resolved the (uninitialized) variable A_world (to nothing), and created the resulting file `.txt`. Secondly, because `.txt` starts with a `.`, it is a "hidden file", as the `ls -a` command reveals.

Let's utilize the curly braces reference syntax to resolve `myuser`'s problems: 

```console
myuser@hostname:~$ echo "filename language changed!" > ${A}_world.txt
myuser@hostname:~$ ls
hello_world.txt       hola_world.txt       .txt
```

When finished with a variable, the variable may be unbound from its value with the `unset` command.

```console
myuser@hostname:~$ unset A
myuser@hostname:~$ echo $A

myuser@hostname:~$
```

## Script positional variables

Positional arguments are arguments passed to a command or script in a specific order, usually separated by spaces. Positional arguments can be accessed, within a bash script file, using special variables such as `$1`, `$2`, `$3`, and so on, where `$1` refers to the first argument, `$2` refers to the second argument, and so on.

Let's see them in action... create a file called `BarackObama.sh` as follows:

```bash
#!/bin/bash

# This script reads 3 positional parameters and prints them out.

echo "$0 invoked with the following arguments: $@"

POSPAR1="$1"
POSPAR2="$2"
POSPAR3="$3"

echo "$1 is the first positional parameter, \$1."
echo "$2 is the second positional parameter, \$2."
echo "$3 is the third positional parameter, \$3."
echo
echo "The total number of positional parameters is $#."

if [ -n "${10}" ]               # Parameters > $9 must be enclosed in {brackets}.
then
  echo "Parameter #10 is ${10}"
fi
```

Execute the script by:

```bash
bash positional.sh Yes We Can 
bash positional.sh Yes We Can bla bla 1 2 3
```

Investigate the script output and make sure you understand each variable. 

## Special bash variables

Special bash variables are built-in variables that hold information about the shell environment and provide useful information for shell scripting.

- `$@` - Expands to the positional parameters, starting from one.
- `$#` - Expands to the number of positional parameters in decimal.
- `$?` - Expands to the exit status of the most recently executed foreground pipeline.
- `$$` - Expands to the process ID of the shell.
- `$0` - Expands to the name of the shell or shell script.
- `$*`  - Expands to all the positional parameters passed to the script or function as a single word

## Variable expansion

Variable expansion is a feature in Bash that allows you to manipulate a variable's value when referencing it. Here are a few basic examples:

#### Default assignment

```bash
${VAR:-word}
```

If `VAR` is unset or null, the expansion of `word` is substituted.  Otherwise, the value of `VAR` is used.

```console
myuser@hostname:~$ VAR=123
myuser@hostname:~$ echo ${VAR:-undefinedValue}
123
myuser@hostname:~$ unset VAR
myuser@hostname:~$ echo ${VAR:-undefinedValue}
undefinedValue
myuser@hostname:~$ echo $VAR
undefinedValue
```

#### Default error message

```bash
${VAR:?word}
```

If `VAR` is null or unset, the expansion of `word` is written to the standard error and the shell, if it is not interactive, exits.

```console
myuser@hostname:~$ VAR=
myuser@hostname:~$ echo ${VAR:?VAR is unset or null}
myuser@hostname:~$ echo $?
```

#### Variable substring

```bash
${parameter:offset}
${parameter:offset:length}
```

This expansion allows you to extract a portion of a string variable based on a specified index and length.

```console
$ string=01234567890abcdefgh
$ echo ${string:7}
7890abcdefgh
$ echo ${string:7:0}

$ echo ${string:7:2}
78
$ echo ${string:7:-2}
7890abcdef
$ echo ${string: -7}
bcdefgh
$ echo ${string: -7:0}

$ echo ${string: -7:2}
bc
```

#### String length

```bash
${#parameter}
```

The length of characters of the expanded value of `parameter` is substituted.

There are [many more](https://tldp.org/LDP/abs/html/parameter-substitution.html) of them!

# Exercises 

### :pencil2: Dated copy

Create a script that takes a valid file path as the first argument and creates a dated copy of the file. 
For example:

```console
myuser@hostname:~$ ./datedcp.sh myfile.txt
myuser@hostname:~$ ls
2022-04-30_myfile.txt
```

### :pencil2: Theater night out booking system

In our course repo, copy the file under `theatre_nighout/init.sh` into an empty directory and execute it.
This script creates 5 directories, each for a famous theater show. 
In each directory there are 50 files, representing 50 available seats for the show.
Create a bash script `available_seat.sh` that takes one argument which is the name of a show and prints the available seats for the show (by simply using `ls` command).
Create another bash script `booking.sh` that takes two arguments - the name of a show and a seat number. 

The selected seat should be marked as booked by deleting the file that represents the seat number.
You should print an informative message to the user upon successful or failed booking.

You can always re-run `init.sh` to test your script again. 

For example:

```console
$ ./init.sh && cd shows
$ ./available_seat.sh Hamilton
Available seats for Hamilton:
1 2 3 4 5 6 7 8 9 10 ... 48 49 50
$ ./booking.sh Hamilton 5
Seat 5 for Hamilton has been booked!
$ ./available_seat.sh Hamilton
Available seats for Hamilton:
1 2 3 4 6 7 8 9 10 ... 48 49 50
$ ./booking.sh Hamilton 5
Error: Seat 5 for Hamilton is already booked!
```

