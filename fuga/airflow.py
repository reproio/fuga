import io
import datetime as dt
import itertools

from google.cloud import storage

from airflow import models
from airflow.contrib.hooks.bigquery_hook import BigQueryHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.operators.bigquery_operator import BigQueryOperator
from airflow.contrib.operators.bigquery_to_gcs import BigQueryToCloudStorageOperator
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator

import pandas as pd

import logging

from fuga.config import get_config


logger = logging.getLogger('{{cookiecutter.experiment_name}}')
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
logger.addHandler(sh)


class BigQueryMaybeCreateEmptyDatasetOperator(BaseOperator):
    template_fields = ('dataset_id', 'project_id')
    ui_color = '#f0eee4'

    @apply_defaults
    def __init__(self,
                 dataset_id,
                 project_id=None,
                 dataset_reference=None,
                 bigquery_conn_id='fuga_default',
                 delegate_to=None,
                 *args, **kwargs):
        self.dataset_id = dataset_id
        self.project_id = project_id
        self.bigquery_conn_id = bigquery_conn_id
        self.dataset_reference = dataset_reference if dataset_reference else {}
        self.delegate_to = delegate_to

        self.log.info('Dataset id: %s', self.dataset_id)
        self.log.info('Project id: %s', self.project_id)

        super(BigQueryMaybeCreateEmptyDatasetOperator, self). \
            __init__(*args, **kwargs)

    def execute(self, context):
        bq_hook = BigQueryHook(bigquery_conn_id=self.bigquery_conn_id,
                               delegate_to=self.delegate_to)

        conn = bq_hook.get_conn()
        cursor = conn.cursor()

        datasets = cursor.get_datasets_list(
            project_id=self.project_id)
        dataset_ids = list(
            d['datasetReference']['datasetId'] for d in datasets)

        if self.dataset_id not in dataset_ids:
            cursor.create_empty_dataset(
                project_id=self.project_id,
                dataset_id=self.dataset_id,
                dataset_reference=self.dataset_reference)


def save_df(df, name):  # XXX: Function name!!
    """Save dataframe to GCS.

    Args:
        df (pandas.DataFrame): Dataframe to save.

    Returns:
        key (string): Key of dataframe blob saved to GCS.

    """
    bucket = storage.Client(get_config('gcp_project_name')) \
        .get_bucket(get_config('bucket_name'))
    key = '{experiment_name}/output/{date_descriptor}/{name}.csv' \
        .format(
            experiment_name=get_config('experiment_name'),
            date_descriptor='{{ ds_nodash }}',
            name=name)

    blob = bucket.blob(key)

    bio = io.BytesIO()
    df.to_csv(bio)
    blob.upload_from_file(bio, rewind=True)
    return key


def get_exported_table_df(table_name):
    """Retrieve exported table file on GCS.

    Args:
        table_name (string): Name of the table to load.

    Returns:
        pandas.DataFrame

    """

    bucket = storage\
        .Client(get_config('gcp_project_name'))\
        .get_bucket(get_config('gcs_bucket_name'))
    key = \
        '{experiment_name}/exported_tables/{table_name}/' \
        '{date_descriptor}/out.csv.gzip'.format(
            experiment_name=get_config('experiment_name'),
            table_name=table_name,
            date_descriptor='{{ ds_nodash }}')
    blob = storage.Blob(key, bucket)
    bio = io.BytesIO()
    blob.download_to_file(bio)
    bio.seek(0)

    return pd.read_csv(bio, compression='gzip')


def get_bq_to_bq_operator(
        sql_or_filename,
        dst_table_name,
        dag=None,
        params={},
        table_expiration_seconds=None,
        partition_expiration_seconds=None):
    """Get templated BigQueryOperator.

    Args:
        sql_or_filename (string): Valid SQL statement or a path to a sql file.
        It can be templated using Jinja in either case.
        dag (airflow.models.DAG): DAG used by context_manager. e.g. `with get_dag() as dag: get_bq_to_bq_operator(..., dag=dag)`. Defaults to None.

    Returns:
        airflow.contrib.operators.bigquery_operator.BigQueryOperator

    """
    dag = dag or models._CONTEXT_MANAGER_DAG
    if dag is None:
        logger.warning('No DAG context was found. The operator may not be associated to any DAG nor appeared in Web UI')

    dst_table_name_with_date_descriptor = \
        '{table_name}{date_descriptor}'.format(
            table_name=dst_table_name,
            date_descriptor='{{ ds_nodash }}')

    dataset_name = '{experiment_name}_database'.format(
        experiment_name=get_config('experiment_name'))

    return BigQueryOperator(
        dag=dag,
        task_id='{experiment_name}.{table_name}.bq_to_bq'
        .format(
            experiment_name=get_config('experiment_name'),
            table_name=dst_table_name),
        sql=sql_or_filename,
        use_legacy_sql=False,
        write_disposition="WRITE_TRUNCATE",
        destination_dataset_table="{gcp_project_name}:{dataset_name}.{table_name}"
        .format(
            gcp_project_name=get_config('gcp_project_name'),
            dataset_name=dataset_name,
            table_name=dst_table_name_with_date_descriptor),

        params=params)


