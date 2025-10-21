import boto3
import logging

class AWS_service:
    
    logger = logging.getLogger(__name__)
    
    aws_params = {"profile":"default",
                  "s3_access_point":"",
                  "s3_bucket_name":"",
                  "comprehend_service_role_name":"",
                  "reflexive_entity_name":"",
                  "reflexive_entity_version":""
                  }
    
    aws_session:boto3.Session = None
    aws_account_number:str = ""
    s3_client = None
    comprehend_client = None
    
    def __init__(self,params:dict[str,str])-> None:
        self.aws_params = params
        return None
    
    def connect(self)->None:
        try:
            self.aws_session = boto3.Session(profile_name=self.aws_params['profile'])
            self.aws_account_number = self.aws_session.client('sts').get_caller_identity().get('Account')
        except Exception as e:
            self.logger.error("Unable to create an AWS session: %s",repr(e))
        else:
            self.logger.info("AWS session created successfully")
        
    def get_s3_client(self)->None:
        try:
            self.s3_client = self.aws_session.client(service_name='s3')
        except Exception as e:
            self.logger.error("Unable to get S3 client: %s",repr(e))
        else:
            self.logger.info("AWS s3 client obtained successfully")
        return None
    
    def get_comprehend_client(self)->None:
        try:
            self.comprehend_client = self.aws_session.client(service_name='comprehend')
        except Exception as e:
            self.logger.error("Unable to get comprehend client: %s",repr(e))
        else:
            self.logger.info("AWS comprehend client obtained successfully")
        return None
             
    # def region(self):
    #     return self.aws_session.region_name
    
    # def access_key(self):
    #     return self.aws_session.get_credentials().access_key

    