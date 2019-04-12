import atexit
import os
import time
import json

#IMPORTING FILES
from analysis import text_analyse

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    WebDriverException,
    )
from dateutil.parser import parse
# Enter your own facebook username and password

global USERNAME, PASSWORD
USERNAME = '58071626'
PASSWORD = 'admin_fyp123'
global RETURN_KEY
RETURN_KEY = Keys.RETURN

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.binary_location = '/app/.apt/usr/bin/google-chrome'
# instantiate a chrome options object so you can set the size and headless preference
options.add_argument("--headless")
options.add_argument("--window-size=1920x1080")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
# 1-Allow, 2-Block, 0-default
preferences = {
    "profile.default_content_setting_values.notifications" : 2,
    "profile.default_content_setting_values.location": 2,
    # We don't need images, only the URLs.
    "profile.managed_default_content_settings.images": 2,
    }
options.add_experimental_option("prefs", preferences)

global driver
browser = webdriver.Chrome(
    executable_path='/app/.chromedriver/bin/chromedriver',
    chrome_options = options
    )
WAIT_TIME = 5

driver.wait = WebDriverWait(driver, WAIT_TIME)

def close_browser():
    """
    Close the browser.
    """
    try:
        driver.quit()
    except WebDriverException:
        # Might be already closed.
        pass

# Make sure browser is always closed, even on errors.
atexit.register(close_browser, driver)

def fb_login():
    """
    Login to facebook using username and password.
    """
    driver.get('https://www.facebook.com/')
    usr = driver.find_element_by_name("email")
    usr.send_keys(USERNAME)
    password = driver.find_element_by_name("pass")
    password.send_keys(PASSWORD)
    password.send_keys(RETURN_KEY)
    #raw_input(
     #   "Confirm that you authenticated with the right user.\n"
      #  "Check no browser popups are there."
       # )

def scroll_down():
    """A method for scrolling the page."""

    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scroll_to_element(element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def move_to_element(element):
    """
    Get element in the current viewport and have to mouse over it.
    """
    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.perform()

def go_to_page(url):
    driver.get(url)

#---LOOPING THROUGH EACH POSTS----
def postLoop(postDiv, array, searchterm, postLimit=False):

    count = 0
    for post in postDiv:
        global t, d, c, contents

        # ---- GET DATE ---- #

        # for recent posts
        date = post.find_element_by_tag_name("abbr").get_attribute("title")

        # obtain date in format DD/MM/YYYY
        dt = parse(date)
        d = str(dt.date())

        # clicking on the post to obtain full content text
        post.find_element_by_class_name('_4rmu').click()
        time.sleep(4)

        # ---- GET CONTENTS --- #
        contents = driver.find_elements_by_tag_name('p')
        c = ""
        for content in contents:
            print(content)
            c = c + content.text + "\t"

        #extract disease details from content to determine whether post is to be discarded or stored in db
        dis, sent = text_analyse.extract_disease(c, 60)
        if dis == "":
            print("post not valid for storage, discarding...")
        else:
            # content is valid therefore post will be further analysed for location details if any, and then stored.
            # if location is already enabled on the post
            try:
                l = post.find_element_by_class_name('_62xw')
                location = l.text

            except:
                # else extract location details from the content
                loc = text_analyse.extract_location(c, 80)
                if loc == "":
                    location = "Not found"
                else:
                    location = loc

            #putting all scraped details together
            data = {
                'diseasetype': searchterm,
                'date': d,
                'location': location,
                'post': sent
            }
            print(data)
            array.append(data)

        time.sleep(1)
        try:
            el = driver.find_element_by_class_name('_n9')
            action = webdriver.common.action_chains.ActionChains(driver)
            action.move_to_element_with_offset(el, 30, 30)
            action.click()
            action.perform()
            time.sleep(2)
        except:
            print("Continuing to next post")
        count = count + 1
        if postLimit == True and count == 2:
            print("Reached post limit - breaking out of loop")
            break
        else:
            continue

def save_to_file(json_arr, path):
    try:
        with open(path, 'a') as outfile:
            json.dump(json_arr, outfile)
    except:
        print("file error")

def scrape_realtime(url, driver):
    data_arr = []

    if url.__contains__('flu'):
        disease = 'influenza'
    if url.__contains__('gastro'):
        disease = 'gastroenteritis'
    if url.__contains__('conjunctivitis'):
        disease = 'conjunctivitis'
    elif url.__contains__('respiratory'):
        disease = 'respiratory infection'

    go_to_page(url, driver)
    time.sleep(3)

    post_div = driver.find_elements_by_class_name("_307z")
    #scroll_div = scrollContainer.find_elements_by_xpath("//div[@class='_o02']")
    postLoop(post_div,data_arr, driver, disease,postLimit=True)

    time.sleep(1)

    return data_arr

def scrape_page(url, diseaseterm, data_arr):

    go_to_page(url)
    time.sleep(3)

    #Looping through the first post/div
    firstdivloop = driver.find_elements_by_xpath("//div[@id='BrowseResultsContainer']/div/div/div/div")
    #firstdivloop = driver.find_elements_by_xpath("//div[@id='BrowseResultsContainer']//div[@class='_6rbb']/div")
    postLoop(firstdivloop,data_arr, diseaseterm)

    try:
        #Looping through the second post/div
        secdivloop = driver.find_elements_by_xpath("//div[@data-testid='paginated_results_pagelet']/div/div/div/div/div/div")
        postLoop(secdivloop,data_arr, diseaseterm)

        #scroll to end of results
        scroll_down()
        time.sleep(3)

        #looping through the rest of the posts
        scrollContainers = driver.find_elements_by_xpath("//div[contains (@id, 'fbBrowseScrollingPagerContainer')]")

        gototop = driver.find_element_by_xpath("//div[@data-testid='paginated_results_pagelet']/div")
        scroll_to_element(gototop)
        time.sleep(3)

        for scrollContainer in scrollContainers:
            scroll_div = scrollContainer.find_elements_by_class_name("_307z")
            #scroll_div = scrollContainer.find_elements_by_xpath("//div[@class='_o02']")
            postLoop(scroll_div, data_arr, diseaseterm)
            time.sleep(1)
    except:
        print("Only two posts found.")

# ----------------END OF FUNCTIONS DEFINITION------------------#
#--------------------------------------------------------------#