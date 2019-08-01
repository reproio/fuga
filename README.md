# Fuga

Fuga is a toolset (and API wrappers) for Google Cloud Composer (Airflow).

## Quickstart (WIP)

### Requirements (WIP)

- gcloud cli tool
- google cloud sdk
- hogehoge

### Create Cloud Composer Environment

Creating new Cloud Composer Environment is not supported by the tool at
the moment.

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
