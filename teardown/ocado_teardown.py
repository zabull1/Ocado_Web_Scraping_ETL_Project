import boto3
import configparser
from botocore.exceptions import ClientError

config = configparser.ConfigParser()
config.read_file(open('../dwh1.cfg'))

KEY                    = config.get('AWS','KEY')
SECRET                 = config.get('AWS','SECRET')
AWS_REGION             = config.get('AWS','AWS_REGION')

DWH_CLUSTER_TYPE       = config.get("DWH","DWH_CLUSTER_TYPE")
DWH_NUM_NODES          = config.get("DWH","DWH_NUM_NODES")
DWH_NODE_TYPE          = config.get("DWH","DWH_NODE_TYPE")

DWH_CLUSTER_IDENTIFIER = config.get("DWH","DWH_CLUSTER_IDENTIFIER")
DWH_DB                 = config.get("DWH","DWH_DB")
DWH_DB_USER            = config.get("DWH","DWH_DB_USER")
DWH_DB_PASSWORD        = config.get("DWH","DWH_DB_PASSWORD")
DWH_PORT               = config.get("DWH","DWH_PORT")

DWH_IAM_ROLE_NAME      = config.get("DWH", "DWH_IAM_ROLE_NAME")

S3_BUCKET_NAME         = config.get("S3", "S3_BUCKET_NAME")

def teardown():
    try:

        ec2 = boto3.resource('ec2',
                region_name=AWS_REGION,
                aws_access_key_id=KEY,
                aws_secret_access_key=SECRET
                )
        s3 = boto3.resource('s3',
                region_name=AWS_REGION,
                aws_access_key_id=KEY,
                aws_secret_access_key=SECRET
            )
            
        iam = boto3.client('iam',aws_access_key_id=KEY,
                aws_secret_access_key=SECRET,
                region_name=AWS_REGION
            )
            
        redshift = boto3.client('redshift',
                region_name=AWS_REGION,
                aws_access_key_id=KEY,
                aws_secret_access_key=SECRET
                )
        
    except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                print("User already exists")
                pass
            else:
                print("Unexpected error: %s" % e)

    try:
        print('tearing down infrastructure.....')
        redshift.delete_cluster( ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,  SkipFinalClusterSnapshot=True)
        iam.detach_role_policy(RoleName=DWH_IAM_ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
        iam.delete_role(RoleName=DWH_IAM_ROLE_NAME)
        print('done')
    except Exception as e:
        print(f"Error: Unabale to teardown infrastructure {e}")  
  

if __name__=='__main__':
     teardown()
    
    