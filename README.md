# Ocado Web Scraping ETL Project

# Description

Ocado is a British company that offers online grocery shopping and delivery services. It also makes and sells technology for online grocery to other countries. Ocado has a partnership with Marks & Spencer, a UK retailer, to sell M&S food products on its website. 
This project aims to scrape the Ocado website for its “Big Price Down” section, which offers discounts on grocery items. The scraped data is then extracted and stored in a data lake (S3) for further processing. The data is then cleaned and loaded to a Redshift data warehouse, where some queries are performed to gain insights into the price trends, customer preferences, and market opportunities.

# Features
- **Web scraping**: This project uses the Selenium library to scrape the Ocado website for the product name, price, review, review count, brand, manufacturer, ingredient, and category of each item in the “Big Price Down” section.
- **Infrastructure as code**: We used Python SDK to create all AWS services needed, such as s3 bucket, redshift cluster, EC2, and IAM roles.
- **Data extraction and storage**: This project uses the boto3 library to extract the scraped data as a CSV file and store it in an S3 bucket.
- **Data cleaning and loading**: This project uses the Pandas library to clean the data and remove duplicates, missing values, or outliers. The cleaned data is then loaded to a Redshift cluster using the psycopg2 library.
- **Data analysis**: This project uses SQL queries to perform various data analyses in redshift.
  
# Questions
- What are the prices of the first 10 products with a review of 4.3 or above?
-	How many people have reviewed the second-worst product?
-	What is the name, manufacturer and website of the 2nd most expensive product?
-	How much does the product cost £5 or more?
-	How many in-house products (i.e., those with Ocado as the Brand name)?
-	What is the name and price of the most expensive product in terms of price per unit? 
-	What ingredient is it made up of? Is it an in-house product?
-	Please classify the products as suitable for vegans or not. How many products fall in both classes?
-	What are the ID, URL and price of the products that contain butter (see the description column)?

# Requirements
-	Python 3.8 or higher
-	Selenium
-	Boto3
-	Pandas
-	Psycopg2
-	AWS account with S3 and Redshift services
  
# Installation
To install this project, follow these steps:
- 1.	Clone this repository to your local machine using git clone https://github.com/your_username/ocado-web-scraping-project.git.
- 2.	Create a virtual environment using python -m venv env and activate it using source env/bin/activate (Linux/Mac) or env\Scripts\activate (Windows).
- 3.	Install the required libraries using pip install -r requirements.txt.
- 4.	Create a S3 bucket and a Redshift cluster using the AWS console or CLI. Note down the bucket name, cluster endpoint, database name, user name, and password.
- 5.	Create a .env file in the project directory and add the following variables with your own values:

```
S3_BUCKET = your_s3_bucket_name 
REDSHIFT_ENDPOINT = your_redshift_cluster_endpoint 
REDSHIFT_DB = your_redshift_database_name 
REDSHIFT_USER = your_redshift_user_name 
REDSHIFT_PASSWORD = your_redshift_password
```

# Usage
To run this project, follow these steps:
- 1.	Run the scrape.py script using python scrape.py. This will scrape the Ocado website and save the data as data.csv in the project directory.
- 2.	Run the extract.py script using python extract.py. This will upload the data.csv file to your S3 bucket.
- 3.	Run the load.py script using python load.py. This will create a table called products in your Redshift database and load the data from your S3 bucket.
- 4.	Run the analyze.py script using python analyze.py. This will execute some SQL queries on your Redshift database and print out the results.

# License
This project is licensed under the MIT License - see the [LICENSE] file for details.
