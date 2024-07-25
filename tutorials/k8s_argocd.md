# ArgoCD and CI/CD pipelines for Kubernetes 

ArgoCD is a continuous delivery tool for Kubernetes applications. 

ArgoCD monitors your Git repo where the Kubernetes YAML manifests define, and sync your cluster according to those manifests.
Your Git repo should always represent the desired application state, this pattern is known as **GitOps**, in which Git source of truth for your service defining. 

1. First, let's create a dedicated GitHub repository to store all Kubernetes YAML manifests. You can name it `NetflixDevOps` or `NetflixInfra` (short of Infrastructure).
   The repo file structure might be look like:

   ```text
   NetflixInfra/
   ├── k8s/
   │   ├── NetflixFrontend/
   │   │   ├── deployment.yaml
   │   │   ├── service.yaml
   │   └── NetflixMovieCatalog/
   │       ├── deployment.yaml
   │       └── service.yaml
   ```

2. Now, let's install ArgoCD in your Kubernetes cluster by: 

   ```bash
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```

3. Visit the UI sever by:

   ```bash
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   ```

   The username is `admin`, the initial password can be retrieved by:

   ```bash 
   kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 --decode
   ```

4. In the ArgoCD UI, after logging in, click the **+ New App** button:

   - Give your app the name `netflix-frontend`, use the project `default`, and change the sync policy to **Automatic**.
   - Connect your `NetflixInfra` repo to Argo CD by setting repository url to the github repo url and set the path to `k8s/NetflixFrontend/` (the path containing your YAML manifests for the frontend service):
   - For **Destination**, set cluster URL to https://kubernetes.default.svc namespace to `default` (the k8s namespace in which you'll deploy your services)
   - After filling out the information above, click **Create**.
5. Repeat the above process for the `NetflixMovieCatalog` service.
6. Test your app definition by updating one of your YAML manifests, commit and push it. 
   Wait for Argo to automatically deploy your changes into the cluster.


# Exercises 

### :pencil2: CI/CD pipeline for Kubernetes

Create a CI/CD pipeline for the NetflixFrontend service based on the below GitHub Actions workflow:

```yaml
name: NetflixFrontend stack build-deploy

on:
  push:
    branches: 
     - main

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - name: Buid and push docker images
        run: |
           # TODO build docker image
           
      - name: Checkout infrastructure repo
        uses: actions/checkout@v3
        with:
          repository: YOUR_NETFLIX_INFRA_REPO  # TODO change me
          token: ${{ secrets.REPO_TOKEN }}  # The GITHUB_TOKEN secret is a GitHub access token. 
          path: ./NetflixInfra

      - name: Update YAML manifests
        run: |
           cd ./NetflixInfra
           # TODO commit & push changes to infra repo
           
           
      - name: Commit and Push changes
        run: |
           cd ./NetflixInfra
           # TODO commit & push changes to infra repo
```
