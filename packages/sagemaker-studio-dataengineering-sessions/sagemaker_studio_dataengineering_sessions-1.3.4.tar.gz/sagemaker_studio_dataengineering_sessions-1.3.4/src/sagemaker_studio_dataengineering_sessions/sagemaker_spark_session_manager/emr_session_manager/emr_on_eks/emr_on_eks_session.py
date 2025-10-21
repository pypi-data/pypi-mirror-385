import os
import ssl
import base64
import requests
from requests.utils import DEFAULT_CA_BUNDLE_PATH
import urllib3

from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.sagemaker_connection_display import SageMakerConnectionDisplay
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.client_utils import create_emr_eks_client
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.exceptions import AuthenticationError
from sagemaker_studio_dataengineering_sessions.sagemaker_spark_session_manager.emr_session_manager.emr_on_ec2.governance_type import GovernanceType
from sagemaker_studio_dataengineering_sessions.sagemaker_spark_session_manager.emr_session_manager.emr_on_eks.connection_tranformer import \
    get_emr_on_eks_connection
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.gateways.emr_eks_gateway import \
    EmrEKSGateway
from sagemaker_studio_dataengineering_sessions.sagemaker_spark_session_manager.emr_session_manager.livy_session import LivySession, AUTHENTICATOR
from sagemaker_studio_dataengineering_sessions.sagemaker_spark_session_manager.spark_session_manager.spark_monitor_widget_utils import add_session_info_in_user_ns, \
    clear_current_connection_in_user_ns
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.constants import (CONNECTION_TYPE_SPARK_EMR_EKS, PROJECT_S3_PATH)
from sagemaker_studio_dataengineering_sessions.sagemaker_spark_session_manager.utils.common_utils import apply_compatibility_mode_configs
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.release_label_utils import \
    compare_emr_release_labels
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.debugging_utils import get_sessions_info_json

import sparkmagic.utils.configuration as conf
from sparkmagic.livyclientlib.endpoint import Endpoint
from sparkmagic.livyclientlib.exceptions import HttpClientException
from sparkmagic.utils.utils import initialize_auth, Namespace
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.gateways.sso_gateway import SSOGateway

AUTH_ERROR_MESSAGE = "Invalid status code '403' from"
SAGEMAKER_EMR_EKS_TRUSTED_CA_COMMENT = "# SageMaker connection trusted certificate for EMR on EKS:"
EMR_VERSION_SUPPORT_FOR_LAKEFORMATION = "emr-7.11.0"
EMR_EKS_VERSION_SUPPORT_FOR_MCMUFFIN = "emr-7.11.0"

