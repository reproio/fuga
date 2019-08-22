# Fuga

Fuga is a toolset (and API wrappers) for Google Cloud Composer (Airflow).

## Quickstart

### Requirements

- gcloud cli tool
- google cloud sdk
- hogehoge

### Create Cloud Composer Environment

Creating new Cloud Composer Environment is not supported by the tool at
the moment.

### Install fuga to Composer Environment

You need to install fuga to Compooser Environment if you want to use
fuga airflow utilities.

<img src="https://cdn-ak.f.st-hatena.com/images/fotolife/a/ayemos/20190822/20190822175602.jpg" width="70%">

### Initialize Fuga environment

Fuga needs to know which GCP project and GCS bucket to use with it.
`fuga environment init` command with let you choose one or create new for each.

```
$ fuga environment init
# follow instructions
```

### Create your experiment

```
$ fuga experiment new my_experiment
...
```

### Deploy your experiment

```
$ cd my_experiment
$ fuga experiment deploy
...
```

### (optional) Create your implementation for KubernetesPodOperator
If you want to use an operator with external dependency which is not
able to be resolved using just PyPI packages, (e.g. MeCab) you may need
to use KuberenetesPodOperator.

Fuga supports generating a scaffold for KuberenetesPodOperator and deploy/rollback(WIP) it on Google Cloud Container Registry.


```
$ fuga pod-operator new my_pod_operator
$ fuga pod-operator deploy my_pod_operator
```
```

