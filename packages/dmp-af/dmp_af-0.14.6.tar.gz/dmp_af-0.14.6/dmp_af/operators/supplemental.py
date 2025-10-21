from typing import TYPE_CHECKING

from airflow.exceptions import AirflowSkipException
from airflow.operators.python import PythonOperator

from dmp_af.conf import Config
from dmp_af.integrations.tableau import is_tableau_installed, tableau_extracts_refresh

if TYPE_CHECKING:
    from dmp_af.parser.dbt_node_model import TableauRefreshTaskConfig


def _tableau_extracts_refresh_dev(*args, **kwargs) -> None:
    import logging

    logging.info('tableau_extracts_refresh is disabled in dev mode.')
    raise AirflowSkipException('tableau_extracts_refresh is disabled in dev mode.')


class TableauExtractsRefreshOperator(PythonOperator):
    template_fields = tuple()

    def __init__(self, tableau_refresh_tasks: 'list[TableauRefreshTaskConfig]', dmp_af_config: Config, **kwargs):
        if not is_tableau_installed():
            raise ImportError('tableauserverclient is not installed. Please install it to use this operator.')

        super().__init__(
            python_callable=tableau_extracts_refresh if not dmp_af_config.dry_run else _tableau_extracts_refresh_dev,
            op_kwargs={
                'tableau_refresh_tasks': tableau_refresh_tasks,
                'dmp_af_config': dmp_af_config,
            },
            **dmp_af_config.retries_config.supplemental_task_retry_policy.as_dict(),
            **kwargs,
        )
