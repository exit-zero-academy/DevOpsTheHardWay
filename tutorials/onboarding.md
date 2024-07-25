# Course Onboarding

## TL;DR

Onboarding steps:

- [Git](#git) and [GitHub account](#GitHub)
- [Ubuntu Desktop workstation](#linux-operating-system)
- [AWS account](#aws-account)
- [PyCharm (or any other alternative)](#pycharm)
- [Clone the course repo](#clone-the-course-repository-into-pycharm)

## GitHub

The website you are visiting now is called **GitHub**.
It's a platform where millions of developers from all around the world collaborate on projects and share code. 

Each project on GitHub is stored in something called a **Git repository**, or **repo** for short. 
A Git repository is like a folder that contains all the files and resources related to a project.
These files can include code, images, documentation, and more.

The content of this course, including all code files, tutorials, and projects, are also stored and provided to you as a Git repo.

If you haven't already, please create a [GitHub account](https://github.com/).

## Linux Operating System

In this course, we'll be using the Linux Operating System (**OS**). Windows won't be part of the party...

Linux comes in various [distributions](https://en.wikipedia.org/wiki/Linux_distribution). 
We will be using **Ubuntu**, a widely-recognized Linux distribution known for its user-friendliness, stability, and extensive community support. 

The course materials were developed and tested with **Ubuntu 22.04** and **24.04**.
For the optimal experience, we recommend using one of these versions.

Below are the methods to install Ubuntu based on your preference:

#### Virtualized Ubuntu using Hyper-V Manager (Windows Users)

For Windows users, an effective way to run Ubuntu is by installing it on a virtual machine (VM) using **Hyper-V Manager**.
This allows you to run Ubuntu alongside your Windows system without altering your existing setup.

Hyper-V Manager is a built-in virtualization platform for Windows 10 Pro, Enterprise, and Education editions.

Follow this tutorial to set up Ubuntu on Hyper-V Manager:   
https://ubuntu.com/server/docs/how-to-set-up-ubuntu-on-hyper-v

Ensure your VM has at least **12GB of RAM** and **80GB of disk space**.

#### Virtualized Ubuntu using VirtualBox

Alternatively, you can set up Ubuntu using **VirtualBox**, another popular virtualization platform. 
VirtualBox offers a free license for personal, educational, and evaluation use.

Follow this guide to install Ubuntu using VirtualBox:   
https://ubuntu.com/tutorials/how-to-run-ubuntu-desktop-on-a-virtual-machine-using-virtualbox

Ensure your VM has at least **12GB of RAM** and **80GB of disk space**.

#### Native Ubuntu Installation

For those who prefer a more integrated experience, you can install Ubuntu directly on your machine, either as your primary OS or alongside an existing Windows installation.

To install Ubuntu as your primary OS:   
https://ubuntu.com/tutorials/install-ubuntu-desktop

## Git

**Git** is a Version Control System (**VCS**), it allows a team to collaborate on the same code project, and save different versions of the code without interfering each other.  
Git is the most popular VCS, you'll find it in almost every software project. 

On your Ubuntu, install Git form: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

As for the difference between **Git** and **GitHub**:   
Git is the tool used for managing the source code on your local machine, while GitHub is a platform that hosts Git projects (a **Hub**).

## AWS Account

In this course, you'll be using AWS (Amazon Web Services) a lot.

**Having access to an AWS account is a must.** 

We know the idea of cloud expenses can be a concern, but there's no need to worry, you are in good hands!

Throughout the course, we'll clearly indicate when a step might incur cloud charges, so you'll understand exactly what you are paying for.  
We put a lot of effort into making sure you get the best from AWS while carefully select cost-effective resources and always look for ways to save you money.
In addition, you'll learn how to avoid unnecessary costs, and keep full control over your cloud spending.

This course is designed for serious learners - think of it as a preparation for real-world work in the industry. 
You’ll gain practical skills just as professionals in the field use AWS on a daily basis.

AWS offers a [free tier](https://aws.amazon.com/free/) with plenty of free resources to get you started, so you can explore and experiment without any initial expense.

To create an AWS account, go to [AWS sign up](https://aws.amazon.com/), click on "Create an AWS Account" and follow the prompts.

## PyCharm

PyCharm is an **Integrated Development Environment (IDE)** software for code development, with Python as the primary programming language. 

The course's content was written with PyCharm as the preferred IDE. 

You can use any other IDE of your choice (e.g. VSCode), but keep in mind that you may experience some differences in functionality and workflow compared to PyCharm.
Furthermore, when it comes to Python programming, PyCharm reigns supreme - unless you enjoy arguing with your tools...

> [!NOTE]
> The last sentence was generated by ChatGPT. For me there is nothing funny in PyCharm vs VSCode debate.

On your Ubuntu, install **PyCharm Community** from: https://www.jetbrains.com/pycharm/download/#section=linux (scroll down for community version).

### Clone the course repository into PyCharm

Cloning a GitHub project creates a local copy of the repository on your local computer.

You'll clone the repository using PyCharm UI:

1. Open PyCharm. 
    - If no project is currently open, click **Get from VCS** on the Welcome screen.
    - If your PyCharm is opened of some existing project, go to **Git | Clone** (or **VCS | Get from Version Control**).

2. In the **Get from Version Control** dialog, specify `https://github.com/exit-zero-academy/DevOpsTheHardWay.git`, the URL of our GitHub repository. 
2. If you are not yet authenticated to GitHub, PyCharm will offer different types of authentication methods. 
   We suggest to choose the **Use Token** option, and click the **Generate** button in order to generate an authentication token in GitHub. 
   After the token was generated in GitHub website, copy the token to the designated place in PyCharm. 
3. In the **Trust and Open Project** security dialog, select **Trust Project**. 

At the end, you should have an opened PyCharm project with all the files and folders from the cloned GitHub repository, ready for you to work with.
