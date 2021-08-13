
from bs4 import BeautifulSoup
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time


def fetchCharacterData(url):
    pageSource = requests.get(url).text
    soup = BeautifulSoup(pageSource, "lxml")
    mainContainer = soup.find("div", {"id": "content"}).find(
        "aside", {"role": "region"})
    characterName = mainContainer.find(
        "h2", {"data-source": "name"}).get_text()
    species = [spec["title"] for spec in mainContainer.find(
        "div", {"data-source": "type"}).find_all("a")] if mainContainer.find(
        "div", {"data-source": "type"}) else []
    gender = mainContainer.find("div", {"data-source": "gender"}).find("div").get_text(
    ) if mainContainer.find("div", {"data-source": "gender"}) else "UKNOWN"
    height = "".join(mainContainer.find(
        "div", {"data-source": "height"}).find("div").find_all(text=True, recursive=False)).strip() if mainContainer.find("div", {"data-source": "height"}) else "UKNOWN"
    weight = "".join(mainContainer.find(
        "div", {"data-source": "weight"}).find("div").find_all(text=True, recursive=False)).strip() if mainContainer.find("div", {"data-source": "weight"}) else "UKNOWN"
    origin = "".join(mainContainer.find(
        "div", {"data-source": "birthp"}).find("div").find_all(text=True, recursive=False)).strip() if mainContainer.find("div", {"data-source": "birthp"}) else "UKNOWN"
    likes = "".join(mainContainer.find(
        "div", {"data-source": "likes"}).find("div").find_all(text=True, recursive=False)).strip() if mainContainer.find("div", {"data-source": "likes"}) else "UKNOWN"
    dislikes = "".join(mainContainer.find(
        "div", {"data-source": "dislikes"}).find("div").find_all(text=True, recursive=False)).strip() if mainContainer.find("div", {"data-source": "dislikes"}) else "UKNOWN"
    age = "".join(mainContainer.find(
        "div", {"data-source": "age"}).find("div").find_all(text=True, recursive=False)).strip() if mainContainer.find("div", {"data-source": "age"}) else "UKNOWN"

    return {"name": characterName,
            "classes": [],
            "description": "",
            "imageURL": "",
            "series": ["Fate-Apocrypha"],
            "age": age,
            "species": species,
            "gender": gender,
            "height": height,
            "weight": weight,
            "origin": origin,
            "likes": likes,
            "dislikes": dislikes}


if __name__ == "__main__":
    while(True):
        with open("data.txt", mode="a", encoding='utf-8') as file:
            url = input("url:")
            if(url == "exit"):
                break
            json.dump(fetchCharacterData(
                url), file)
            file.write("\n")

    pass
