#%%
from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests as req
import time
import pandas as pd
from pprint import pprint
import pymongo

def scrape():
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    news_url="https://mars.nasa.gov/news/?page=7&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(news_url)
    news_html = browser.html
    news_soup = bs(news_html, 'html.parser')
    article_titles = news_soup.find_all('h3')
    articles = news_soup.find_all('div', class_='rollover_description_inner')
    news_title = article_titles[6].text
    news_desc = articles[6].text
    image_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(image_url)
    browser.click_link_by_partial_text("FULL IMAGE")
    image_html = browser.html
    image_soup = bs(image_html, 'html.parser')
    c = 0
    while c < 15:
        try:
            partial_url = image_soup.find_all('div', class_="fancybox-dark-skin")[0].img['src']
            break
        except:
            c+=1
            print(f"Attempt #{c}  to pull Featured has failed")
            time.sleep(1.5)
            image_html = browser.html
            image_soup = bs(image_html, 'html.parser')
    featured_image_url = f"http://jpl.nasa.gov{partial_url}"
    table = pd.read_html("https://space-facts.com/mars/")
    table = table[0]
    table.set_index(0, inplace=True)
    table.columns = ['Mars']
    table.index.names = ['Description']
    table_html = table.to_html()
    hemisphere_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    hemisphere_html = req.get(hemisphere_url).text
    hemisphere_soup = bs(hemisphere_html, 'html.parser')
    hemisphere_titles = []
    for bite in hemisphere_soup.find_all('div', class_ = "item"):
        hemisphere_titles.append(bite.h3.text)
    hemisphere_titles_images = []
    for title in hemisphere_titles:
        browser.visit(hemisphere_url)
        browser.click_link_by_partial_text(title)
        hemisphere_soup = bs(browser.html, 'html.parser')
        hemisphere_titles_images.append({
            "title":title.replace('\n',''),
            "img_url":hemisphere_soup.find('div', class_="downloads").ul.li.a['href']
        })

    ouput = {}
    ouput['News_Title'] = news_title.replace('\n','')
    ouput['News_Desc'] = news_desc.replace('\n','')
    ouput['Featured_Image'] = featured_image_url
    ouput['Table'] = table_html
    ouput['Hemisphere_List'] = hemisphere_titles_images

    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.MarsDB
    db.mars.drop()
    db.mars.insert_one(
        ouput
    )
#%%
#   Here is a default dataset.  Scraping takes a while and loading a default will create a 
#snappy initial load
def def_db():
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.MarsDB
    db.mars.insert_one(
        {   'News_Title': 'The Red Planet',
            'News_Desc': "The team also fueled the rover's sky crane to get ready for this summer's history-making launch.",
            'Featured_Image': 'http://jpl.nasa.gov/spaceimages/images/mediumsize/PIA00271_ip.jpg',
            'Table': '<table border="1" class="dataframe">\n  <thead>\n    <tr style="text-align: right;">\n      <th></th>\n      <th>Mars</th>\n    </tr>\n    <tr>\n      <th>Description</th>\n      <th></th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <th>Equatorial Diameter:</th>\n      <td>6,792 km</td>\n    </tr>\n    <tr>\n      <th>Polar Diameter:</th>\n      <td>6,752 km</td>\n    </tr>\n    <tr>\n      <th>Mass:</th>\n      <td>6.39 × 10^23 kg (0.11 Earths)</td>\n    </tr>\n    <tr>\n      <th>Moons:</th>\n      <td>2 (Phobos &amp; Deimos)</td>\n    </tr>\n    <tr>\n      <th>Orbit Distance:</th>\n      <td>227,943,824 km (1.38 AU)</td>\n    </tr>\n    <tr>\n      <th>Orbit Period:</th>\n      <td>687 days (1.9 years)</td>\n    </tr>\n    <tr>\n      <th>Surface Temperature:</th>\n      <td>-87 to -5 °C</td>\n    </tr>\n    <tr>\n      <th>First Record:</th>\n      <td>2nd millennium BC</td>\n    </tr>\n    <tr>\n      <th>Recorded By:</th>\n      <td>Egyptian astronomers</td>\n    </tr>\n  </tbody>\n</table>',
            'Hemisphere_List': [{'title': 'Cerberus Hemisphere Enhanced',
            'img_url': 'https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/cerberus_enhanced.tif/full.jpg'},
            {'title': 'Schiaparelli Hemisphere Enhanced',
            'img_url': 'https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/schiaparelli_enhanced.tif/full.jpg'},
            {'title': 'Syrtis Major Hemisphere Enhanced',
            'img_url': 'https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/syrtis_major_enhanced.tif/full.jpg'},
            {'title': 'Valles Marineris Hemisphere Enhanced',
            'img_url': 'https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/valles_marineris_enhanced.tif/full.jpg'}]}
                )
# %%
