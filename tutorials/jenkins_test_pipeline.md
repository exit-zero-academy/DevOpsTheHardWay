# Pull Request testing

## Motivation

Let's review the Git workflow we've implemented throughout the course:

![][git_envbased]

1. Developers branching our from an up-to-date `main` branch into their feature branch. 
2. They commit changes into their feature branch.
3. At some point, they want to test their changes in Development environment. They merge the feature branch into `dev` branch, and push to remote.
4. After the changes have been tested in development environment and a few more fixes has been committed, the developer creates a Pull Request from their feature branch into `main`.
5. The `main` branch can be deployed to production environment directly after the merge. 

A Pull Request is a crucial point for testing and review code changes before they are merged into the `main` branch (and deployed to production systems from there). 

Let's build a **testing pipeline** on an opened Pull Request.

So far we've seen how pipelines can be built around a single branch (e.g. `main`). 
Now we would like to create a new pipeline which will be triggered on **every PR branch** that is created in GitHub.
For that we will utilize Jenkins [multi-branch pipeline](https://www.jenkins.io/doc/book/pipeline/multibranch/).

## Create a multi-branch pipeline

1. In the [NetflixFrontend][NetflixFrontend] repo, create the `pipelines/test.Jenkinsfile` pipeline as follows:

```text
pipeline {
    agent any

    stages {
        stage('Tests before build') {
            parallel {
             stage('Unittest') {
                 steps {
                     sh 'echo unittesting...'
                 }
             }
             stage('Lint') {
                 steps {
                     sh 'echo linting...'
                 }
             }
            }
        }
        stage('Build and deploy to Test environment') {
            steps {
                sh 'echo trigger build and deploy pipelines for test environment... wait until successful deployment'
            }
        }
        stage('Tests after build') {
            parallel {
              stage('Security vulnerabilities scanning') {
                    steps {
                        sh 'echo scanning for vulnerabilities...'
                    }
              }
              stage('API test') {
                 steps {
                     sh 'echo testing API...'
                 }
              }
              stage('Load test') {
                  steps {
                      sh 'echo testing under load...'
                  }
              }
            }
        }
    }
}
```

To save time and compute resources, we used the [`parallel`](https://www.jenkins.io/doc/book/pipeline/syntax/#parallel) directive to run the test stages in parallel, while failing the whole build when one of the stages is failed.


2. Commit and push your changes.
3. From the Jenkins dashboard page, choose **New Item**, and create a **Multibranch Pipeline** named `NetflixFrontendTesting`.
4. Under **Branch Sources** choose **Add source**, then **GitHub**.
5. Choose your GitHub credentials.
6. Under **Repository HTTPS URL**, enter your NetflixFrontend repo URL.
7. Under **Behaviors**, delete all behaviors other than **Discover pull requests from origin**. Configure this behavior to **Merging the pull request with the target branch revision**.
8. Under **Build Configuration**, specify the path to the testing Jenkinsfile.
9. Create the pipeline. 

### Test the pipeline

1. From branch `main` create a new branch change some code lines. Push the branch to remote.
1. In your app GitHub page, create a Pull Request from your branch into `main`.
1. Watch the triggered pipeline in Jenkins. 

## Protect branch `main`

We also would like to protect the `main` branch from being merged and pushed by non-tested branches.

1. From GitHub main repo page, go to **Settings**, then **Branches**.
2. **Add branch protection rule** for the `main` branch as follows:
   1. Check **Require a pull request before merging**.
   2. Check **Require status checks to pass before merging** and search the `continuous-integration/jenkins/pr-merge` check done by Jenkins.
   3. Save the protection rule.

Your `main` branch is now protected and no code can be pushed into it unless the PR is reviewed by other team member and passed all automatic tests done by Jenkins.

## Automated testing

Automated testing is a very broad topic. In this section we will lightly cover 2 types of testing: **code linting**, **security vulnerabilities testing**.

### Code linting (in Node.js)

[ESLint](https://eslint.org/) is a [static code analyser](https://en.wikipedia.org/wiki/Static_program_analysis) for JavaScript.
ESList analyzes your code **without actually running it**.
It checks for syntax errors, enforces a coding standard, and can make suggestions about how the code could be refactored.

Linting your NetflixFrontend code is simply done by the `npm run lint` command. 

- Integrate the linting check in `test.Jenkinsfile` under the **Lint** stage.
- Note that the `npm` command is required to be available in the Jenkins runtime, edit the `jenkins-agent.Dockerfile` accordingly in order to install it on the agent image, and re-run the docker compose project (with the `--build` flag so the compose will build the new image).
- The lint results would be printed into `lintingResult.xml` file, use the [junit plugin](https://plugins.jenkins.io/junit/) to publish the results in your Jenkins dashboard:

```diff
stage('Lint') {
   steps {
       ...
   }
+  post {
+      always {
+          junit 'lintingResult.xml'
+      }
+  }
}
```

### Security vulnerabilities scanning 

Integrate `snyk` image vulnerability scanning into your pipline.

- Create a **Secret text** credentials containing the Snyk API token.
- Use the [`withCredentials` step](https://www.jenkins.io/doc/pipeline/steps/credentials-binding/), read your Snyk API secret as `SNYK_TOKEN` env var, and perform the security testing using simple `sh` step and `synk` cli.
- Sometimes, Snyk alerts you for a vulnerability that has no update available, or that you do not believe to be currently exploitable in your application. You can ignore a specific vulnerability in a project using the [`snyk ignore`](https://docs.snyk.io/snyk-cli/test-for-vulnerabilities/ignore-vulnerabilities-using-snyk-cli) command:

```text
snyk ignore --id=<ISSUE_ID>
```

- Use [Snyk Jenkins plugin](https://docs.snyk.io/integrations/ci-cd-integrations/jenkins-integration-overview) or use the [Jenkins HTML publisher](https://plugins.jenkins.io/htmlpublisher/) plugin together with [snyk-to-html](https://github.com/snyk/snyk-to-html) project to generate a UI friendly Snyk reports in your pipeline page.


[git_envbased]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/git_envbased.png