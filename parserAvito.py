from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
import time
import csv
import base64
from PIL import Image
from pytesseract import image_to_string

sleeping_time = 3           # "human" delay


def parse_final_page(driver, url):
    print('[+]', url, sep=' ')
    current_item = 0
    while True:
        elements = driver.find_elements_by_class_name("description-title-link")
        element = elements[current_item]
        element.click()

        element = driver.find_element_by_class_name("seller-info-name")
        name = element.text

        element = driver.find_element_by_xpath("//div[@class='seller-info-prop']/div[@class='seller-info-value']")
        location = element.text

        number_element = driver.find_element_by_class_name("item-actions-line")
        number_element.click()
        time.sleep(sleeping_time)
        try:
            e = driver.find_element_by_class_name("item-phone-big-number")
            e = e.find_element_by_tag_name("img")
            e = e.get_attribute("src")
            e = e.split(",")[1]
            e = base64.b64decode(e)
            file = open("number.png", "w+b")
            file.write(e)
            file.close()

            path_image = "number.png"
            numbers_image = Image.open(path_image)
            number = image_to_string(numbers_image)

            print(current_item, name, number, location, sep=" ")
            output_file = open("db.csv", "a")
            writer = csv.writer(output_file)
            inserted_row = [name, number, location]
            writer.writerow(inserted_row)
            output_file.close()
        except NoSuchElementException:
            print("Exception!!!")

        if current_item == len(elements) - 1:
            driver.get(url)
            try:
                element = driver.find_element_by_class_name("js-pagination-next")
                element.click()
                url = driver.current_url
                print('[+]', url, sep=' ')
                current_item = 0
            except NoSuchElementException:
                break
        else:
            current_item += 1
            driver.get(url)
    return


def circumvention(url, driver):
    elements = driver.find_elements_by_class_name("js-catalog-counts__link")
    if elements:
        for i in range(0, len(elements)):
            next_url = elements[i].get_attribute("href")
            driver.get(next_url)
            circumvention(next_url, driver)
            driver.get(url)
            elements = driver.find_elements_by_class_name("js-catalog-counts__link")
    else:
        if "view=list" not in url:
            url = url.split("?")[0] + "?view=list"
            try:
                driver.get(url)
            except WebDriverException:
                print("WebDriverException!!!\nThere isn't requested page!")

        parse_final_page(driver, url)
        print(url)
        return


start_urls = [
    # "https://www.avito.ru/krasnoyarsk/odezhda_obuv_aksessuary/zhenskaya_odezhda/bryuki/40-42_xs?view=list",
    # "https://www.avito.ru/krasnoyarsk",
    'https://www.avito.ru/krasnoyarsk/koshki?view=list&s_trg=10',
]

try:
    output_file = open("db.csv", "r")
except FileNotFoundError:
    output_file = open('db.csv', 'w')
    output_file.close()
    output_file = open("db.csv", "r")
reader = csv.DictReader(output_file,
                        fieldnames=["id", "name", "phone_number", "region", "url"])

last_rec_id = sum(1 for row in reader)

for row in reader:
    last_rec_id = row["id"]
if last_rec_id == -1:
    print("[+] Detected 0 records in the DB")
else:
    print("[+] Detected %d records in the DB" % last_rec_id)
output_file.close()


for url in start_urls:
    driver = webdriver.Chrome()
    driver.get(url)
    circumvention(url, driver)

    driver.close()
