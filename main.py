
import time
import os
import hashlib
import requests
import urllib.request
from bs4 import BeautifulSoup as bs
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

# import webbrowser

NUM_BUFFER_PAGE = 5
SEARCH_CYCLE = 6
NOT_SEARCHED_LIMIT = 30
ORG_PAGE_ADDR = "https://imgdb.in/"
ORG_PAGE_ADDR2 = "https://imgdb.in/v2/"
# ERR_STR = "<script>location.href="https://image.kilho.net/?err=1";</script>"


def get_nextPage(PageStr):
    is_not_done = True
    idx = 3
    while is_not_done:
        if PageStr[idx] == "9":
            riseChar = "a"
            is_not_done = False
        elif PageStr[idx] == "z":
            riseChar = "A"
            is_not_done = False
        elif PageStr[idx] == "Z":
            riseChar = "0"
            PageStr = PageStr[:idx] + riseChar + PageStr[idx + 1 :]
            idx -= 1
            if idx < 0:
                is_not_done = False
            continue
        else:
            riseChar = chr(ord(PageStr[idx]) + 1)
            is_not_done = False
        PageStr = PageStr[:idx] + riseChar + PageStr[idx + 1 :]

    return PageStr


def get_index_str(initStr: str):
    PageStr = initStr
    res = []
    for i in range(NUM_BUFFER_PAGE):
        PageStr = get_nextPage(PageStr)
        res.append(PageStr)
    return res


def calc_file_hash(path):
    f = open(path, "rb")
    data = f.read()
    hash = hashlib.md5(data).hexdigest()
    return hash


def reset_init():
    reset_init.counter += 1

    driver = webdriver.Chrome()
    driver.get(ORG_PAGE_ADDR2)
    p = driver.find_element_by_xpath('//*[@id="upload_media"]/div/input[@type="file"]')
    p.send_keys(os.path.abspath("dummy.png"))
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "gallery-items"))
    )
    resStr = driver.current_url[-4:]
    driver.execute_script("javascript:file_delete()")
    WebDriverWait(driver, 20).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    alert.accept()
    print(reset_init.counter, end="  ")
    print(datetime.now())
    driver.quit()
    return resStr


def get_images():
    global initStr
    get_images.counter += 1
    if get_images.counter > NOT_SEARCHED_LIMIT:
        get_images.counter = 0
        initStr = reset_init()
    SearchList = get_index_str(initStr)
    for addr in SearchList:
        page = requests.get(ORG_PAGE_ADDR + addr)
        soup = bs(page.text, "html.parser")
        if len(page.text) > 70:
            initStr = addr
            print(initStr, end="  ")
            print(datetime.now())
            get_images.counter = 0
            gg = soup.select("img.img-responsive.gallery-items")
            ImgAddr = gg[0].attrs["src"]
            ImgExt = ImgAddr[len(ImgAddr) - ImgAddr[::-1].find(".") - 1 :]

            urllib.request.urlretrieve(ImgAddr, "storage/temp" + ImgExt)
            # os.path.exists(file):
            os.system(
                "mv storage/temp"
                + ImgExt
                + " storage/"
                + calc_file_hash("storage/temp" + ImgExt)
                + ImgExt
            )
    return


def main():
    global initStr
    while True:
        try:
            start_time = time.time()

            reset_init.counter = 0
            initStr = reset_init()
            get_images.counter = 0
            while True:
                current_time = time.time()
                elapsed_time = current_time - start_time

                if elapsed_time > SEARCH_CYCLE:
                    start_time = time.time()
                    get_images()
        except:
            continue
    return


if __name__ == "__main__":
    main()
