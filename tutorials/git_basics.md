# Git Version Control System (VCS)

This tutorial summarizes the great [ProGit book](https://git-scm.com/book/en/v2) written by Scott Chacon and Ben Straub and published by Apress.

## The idea of version control system 

What is "version control", and why should you care? Version control is a system that records changes to a file or set of files over time so that you can recall specific versions later. 

It allows you to revert selected files back to a previous state, revert the entire project back to a previous state, compare changes over time, see who last modified something that might be causing a problem, who introduced an issue and when, and more. 


Many people's version-control method of choice is to copy files into another directory (perhaps a time-stamped directory, if they're clever). This approach is very common because it is so simple, but it is also incredibly error prone. It is easy to forget which directory you're in and accidentally write to the wrong file or copy over files you don't mean to.

To deal with this issue, programmers long ago developed local Version Control Systems (VCSs) that had a simple database that kept all the changes to files under revision control.

![][git_vcs1]


The next major issue that people encounter is that they need to collaborate with developers on other systems.
To deal with this problem, Distributed Version Control Systems (DVCSs), such as Git were developed. 
These systems have a remote server(s) that contains all the versioned files, and a number of clients hold fully mirror the repository locally, including its full history.
Thus, if any server dies, any of the client repositories can be copied back up to the server to restore it. Every clone is really a full backup of all the data.

![][git_vcs2]


## Introducing Git

So, what is Git in a nutshell? This is an important section to absorb, because if you understand what Git is and the fundamentals of how it works, then using Git effectively will probably be much easier for you.

### Snapshots, not differences

Git thinks of its data like a **series of snapshots** of a miniature filesystem.
Every time you commit, or save the state of your project, Git basically takes a picture of what all your files look like at that moment and stores a reference to that snapshot. 
To be efficient, if files have not changed, Git doesn't store the file again, just a **link** to the previous identical file it has already stored. 
Git thinks about its data more like a stream of snapshots.

![][git_versions]

In the above figure, dashed files are just links to their previous versions since they have not been changes since then.


## The three states

Pay attention now - here is the main thing to remember about Git if you want the rest of your learning process to go smoothly. Git has three main states that your files can reside in: **modified**, **staged**, and **committed**:

- Modified means that you have changed the file but have not committed it to your database yet. 
- Staged means that you have marked a modified file in its current version to go into your next commit snapshot. 
- Committed means that the data is safely stored in your local database.

This leads us to the three main sections of a Git project: the working tree, the staging area, and the Git directory.

![][git_areas]


The working tree is a single checkout of one version of the project. These files are pulled out of the compressed database in the Git directory and placed on disk for you to use or modify.

The staging area is a file, generally contained in your Git directory, that stores information about what will go into your next commit. Its technical name in Git parlance is the "index", but the phrase "staging area" works just as well.

The Git directory is where Git stores the metadata and object database for your project. This is the most important part of Git, and it is what is copied when you `clone` a repository from another computer.



The basic Git workflow goes something like this:

- You modify files in your working tree. 
- You selectively stage just those changes you want to be part of your next commit, which adds only those changes to the staging area.
- You do a commit, which takes the files as they are in the staging area and stores that snapshot permanently to your Git directory.

If a particular version of a file is in the Git directory, it's considered **committed**.
If it has been modified and was added to the staging area, it is **staged**.
And if it was changed since it was checked out but has not been staged, it is **modified**.

We will see it in action soon!

## Getting a git repository

You typically obtain a Git repository by cloning an existing repository from somewhere.

**Clone** is the process of getting a copy of an existing Git repository.

```bash
git clone https://github.com/exit-zero-academy/NetflixMovieCatalog
```

> [!NOTE]
> **You have to execute this command from a directory which is not a Git project itself.** 

That creates a directory named `NetflixMovieCatalog`, initializes a `.git` directory inside it (this what turns the directory into "Git repo"), pulls down all the data for that repository, and checks out a working copy of the latest version. If you go into the new `NetflixMovieCatalog` directory that was just created, you'll see the project files in there, ready to be worked on or used.

Git has a number of different transfer protocols you can use. The previous example uses the `https://` protocol, but you may also `git@github.com:exit-zero-academy/NetflixMovieCatalog.git`, which uses the SSH transfer protocol.

> [!NOTE]
> You can also initialize a fresh Git repo locally. 
> If you have a project directory that is currently not under version control and you want to start controlling it with Git, you first need to go to that project's directory.
> 
> ```bash 
> cd /home/user/my_project
> git init
> ```
> 
> At this point, nothing in your project is tracked yet. 



