import csv

from bs4 import BeautifulSoup as bs
import requests

URL = "https://www.caring.com"


def get_state_links():
    """obtains all states from domain"""
    soup = webscrape_request("https://www.caring.com")
    state_links = [a['href'] for a in soup.find(id="top-states").findAll("a")]
    return state_links


def get_city_links(link):
    """ obtains all city links from state page"""
    soup = webscrape_request(f"https://www.caring.com{link}")
    links = []
    for city in soup.find(id="cities").findAll(class_="lrtr-list-item"):
        links.append(
            city.find("a", href=True)['href'])
    return links


def webscrape_request(url=URL):
    """opening up connection, grabbing page"""
    response = requests.get(url)
    html = response.content
    soup = bs(html, "html.parser")
    return soup


def webscrape_addresses(soup):
    names, keywords, addresses = [], [], []

    for name in soup.findAll('h3'):
        # filter out non caring.com links
        if not name.find("a"):
            continue
        names.append(name.getText().strip())

    for keyword in soup.findAll(class_='provides'):
        keywords.append(keyword.getText().strip())

    for address in soup.findAll(class_='address'):
        addresses.append(address.getText().strip())

    return names, keywords, addresses


def export_csv(names, keywords, addresses):
    """writes all scrapped information into a csv"""
    with open("facility_info.csv", "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        for name, keyword, address in zip(names, keywords, addresses):
            writer.writerow([name, keyword, address])


if __name__ == "__main__":
    names, keywords, addresses = [], [], []

    state_links = get_state_links()
    for link in state_links:
        links = get_city_links(link)
        for link in links:
            print("processing link", link)
            soup = webscrape_request(link)
            city_names, city_keywords, city_addresses = (
                webscrape_addresses(soup))

            try:
                assert (
                    len(city_names) == len(city_keywords)
                    == len(city_addresses)
                )
                #print(f"found {len(city_names)} city names")
            except AssertionError:
                # TODO: see why and add workaround to code
                print("ERROR processing", link)
            else:
                names.extend(city_names)
                keywords.extend(city_keywords)
                addresses.extend(city_addresses)

    export_csv(names, keywords, addresses)
