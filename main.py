from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
import time
# import logging
import json

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
            break
    

def getting_comments(driver, chapter_link, wait):
    story_details = []
    chapterComments = []
    driver.get(chapter_link)
    commentContainer = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="story-part-comments"]/div')))
    selecting_button(driver, commentContainer, wait)
    comments = commentContainer.find_elements(By.CLASS_NAME, 'comment-card-container')
    for i in comments:
        text = i.find_element(By.TAG_NAME, 'pre')
        print(text.text)
        chapterComments.append(text.text)
    
    driver.back()
    return {"link" : chapter_link, 
            "comments" : chapterComments}


def get_link_from_story(driver, story_link, wait):
    json_dump = []
    driver.get(story_link)
    chaperContainer = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div[1]/div[7]")))
    links = chaperContainer.find_elements(By.TAG_NAME,"a")
    # for link in links:
    for link in links:
        # print(link.get_attribute("href"))
        entry = getting_comments(driver, link.get_attribute("href"), wait)
        # json_dump.append(entry)
        
        with open("wattpad.json", "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=4, ensure_ascii=False)
    


def main():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    genreLinks = ["https://www.wattpad.com/stories/lgbt", "https://www.wattpad.com/stories/shortstory", "https://www.wattpad.com/stories/poetry","https://www.wattpad.com/stories/romance",]
    
    for genre in genreLinks:
        driver.get(genre)
        container = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="scroll-div"]/div/ul')))
        scrollingDown(driver)
        story_links = container.find_elements(By.TAG_NAME,"a")
        hrefLinks = []
        for link in story_links:
            hrefLinks.append(link.get_attribute("href"))
        
        for a in hrefLinks:
            wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="scroll-div"]/div/ul')))
            if a and "https://www.wattpad.com/story" in a:
                get_link_from_story(driver, a, wait)
                driver.back()
    


main()
