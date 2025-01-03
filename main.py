#____________________________________________________IMPORTS_________________________________________________________________________
import os
import time
import json
import datetime
from icecream import ic
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
ic.configureOutput(includeContext=True)
#______________________________________________________________Browser Setup_________________________________________________________
def chromeBrowser():
    try:
        os.system("taskkill /f /im chrome.exe")
    except:
        pass
    options = Options()
    
    dataDir = os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data")
    options.add_argument(f"--user-data-dir={dataDir}")
    options.add_argument("--profile-directory=Default")
    
    service = Service(ChromeDriverManager().install())
    
    return webdriver.Chrome(options=options, service=service)

def edgeBrowser():
    options = Options()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    # Enable verbose logging for debugging
    options.add_argument("--enable-logging")
    options.add_argument("--v=1")
    options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    driver_path = r"C:\path\to\msedgedriver.exe"
    return webdriver.Edge(executable_path=driver_path, options=options)
#_____________________________________________________________Data management_________________________________________________________
def dataManagement(file, date, status=None):
    try:
        with open(file, "r") as f:
            dateData = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        dateData = {}
    if status is None:
        if date in dateData:
            ic("qns solved . . .")
            return None
        return dateData
    dateData[date] = status
    with open(file, "w") as f:
        json.dump(dateData, f, indent=4)
    return None
#__________________________________________________________________________main script . . .
def main():
    file = 'D:\\AutoLeetcode\\leetcodeStreak.json'
    ic(file)
    date = datetime.date.today().isoformat()
    dateData = dataManagement(file, date)
    if dateData is None:
        return
    driver = chromeBrowser()
    try:
        # setting the link
        driver.get("https://leetcode.com/problemset/")
        # waiting to load the qns pannel
        WebDriverWait(driver, 60).until(
            ec.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[4]/div[2]/div[2]/div[1]/div/div[2]"))
        )
        #navigate to the problem of the day
        while True:
            try:
                # Construct the dynamic XPath
                xpath = f"/html/body/div[1]/div[1]/div[4]/div[2]/div[2]/div[1]/div/div[2]/a[{datetime.date.today().day}]"
                qnsTab = WebDriverWait(driver, 60).until(
                    ec.element_to_be_clickable((By.XPATH, xpath))
                )
                qnsTab.click()
                break  
            except Exception as e:
                ic(f"Retrying on qns of the day, Error: {e}")
        # switiching the tab, controll given to new tab . . .
        tabs = driver.window_handles
        driver.switch_to.window(tabs[-1])
        # opening editorial section . . .
        while True:
            try:
                editorialSec = WebDriverWait(driver,20).until(
                    ec.element_to_be_clickable((By.XPATH,"/html/body/div[1]/div[2]/div/div/div[4]/div/div/div[1]/div[1]/div[1]/div/div[3]/div"))
                )
                editorialSec.click()
                driver.execute_script("arguments[0].scrollIntoView(true);", editorialSec)
                break
            except Exception as e:
                ic(e) 
        # getting playground link . . .
        retries = 5
        content = ""
        while retries > 0:
            try:
                solDiv = WebDriverWait(driver, 10).until(
                    ec.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/div/div[4]/div/div/div[5]/div/div[2]/div/div[2]/div/div'))
                )                                             #/html/body/div[1]/div[2]/div/div/div[4]/div/div/div[5]/div/div[2]/div/div[2]/div/div
                content = driver.execute_script("return arguments[0].innerHTML;", solDiv)
                if content.strip():  # Break if non-empty content is retrieved
                    ic(content[:100])
                    break
            except Exception as e:
                retries -= 1
                time.sleep(2)
        # getting list of all solutions . . .
        soup = BeautifulSoup(content, "html.parser")
        ic(soup.prettify())
        iFrames = soup.find_all("iframe")
        ic(iFrames)
        iFrame = []
        for i, iframe in enumerate(iFrames, 1):
            src = iframe.get("src", "No src attribute found")
            iFrame.append(src)
        # opening playground to copy code . . .
        ic(iFrame)
        driver.get(iFrame[-1])
        copyBtn = WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.XPATH,"/html/body/div[1]/div/div[1]/div[2]/button"))
        )
        copyBtn.click()
        driver.back() # back to the qns of the day tab . . .
        # for selecting the writing section . . .
        writerDiv = WebDriverWait(driver, 20).until(
            ec.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div/div/div[4]/div/div/div[8]/div/div[2]/div[1]/div/div/div[1]/div[2]/div[1]/div[5]"))
        )
        writerDiv.click()
        driver.implicitly_wait(2)
        # pasting the copied code . . .
        action = ActionChains(driver)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        # submit the code . . .
        submit = WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.XPATH,"/html/body/div[1]/div[2]/div/div/div[3]/div/div/div[1]/div/div/div[2]/div/div[2]/div/div[3]/div[3]/div/button"))
        )
        submit.click()
        #saving the data . . .
        dataManagement(file, date, "solved")
    except Exception as e:
        ic(f"Error occurred: {e}")
    finally:
        time.sleep(30)
        driver.quit()
if __name__ == "__main__":
    main()