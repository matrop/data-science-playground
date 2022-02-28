from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

from airflow.providers.postgres.hooks.postgres import PostgresHook


class FileToPostgresOperator(BaseOperator):
    """Uploads a tsv file into a Postgres DB using the efficient COPY command

    Args:
        postgres_conn_id (str): Conn ID of Postgres DB in Airflow
        target_table (str): Table in which to load the data
        source_file (str): File which contents should be uploaded
    """
    template_fields = ["source_file"]
    ui_color = "#0000aa"

    @apply_defaults
    def __init__(
        self,
        postgres_conn_id: str,
        target_table: str,
        source_file: str,
        *args,
        **kwargs,
    ) -> None:
        super(FileToPostgresOperator, self).__init__(*args, **kwargs)
        self.postgres_conn_id = postgres_conn_id
        self.target_table = target_table
        self.source_file = source_file

    def execute(self, **kwargs) -> None:
        """Execute the operator
        """
        hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        hook.bulk_load(
            table=self.target_table,
            tmp_file=self.source_file,
        )
