import boto3
import json
import configparser
from botocore.exceptions import ClientError
import time
import  psycopg2

ClusterProps=[]

config = configparser.ConfigParser()
config.read_file(open('../dwh1.cfg'))

KEY                    = config.get('AWS','KEY')
SECRET                 = config.get('AWS','SECRET')
AWS_REGION             = config.get('AWS','AWS_REGION')

S3_BUCKET_NAME         = config.get("S3", "S3_BUCKET_NAME")

DWH_CLUSTER_TYPE       = config.get("DWH","DWH_CLUSTER_TYPE")
DWH_NUM_NODES          = config.get("DWH","DWH_NUM_NODES")
DWH_NODE_TYPE          = config.get("DWH","DWH_NODE_TYPE")

DWH_CLUSTER_IDENTIFIER = config.get("DWH","DWH_CLUSTER_IDENTIFIER")
DWH_DB                 = config.get("DWH","DWH_DB")
DWH_DB_USER            = config.get("DWH","DWH_DB_USER")
DWH_DB_PASSWORD        = config.get("DWH","DWH_DB_PASSWORD")
DWH_PORT               = config.get("DWH","DWH_PORT")

DWH_IAM_ROLE_NAME      = config.get("DWH", "DWH_IAM_ROLE_NAME")


def conf():
    try:

        # def clients():
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

        #1.1 Create the role 
        try:
            print("1.1 Creating a new IAM Role") 
            redshift_role = iam.create_role(
                Path='/',
                RoleName=DWH_IAM_ROLE_NAME,
                Description = "Allows Redshift clusters to call AWS services on your behalf.",
                AssumeRolePolicyDocument=json.dumps(
                    {'Statement': [{'Action': 'sts:AssumeRole',
                    'Effect': 'Allow',
                    'Principal': {'Service': 'redshift.amazonaws.com'}}],
                    'Version': '2012-10-17'})
            )    
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                pass
            else:
                print("Unexpected error: %s" % e)

        #Attaching policy    
        print("1.2 Attaching Policy")

        iam.attach_role_policy(RoleName=DWH_IAM_ROLE_NAME,
                            PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
                            )['ResponseMetadata']['HTTPStatusCode']

        print("1.3 Get the IAM role ARN")
        roleArn = iam.get_role(RoleName=DWH_IAM_ROLE_NAME)['Role']['Arn']

        print(roleArn)
    
    except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                print("User already exists")
                pass
            else:
                print("Unexpected error: %s" % e)

    try:
        response = redshift.create_cluster(        
            #HW
            ClusterType=DWH_CLUSTER_TYPE,
            NodeType=DWH_NODE_TYPE,
            NumberOfNodes=int(DWH_NUM_NODES),

            #Identifiers & Credentials
            DBName=DWH_DB,
            ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,
            MasterUsername=DWH_DB_USER,
            MasterUserPassword=DWH_DB_PASSWORD,
            
            #Roles (for s3 access)
            IamRoles=[roleArn]  
        )
        time.sleep(240)
        ClusterProps = redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]
       
    

    except ClientError as e:
        if e.response['Error']['Code'] == 'ClusterAlreadyExists':
            print("Cluster already exists")
            ClusterProps = redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]
            pass
        else:
            print("Unexpected error: %s" % e)

    # Create Security group inbound rule
    # Open an incoming  TCP port to access the cluster ednpoint
    try:
        vpc = ec2.Vpc(id=ClusterProps['VpcId'])
        defaultSg = list(vpc.security_groups.all())[0]
        # print(defaultSg)
        
        defaultSg.authorize_ingress(
            GroupName= 'default',  
            CidrIp='0.0.0.0/0',  
            IpProtocol='TCP',  
            FromPort=int(DWH_PORT),
            ToPort=int(DWH_PORT)
        )
    except ClientError as e:
        print("Unexpected error: %s" % e)
    
    return ClusterProps,roleArn
    
   

def redshift_query(ClusterProps, roleArn):
    try:
        conn = psycopg2.connect(dbname=DWH_DB, user=DWH_DB_USER, 
                                password=DWH_DB_PASSWORD, host=ClusterProps['Endpoint']['Address'], port=5439)
        print('Connection succesfully created')

        query = "create table  if not exists ocado (id varchar(1024), link varchar(1024), img varchar(2048), title varchar(1024), weight varchar(1024), price varchar(1024), price_per_unit varchar(1024), review varchar(1024), review_count varchar(1024), description varchar(2048), country varchar(1024), brand varchar(1024), manufacturer varchar(2048), ingredient varchar(2048), information varchar(2048))"
    
        cur = conn.cursor()

        cur.execute(query)
        conn.commit()
        print('Table created')
        time.sleep(120)

    except Exception as e:
        print("Error: Could not make connection to the database")
        print(e)

    try:
        cur.execute(f"copy {DWH_CLUSTER_IDENTIFIER} from 's3://{S3_BUCKET_NAME}/ocado.csv' iam_role '{roleArn}' csv IGNOREHEADER 1 FILLRECORD;")
        conn.commit()
        print('Ocado table populated')

    except Exception as e:
        print("Error: Could not copy from s3 to the redshift")
        print(e)
   

                
ClusterProps, roleArn = conf() 
redshift_query(ClusterProps, roleArn)
