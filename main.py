from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
import time
import logging
import json
import re

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logging_info.log")
    ]
)

def scrollingDown(driver):
    last_height = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = driver.execute_script("return document.body.scrollHeight")
        time.sleep(1)
        if(last_height == new_height):
            break
    
        last_height = new_height
        

def selecting_button(driver, element, wait):
    while True:
        try:
            div_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME,'show-more-btn')))
            driver.execute_script("arguments[0].scrollIntoView();",div_element)
            button = div_element.find_element(By.TAG_NAME, 'button')
            driver.execute_script("arguments[0].click();",button)
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
            logging.info("Pressing comment button has finished")
            break
    

def getting_comments(driver, chapter_link, wait):
    chapterComments = []
    driver.get(chapter_link)
    commentContainer = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="story-part-comments"]/div')))
    selecting_button(driver, commentContainer, wait)

    comments = commentContainer.find_elements(By.CLASS_NAME, 'comment-card-container')

    story_stats = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'story-stats')]")))

    views = story_stats.find_element(By.CLASS_NAME, 'reads').text
    likes = story_stats.find_element(By.CLASS_NAME, 'votes').text
    numberofComment = story_stats.find_element(By.CLASS_NAME, 'comments').text
    
    for i in comments:
        try:
            text = i.find_element(By.TAG_NAME, 'pre')
            chapterComments.append(text.text)
        except:
            logging.warning("ONE comment couldn't be processed")
            continue
    
    return {"link" : chapter_link, 
            "views": views,
            "likes": likes,
            "number of comments": numberofComment,
            "comments" : chapterComments}


def get_link_from_story(driver, story_link, wait):
    full_text = []
    driver.get(story_link)
    chaperContainer = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div[1]/div[7]")))
    links = chaperContainer.find_elements(By.TAG_NAME,"a")
    hrefSeen = []
    title = driver.find_element(By.CLASS_NAME, "gF-N5").text
    logging.info(f"Looking into {title}")
    stats = driver.find_elements(By.CLASS_NAME, "_0jt-y")
    chapter_statistics = []

    for stat in stats:
        try:
            sr = stat.find_element(By.XPATH,'.//span[@class="sr-only"]')
            clean = re.sub(r'[A-Za-z]', '', sr.text).strip()
            chapter_statistics.append(clean)

        except Exception as e:
            logging.warning(f"An error has occured, look at {e}")

    for story in links:
        if story and story.get_attribute("href") not in hrefSeen:
            hrefSeen.append(story.get_attribute("href"))

    for link in hrefSeen:
        try:
            entry = getting_comments(driver, link, wait)
            full_text.append(entry)
        except TimeoutException:
            logging.warning(f"Took to long to load. Skipping {link}")
            continue

        driver.get(story_link)
    # json_dump.append(entry)
    with open("wattpad.json", "r", encoding="utf-8") as f:
        try:
            json_dump = json.load(f)
        except json.decoder.JSONDecodeError as e:
            json_dump = []
            logging.warning(f"Failed to decode JSON: {e}")
        except ValueError as e:
            json_dump = []
            logging.warning(f"Value error: {e}")
        except:
            logging.warning(f"It is getting any error's in general{e}")
            json_dump = []
    
    with open("wattpad.json", "w", encoding="utf-8") as f:
        try:
            json_dump.append(
                {   "Title" : title,
                    "Story Link" : story_link,
                    "Reads" : chapter_statistics[0],
                    "Votes" : chapter_statistics[1],
                    "Story Details" : full_text}
                )
            json.dump(json_dump, f, indent=4, ensure_ascii=False)
        except:
            logging.warning(f"Couldn't dump one of the stories")
    


def main():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    genreLinks = ["https://www.wattpad.com/stories/lgbt", "https://www.wattpad.com/stories/shortstory", "https://www.wattpad.com/stories/poetry","https://www.wattpad.com/stories/romance",]
    json_dump = []
    for genre in genreLinks:
        driver.get(genre)
        container = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="scroll-div"]/div/ul')))
        scrollingDown(driver)
        story_links = container.find_elements(By.TAG_NAME,"a")
        hrefLinks = []

        for link in story_links:
            if(link.get_attribute("href") not in hrefLinks and "https://www.wattpad.com/story" in link.get_attribute("href")):
                hrefLinks.append(link.get_attribute("href"))
        
        for a in hrefLinks:
            wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="scroll-div"]/div/ul')))
            if a and "https://www.wattpad.com/story" in a:
                get_link_from_story(driver, a, wait)
                logging.info("Finished one story")
                driver.get(genre)
    


main()


#  with open("wattpad.json", "r", encoding="utf-8") as f:
#                     try:
#                         json_dump = json.load(f)
#                     except json.decoder.JSONDecodeError as e:
#                         json_dump = []
#                         print(f"Failed to decode JSON: {e}")
#                     except ValueError as e:
#                         json_dump = []
#                         print(f"Value error: {e}")
                
#                 with open("wattpad.json", "w", encoding="utf-8") as f:
#                     newList = {
#                         "author": "Me",

#                         "story_details": whole_list,
#                     }