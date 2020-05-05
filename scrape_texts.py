#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# For any queries, reporting bugs, feel free to approach the developer, Chaitanya S Lakkundi [firstname].[lastname] @ gmail.com

import requests
from bs4 import BeautifulSoup

"""

Patterns to look for

https://www.sankara.iitk.ac.in/ganesha-devotional-hyms?language=dv&field_text_tid=30
https://www.sankara.iitk.ac.in/devi-devotional-hyms?language=dv&field_text_tid=35
https://www.sankara.iitk.ac.in/vishnu-devotional-hyms?language=dv&field_text_tid=49
https://www.sankara.iitk.ac.in/shiva-devotional-hyms?language=dv&field_text_tid=67
https://www.sankara.iitk.ac.in/subramanya-devotional-hyms?language=dv&field_text_tid=70
https://www.sankara.iitk.ac.in/miscellaneous-devotional-hymns?language=dv&field_text_tid=7

class views-field-body to get shlokas
id edit-field-text-tid to select dropdown of texts

https://www.sankara.iitk.ac.in/preliminary-texts?language=dv&field_text1_tid=71
id edit-field-text1-tid

https://www.sankara.iitk.ac.in/comprehensive-texts?language=dv&field_text2_tid=104
id edit-field-text2-tid

"""

devotional_links = [
    "https://www.sankara.iitk.ac.in/ganesha-devotional-hyms",
    "https://www.sankara.iitk.ac.in/devi-devotional-hyms",
    "https://www.sankara.iitk.ac.in/vishnu-devotional-hyms",
    "https://www.sankara.iitk.ac.in/shiva-devotional-hyms",
    "https://www.sankara.iitk.ac.in/subramanya-devotional-hyms",
    "https://www.sankara.iitk.ac.in/miscellaneous-devotional-hymns"
]

preliminary_links = ["https://www.sankara.iitk.ac.in/preliminary-texts"]
comprehensive_links = ["https://www.sankara.iitk.ac.in/comprehensive-texts"]

s = requests.Session()


def check_shloka_body(body):
    # Generally the first shloka contains intro details such as title and the like along with the actual shloka.
    # The last shloka also often contains additional details after shloka.
    # Need to strip them off. Either manually or automatically.
    pass


def scrape_shlokas(link):
    corpus = {}
    data = s.get(link).text
    soup = BeautifulSoup(data, "html.parser")
    options = soup.select("#edit-field-text-tid")[0].find_all("option")

    for option in options:
        if option.get("selected","") == "selected":
            corpus["name"] = option.text
            break

    body = [b.text.strip() for b in soup.select(".views-field-body")]
    corpus["body"] = body

    return corpus


def scrape(link, selector_id):
    data = s.get(link).text
    soup = BeautifulSoup(data, "html.parser")
    selector_name = soup.select("#edit-field-text-tid")[0].get("name")
    options = soup.select("#edit-field-text-tid")[0].find_all("option")
    sub_links = []

    for option in options:
        sub_links.append(link + "?language=dv&" + selector_name + "=" + option.get("value"))

    # Even though the first page is fetched once again in the following loop, it is intentionally done so to separate functionalities.

    corpora = []

    for sl in sub_links:
        corpus = scrape_shlokas(sl)
        corpora.append(corpus)


def get_chandas(shloka):
    # Given a shloka input, return the meter or chandas obtained from shreevatsa sanskrit meters and ksu-shloka-architect.
    
    # https://sanskritmetres.appspot.com/
    
    # Within a text, if only one or two different chandas are found, then notify for manual verification
    pass


def calculate_statistics():
    # After chandas for all shlokas has been obtained, get the frequency of chandas.
    # What percentage of texts (in number of texts or lines?) are in poetry form?
    # Frequency of letters used. Swara frequency and vyanjana frequency.
    # Morph analysis can be done only after sandhi split.
    pass


def main():
    for link in devotional_links:
        scrape(link, "field_text_tid")

    for link in preliminary_links:
        scrape(link, "field_text1_tid")

    for link in comprehensive_links:
        scrape(link, "field_text2_tid")

    calculate_statistics()


if __name__ == "__main__":
    main()