

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


site = "https://www.expat.com/fr/entreprises/afrique/tunisie/8_services-juridiques/avocats/"


def getNumberOFSearchLinks(entry):
    try:
        pageSource = requests.get(entry).text
        soup = BeautifulSoup(pageSource, "lxml")
        li = soup.find("ul", {"class": "cd-pagination"}).find_all("li")
        return int(li[-1].find("a")["href"].split("/")[-2])
    except:
        return 1


def getLawyersDataFromSearchLink(url):
    result = []
    pageSource = requests.get(url).text
    soup = BeautifulSoup(pageSource, "lxml")
    LawyersCards = soup.find_all(
        "li", {"itemtype": "https://schema.org/LocalBusiness"})
    for card in LawyersCards:
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

        result.append({"cabinetName": cabinetName,
                       "lawyerName": ownerName.strip(),
                       "phoneNumber": phoneNumber,
                       "address": address,
                       "gov": gov})
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
        with open(csvPath, 'w', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csvHeader)
            writer.writeheader()
            for d in data:

                writer.writerow(d)
    except IOError:
        print("I/O error")


csvHeader = ["cabinetName", "lawyerName", "phoneNumber",
             "address", "gov"]
csvPath = "scraped data/expat.com data.csv"


if __name__ == "__main__":
    pageNumbers = getNumberOFSearchLinks(site)
    lawyersData = []
    print("there is {} search page to get lawyers data from ".format(pageNumbers))
    print("getting lawyers data..")
    for i in range(1, pageNumbers+1):
        lawyersData += getLawyersDataFromSearchLink(site+str(i))
        print("fetched data from page number {}".format(i))
    print("writing data to CSV file")
    writeToCSV(csvPath, csvHeader, lawyersData)
    print("job is done")
