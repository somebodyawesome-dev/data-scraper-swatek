# lxml required
# beautifulsoup4 required
# requests required
# csv required

# chrome webdriver required
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import csv

site = "https://www.conseil-juridique.net/0/avocats-0-0-111-0-0-3_1.htm"

sitesToscrap = []


def formatPhoneNumber(number: str):
    result = ""
    i = len(number)-1
    while i >= 0 and len(result) < 8:
        if number[i].isdigit():
            result = number[i]+result
        i -= 1
    return result


def getLawyerLinks(link):
    global sitesToscrap
    result = []
    sitesToscrap.append(link)
    driver = webdriver.Chrome()
    driver.get(link)
    sitesToscrap += [ele.get_attribute('href') for ele in driver.find_element(
        By.XPATH, "/html/body/div[1]/div[4]/div[1]/div[5]/b").find_elements_by_xpath(".//*") if ele.get_attribute('href') != None]
    driver.quit()
    for s in sitesToscrap:
        result = result + getLawyerProfiles(s)

    return result


def getLawyerProfiles(link):
    pageSource = requests.get(link).text
    soup = BeautifulSoup(pageSource, "lxml")
    lawyerCards = soup.find_all("div", class_="profil_infos_content")
    return ["https://www.conseil-juridique.net/"+card.find("a")["href"] for card in lawyerCards]


def isValideNumber(number):
    return not(number[0] == "0" or number[0] == "1" or number[0] == "6" or number[0] == "8")


def getLawyerData(link):
    try:
        driver = webdriver.Chrome()
        driver.get(link)
        data = driver.find_element_by_xpath(
            "/html/body/div/div[4]/div[3]/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]").get_attribute('innerHTML').split("<br>")
        phoneNumber = formatPhoneNumber(data[3].strip()[6:])
        if len(data) >= 4 and "Tél" in data[3] and isValideNumber(phoneNumber):
            lawyerData = {"laywerName": data[0].strip(
            ), "laywerAdresse": data[1].strip(),
                "lawyerCodePostal": data[2].strip().split(" ")[0],
                "lawyerGov": data[2].strip().split(" ")[1],
                "lawyerTelephone": phoneNumber}
            driver.quit()
            return lawyerData
        else:
            driver.quit()
            return None

    except:
        return None


def writeToCSV(csvPath, csvHeader, data):
    try:
        with open(csvPath, 'w', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csvHeader)
            writer.writeheader()
            for d in data:
                writer.writerow(d)
    except IOError:
        print("I/O error")


csvHeader = ["laywerName", "lawyerGov",
             "lawyerCodePostal", "laywerAdresse", "lawyerTelephone"]
csvPath = "scraped data/conseil-juridique.net data.csv"

if __name__ == "__main__":
    print("loading..")
    print("getting lawyers links ...")
    lawyerLinks = getLawyerLinks(site)
    lawyersData = []
    print("scraping lawyers data ...")
    for lawyerLink in lawyerLinks:
        data = getLawyerData(lawyerLink)
        if data != None:
            lawyersData.append(data)
            print("scraped {}".format(lawyerLink))
    print("write scraped data to csv file")
    writeToCSV(csvPath, csvHeader, lawyersData)
    print("job is done ! ")
