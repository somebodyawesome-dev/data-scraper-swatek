
# lxml required
# beautifulsoup4 required
# requests required
# csv required

# chrome webdriver required
from bs4 import BeautifulSoup
import requests
import csv

pageNumbers = 0

site = "https://www.ecoles.com.tn/etablissements?titreville=&ville=All&nature=All"

csvHeader = ["schoolName", "schoolType", "schoolGov",
             "schoolAdresse", "schoolPhoneNumber", "schoolEmail"]
csvPath = "scraped data/ecole.com.tn data.csv"

gov = []


def initGov(url):
    global gov
    pageSource = requests.get(url).text
    soup = BeautifulSoup(pageSource, "lxml")
    govsHolder = [g.get_text() for g in soup.find(
        "select", {"id": "edit-ville"}).find_all("option")][1:]
    i = -1
    for g in govsHolder:
        if not g[0] == "-":
            gov.append([])
            i += 1
            gov[i].append(g)
        else:
            gov[i].append(g[1:])


def getNumberOfSitesToScrap(url):
    pageSource = requests.get(url).text
    soup = BeautifulSoup(pageSource, "lxml")
    return int(soup.find("li", class_="pager__item pager__item--last").find("a")["href"].replace("?titreville=&ville=All&nature=All&page=", ""))


def getSchoolsData(pageNumber: int):
    global site
    result = []
    pageSource = requests.get(site+"&page="+str(pageNumber)).text
    soup = BeautifulSoup(pageSource, "lxml")
    schoolsCards = soup.find_all("div", class_="imagebox")
    for card in schoolsCards:
        data = fetchDataFromCard(card)
        result.append(data)
    return result


def fetchDataFromCard(card):
    schoolName = card.find(
        "div", class_="title-content").find("a").get_text().strip()
    schoolType = "/".join([typ.get_text()
                           for typ in card.find("ul", class_="rating").find_all("span")])
    boxDescription = card.find("div", class_="box-desc").find_all("li")

    schoolAdresse = boxDescription[0].get_text(
    ).strip()+" ,"+card.find("li", class_="address").find("a").get_text()

    schoolGov = getVileFromtitreVille(
        card.find("li", class_="address").find("a").get_text())

    schoolPhoneNumber = formatPhoneNumber(
        boxDescription[1].get_text()) if len(boxDescription) >= 2 else "None"
    schoolEmail = boxDescription[2].get_text() if len(
        boxDescription) >= 3 else "None"

    return {"schoolName": schoolName, "schoolType": schoolType, "schoolGov": schoolGov, "schoolAdresse": schoolAdresse, "schoolPhoneNumber": schoolPhoneNumber, "schoolEmail": schoolEmail}


def formatPhoneNumber(numbers: str):
    arr = numbers.split("/")
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


def getVileFromtitreVille(titre):
    global gov
    for g in gov:
        if titre in g:
            return g[0]
    return titre


if __name__ == "__main__":
    pageNumbers = getNumberOfSitesToScrap(site)
    print("there is {} pages to scrap".format(pageNumbers))
    initGov(site)
    print("initialisation govs")
    schoolsData = []
    print("scraping data..")
    for i in range(1, pageNumbers+1):
        schoolsData += getSchoolsData(i)
        print("scraped {} ".format(i))
    print("writing results to CSV file")
    writeToCSV(csvPath, csvHeader, schoolsData)
    print("job is done!")
