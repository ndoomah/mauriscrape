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

def close_browser(driver):
    """
    Close the browser.
    """
    try:
        driver.quit()
    except WebDriverException:
        # Might be already closed.
        pass


def fb_login(driver):
    """
    Login to facebook using username and password.
    """
    driver.get('https://www.facebook.com/')
    time.sleep(3)
    usr = driver.find_element_by_id("email")
    usr.send_keys(USERNAME)
    time.sleep(1)
    password = driver.find_element_by_id("pass")
    password.send_keys(PASSWORD)
    password.send_keys(RETURN_KEY)
    #raw_input(
     #   "Confirm that you authenticated with the right user.\n"
      #  "Check no browser popups are there."
       # )

def scroll_down(driver):
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

def scroll_to_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def move_to_element(driver, element):
    """
    Get element in the current viewport and have to mouse over it.
    """
    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.perform()

def go_to_page(url, driver):
    driver.get(url)

#---LOOPING THROUGH EACH POSTS----
def postLoop(postDiv, array, driver, searchterm, postLimit=False):

    count = 0
    for post in postDiv:

    # scraping the post's title/name

        global t, d, c, contents
        """ --- post's title is not really needed ---
                title = driver.find_element_by_tag_name('h5')
                t = title.text
        """

        # ---- GET DATE ---- #

        #for recent posts
        date = post.find_element_by_tag_name("abbr").get_attribute("title")
        #date = post.find_element_by_class_name("timestampContent")
        #date = driver.find_element_by_xpath("//span[@class='timestampContent']")
        #t = date.rsplit('at',1)[0] #to remove time and only store date
        dt = parse(date)
        d = str(dt.date())

        # post.find_element_by_class_name('_6-co').click()
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
            #content is valid therefore post will be further analysed for location details if any, and then stored.

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

            #putting all scraped details into json file
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

def scrape_page(url, driver, diseaseterm, data_arr):

    go_to_page(url, driver)
    time.sleep(3)

    #Looping through the first post/div
    firstdivloop = driver.find_elements_by_xpath("//div[@id='BrowseResultsContainer']/div/div/div/div")
    #firstdivloop = driver.find_elements_by_xpath("//div[@id='BrowseResultsContainer']//div[@class='_6rbb']/div")
    postLoop(firstdivloop,data_arr,driver, diseaseterm)

    try:
        #Looping through the second post/div
        secdivloop = driver.find_elements_by_xpath("//div[@data-testid='paginated_results_pagelet']/div/div/div/div/div/div")
        postLoop(secdivloop,data_arr,driver, diseaseterm)

        #scroll to end of results
        scroll_down(driver)
        time.sleep(3)

        #looping through the rest of the posts
        scrollContainers = driver.find_elements_by_xpath("//div[contains (@id, 'fbBrowseScrollingPagerContainer')]")

        gototop = driver.find_element_by_xpath("//div[@data-testid='paginated_results_pagelet']/div")
        scroll_to_element(driver, gototop)
        time.sleep(3)

        for scrollContainer in scrollContainers:
            scroll_div = scrollContainer.find_elements_by_class_name("_307z")
            #scroll_div = scrollContainer.find_elements_by_xpath("//div[@class='_o02']")
            postLoop(scroll_div, data_arr, driver, diseaseterm)
            time.sleep(1)
    except:
        print("Only two posts found.")

# ----------------END OF FUNCTIONS DEFINITION------------------#
#--------------------------------------------------------------#