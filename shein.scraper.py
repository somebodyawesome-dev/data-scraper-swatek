from bs4 import BeautifulSoup
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time


# entryUrl = "https://fr.shein.com/Clothing-c-2035.html?ici=fr_tab01navbar04"
# entryUrl = "https://fr.shein.com/Men-Clothing-c-1969.html?ici=fr_tab04navbar03&scici=navbar_MenHomePage~~tab04navbar03~~3~~real_1969~~~~0&srctype=category&userpath=category%3EV%C3%8ATEMENTS"
entryUrl = "https://fr.shein.com/Clothing-c-2035.html?ici=fr_tab01navbar04&scici=navbar_WomenHomePage~~tab01navbar04~~4~~webLink~~~~0&srctype=category&userpath=category%3EV%C3%8ATEMENTS&tag_ids=70007004"
basesUrl = "https://fr.shein.com"
secondBaseUrl = "https://www.shein.com"


def getTotalPageNumber(entry_url, driver):

    driver.get(entry_url)
    soup = BeautifulSoup(driver.page_source, "lxml")

    return int(soup.find("span", class_="S-pagination__total").get_text().strip().split(" ")[0])


def getItemsFromPage(url: str):
    pageSource = requests.get(url).text
    soup = BeautifulSoup(pageSource, "lxml")
    return [ele.find("a")["href"] for ele in soup.find_all("section", {"role": "listitem"})]


def getDataFromRoute(url, driver):

    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "lxml")
    itemName = soup.find(
        "div", {"class": "product-intro__head-name"}).get_text().strip()
    priceContainer = soup.find("div", class_="product-intro__head-price")
    itemPrice = priceContainer.find(
        "div", class_="original").find("span").get_text().strip() if priceContainer.find("div", class_="original") else "{} au lieu {}".format(
        priceContainer.find("span").get_text().strip(), priceContainer.find("del", {"class": "del-price"}).get_text().strip())
    sizes = [size.find("span", {"class": "inner"}).get_text().strip()
             for size in soup.find("div", "product-intro__size-choose").find_all('div', {"class": "product-intro__size-radio"})]
    descriptionTables = []
    descriptionTables = [x.find_all("div", "product-intro__description-table-item")
                         for x in soup.find_all("div", {"class": "product-intro__description-table"})]

    description = [desc.find("div", {"class": "key"}).get_text().strip(
    )+desc.find("div", {"class": "val"}).get_text().strip() for desc in (descriptionTables[0] if len(descriptionTables) == 1 else descriptionTables[1])]
    colors = [color["aria-label"] for color in soup.find("div", {"class": "product-intro__color-choose"}).find_all(
        "div", {"class": "product-intro__color-radio"})] if soup.find("div", {"class": "product-intro__color-choose"}) else []

    images = [img.find("img")["data-src"][2:] for img in soup.find("div", {"class": "product-intro__gallery"}).find(
        "div", {"class": "product-intro__main"}).find("div", {"class": "swiper-wrapper"}).find_all("div", {"class": "swiper-slide"})]
    return {"nomProduit": itemName, "prix": itemPrice, "tailles": sizes, "description": description, "couleurs": colors, "imagesUrl": images}


csvHeader = ["nomProduit",  "prix", "tailles",
             "description", "couleurs", "imagesUrl"]
csvPath = "scraped data/shein femme v2.csv"


def writeToCSV(csvPath, csvHeader, data):
    try:
        with open(csvPath, 'w+', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csvHeader)
            writer.writeheader()
            for d in data:
                writer.writerow(d)
            print("job is done")
    except IOError as e:
        print("I/O error")
        print(str(e))


if __name__ == "__main__":
    driver = None
    itemsRoute = []
    i = 1
    err = 0
    data = []
    try:
        print("Searching for how many pages to scratch routs from...")
        driver = webdriver.Chrome()
        pagesNumber = getTotalPageNumber(entryUrl, driver)
        print("there is {} pages".format(pagesNumber))

        print("scratching the routes")
        for i in range(1, pagesNumber+1):
            itemsRoute += getItemsFromPage(entryUrl+"&page="+str(i))
            print("scratched the page number {}".format(i))
        data = []
        print("scraping data from the fetched routes ")

        for route in itemsRoute:
            try:
                data += [getDataFromRoute(basesUrl+route, driver)]
            except KeyboardInterrupt:
                break
            except:
                try:
                    data += [getDataFromRoute(secondBaseUrl+route, driver)]
                except:
                    err += 1
            i += 1
            print("[{}/{}][Errors:{}]-scraping {}".format(i,
                                                          len(itemsRoute), err, route))
        driver.close()
        print("writing data to csv file")
        writeToCSV(csvPath, csvHeader, data)
        print("job is done")
    except Exception as e:
        with open("data.txt", mode="a", encoding='utf-8') as file:
            for d in data:
                json.dump(d, file)
                file.write("\n")
        print(str(e))
        if driver:
            driver.close()