def get_maybe_create_dataset_operator(
        dag=None,
        table_expiration_seconds=2678400,  # 60 * 60 * 24 * 31
        partition_expiration_seconds=2678400):
    """Get templated BigQueryOperator.

    Args:
        dag (airflow.models.DAG): DAG used by context_manager. e.g. `with get_dag() as dag: get_bq_to_bq_operator(..., dag=dag)`. Defaults to None.
        table_expiration_seconds (int): Default expiration time (in seconds) for tables in created datset.
        partition_expiration_seconds (int): Default expiration time (in seconds) for partitions in created datset.


    Returns:
        airflow.contrib.operators.bigquery_operator.BigQueryOperator

    """
    dag = dag or models._CONTEXT_MANAGER_DAG
    dataset_name = '{experiment_name}_database'.format(
        experiment_name=get_config('experiment_name'))

    return BigQueryMaybeCreateEmptyDatasetOperator(
        dag=dag,
        task_id='{experiment_name}.create_dataset'
        .format(
            experiment_name=get_config('experiment_name')),
        project_id=get_config('gcp_project_name'),
        dataset_id=dataset_name,
        dataset_reference={
            "description":
                "Dataset for experiment {experiment_name}."
                " Auto generated by fuga.",
            "defaultTableExpirationMs": str(table_expiration_seconds * 1000),
            "defaultPartitionExpirationMs": str(partition_expiration_seconds * 1000)})


def get_export_table_operator(table_name, dag=None):
    """Get templated BigQueryToCloudStorageOperator.

    Args:
        table_name (string): Name of the table to export.
        dag (airflow.models.DAG): DAG used by context_manager. e.g. `with get_dag() as dag: get_export_table_operator(..., dag=dag)`. Defaults to None.

    Returns:
        airflow.contrib.operators.bigquery_operator.BigQueryOperator

    """
    if dag is None:
        logger.warning('No DAG context was found. The operator may not be associated to any DAG nor appeared in Web UI')

    date_descriptor = '{{ ds_nodash }}'
    table_name_with_date_descriptor = \
        '{table_name}{date_descriptor}'.format(
            table_name=table_name,
            date_descriptor=date_descriptor)

    return BigQueryToCloudStorageOperator(
        dag=dag or models._CONTEXT_MANAGER_DAG,
        task_id='{experiment_name}.{table_name}.export'
        .format(
            experiment_name=get_config('experiment_name'),
            table_name=table_name),
        source_project_dataset_table='{gcp_project_name}.{database_name}.{table_name}'
        .format(
            gcp_project_name=get_config('gcp_project_name'),
            database_name='%s_database' % get_config('experiment_name'),
            table_name=table_name_with_date_descriptor),
        # TODO: 1GB以上のデータに対応
        # https://cloud.google.com/bigquery/exporting-data-from-bigquery#exportingmultiple
        destination_cloud_storage_uris=[
            'gs://{bucket_name}/{experiment_name}/exported_tables/'
            '{table_name}/{date_descriptor}/'
            'out.csv.gzip'.format(
                bucket_name=get_config('bucket_name'),
                experiment_name=get_config('experiment_name'),
                date_descriptor=date_descriptor,
                table_name=table_name)],
        compression="GZIP")


def get_dag(start_date=None, schedule_interval=None, **xargs):
    default_args = {
        'start_date': start_date or dt.datetime.today(),
        'retries': 1,
        'email_on_failure': True}
    if models.Variable.get("notification_email_address", None) is not None:
        defaualt_args['email'] = models.Variable.get("notification_email_address")
    default_dag_args = dict(itertools.chain(
        default_args.items(),
        xargs.items()))

    return models.DAG(
        '{experiment_name}_dag'.format(
            experiment_name=get_config('experiment_name')),
        schedule_interval=schedule_interval or dt.timedelta(days=1),
        default_args=default_dag_args,
        catchup=False)


def get_kubernetes_pod_operator(
        operator_name=None,
        operator_image=None,
        cmds=['python', 'main.py'],
        env_vars=None,
        dag=None,
        image_tag=None):
    """Get templated KubernetesPodOperator.

    Intended to be used with your own implementations of kuberenetes pod operator
    bootstrapped using `new_pod_operator` command.

    Args:
        operator_name (string): Name of the operator. Defaults to None. e.g. `train-operator`
        operator_image (string): Name of the operator image. Defaults to None.
        Mutually exclusive to `operator_name` param.
        e.g. `gcr.io/my-project/my-experience_train-operator`
        cmds (list[str]): Command overrides for the pod.
        env_vars (dict): Env vars overrides for the pod.
        dag (airflow.models.DAG): DAG used by context_manager. e.g. `with get_dag() as dag: get_kuberenetes_pod_operator(..., dag=dag)`. Defaults to None.

    Returns:
        airflow.contrib.operators.kubernetes_pod_operator.KubernetesPodOperator
    """

    if dag is None:
        logger.warning('No DAG context was found. The operator may not be associated to any DAG nor appeared in Web UI')

    if (operator_name is None and operator_image is None) or \
            (operator_name is not None and operator_image is not None):
        raise Exception('''You need to specify either one of `opertor_name` or `operator_image` param''')
    elif operator_name is not None:
        image = 'gcr.io/{gcp_project_name}/{experiment_name}_{operator_name}'\
            .format(
                gcp_project_name=get_config('gcp_project_name'),
                experiment_name=get_config('experiment_name'),
                operator_name=operator_name)
    elif operator_image is not None:
        image = operator_image

    image_tag = image_tag or 'LATEST'

    return KubernetesPodOperator(
        dag=dag or models._CONTEXT_MANAGER_DAG,
        task_id='{experiment_name}_{operator_name}'.format(
            experiment_name=get_config('experiment_name')
                .replace('-', '_'),
            operator_name=operator_name.replace('-', '_')),
        name='{experiment_name}__{operator_name}:{image_tag}'.format(
            experiment_name=get_config('experiment_name').replace('_', '-'),
            operator_name=operator_name.replace('_', '-')),
        namespace='default',
        # Parameterize tags
        image=image,
        image_pull_policy='Always',
        cmds=cmds,
        env_vars=env_vars,
        startup_timeout_seconds=3600)
