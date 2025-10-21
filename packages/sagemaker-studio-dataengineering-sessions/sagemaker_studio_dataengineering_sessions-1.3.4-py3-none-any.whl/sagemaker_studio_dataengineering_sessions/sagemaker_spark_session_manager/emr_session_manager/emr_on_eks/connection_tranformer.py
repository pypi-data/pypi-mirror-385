from typing import Tuple
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.exceptions import ConnectionDetailError
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.sagemaker_toolkit_utils import SageMakerToolkitUtils
from sagemaker_studio_dataengineering_sessions.sagemaker_spark_session_manager.emr_session_manager.emr_on_ec2.governance_type import GovernanceType
from sagemaker_studio_dataengineering_sessions.sagemaker_spark_session_manager.emr_session_manager.emr_on_eks.emr_on_eks_connection import \
    EmrOnEKSConnection
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.constants import \
    (CONFIGURATION_NAME_SPARK_CONFIGURATIONS, CONFIGURATION_NAME_SPARK_DEFAULTS)

def get_emr_on_eks_connection(connection_name: str) -> EmrOnEKSConnection:
    connection_details = SageMakerToolkitUtils.get_connection_detail(connection_name, True)
    connection_name = connection_details["name"]
    connection_id = connection_details["connectionId"]
    runtime_role_arn = connection_details["environmentUserRole"]
    idcApplicationArn = ""
    if SageMakerToolkitUtils.has_key_chain_in_connection_detail(connection_details,
                                                                  ["props", "sparkEmrProperties", "idcApplicationArn"]):
            idcApplicationArn = connection_details["props"]["sparkEmrProperties"]["idcApplicationArn"]
    region = connection_details["physicalEndpoints"][0]["awsLocation"]["awsRegion"]
    if SageMakerToolkitUtils.has_key_chain_in_connection_detail(connection_details, 
                                                                ["props", "sparkEmrProperties", "livyEndpoint"]):
        livy_endpoint = connection_details["props"]["sparkEmrProperties"]["livyEndpoint"]
        managed_endpoint_arn = connection_details["props"]["sparkEmrProperties"]["managedEndpointArn"]
    else:
        raise ConnectionDetailError("Cannot get livy endpoint from connection")
    
    if SageMakerToolkitUtils.has_key_chain_in_connection_detail(connection_details,
                                                              ["props", "sparkEmrProperties", "computeArn"]):
        virtual_cluster_id = connection_details["props"]["sparkEmrProperties"]["computeArn"].split("/")[-1]
    else:
        raise ConnectionDetailError("Cannot get virtual cluster id from connection")
    
    if SageMakerToolkitUtils.has_key_chain_in_connection_detail(connection_details, 
                                                                ["props", "sparkEmrProperties", "certificateData"]):
        certificate_data = connection_details["props"]["sparkEmrProperties"]["certificateData"]
    else:
        raise ConnectionDetailError("Cannot get SSL Certificate from connection")

    spark_configs = {}
    spark_defaults = {}
    if "configurations" in connection_details and type(connection_details["configurations"]) == list:
        for config in connection_details["configurations"]:
            if config["classification"] == CONFIGURATION_NAME_SPARK_CONFIGURATIONS:
                spark_configs = config["properties"]
            elif config["classification"] == CONFIGURATION_NAME_SPARK_DEFAULTS:
                spark_defaults = config["properties"]

    return EmrOnEKSConnection(connection_name=connection_name,
                              connection_id=connection_id,
                              virtual_cluster_id=virtual_cluster_id,
                              url=livy_endpoint,
                              runtime_role_arn=runtime_role_arn,
                              managed_endpoint_arn=managed_endpoint_arn,
                              spark_configs=spark_configs,
                              spark_defaults=spark_defaults,
                              region=region,
                              certificate_data=certificate_data,
                              idcApplicationArn=idcApplicationArn)

def get_managed_endpoint_credentials(connection_id: str) -> Tuple[str, str]:
    connection_details = SageMakerToolkitUtils.get_connection_detail_from_id(connection_id, True)
    if (SageMakerToolkitUtils.has_key_chain_in_connection_detail(
            connection_details, ["props", "sparkEmrProperties", "managedEndpointCredentials", "token"]) and
            SageMakerToolkitUtils.has_key_chain_in_connection_detail(
                connection_details, ["props", "sparkEmrProperties", "managedEndpointCredentials", "id"])):
        id = connection_details["props"]["sparkEmrProperties"]["managedEndpointCredentials"]["id"]
        token = connection_details["props"]["sparkEmrProperties"]["managedEndpointCredentials"]["token"]
    else:
        raise ConnectionDetailError("Cannot get managed endpoint credentials from connection")
    return id, token
