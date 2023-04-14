# Contributing

parsi.io welcomes any constructive contribution from the community and the team is more than willing to work on problems you have encountered to make it a better project.

please read the contribution guide to optimize your contribution

## Environment Setup

To contribute to parsi.io, we would like to first guide you to set up a proper development environment so that you can better implement your code. It is good to install this system from source with the `editable` flag (`-e`, for development mode) so that your change to the source code will be reflected in runtime without repeated installation and uninstallation. Here are the steps to set up the development environment.

1. Uninstall any existing parsi.io distribution.

```shell
pip uninstall parsi.io
```

2. Clone the repository to local workspace

```shell
git clone https://github.com/language-ml/parsi.io.git
cd parsi.io
```

3. Install using pip with *-e* flag.

```shell
pip install <options> -e .
```

## Contribution Guide

You need to follow these steps below to make contribution to the main repository via pull request. You can learn about the details of pull request [here](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests).

### 1. Fork the Official Repository

Firstly, you need to visit the [Parsi.io repository](https://github.com/language-ml/parsi.io.git) and fork into your own account. The `fork` button is at the right top corner of the web page alongside with buttons such as `watch` and `star`.

Now, you can clone your own forked repository into your local environment.

```shell
git clone https://github.com/<YOUR-USERNAME>/parsi.io.git
```

### 2. Configure Git

You need to set the official repository as your upstream so that you can synchronize with the latest update in the official repository. You can learn about upstream [here](https://www.atlassian.com/git/tutorials/git-forks-and-upstreams).

Then add the original repository as upstream

```shell
cd parsi.io
git remote add upstream https://github.com/language-ml/parsi.io.git
```

you can use the following command to verify that the remote is set. You should see both `origin` and `upstream` in the output.

```shell
git remote -v
```

### 3. Synchronize with Official Repository

Before you make changes to the codebase, it is always good to fetch the latest updates in the official repository. In order to do so, you can use the commands below.

```shell
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

Otherwise, you can click the `fetch upstream` button on the github webpage of the main branch of your forked repository. Then, use these commands to sync.

```
git checkout main
git fetch main
```

### 4. Create a New Branch

You should not make changes to the `main` branch of your forked repository as this might make upstream synchronization difficult. You can create a new branch with the appropriate name. General branch name format should start with `hotfix/` and `feature/`. `hotfix` is for bug fix and `feature` is for addition of a new feature.

*For example, if you are adding a name extraction module a proper name could be: feature/add-name-extraction*


```shell
git checkout -b <NEW-BRANCH-NAME>
```

### 5. Implementation and Code Commit

Now you can implement your code change in the source code. Remember that you installed the system in development, thus you do not need to uninstall and install to make the code take effect. The code change will be reflected in every new PyThon execution.
You can commit and push the changes to your local repository. The changes should be kept logical, modular and atomic. Furthermore, make sure all tests in the parsi_io/test directory are running smoothly after your contribution. If you are adding a new feature, add proper tests to the mentioned directory. 

```shell
git add <CHANGED FILES ADDRESS>
git commit -m "<COMMIT-MESSAGE>"
git push -u origin <NEW-BRANCH-NAME>
```

**Make sure you add your name as a contributor to the list of contributors in the README file.**


### 6. Open a Pull Request

You can now create a pull request on the GitHub webpage of your repository. The source branch is `<NEW-BRANCH-NAME>` of your repository and the target branch should be `main` of `language-ml/parsi.io`. After creating this pull request, you should be able to see it [here](https://github.com/language-ml/parsi.io/pulls).

Write clearly what feature you are working on and what features from parsi.io you have used for it.

In case of code conflict, you should rebase your branch and resolve the conflicts manually.