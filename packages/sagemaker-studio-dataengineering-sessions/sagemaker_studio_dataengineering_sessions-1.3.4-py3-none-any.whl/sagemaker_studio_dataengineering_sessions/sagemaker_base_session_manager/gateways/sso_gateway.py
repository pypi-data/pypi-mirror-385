import logging
import boto3
import os
import botocore

class SSOGateway:
    def __init__(self, profile: str | None = None, region: str | None = None):
        self.initialize_clients(profile, region)

    def initialize_clients(self, profile=None, region=None):
        self.sso_admin_client = self.create_sso_admin_client(profile, region)
        self.logger = logging.getLogger(__name__)

    def create_sso_admin_client(self, profile=None, region=None):
        os.environ['AWS_DATA_PATH'] = self._get_aws_model_dir()
        if not region:
            raise ValueError("Region must be set.")
        if profile:
            return boto3.Session(profile_name=profile).client(
                "sso-admin", region_name=region
            )
        else:
            return boto3.Session().client(
                "sso-admin",
                region_name=region)

    def _get_aws_model_dir(self):
        try:
            import sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager
            path = os.path.dirname(sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.__file__)
            return path + "/boto3_models"
        except ImportError:
            raise RuntimeError("Unable to import sagemaker_base_session_manager, "
                               "thus cannot initialize sso client.")

    def get_user_background_session_status(self, application_arn: str) -> bool:
        """
        Get the user background session status for a given application

        Args:
            application_arn: The ARN of the application

        Returns:
            bool: True if user background sessions are enabled, False otherwise
        """
        if not application_arn:
            return False

        try:
            self.logger.info(f"Calling get_application_session_configuration with application ARN: {application_arn}")
            response = self.sso_admin_client.get_application_session_configuration(
                ApplicationArn=application_arn
            )
            background_sessions_enabled = response.get('UserBackgroundSessionApplicationStatus') == 'ENABLED'
            self.logger.info(f"User background session status: {background_sessions_enabled}")
            return background_sessions_enabled

        except Exception as e:
            self.logger.error(f"Failed to get application session configuration for ARN {application_arn}: {str(e)}")
            return False