class EmrOnEKSSession(LivySession):
    def __init__(self, connection_name: str):
        # The connection_details are required to get the profile, which is needed for super.__init__
        self.connection_details = get_emr_on_eks_connection(connection_name)
        super().__init__(connection_name)
        self.connection_type = CONNECTION_TYPE_SPARK_EMR_EKS
        self.emr_client = create_emr_eks_client(self.profile, self.connection_details.region)
        self.emr_eks_gateway = EmrEKSGateway(self.emr_client)
        self.release_label =self._get_release_label()
        try:
            if (self.release_label and
                compare_emr_release_labels(self.connection_details.release_label, EMR_EKS_VERSION_SUPPORT_FOR_MCMUFFIN) >= 0 and
                self.connection_details.idcApplicationArn):
                self.user_background_session_enabled = self.sso_gateway.get_user_background_session_status(
                    self.connection_details.idcApplicationArn
                )
        except Exception as e:
            self.get_logger().error(f"Error checking background session status: {str(e)}")
            self.user_background_session_enabled = False
        conf.override(conf.authenticators.__name__, AUTHENTICATOR)
        
        # EKS will always expect Auth for Livy
        args = Namespace(
            connection_id=self.connection_details.connection_id,
            auth="EKS_Custom_Auth",
            url=self.connection_details.url,
        )
        self.auth = initialize_auth(args)

    def create_livy_endpoint(self):
        self.auth.refresh_credentials()
        return Endpoint(self.connection_details.url, self.auth)

    def _is_fta_supported(self):
        self.get_logger().info(f"Checking if compatibility mode is enabled for EMR EKS, emr release label is {self.release_label}")
        is_supported_emr_release = compare_emr_release_labels(self.release_label, EMR_VERSION_SUPPORT_FOR_LAKEFORMATION) >= 0
        if self._is_compatibility_mode_enabled() and is_supported_emr_release:
            return True
        return False

    def handle_exception(self, e: Exception):
        if isinstance(e, HttpClientException) and AUTH_ERROR_MESSAGE in str(e) and self.auth:
            self.auth.refresh_credentials()
            raise AuthenticationError("Authentication failed. Please try rerun the cell.")
        else:
            raise e
        
    def _apply_compatibility_mode_configs(self):
        if self._is_fta_supported():
            self.get_logger().info(f"Applying compatibility mode configs for EMR EKS cluster {self.connection_details.virtual_cluster_id}")
            self.config_dict["conf"] = apply_compatibility_mode_configs(self.config_dict["conf"])

    def _is_compatibility_mode_enabled(self):
        spark_defaults = self.connection_details.spark_defaults
        if spark_defaults is None:
            return False
        
        return spark_defaults.get('spark.emr-containers.lakeformation.enabled', 'false').lower() == 'false'

    def configure_properties(self) -> any:
        self.config_dict.setdefault("conf", {})
        self._apply_compatibility_mode_configs()
        self.config_dict["conf"].update({
            "spark.hadoop.hive.metastore.client.factory.class": "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory",
            "spark.kubernetes.file.upload.path": PROJECT_S3_PATH
        })
        conf.override(conf.session_configs.__name__, self.config_dict)
        return conf.get_session_properties(self.language)

    def pre_session_creation(self):
        # disable warnings to make sure output is clean
        super().pre_session_creation()
        urllib3.disable_warnings()

        with open(DEFAULT_CA_BUNDLE_PATH, 'r') as ca_cert:
            content = ca_cert.read()
            if f"{SAGEMAKER_EMR_EKS_TRUSTED_CA_COMMENT} {self.connection_details.connection_id}" in content:
                self.get_logger().info("The trusted certificate is already present on space")
                return
        try:
            # Decode the base64 certificate data
            decoded_cert_data = base64.b64decode(self.connection_details.certificate_data).decode('utf-8')
            with open(DEFAULT_CA_BUNDLE_PATH, "a") as destination_file:
                destination_file.write(f"\n{SAGEMAKER_EMR_EKS_TRUSTED_CA_COMMENT} {self.connection_details.connection_id}\n")
                destination_file.writelines(f"{decoded_cert_data}\n")
            # REQUESTS_CA_BUNDLE is the default cert path, however we still need to
            # set REQUESTS_CA_BUNDLE to force reload the newly added content of DEFAULT_CA_BUNDLE_PATH.
            # Otherwise the newly added pem will not be loaded and verification will fail
            os.environ['REQUESTS_CA_BUNDLE'] = DEFAULT_CA_BUNDLE_PATH
            exc = self._surface_verify_ssl_error()
            if exc is None:
                self.get_logger().info("Certificate verification for HTTPS succeeded.")
            elif isinstance(exc, requests.exceptions.SSLError) or isinstance(
                exc, ssl.SSLError
            ):
                SageMakerConnectionDisplay.send_error(f"Certificate verification for HTTPS request failed. "
                                                    f"Error: [{exc.__class__.__name__}: {exc}]")
        except Exception as e:
            self.get_logger().warning(f"Unable to configure the trusted certificate because of error: {e.__class__.__name__}: {e}\n Skipping")

    def pre_run_statement(self):
        session = self._get_session()
        session_id = session.id
        clear_current_connection_in_user_ns()

        # Get YARN application ID (Job Run ID)  
        try:
            app_id = self.spark_magic.spark_controller.get_app_id(self.connection_name)
        except Exception as e:
            self.get_logger().warning(f"Could not get YARN app_id for EMR EKS connection {self.connection_name}: {e}")
            app_id = None

        add_session_info_in_user_ns(connection_name=self.connection_name,
                                    connection_type=CONNECTION_TYPE_SPARK_EMR_EKS, 
                                    session_id=session_id,
                                    application_id=app_id)

    # Temp solution for local SHS until EKS provide Live/Persistent App UI
    def _print_endpoint_info(self, info_sessions, current_session_id):
        if info_sessions:
            current_session = next((session for session in info_sessions if session.id == current_session_id), None)
            if current_session:
                try:
                    # Extract account ID from runtime role ARN
                    account_id = self.connection_details.runtime_role_arn.split(':')[4] if self.connection_details.runtime_role_arn else ""
                    
                    # Get virtual cluster ID
                    virtual_cluster_id = self.connection_details.virtual_cluster_id
                    
                    # Get livy endpoint ID from managed_endpoint_arn
                    livy_endpoint_id = self.connection_details.managed_endpoint_arn.split('/')[-1]
                    
                    # Get app ID
                    app_id = self.get_app_id()

                    livy_internal_session_id = app_id.replace("spark-", "")
                    
                    # Construct the new S3 path format
                    event_logs_location = f"{PROJECT_S3_PATH}/{account_id}/{virtual_cluster_id}/endpoints/{livy_endpoint_id}/sparklogs/eventlog_v2_{app_id}/"
                    driver_logs_location = f"{PROJECT_S3_PATH}/{virtual_cluster_id}/endpoints/{livy_endpoint_id}/containers/{app_id}/{livy_internal_session_id}/stderr.gz"
                    display_obj = get_sessions_info_json(self.get_app_id(), self.connection_name, driver_logs_location, event_logs_location)
                    SageMakerConnectionDisplay.display(display_obj)
                except Exception as e:
                    self.get_logger().warning(f"Unable to generate log location because of error: {e}")
            else:
                SageMakerConnectionDisplay.write_msg(f"Session {current_session_id} not found in active sessions.")
        else:
            SageMakerConnectionDisplay.write_msg("No active sessions.")

    def _surface_verify_ssl_error(self):
        """
        _surface the error to the user if there will be SSL errors.
        :return:
        """
        try:
            requests.get(self.connection_details.url, verify=True)
        except (ssl.SSLError, requests.exceptions.SSLError, OSError, Exception) as e:
            """
            Also catch generic "Exception" so that this code path doesn't fail execution. Most likely, the same Exception will
            also be raised when we try to actually connect to execute the connection to given host:port. Relegate failure to that code path.
            """
            return e

        return None

    def _install_from_pip(self) -> any:
        # install from pip is not supported in emr eks
        pass

    def _set_libs(self, properties):
        pass

    def _lakeformation_session_level_setting_supported(self) -> bool:
        return False

    def _get_release_label(self):
        spark_defaults = self.connection_details.spark_defaults
        if spark_defaults is None:
            return None
        
        return spark_defaults.get('spark.emr.releaseLabel', None)