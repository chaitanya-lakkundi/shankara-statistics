#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# For any queries, reporting bugs, feel free to approach the developer, Chaitanya S Lakkundi [firstname].[lastname] @ gmail.com

import requests
from bs4 import BeautifulSoup
from os import makedirs
import json
import re
from glob import glob

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

import sys
sys.path.append("vendor/shreevatsa_sanskrit_meters/")

from vendor.shreevatsa_sanskrit_meters.identifier_pipeline import *

identifier = IdentifierPipeline()

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


def sanitize_shloka_body(body):
    # Generally the first shloka contains intro details such as title and the like along with the actual shloka.
    # The last shloka also often contains additional details after shloka.
    # Need to delete them. Either manually or automatically.
    pass


def scrape_shlokas(link, selector_id):
    corpus = {}
    data = s.get(link)
    soup = BeautifulSoup(data.text, "html.parser")
    options = soup.select("#" + selector_id)[0].find_all("option")

    for option in options:
        if option.get("selected","") == "selected":
            corpus["name"] = option.text.strip()
            # WX encoding format does not have any characters which may conflict with file path. The charset is A-z thereby making it safe to use for a filename.
            # Problems in other encoding schemes.
            # SLP1 = Anunasika is represented by a tilde.
            # ITRANS = ~Na for ङ
            # HK = Harvard-Kyoto does not distinguish अइ (a followed by i, in separate syllables from ऐ.
            corpus["filename"] = transliterate(corpus["name"], sanscript.DEVANAGARI, sanscript.WX)
            break

    body = []

    for b in soup.select(".views-field-body p font"):
        btext = []
        
        for bc in b.contents:
            if isinstance(bc, str):
                btext.append(bc)
            else:
                btext.append("\n")

        body.append("".join(btext))

    corpus["url"] = link
    corpus["body"] = body

    return corpus


def scrape(link, selector_id, folder_name):
    
    print("scrape ", link)

    data = s.get(link).text
    soup = BeautifulSoup(data, "html.parser")
    selector_name = soup.select("#" + selector_id)[0].get("name")
    options = soup.select("#" + selector_id)[0].find_all("option")
    sub_links = []

    for option in options:
        sub_links.append(link + "?language=dv&" + selector_name + "=" + option.get("value"))

    # Even though the first page is fetched once again in the following loop, it is intentionally done so to separate functionalities.

    for sl in sub_links:
        corpus = scrape_shlokas(sl, selector_id)

        makedirs("corpus/" + folder_name, exist_ok=True)
        with open("corpus/" + folder_name + "/" + corpus["filename"] + ".json", "w") as fd:
            json.dump(corpus, fd, ensure_ascii=False, indent=2)


def get_chandas(shloka):
    # Given a shloka input, return the meter or chandas obtained from shreevatsa sanskrit meters and ksu-shloka-architect.
    
    # https://sanskritmetres.appspot.com/
    
    # Within a text, if only one or two different chandas are found, then notify for manual verification

    # For first shloka in a text and last shloka in a text, special handling. If chandas not found, ie. status == False, then for first shloka, strip first line and again check for chandas .. go on. For last shloka, strip last line and again check .. go on.

    # Another preliminary check could be if split components by newline is more than 4

    # Observation: In last shloka, additional shloka ending details are separated by 3 newlines in the corpus.
    if "\n\n\n" in shloka:
        shloka = shloka.split("\n\n\n")[0]

    shloka = re.split(r"[\n]+", shloka)

    if len(shloka) > 8:
        print("\nComponents more than 8. = ", len(shloka))
        print("\n".join(shloka))

    found = False
    chandas = ""

    # assuming shlokas are at least of two lines
    while not found and len(shloka) >= 2:
        match_results = identifier.IdentifyFromText("\n".join(shloka))

        try:
            found = match_results[0]
            chandas = match_results[1][0]
        except:
            chandas = ""
        # delete lines starting from top
        shloka = shloka[1:]

    return chandas


def calculate_statistics():
    # After chandas for all shlokas has been obtained, get the frequency of chandas.
    # What percentage of texts (in number of texts or lines?) are in poetry form?
    # Frequency of letters used. Swara frequency and vyanjana frequency.
    # Morph analysis can be done only after sandhi split.

    corpus_filenames = glob("corpus/**/*.json")
    
    for cfilename in corpus_filenames:

        print(cfilename)

        with open(cfilename) as fd:
            corpus = json.load(fd)

        chandas_list = []
        
        for shloka in corpus["body"]:
            chandas = get_chandas(shloka)
            chandas_list.append(chandas)

        corpus["chandas_list"] = chandas_list

        with open(cfilename, "w") as fd:
            json.dump(corpus, fd, ensure_ascii=False, indent=2)


def main():

    # for link in devotional_links:
    #     scrape(link, "edit-field-text-tid", link.split("/")[-1])

    # for link in preliminary_links:
    #     scrape(link, "edit-field-text1-tid", link.split("/")[-1])

    # for link in comprehensive_links:
    #     scrape(link, "edit-field-text2-tid", link.split("/")[-1])

    calculate_statistics()


if __name__ == "__main__":
    main()