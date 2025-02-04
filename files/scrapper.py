from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


def facebook_login(driver,email,password):
  

  driver.get('https://www.facebook.com/login')
  wait = WebDriverWait(driver, 10)
  email_field =wait.until(EC.element_to_be_clickable((By.XPATH,"""//*[@id="email"]""")))
  email_field.send_keys(email) 
  password_field = wait.until(EC.element_to_be_clickable((By.XPATH,"""//*[@id="pass"]""")))
  password_field.send_keys(password)

  login_button = wait.until(EC.element_to_be_clickable((By.XPATH, """//*[@id="loginbutton"]""")))
  login_button.click()

  time.sleep(3)


def visit_facebook_profile(driver, username):
    driver.get("https://www.facebook.com")
    wait = WebDriverWait(driver, 10)
    search_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Search Facebook']")))
    search_box.click()
    search_box.send_keys(username)
    search_box.send_keys(Keys.RETURN)

    time.sleep(3)  

    try:  
        profile_link_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.x1cy8zhl.x78zum5.xl56j7k.xq8finb > div > a")))
        
        profile_url = profile_link_element.get_attribute("href")
        print(f"Profile URL: {profile_url}")

        driver.get(profile_url)
        time.sleep(5)
        return profile_url
    except Exception as e:
        print("Profile link not found:", e)
        return None
def scrape_page(driver, page_url):
    try:
    
        driver.get(page_url)
       
        wait = WebDriverWait(driver, 20)
        
        data = {}
        
        try:
            
            email_id = wait.until(EC.presence_of_element_located((By.XPATH,
                """/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/ul/div[3]/div[2]/div/div/span""")))
            data['email'] = email_id.text
            print(f"Email: {data['email']}")
        except Exception as e:
            print(f"Error getting email: {str(e)}")
            data['email'] = None

        try:
            
            page_info = wait.until(EC.presence_of_element_located((By.XPATH,
                """/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/ul/div[1]/div[2]/div/div/div/span/div/span""")))
            data['page_info'] = page_info.text
            print(f"Page Info: {data['page_info']}")
        except Exception as e:
            print(f"Error getting page info: {str(e)}")
            data['page_info'] = None
        try:
       
            page_url = wait.until(EC.presence_of_element_located((By.XPATH,
                """/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/ul/div[4]/div[2]/div/a/div/div/span""")))
            data['page_url'] = page_url.text
            print(f"Page url: {data['page_url']}")
        except Exception as e:
            print(f"Error getting page url: {str(e)}")
            data['page_url'] = None
      

        try:
        
            profile_pic = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 
                "div[role='main'] image[preserveAspectRatio='xMidYMid slice']")))
            profile_pic_link = profile_pic.get_attribute("xlink:href")
            data['profile_pic'] = profile_pic_link
            print(f"Profile picture (Method 1): {profile_pic_link}")
        except Exception as e:
            print(f"Method 1 failed: {str(e)}") 
           

        try:
        
            page_name = wait.until(EC.presence_of_element_located((By.XPATH,
                """/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[1]/div/div/span/h1""")))
            data['page_name'] = page_name.text
            print(f"Page Name: {data['page_name']}")
        except Exception as e:
            print(f"Error getting page name: {str(e)}")
            data['page_name'] = None

        try:
          
            total_followers = wait.until(EC.presence_of_element_located((By.XPATH,
                """/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[2]/span/a[1]""")))
            data['followers'] = total_followers.text
            print(f"Followers: {data['followers']}")
        except Exception as e:
            print(f"Error getting followers count: {str(e)}")
            data['followers'] = None

        try:
          
            total_likes = wait.until(EC.presence_of_element_located((By.XPATH,
                """/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[2]/span/a[1]""")))
            data['likes'] = total_likes.text
            print(f"Likes: {data['likes']}")
        except Exception as e:
            print(f"Error getting likes count: {str(e)}")
            data['likes'] = None

        try:
            #used scroll instead of xpath
            driver.execute_script("window.scrollTo(0, 300)")
            time.sleep(2)
            about_page = wait.until(EC.element_to_be_clickable((By.XPATH,
                """/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div/a[2]/div[1]""")))
            about_page.click()
            time.sleep(2)

            
            page_sd = wait.until(EC.element_to_be_clickable((By.XPATH,
                """/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[1]/div[3]/a""")))
            page_sd.click()
            time.sleep(2)

          
            page_number = wait.until(EC.presence_of_element_located((By.XPATH,
                """/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[1]/span""")))
            data['page_number'] = page_number.text
            print(f"Page Number: {data['page_number']}")
            creation_date = wait.until(EC.presence_of_element_located((By.XPATH,"""/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div/div[3]/div/div/div[2]/div[1]/span""")))
            data['creation date'] = creation_date.text
            print(creation_date.text)

        except Exception as e:
            print(f"Error in about page navigation: {str(e)}")
            data['page_number'] = None

        return data

    except Exception as e:
        print(f"Major error occurred: {str(e)}")
        return None

