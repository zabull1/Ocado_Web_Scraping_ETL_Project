import time
import uuid
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException


class Ocado_scraper:

    def __init__(self, url = 'https://www.ocado.com/webshop/startWebshop.do'):

        try:
            # s = Service('/usr/local/bin/chromedriver')

            options = webdriver.ChromeOptions()
            # options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument('--disable-dev-shm-usage')

            time.sleep(5)

            # self.driver = webdriver.Chrome()
            # self.driver = webdriver.Chrome(service= s, options = options )
            self.driver = webdriver.Remote('http://selenium:4444/wd/hub', options=options)

            self.driver.get(url)
            print('Ocado Scraper Started')
        except Exception as e:
            print(f'Error starting bot: {e}')
    
    def accept_cookies(self, id = "onetrust-accept-btn-handler"):

        time.sleep(2)
        try:
            self.driver.find_element(By.ID, id ).click()
            print('Cookies Accepted')
        except NoSuchElementException:
            print('No Cookies Found')
        except TimeoutException:
            print('No Cookies Found')
    
    def big_price_drop(self, xpath = '//*[@id="content"]/div[1]/div[1]/div/ul[1]/li[2]/a'):

        time.sleep(2)
        try:
            self.driver.find_element(By.XPATH, xpath).click()
            print("Navigated to 'Big Price Drop' section ")
        except NoSuchElementException:
            print('Not Found')
        except TimeoutException:
            print('Not Found')
    
    def find_container(self, xpath = '//*[@id="main-content"]/div[2]/div[2]/ul'):
       return self.driver.find_element(By.XPATH, xpath)
    
    def extract_links(self):
        print('extracting links for each item.....')

        self.container = self.find_container()

       # Set the number of steps for scrolling
        num_steps = 20

        # Perform the scrolling in steps
        for _ in range(num_steps):
            # Scroll the page
            self.driver.execute_script("window.scrollBy(0, window.innerHeight)")
            # Wait for the page to load all elements
            time.sleep(3)  

        # Scroll to the end of the page
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for all elements to be loaded
        wait = WebDriverWait(self.container, 60)
        gorcery_list = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'a')))

        self.link_list = []
        for gorcery in gorcery_list:
            try:
             self.link_list.append(gorcery.get_attribute('href'))
            except NoSuchElementException:
            #  self.link_list.append('N/A')
                pass

        # print('dropping N/A links .....')
        # self.link_list = [item for item in self.link_list if item != 'N/A']
    

    def extract_multiple_page_links(self, pages ):
        for _ in range(pages):
            self.driver.find_element(By.XPATH , '//*[@id="main-content"]/div[2]/div[2]/div[3]/button').click()
        self.extract_links()

        
    def extract_data(self, pages=0):
        self.gorcery_dict = {
            'ID':[],
            'Link': [],
            'img':[],
            'Title': [],
            'weight': [],
            'Price': [],
            'Price_per_unit': [],
            'Review': [],
            'Review_count':[],
            'description': [],
            'Country':[],
            'Brand':[],
            'manufacturer':[],
            'ingredient':[],
            'information':[],
            }
        
        self.extract_multiple_page_links( pages)

        print('getting item information......')
        
        
        n = 1
        for link in self.link_list[:5]: # delete '[:5]' if you want to scrape all products
            print(f'starting...... {n}')
            id = str(uuid.uuid4())
            self.gorcery_dict['ID'].append(id)
            self.gorcery_dict['Link'].append(link)


            self.driver.get(link)
            time.sleep(1)
            try:
                img = self.driver.find_element(By.XPATH, '//*[@id="overview"]/section[1]/div/div/div[1]/img').get_attribute('src')
                self.gorcery_dict['img'].append(img)
            except NoSuchElementException:
                self.gorcery_dict['img'].append('N/A')
            
            time.sleep(1)
            try:
                title = self.driver.find_element(By.XPATH, '//*[@id="overview"]/section[1]/header/h1').text
                self.gorcery_dict['Title'].append(title)
            except NoSuchElementException:
                self.gorcery_dict['Title'].append('N/A')
            
              
            time.sleep(1)
            try:
                weight = self.driver.find_element(By.XPATH, '//*[@id="overview"]/section[1]/header/h1/span').text
                self.gorcery_dict['weight'].append(weight)
            except NoSuchElementException:
                self.gorcery_dict['weight'].append('N/A')
            
              
            time.sleep(1)
            try:
                price = self.driver.find_element(By.XPATH, '//*[@id="overview"]/section[2]/div[1]/div/h2').text
                self.gorcery_dict['Price'].append(price)
            except NoSuchElementException:
                self.gorcery_dict['Price'].append('N/A')
            
              
            time.sleep(1)
            try:
                price_per_unit = self.driver.find_element(By.XPATH, '//*[@id="overview"]/section[2]/div[1]/div/span').text
                self.gorcery_dict['Price_per_unit'].append(price_per_unit)
            except NoSuchElementException:
                self.gorcery_dict['Price_per_unit'].append('N/A')

            
            time.sleep(1)
            try:
                review = self.driver.find_element(By.XPATH, '//*[@id="overview"]/section[1]/header/div/a[1]/div/span[1]/span').get_attribute('title')
                self.gorcery_dict['Review'].append(review)
            except NoSuchElementException:
                self.gorcery_dict['Review'].append('N/A')
            
            time.sleep(1)
            try:
                review_count = self.driver.find_element(By.XPATH, '//*[@id="overview"]/section[1]/header/div/a[1]/div/span[2]').text
                self.gorcery_dict['Review_count'].append(review_count)
            except NoSuchElementException:
                self.gorcery_dict['Review_count'].append('N/A')

            time.sleep(1)
            try:
                description = self.driver.find_element(By.XPATH, '//*[@id="productInformation"]/div[2]/div[1]/div[2]/div/div[1]/div').text
                self.gorcery_dict['description'].append(description)
            except NoSuchElementException:
                self.gorcery_dict['description'].append('N/A')
            
            time.sleep(1)
            try:
                e = self.driver.find_element(By.XPATH,'//*[@id="productInformation"]/div[2]/div[3]/div[1]/div/button')
                self.driver.execute_script("arguments[0].click();", e)
            except NoSuchElementException:
                pass

            time.sleep(1)
            try:
                country = self.driver.find_element(By.XPATH, '//*[@id="productInformation"]/div[2]/div[1]/div[2]/div/div[3]/div').text
                self.gorcery_dict['Country'].append(country)
            except NoSuchElementException:
                self.gorcery_dict['Country'].append('N/A')

            time.sleep(1)
            try:
                manufacturer = self.driver.find_element(By.XPATH, '//*[@id="productInformation"]/div[2]/div[3]/div[2]/div/div[4]/div').text
                self.gorcery_dict['manufacturer'].append(manufacturer)
            except NoSuchElementException:
                self.gorcery_dict['manufacturer'].append('N/A')
            
            time.sleep(1)
            try:
                brand = self.driver.find_element(By.XPATH, '//*[@id="productInformation"]/div[2]/div[3]/div[2]/div/div[1]/div').text
                self.gorcery_dict['Brand'].append(brand)
            except NoSuchElementException:
                self.gorcery_dict['Brand'].append('N/A')

            time.sleep(1)
            try:
                ingredient = self.driver.find_element(By.XPATH, '//*[@id="productInformation"]/div[3]/div/div[2]/div[2]/div/div[1]/div').text
                self.gorcery_dict['ingredient'].append(ingredient)
            except NoSuchElementException:
                self.gorcery_dict['ingredient'].append('N/A')

            time.sleep(1)
            try:
                information = self.driver.find_element(By.XPATH, '//*[@id="productInformation"]/div[3]/div/div[2]/div[2]/div/div[2]/div').text
                self.gorcery_dict['information'].append(information)
            except NoSuchElementException:
                self.gorcery_dict['information'].append('N/A')

            print(f'finished...... {n}')
            n = n + 1
    
    
    def teardown(self):    
        self.driver.quit()
                
    def get_dataframe(self):
        df = pd.DataFrame(self.gorcery_dict)
        return df
    


            
# if __name__ == '__main__':
#     ocado = Ocado_scraper()
#     ocado.accept_cookies()
#     ocado.big_price_drop()
#     ocado.extract_data()
#     ocado.teardown()
#     ocado.get_dataframe()
