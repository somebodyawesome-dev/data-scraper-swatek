# lxml required
# beautifulsoup4 required
# requests required
# csv required
# chrome webdriver required

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time


def getSearchLinks(entry: str):

    result = []
    driver = webdriver.Chrome()
    driver.implicitly_wait(2)
    driver.get(entry)
    driver.find_element_by_id("select2-select-profession-container").click()
    searchLinkIDs = [item.get_attribute('id').split("-")[-1] for item in driver.find_elements_by_class_name(
        "select2-results__option") if "catID#" in item.get_attribute('id')]
    # for each id
    print(searchLinkIDs)
    driver.refresh()
    for id in searchLinkIDs:
        # driver.execute_script("arguments[0].setAttribute('aria-activedescendant',arguments[1])", driver.find_element_by_id(
        #     "select2-select-profession-container").find_element_by_xpath(".."), id)
        driver.find_element_by_id(
            "select2-select-profession-container").click()
        for item in driver.find_elements_by_class_name("select2-results__option"):
            if item.get_attribute('id').split("-")[-1] == id:
                item.click()

                break
        driver.find_element_by_id("btn-search").click()
        time.sleep(2)
        result.append(driver.current_url)
    return result


def getNumberOFSearchLinks(entry):
    try:
        pageSource = requests.get(entry).text
        soup = BeautifulSoup(pageSource, "lxml")
        li = soup.find("ul", {"class": "cd-pagination"}).find_all("li")
        return int(li[-1].find("a")["href"].split("/")[-2])
    except:
        return 1


def getDataFromSearchLink(url):
    result = []
    pageSource = requests.get(url).text
    soup = BeautifulSoup(pageSource, "lxml")
    LawyersCards = soup.find_all(
        "li", {"itemtype": "https://schema.org/LocalBusiness"})
    for card in LawyersCards:
        try:
            cabinetName = card.find(
                "span", {"class": "business-name"}).get_text().strip()
            rows = card.find_all("div", {"class": "row top-space"})
            ownerName = rows[0].find("div", class_="col-sm-5").find(
                "div", class_="detailed-info").get_text() if (rows[0].find("div", class_="col-sm-5")) else "None"
            phoneNumber = formatPhoneNumber(rows[0].find("div", class_="col-sm-7 telephone").find(
                "span", class_="phone-number").get_text()) if (rows[0].find("div", class_="col-sm-7 telephone")) else "None"
            addressSpan = rows[1].find("table", class_="detailed-info addr") if len(
                rows) > 1 and rows[1].find("table", class_="detailed-info addr") else None
            address = formatAdresse(addressSpan.find("span", {"itemprop": "address"}).get_text(
            )) if addressSpan and addressSpan.find("span", {"itemprop": "address"}) else "None"
            gov = formatAdresse(addressSpan.find("span", {"itemprop": "addressRegion"}).get_text(
            ), trimeNumber=True) if addressSpan and addressSpan.find("span", {"itemprop": "addressRegion"}) else "None"
            typeBusiness = card.find("a", {"class": "services"}).get_text().split(
                " in ")[0] if(card.find("a", {"class": "services"})) else "None"

            result.append({"businessName": cabinetName,
                           "typeBusiness": typeBusiness,
                           "ownerName": ownerName.strip(),
                           "phoneNumber": phoneNumber,
                           "address": address,
                           "gov": gov})
        except:
            continue
    return result


def formatAdresse(adr: str, trimeNumber=False):
    result = str(adr).replace("\n", "").replace("\t", "").replace("\r", "")
    trimIndex = 0
    for i in range(len(adr)):
        if not adr[i].isalpha() and (not adr[i].isdigit() or trimeNumber and adr[i].isdigit()):
            trimIndex += 1
        else:
            break
    result = result[trimIndex:]
    trimIndex = len(result)
    for i in range(len(adr)-1, -1, -1):
        if not adr[i].isalpha() and (not adr[i].isdigit() or trimeNumber and adr[i].isdigit()):
            trimIndex -= 1
        else:
            break
    result = result[:trimIndex]
    return result


def formatPhoneNumber(numbers: str):
    arr = numbers.split("-")
    for i in range(len(arr)):
        arr[i] = trimPhoneNumber(arr[i])
    return "/".join(arr)


def trimPhoneNumber(number):
    result = ""
    i = len(number)-1
    while i >= 0 and len(result) < 8:
        if number[i].isdigit():
            result = number[i]+result
        i -= 1
    return result


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


csvHeader = ["businessName", "typeBusiness", "ownerName", "phoneNumber",
             "address", "gov"]
csvPath = "scraped data/expat.com data .csv"


def scrapExpatLink(url):
    print("scrapping {}".format(url))
    pageNumbers = getNumberOFSearchLinks(url)
    data = []
    print("there is {} search page to get  data from ".format(pageNumbers))
    print("getting data..")
    for i in range(1, pageNumbers+1):
        data += getDataFromSearchLink(url+str(i))
        print("fetched data from page number {}".format(i))
    return data


if __name__ == "__main__":
    linksToScrap = getSearchLinks(
        "https://www.expat.com/en/business/africa/tunisia/9_engineering-construction/")
    scrapedData = []
    for link in linksToScrap:
        scrapedData += scrapExpatLink(link)
    print("writing data to CSV file")
    writeToCSV(csvPath, csvHeader, scrapedData)
