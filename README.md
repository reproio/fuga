(This project is in public-beta status)

# Fuga \['fu:ga\]

[![pypi](https://img.shields.io/pypi/v/fuga.svg)](https://pypi.python.org/pypi/fuga)
[![CircleCI](https://circleci.com/gh/reproio/fuga.svg?style=svg)](https://circleci.com/gh/reproio/fuga)
[![Documentation Status](https://readthedocs.org/projects/reproiofuga/badge/?version=latest)](https://reproiofuga.readthedocs.io/en/latest/?badge=latest)

Fuga is a toolset (and API wrappers) for Google Cloud Composer (Airflow),
which allows Composer users to develop/deploy workflows easier and in
more organized way.

## Quickstart

### Install Requirements

- [gcloud](https://cloud.google.com/sdk/docs/quickstarts)
- Python 3+

Note: pyenv always provides an entrypoint for both python2/3 and throw an
error when one doesn't actually exists, which makes gcloud cli crashes at its
runtime. To prevent this, use something like `pyenv global 3.x.x 2.x.x` to
provide both python2/3 or `alias python2=python` to let your system choose
where to route the command.

### Install fuga (cli)

```
$ # (on your own machine)
$ pip install fuga
```

### Install fuga templates

Fuga powers [cookiecutter](https://github.com/cookiecutter/cookiecuttering) to offer various
templates/boilerplates for fuga experiments.
You need to install it to your environment before using fuga.

```
$ git clone git@github.com:reproio/fuga-cookiecutter-experiment-default.git \
  ~/.cookiecutters/fuga-cookiecutter-experiment-default
$ git clone git@github.com:reproio/fuga-cookiecutter-pod-operator-default.git \
  ~/.cookiecutters/fuga-cookiecutter-pod-operator-default
```

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

Fuga supports generating a scaffold for KuberenetesPodOperator and
deploy(and rollback(WIP)) it on Google Cloud Container Registry.

```
$ cd my_experiment
$ fuga pod-operator new my_pod_operator
...
$ fuga pod-operator deploy my_pod_operator
...
```

