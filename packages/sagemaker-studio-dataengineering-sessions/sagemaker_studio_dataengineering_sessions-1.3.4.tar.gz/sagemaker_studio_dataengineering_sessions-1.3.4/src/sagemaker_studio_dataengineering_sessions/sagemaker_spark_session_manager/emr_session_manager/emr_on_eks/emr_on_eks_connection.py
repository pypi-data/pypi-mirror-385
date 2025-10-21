from sagemaker_studio_dataengineering_sessions.sagemaker_spark_session_manager.spark_session_manager.spark_connection import \
    SparkConnection

class EmrOnEKSConnection(SparkConnection):
    def __init__(self,
                 connection_name: str,
                 connection_id: str,
                 virtual_cluster_id: str,
                 url: str,
                 runtime_role_arn: str,
                 managed_endpoint_arn: str,
                 region: str,
                 certificate_data: str,
                 idcApplicationArn: str,
                 spark_configs: dict[str, any] | None = None,
                 spark_defaults: dict[str, any] | None = None):
        super().__init__(connection_name=connection_name,
                         connection_id=connection_id,
                         region=region,
                         spark_configs=spark_configs)
        self.virtual_cluster_id = virtual_cluster_id
        self.url = url
        self.runtime_role_arn = runtime_role_arn
        self.managed_endpoint_arn = managed_endpoint_arn
        self.certificate_data = certificate_data
        self.spark_defaults = spark_defaults
        self.idcApplicationArn = idcApplicationArn
