# lxml required
# beautifulsoup4 required
# requests required
# csv required

# chrome webdriver required
from bs4 import BeautifulSoup
import requests
import csv

site = "http://www.info-maman.com/fr/filtre/annuaire-des-etablissements/tous/tous/tous/q/"
csvHeader = ["establishmentName", "establishmentGov", "establishmentVille",
             "establishmentType", "establishmentAddresse", "establishmentNumber"]
csvPath = "scraped data/info-maman.com data.csv"


def getNumberOFSearchLinks(entry):
    pageSource = requests.get(entry).text
    soup = BeautifulSoup(pageSource, "lxml")
    return(int(soup.find("a", {"title": "Fin"})["href"].replace(
        "http://www.info-maman.com/fr/filtre/annuaire-des-etablissements/tous/tous/tous/q/", "")))


def getEstablishmentLinks(url):
    pageSource = requests.get(url).text
    soup = BeautifulSoup(pageSource, "lxml")
    return [box.find("div", {"class": "name name1"}).find("a")["href"] for box in soup.find_all("div", {"class": "box-product-item"})]


def getEstablishmentData(url):
    try:
        pageSource = requests.get(url).text
        soup = BeautifulSoup(pageSource, "lxml")
        establishmentName = soup.find(
            "div", {"class": "cats_manzah"}).find("h1").get_text()
        establishmentLocation = soup.find(
            "div", {"class": "menzah5"}).get_text().split("-")
        establishmentGov = establishmentLocation[0].strip()
        establishmentVille = establishmentLocation[1].strip()
        establishmentType = url.split("/")[-2].replace("-", " ")

        establishmentDesc = [p.get_text() for p in soup.find(
            "div", {"class": "cat_contenu"}).find_all("p")]
        establishmentAddresse = establishmentDesc[0].replace(
            " Adresse : ", "") if len(establishmentDesc) >= 1 else "None"
        establishmentNumber = formatPhoneNumber(
            establishmentDesc[1]) if len(establishmentDesc) >= 2 else "None"
        return {"establishmentName": establishmentName,
                "establishmentGov": establishmentGov,
                "establishmentVille": establishmentVille,
                "establishmentType": establishmentType,
                "establishmentAddresse": establishmentAddresse,
                "establishmentNumber": establishmentNumber}
    except:
        print("some error occured !")
        return None


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


if __name__ == "__main__":
    print("loading ...")
    pagesNumber = getNumberOFSearchLinks(site)

    establishmentLinks = []
    print("there is {} search page to get establishments links from ".format(pagesNumber))
    print("getting establishments links ..")
    for i in range(1, pagesNumber+1):
        establishmentLinks += getEstablishmentLinks(site+str(i))
        print("fetched link from page number {}".format(i))
    print("scraping data from links")
    establishmentsData = []
    for link in establishmentLinks:
        data = getEstablishmentData(link)
        if(data != None):
            establishmentsData.append(data)
            print("scraped : {}".format(link))
    print("writing data to CSV file")
    writeToCSV(csvPath, csvHeader, establishmentsData)
    print("job is done")
