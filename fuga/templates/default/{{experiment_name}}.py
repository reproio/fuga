# airflow DAG (Don't delete it!
# ref: https://github.com/apache/airflow/commit/fdb7e949140b735b8554ae5b22ad752e86f6ebaf#diff-ced4fd65ce02db58eed692eef6e01d05R202

from fuga.airflow import (
    get_dag,
    get_maybe_create_dataset_operator,
    get_bq_to_bq_operator,
    get_export_table_operator,
    get_kubernetes_pod_operator)


with get_dag(email_on_failure=False) as dag:
    dst_table_name = 'my_train_data'

    # Create BQ dataset if not exists
    create_bq_dataset_operator = get_maybe_create_dataset_operator(
        dag=dag)

    # Transfer query results to the table under repro-lab.
    data_bq_to_bq_operator = get_bq_to_bq_operator(
        'sql/{dst_table_name}.sql'.format(dst_table_name=dst_table_name),
        dst_table_name=dst_table_name,
        dag=dag,
        params={'keyword': 'Beethoven'})

    create_bq_dataset_operator >> data_bq_to_bq_operator

    # Export table to GCS
    data_export_operator = get_export_table_operator(
        table_name=dst_table_name,
        dag=dag)

    data_bq_to_bq_operator >> data_export_operator

    # Run your KubernetesPodOperator
    train_pod_operator = get_kubernetes_pod_operator(
        operator_name='train',
        # There's only a few ways to pass airflow's macro to the container
        env_vars={
            'BATCH_DATE': {{ "'{{ ds }}'" }}},
        dag=dag)

    data_export_operator >> train_pod_operator
