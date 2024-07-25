# GitHub Actions and the simple CI/CD pipeline 

CI/CD (Continuous integration and continuous deployment) is a methodology which automates the deployment process of software project.
We'll spend fairly amount of time to discuss this topic. But for now we want to achieve a simple outcome:

When you make changes to your code locally, commit, and push them, a new automated pipeline connects to an EC2 instance, and deploys the new version of the app.

No need to manually connect to your EC2, no need manually install dependencies, stop the running server, pulls the new code version, and launch the server - everything from code changes to deployment is seamlessly done by an automatic process.
This is why it is called **Continuous Deployment**, because on every code change, a new version of the app is being deployed automatically.

To achieve that, we will use a platform which is part of GitHub, called **GitHub Actions**.

1. First, get yourself familiar with how GitHub Actions works: https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions. 
2. The GitHub Actions **Workflow** skeleton is already written for you and available under `.github/workflows/service-deploy.yaml` in the NetflixMovieCatalog repo. Carefully review it, and feel free to customize it according to your specific requirements.

   Note that in order to automate the deployment process you the app, the workflow should have an SSH private key that authorized to connect to your instance. Sice we **NEVER** store secrets in a git repo, you should configure a **Secret** in GitHub Actions and provide it to the workflow as an environment variable, as follows:
   - Go to your project repository on GitHub, navigate to **Settings** > **Secrets and variables** > **Actions**.
   - Click on **New repository secret**.
   - Define a secret named `SSH_PRIVATE_KEY` with the private key value to connect to your EC2.
   - Take a look how this secret is being used in the workflow `service-deploy.yaml` YAML.
4. Make some changes to your app, then commit and push it. Notice how the **Netflix Movie Catalog Service Deployment** workflow automatically kicked in. Once the workflow completes successfully, your new application version should be automatically deployed in your EC2 instance. Make sure the service is working properly and reflects the code changes you've made. 

**Note:** Your EC2 instances should be running while the workflow is running. **Don't forget to turn off the machines when you're done**.


## Git workflows

**Git workflows** refer to the different approaches or strategies that teams can adopt when using Git in their software development projects.

## GitFlow

[Gitflow](https://nvie.com/posts/a-successful-git-branching-model/) (by Vincent Driessen at nvie) is a git branching model that involves the use of feature branches and multiple primary branches. 

![][git_gitflow]

## Trunk-based

The **Trunk-based** workflow is a development approach where all developers work on a single branch called the `trunk` or `main` branch.
It encourages small, frequent commits and emphasizes **continuous integration and delivery** (CI/CD).
This workflow promotes collaboration and reduces integration issues but requires strong automated testing and a high level coding skills of team members.

<img src="https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_trunkbased.png" width="30%">

The workflow is very straightforward:

1. Developers commit their changes directly into `main`, then push their work to remote. Developers _may_ create a short-lived feature branch to test their work locally. The `main` branch is **always** assumed to be stable, without any issues, ready to be released in any moment. 
2. At some point, developers release a new version by branching out from `main` into to `release` branch. A few more changes might be committed before the release is ready.


## Pull Requests

GitHub allows you to configure protection rule on branches. For example, it's a very common practice to protect branch `main` from being pushed directly from developer's machines.
Since this branch usually reflects the version running in production, we want to ensure that only thoroughly reviewed and tested changes are merged into it.
This can be achieved by requiring **Pull Requests**, **code reviews**, and passing **status checks** before any changes are integrated.

1. Create a [branch protection rule](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule#creating-a-branch-protection-rule) that protects direct push to branch `main` and require a Pull Request review.
2. Create a branch from `main`, commit and push some changes. 
3. In the GitHub repo page, click on **Pull Requests (PR)** and create a PR from your feature branch into the `main` branch of your fork. 
4. "Review" the PR and merge it. 


[git_gitflow]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_gitflow.png