### Recording changes to the repository

If you want to start version-controlling files, use the `add` and `commit` commands. 

```bash
# create files
touch myfile.txt myfile2.txt

# stage it
git add myfile.txt
git add myfile2.txt

# commit your stages changes
git commit -m 'my first commit in git tutorial'
```

Typically, you'll want to start making changes and committing snapshots of your changes into your repository each time the project reaches a state you want to record.

Remember that each file in your working directory can be in one of two states: **tracked** or **untracked**.
Tracked files are files that Git knows about. Untracked files are everything else - any files in your working directory that were not in your last snapshot and are not in your staging area.

As you work, you selectively stage your modified files and then commit all those staged changes, and the cycle repeats.

![][git_areas2]

### Checking the status of your files

The main tool you use to determine which files are in which state is the `git status` command. 
If you run this command directly after a clone, or just committed repo, you should see something like this:

```console
$ git status
On branch master
nothing to commit, working tree clean
```

This means you have a clean working directory.

### Tracking new files

Let's say you add a new file to your project, a simple `README` file.
If the file didn't exist before, and you run `git status`, you see your untracked file like so:

```console
$ echo 'This is a simple Netflix movies catalog API' > README
$ git status
On branch master
Untracked files:
  (use "git add <file>..." to include in what will be committed)

    README

nothing added to commit but untracked files present (use "git add" to track)
```

Untracked basically means that Git sees a file you didn't have in the previous snapshot (commit), and which hasn't yet been staged.

Let's start tracking the `README` file:

```console
$ git add README
```


If you run your status command again, you can see that your `README` file is now tracked and staged to be committed:

```console
$ git status
On branch master
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)

    new file:   README
```

You can tell that it's staged because it's under the "Changes to be committed" heading.

### Staging modified files

Let's change a file that was already tracked. 
If you change a previously tracked file called `myfile.txt` and then run your `git status` command again, you get something that looks like this:

```console
$ echo "hi" >> myfile.txt
$ git status
On branch master
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    new file:   README

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

    modified:   myfile.txt
```

Let's run `git add` now to stage the `myfile.txt` file, and then run `git status` again:

```console
$ git add myfile.txt
$ git status
On branch master
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    new file:   README
    modified:   myfile.txt
```

Both files are staged and will go into your next commit.

At this point, suppose you remember one little change that you want to make in `myfile.txt` before you commit it.
You open it again and make that change, and you're ready to commit.
However, let's run `git status` one more time:

```console
$ echo "hi again" >> myfile.txt
$ git status
On branch master
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    new file:   README
    modified:   myfile.txt

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

    modified:   myfile.txt
```

It turns out that Git stages a file exactly as it is when you run the `git add` command.

If you commit now, the version of `myfile.txt` as it was when you last ran the `git add` command is how it will go into the commit, not the version of the file as it looks in your working directory when you run `git commit`.


### Ignoring files

Often, you'll have a class of files that you don't want Git to automatically add or even show you as being untracked. 
These are generally automatically generated files such as log files or files produced by your build system. 
In such cases, you can create a file listing patterns to match them named `.gitignore`. 
Here is an example `.gitignore` file:

```console
$ cat .gitignore
__pycache__/
.venv
venv/
.idea/
```

You should `add` and `commit` the `.gitignore` file. 

GitHub maintains a fairly comprehensive list of good `.gitignore` file examples for dozens of projects and languages at https://github.com/github/gitignore if you want a starting point for your project.

### Viewing your staged and unstaged changes

What have you changed but not yet staged? And what have you staged that you are about to commit?

If you want to know exactly what you changed, not just which files were changed - you can use the `git diff` command.

To see what you've **changed** but not yet **staged**, type `git diff` with no other arguments:

```console
$ git diff
diff --git a/myfile.txt b/myfile.txt
index 45b983b..f5f1de4 100644
--- a/myfile.txt
+++ b/myfile.txt
@@ -1 +1,2 @@
 hi
+hi again
```

That command compares what is in your working directory with what is in your staging area.

If you want to see what you've staged that will go into your next commit, you can use `git diff --staged`.

```console
$ git diff --staged
diff --git a/README b/README
new file mode 100644
index 0000000..56266d3
--- /dev/null
+++ b/README
@@ -0,0 +1 @@
+This is a simple Netflix movies catalog API
diff --git a/myfile.txt b/myfile.txt
index e69de29..45b983b 100644
--- a/myfile.txt
+++ b/myfile.txt
@@ -0,0 +1 @@
+hi
```

