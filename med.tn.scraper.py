

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


def isPhoneNumber(numb: str):
    return not(numb[0] == '3' or numb[0] == '7')


def getDoctorsLinksFromSearchLink(link):
    driver = webdriver.Chrome()
    # open search page that we want to scrapp data from
    driver.get(link)

    # load data until there's no more data
    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'btn-viewmore'))).click()
        except:
            break
    # get page source
    pageSource = driver.execute_script(
        "return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(pageSource, "lxml")
    doctorCards = soup.find_all(
        "div", class_="card-doctor-top")
    # close web driver
    driver.quit()
    return [doct.find("a")["href"] for doct in doctorCards]


def getDoctorsDataFromListOfLinks(links):
    doctData = []
    for link in links:
        aux = getDoctorDataFromLink(link)
        if not(len(aux["docNumbers"]) == 0 or aux in docData):
            doctData.append(aux)
        print("scraped {}".format(link))

    return doctData


def getDoctorDataFromLink(link):
    htmlText = requests.get(link).text
    soupLink = BeautifulSoup(htmlText, "lxml")
    return {"docName": soupLink.find("h1", class_="profile__label--name").get_text(
    )[1:], "docSpeciality": soupLink.find("div", class_="profile__label--spe").get_text(),
        "docGov": soupLink.find("div", class_="profile__label--adr").get_text(),
        "docAdr": soupLink.find("span", class_="profile__adr").get_text().strip(),
        "docNumbers": "/".join([trimPhoneNumber(numb["href"][8:]) for numb in soupLink.find_all("a", class_="calltel") if isPhoneNumber(numb["href"][8:])])}


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
        print("operation succed !!")
    except IOError:
        print("I/O error")


# globale variables
csvHeader = ['docName', "docSpeciality", "docGov", "docAdr", "docNumbers"]
csvPath = ["scraped data/med.tn data.csv",
           "scraped data/scraped data custom link.csv"]

docData = []

if __name__ == "__main__":
    # while True:
    #     print("1.fetch all data from med.tn")
    #     print("2.fetch data from search link")
    #     print("3.close app")
    #     choice = input("")
    #     if choice == "1":

    print("loading..it might take a while dont lose faith")
    docData += getDoctorsDataFromListOfLinks(
        getDoctorsLinksFromSearchLink("https://www.med.tn/medecin"))
    print("writing data to CSV file")
    writeToCSV(csvPath[0], csvHeader, docData)
    # elif choice == "2":
    #     # scrap specifique link
    #     linkToScrap = input("enter search link :")
    #     print("loading..")
    #     writeToCSV(csvPath[1], csvHeader, getDoctorsDataFromListOfLinks(
    #         getDoctorsLinksFromSearchLink(linkToScrap)))
    # elif choice == "3":
    #     # close app
    #     break
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
