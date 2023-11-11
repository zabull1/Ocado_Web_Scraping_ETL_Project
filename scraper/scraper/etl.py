from scraper import Ocado_scraper
import boto3
from io import BytesIO
from dotenv import load_dotenv
import os
import pandas as pd

class pipeline():

    def __init__(self):
        self.ocado = Ocado_scraper()

    def extract(self):
        print('extracting data ......')
        self.ocado.accept_cookies()
        self.ocado.big_price_drop()
        self.ocado.extract_data()
        self.ocado.teardown()
        self.df = self.ocado.get_dataframe()
        print('data extracted ......')
        return self.df
    

    def transform(self):
        print('transforming data ......')
        self.df.columns = self.df.columns.str.lower()
        self.df.astype('str')

        title =[]
        for index, row in self.df.iterrows():
            try:
                title.append(row['title'].replace(row['weight'], ''))
            except Exception as e:
                title.append(row['title'])
        self.df['title'] = pd.Series(title).astype('str')

        price =[]
        for index, row in self.df.iterrows():
            try:
                if row['price'].startswith('£'):
                    price.append(row['price'][1:])
                else:
                    price.append(int(row['price'][:-2])*0.01)
            except Exception as e:
                price.append(row['price'])
        self.df['price'] = pd.Series(price).astype('str')

        review=[]
        for index, row in self.df.iterrows():
            try:
                review.append(row['review'].split(' ')[1])
            except Exception as e:
                review.append(row['review'])
        self.df['review'] = pd.Series(review).astype('str')

        self.df['country'] = self.df['country'].str.extract(r'(United Kingdom|UK|EU|Denmark|Scotland|Italy|Germany|Netherlands|Hungary|Ireland|France|Spain)', expand=True).replace('UK', 'United Kingdom')
    
        review_count=[]
        for index, row in self.df.iterrows():
            try:
                review_count.append(row['review_count'][1:-1])
            except Exception as e:
                review_count.append(row['review_count'])

        self.df['review_count'] = pd.Series(review_count).astype('str')

        self.df['description'] = self.df['description'].apply(lambda x: f'"{x}"')
        self.df['brand'] = self.df['brand'].apply(lambda x: f'"{x}"')
        self.df['manufacturer'] = self.df['manufacturer'].apply(lambda x: f'"{x}"')
        self.df['ingredient'] = self.df['ingredient'].apply(lambda x: f'"{x}"')
        self.df['information'] = self.df['information'].apply(lambda x: f'"{x}"')

        print('data transformed')

        return self.df
    
    def save_as_csv(self):
        print('saving data to ./data/ocado.csv.....') 
        if not os.path.exists("data"): 
            os.makedirs("data")
        self.df.to_csv('./data/ocado.csv')
        print('saved data to ./data/ocado.csv')

    def load_to_s3(self,AWS_ACCESS_KEY , AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME, s3_key_name= 'ocado.csv'):
        print('loading data into s3.....')
        csv_buffer = BytesIO()
        self.df.to_csv(csv_buffer, index=False)    
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        # Upload the file
        # s3.upload_file(local_file_path, S3_BUCKET_NAME, s3_key_name)
        s3.put_object(Bucket=S3_BUCKET_NAME, Key= s3_key_name, Body=csv_buffer.getvalue())
        print('loaded data into s3')


    def load_to_redshift(self):
        return

if __name__ == '__main__':

    load_dotenv()

    aws_access_key_id = os.environ['AWS_ACCESS_KEY']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
    region_name = os.environ['AWS_REGION']
    aws_bucket = os.environ['S3_BUCKET_NAME']
    
    ocado = pipeline()
    ocado.df = ocado.extract()
    ocado.df = ocado.transform()
    ocado.load_to_s3(aws_access_key_id, aws_secret_access_key, region_name, aws_bucket)
    ocado.save_as_csv()