Let's stage all your changes:

```console
$ git add README myfile.txt
```

### Committing your changes

Now that your staging area is set up the way you want it, you can commit your changes.

```console
$ git commit -m "Add README to the project"
[master 14e3493] Add README to the project
 2 files changed, 3 insertions(+)
 create mode 100644 README
```

You can see that the commit has given you some output about itself: which branch you committed to (`master`), what SHA-1 checksum the commit has (`14e3493`), how many files were changed, and statistics about lines added and removed in the commit.

Every time you perform a commit, you're recording a snapshot of your project that you can revert to or compare to later.

### Removing files

To remove a file from Git, you have to remove it from your tracked files (more accurately, remove it from your staging area) and then commit.

```console
$ rm myfile.txt
$ git add myfile.txt
$ git status
On branch master
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	deleted:    myfile.txt
```

**Tip**: The `git rm` command does `rm` and `git add` for you, so you don't need to execute 2 different commands whenever you want to remove a file.

The next time you commit, the file will be gone and no longer tracked.

## Viewing the commit history

The most basic and powerful tool to look back in the commit history is the `git log` command:

```console
$ git log
commit ca82a6dff817ec66f44342007202690a93763949
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Mon Mar 17 21:52:11 2008 -0700

    Change version number

commit 085bb3bcb608e1e8451d4b2432f8ecbe6306e7e7
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Sat Mar 15 16:40:33 2008 -0700

    Remove unnecessary test

commit a11bef06a3f659402fe7563abf99ad00de2209e6
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Sat Mar 15 10:31:28 2008 -0700

    Initial commit
```

As you can see, this command lists each commit with its **SHA-1 checksum**, the **author's name and email**, the **date** written, and the **commit message**.

## Tagging

Typically, developers use tags functionality to mark release points (`v1.0`, `v2.0` and so on). 

```console 
$ git tag
v1.0
v2.0
```

This command lists the tags in alphabetical order.

Git supports two types of tags: **lightweight** and **annotated**.

### Lightweight tags

A lightweight tag is just a **pointer** to a specific commit.
To create a lightweight tag, just provide a tag name:

```console 
$ git tag v1.4-lw
```

### Annotated tags

Annotated tag is very much like a commit object - it's checksummed, contain the tagger name, email, and date; have a tagging message.
To create an annotated tag, provide the `-a` flag and a tag message:

```console
$ git tag -a v1.4 -m "my version 1.4"
```

You can see the tag data along with the commit that was tagged by using the `git show` command:

```console
$ git show v1.4
tag v1.4
Tagger: Ben Straub <ben@straub.cc>
Date:   Sat May 3 20:19:12 2014 -0700

my version 1.4

commit ca82a6dff817ec66f44342007202690a93763949
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Mon Mar 17 21:52:11 2008 -0700

    Change version number
```

> [!NOTE]
> By default, the `git push` command doesn't transfer tags to remote servers.
> You will have to explicitly push tags to a shared server after you have created them by `git push .... --tags`


# Exercises 

### :pencil2: Unmodifying a modified file 

1. In your Git repo, modify some of the committed files. 
2. Now you realize that you don't want to keep your changes, how to revert it back to what it looked like when you last committed?
3. Now modify some of the committed file and stage it. 
4. How to unstage and revert it back to what it looked like when you last committed?

### :pencil2: Add to `.gitignore` after commit

Create a file with `.mp4` extension and commit it. 

Now you realize that you need add files with `.mp4` extensions to the `.gitignore`. 

How can you do it?

### :pencil2: Checking out tags

Your local `NetflixMovieCatalog` repo has a tag `v1.0.0`.

Let's say that you want to develop a new version of the app, starting from the point where the repo was tagged by `v1.0.0`.

You can checkout this tag by:

```bash
git checkout v1.0.0
```

Then make a few more commits, and go back to the "tip" of your main branch by:

`git checkout main`

Use `git log` to determine what happened to the commits you've just created?  
What are the ill side effects when you put your repository in **detached HEAD** state?

![][git_deatched_head]


[git_vcs1]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_vcs1.png
[git_vcs2]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_vcs2.png
[git_versions]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_versions.png
[git_areas]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_areas.png
[git_areas2]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_areas2.png
[git_deatched_head]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_deatched_head.gif