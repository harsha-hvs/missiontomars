# Import functionalities
from splinter import Browser
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

# instantiate the splinter object 
def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():

    #Initiate Object Of chromedriver
    executable_path = {'executable_path': "chromedriver.exe"}
    browser = Browser('chrome', **executable_path, headless=False)

    # Scrape the NASA Data
    nasa_url = "https://mars.nasa.gov/news/"
    nasa_response = requests.get(nasa_url)
    nasa_soup = BeautifulSoup(nasa_response.text, "html.parser")
    news_title = (nasa_soup.find("div", class_="content_title").find('a').text).replace('\n', '')
    news_description = (nasa_soup.find("div", class_="rollover_description_inner").text).replace('\n', '')

    # Scrape the JPL MARS site for the image
    mars_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    mars_response = requests.get(mars_url)
    mars_soup = BeautifulSoup(mars_response.text, "lxml")
    featured_image_style =  mars_soup.find("div", class_="carousel_items").find('article')['style']
    featured_image_url = "".join(mars_url.split("/spaceimages")[0]) + re.findall("url\('(.*?)'\)", featured_image_style)[0]

    # Scrape the NASA Data
    twitter_url = "https://twitter.com/marswxreport?lang=en"
    twitter_response = requests.get(twitter_url)
    twitter_soup = BeautifulSoup(twitter_response.text, "html.parser")
    mars_weather = ''.join((twitter_soup.find("div", class_="js-tweet-text-container").find('p').text).partition("hPa")[:2])

    # Scrape the facts Data
    facts_url = 'https://space-facts.com/mars/'
    facts_tables = pd.read_html(facts_url)
    facts_df = facts_tables[1]
    facts_df.columns = ['Description','Value']
    facts_df.set_index('Description', inplace=True)
    facts_table = facts_df.to_html().replace('\n', '')

    # Scrape the JPL MARS site for the image
    hemisphere_image_urls=[]
    hemis_browser = init_browser()
    mars_hemispheres = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    hemis_browser.visit(mars_hemispheres)
    hemispheres_html = hemis_browser.html
    hemispheres_soup = BeautifulSoup(hemispheres_html, "lxml")
    hemispheres_div = hemispheres_soup.find_all("div", class_="description")
    for index,div in enumerate(hemispheres_div):
        hemisphere_dict={}
        hemisphere_dict["title"] = div.find('h3').text
        ##Get url
        #hemisphere_url = div.find('a')['href']
        #Visit page
        hemis_browser.click_link_by_partial_text(hemisphere_dict["title"])
        #Extract image 
        hemisphere_url_html = hemis_browser.html
        hemisphere_url_soup = BeautifulSoup(hemisphere_url_html, "lxml")
        hemisphere_dict["img_url"] = hemisphere_url_soup.find("div", class_="downloads").find('li').find('a')['href']
        hemisphere_image_urls.append(hemisphere_dict)
        hemis_browser.back()
    # Close the browser after scraping
    hemis_browser.quit()

    scrapped_listings = {
        "news_title": news_title,
        "news_paragraph": news_description,
        "featured_image": featured_image_url,
        "weather": mars_weather,
        "facts": facts_table,
        "hemispheres": hemisphere_image_urls        
    }

    return scrapped_listings

if __name__ == "__main__":
    pass

