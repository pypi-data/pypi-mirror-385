import logging

class EmrEKSGateway():

    logger = logging.getLogger(__name__)
    def __init__(self, emr_eks):
        self.emr_eks = emr_eks
