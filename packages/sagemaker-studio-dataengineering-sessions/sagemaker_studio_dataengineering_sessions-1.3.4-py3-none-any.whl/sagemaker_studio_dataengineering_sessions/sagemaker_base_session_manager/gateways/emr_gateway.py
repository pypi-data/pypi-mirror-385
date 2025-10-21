import logging
import boto3
import asyncio
from typing import Dict, Any, Coroutine


 
class EmrGateway():
    """
    EmrGateway class to abstract the boto3 emr client
    """
    logger = logging.getLogger(__name__)
    def __init__(self, emr):
        self.emr = emr
 
    def get_on_cluster_app_ui_presigned_url(self,
                                            cluster_id: str,
                                            on_cluster_app_ui_type: str,
                                            execution_role_arn: str) -> Dict[str, Any]:
        self.logger.info(f"get_on_cluster_app_ui_presigned_url with cluster id:{cluster_id}, "
                         f"on_cluster_app_ui_type: {on_cluster_app_ui_type}, execution_role_arn: {execution_role_arn}")
        try:
            self.logger.info(f"calling get_on_cluster_app_ui_presigned_url with cluster id:{cluster_id}, " 
                             f"on_cluster_app_ui_type: {on_cluster_app_ui_type}, execution_role_arn: {execution_role_arn}")
            result = self.emr.get_on_cluster_app_ui_presigned_url(ClusterId=cluster_id,
                                                                  OnClusterAppUIType=on_cluster_app_ui_type,
                                                                  ExecutionRoleArn=execution_role_arn)
            self.logger.info(result)
            return result
        except Exception as e:
            self.logger.error(f"get_on_cluster_app_ui_presigned_url "
                              f"failed for cluster id: {cluster_id}, "
                              f"on_cluster_app_ui_type: {on_cluster_app_ui_type}, "
                              f"execution_role_arn: {execution_role_arn}, because of: {e}")
            raise e

    def get_ec2_release_label(self, cluster_id: str) -> str:
        """
        Get EMR cluster release label using describe-cluster API call

        Args:
            cluster_id (str): The ID of the EMR cluster

        Returns:
            str: EMR release label (e.g. 'emr-7.11.0') or None if not found
        """
        try:
            self.logger.info(f"Getting release label for cluster ID: {cluster_id}")
            response = self.emr_client.describe_cluster(
                ClusterId=cluster_id
            )
            release_label = response.get('Cluster', {}).get('ReleaseLabel')
            self.logger.info(f"Found release label: {release_label}")
            return release_label
        except Exception as e:
            self.logger.error(f"Failed to get release label for cluster ID {cluster_id}: {str(e)}")
            raise e
