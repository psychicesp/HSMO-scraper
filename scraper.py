#%%
from splinter import Browser
from bs4 import BeautifulSoup
import requests as req
import time
import pandas as pd
from pprint import pprint
from datetime import datetime
time_format = '%d %B %Y %I:%M%p'
url = 'https://www.hsmo.org/adopt/'
executable_path = {'executable_path': 'chromedriver.exe'}
#%%
def scrape():
    browser = Browser('chrome', **executable_path, headless=False)
    browser.visit(url)
    time.sleep(1)
    doggie_soup = BeautifulSoup(browser.html, 'html.parser')
    browser.quit()
    dog_bites = doggie_soup.find_all("div", class_ = "animal_upper")
    dogs = []
    for dog_bite in dog_bites:
        dog = {
            'ID':0,
            'Name':'',
            'Sex':'',
            'Breed':'',
            'Age':'',
            'Color':'',
            'Location':'',
            'First_Found':0,
            'Last_Found':0
        }
        dog['Name'] = dog_bite.find("div", class_ = "animal_name").text
        dog['ID'] = dog_bite.find("div", class_ = "animal_id").text.replace('(','').replace(')','')
        dog_desc = dog_bite.find_all("div", class_ = "animal_desc")
        dog['Sex'] = dog_desc[1].text
        dog['Breed'] = dog_desc[0].text
        dog['Age'] = dog_desc[2].text
        dog['Color'] = dog_desc[3].text
        dog['Location'] = dog_bite.find("div", class_ = "animal_location").text
        dog['First_Found'] = datetime.now().strftime(time_format)
        dogs.append(dog)
    new_doggie_df = pd.DataFrame(dogs)
    new_doggie_df = new_doggie_df.set_index('ID')
    new_doggie_df.to_csv('New_Dogs.csv')
    doggie_df = pd.read_csv('Dogs.csv').set_index('ID')
    for index, row in new_doggie_df.iterrows():
        if index in doggie_df.reset_index()['ID'].to_list():
            doggie_df.loc[index, 'Last_Found'] = row['First_Found']
    doggie_df = pd.concat([doggie_df, new_doggie_df])
    doggie_df = doggie_df.groupby('ID').first()
    doggie_df.to_csv('Dogs.csv')

def run_loop():
    c = 0
    while c<20000:
        try:
            scrape()
            c+=1
            print(f"Ran {c} times.  Last ran {datetime.now().strftime(time_format)}")
        except:
            try:
                print("     Had an error, trying again in 5 seconds...")
                time.sleep(5)
                scrape()
                print(f"Ran {c} times.  Last ran {datetime.now().strftime(time_format)}")
            except:
                try:
                    print("         Had another error, trying again in 5 minutes")
                    time.sleep(300)
                    scrape()
                    print(f"Ran {c} times.  Last ran {datetime.now().strftime(time_format)}")
                except:
                    print("             Had YET ANOTHER error, skipping this cycle")
        time.sleep(1800)
#%%
