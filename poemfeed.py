"""
The idea, is for me to crawl the poetry foundation’s, poem of the day page at
https://www.poetryfoundation.org/poems/poem-of-the-day and put it into an rss
file, so that i can read it in my RSS reader
"""

from datetime import date, datetime, timedelta

import requests
from bs4 import BeautifulSoup
import PyRSS2Gen


def main():
    """
    Takes the Poetry foundation daily poem link, gets an updated link if a new poem is posted and then creates an rss feed file.
    """
    poempage = "https://www.poetryfoundation.org/poems/poem-of-the-day"
    reply = get_page_from_pf(poempage)
    if reply:
        create_rss_feed(reply)


def get_page_from_pf(link):
    """
    Parses the PF daily poem link page. If it is updated, then it goes and fetches the link to the actual poem page and returns it

    :param link: url
    :type link: string
    :return: url
    :rtype: string
    """
    rawhtml = requests.get(link)
    soup = BeautifulSoup(rawhtml.text, "html.parser")

    look_full_poem_url = soup.find_all("a", string="Read More")
    get_first_element_from_poem_url = look_full_poem_url[0]
    full_poem_url = get_first_element_from_poem_url.attrs["href"]

    date_of_poem_str = soup.find("meta", {"name": "dcterms.Date"}).get("content")
    date_of_poem = datetime.strptime(date_of_poem_str, "%Y-%m-%d")
    date_of_poem = date_of_poem.date()
    today_date = date.today()

    if date_of_poem == today_date:
        return full_poem_url
    elif date_of_poem == today_date - timedelta(days=1):
        return full_poem_url
    else:
        return None


def create_rss_feed(poemlink):
    """
    Takes the link that we fetched and then writes it to an xml file for a feed reader to fetch

    :param poemlink: url
    :type poemlink: string
    """
    rss = PyRSS2Gen.RSS2(
        title="Jason's PF feed",
        link=poemlink,
        description="Poem of the day",
        lastBuildDate=datetime.now(),
        items=[
            PyRSS2Gen.RSSItem(
                title=f"Poem for {date.today()}",
                link=poemlink,
                guid=PyRSS2Gen.Guid(f"Poem for {date.today()}"),
                pubDate=datetime.now(),
            ),
        ],
    )

    rss.write_xml(open("poem.xml", "w"))


#   create and write_to_rss_feed
if __name__ == "__main__":
    main()
