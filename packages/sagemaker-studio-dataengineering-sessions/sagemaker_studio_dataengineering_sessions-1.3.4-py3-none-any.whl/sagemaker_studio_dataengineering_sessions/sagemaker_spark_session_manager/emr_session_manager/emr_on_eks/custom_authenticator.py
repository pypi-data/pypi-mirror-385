from sagemaker_studio_dataengineering_sessions.sagemaker_spark_session_manager.emr_session_manager.emr_on_ec2.connection_transformer import get_username_password
from requests.auth import HTTPBasicAuth
from sagemaker_studio_dataengineering_sessions.sagemaker_spark_session_manager.emr_session_manager.emr_on_eks.connection_tranformer import get_managed_endpoint_credentials
from sparkmagic.auth.customauth import Authenticator
from sparkmagic.utils.sparklogger import SparkLog

class EMRonEKSCustomAuthenticator(HTTPBasicAuth, Authenticator):
    """Custom authenticator for SparkMagic for EMR on EKS.
    This Authenticator is almost identical to HTTPBasicAuth
    https://requests.readthedocs.io/en/latest/user/authentication/#basic-authentication
    Except that we provide a way to refresh_credentials
    1. read the creds using SageMakerToolkit
    2. update the creds
    3. and add required headers to the request.
   """
    def __init__(self, parsed_attributes=None):
        Authenticator.__init__(self, parsed_attributes)
        self.logger = SparkLog("EMRonEKSCustomAuthenticator")
        if parsed_attributes is not None:
            self.url = parsed_attributes.__dict__["url"]
            self.connection_id = parsed_attributes.__dict__["connection_id"]
            id, token = get_managed_endpoint_credentials(self.connection_id)
            self.username = id
            self.password = token
            HTTPBasicAuth.__init__(self, self.username, self.password)
        else:
            self.url = ""
            self.connection_id = None

    def refresh_credentials(self):
        self.logger.info("Refreshing credentials...")
        id, token = get_managed_endpoint_credentials(self.connection_id)
        self.username = id
        self.password = token

    def __call__(self, request):
        return HTTPBasicAuth.__call__(self, request)

    def __hash__(self):
        return hash((self.url, self.connection_id, self.__class__.__name__))
