import io

from google.cloud import storage
import pandas as pd
from fuga.config import get_config


def save_df(df, name):
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


def get_exported_table_df(table_name, date=None):
    """Retrieve exported table file on GCS.

    Args:
        table_name (string): Name of the table to load.

    Returns:
        pandas.DataFrame

    """

    bucket = storage \
        .Client(get_config('gcp_project_name')) \
        .get_bucket(get_config('bucket_name'))
    key = \
        '{experiment_name}/exported_tables/{table_name}/' \
        '{date_descriptor}/out.csv.gzip'.format(
            experiment_name=get_config('experiment_name'),
            table_name=table_name,
            date_descriptor=date or '{{ ds_nodash }}')
    blob = storage.Blob(key, bucket)
    bio = io.BytesIO()
    blob.download_to_file(bio)
    bio.seek(0)

    return pd.read_csv(bio, compression='gzip')
