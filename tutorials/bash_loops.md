# Bash loops brief

## `for` loops 

`for` loops in Bash are used to iterate over a set of values. Here is the basic syntax of a `for` loop:

```bash
for var in values
do
    # commands
done
```

`var` is a variable that will be set to each value in `values` in turn. `values` can be a list of words separated by spaces, or a command that generates a list of values. Here is an example that prints out the numbers from 1 to 5:

```bash
for i in 1 2 3 4 5
do
    echo $i
done
```

You can also use the `seq` command to generate a sequence of numbers:

```bash
for i in $(seq 1 5)
do
    echo $i
done
```

> #### 🧐 Test yourself 
> 
> Use command substitution `$()` and write a `for` loop that iterates over the files in your home directory.

## `while` loops 

`while` loops in Bash are used to repeat a block of commands as long as a certain condition is true (ends with exit code 0). Here is the basic syntax of a `while` loop:

```bash
while condition
do
    # commands
done
```

`condition` is a command or expression that returns either 0 (true) or non-zero (false). Here is an example that prints out the numbers from 1 to 5 using a `while` loop:

```bash
i=1
while [ $i -le 5 ]
do
    echo $i
    let i=$i+1
done
```

In this example, `i` is initialized to 1, and the loop continues as long as `i` is less than or equal to 5. `i` is incremented by 1 using the expression `let i=$i+1`.

# Exercises 

### :pencil2: Blur an image

Create a script called `blur.sh`, which can be used to blur images. 
Use the `convert` command for the actual image processing.
The script should expect as arguments multiple filenames of the images to be blurred. 
You need to test that the file content is indeed an image (`file` or `stat`).
The script should generate a new file of the blurred image, and if the new image is successfully generated, replace the original image with the blurred one.


### :pencil2: Bad elusive command

Say you have a command that fails rarely.
In order to debug it you need to capture its output, but it can be time consuming to get a failure run.
Write a bash script that runs the following script until it fails and captures its standard output and error streams to files and prints everything at the end. 
Report how many runs it took for the script to fail.

```bash
#!/bin/bash

n=$(( RANDOM % 100 ))
if [[ n -eq 42 ]]; then
   echo "Something went wrong"
   exit 1
fi

echo "Everything went according to plan"
```
