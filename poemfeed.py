"""
The idea, is for me to crawl the poetry foundation’s, poem of the day page at
https://www.poetryfoundation.org/poems/poem-of-the-day and put it into an rss
file, so that i can read it in my RSS reader
"""

from datetime import date, datetime, timedelta

import httpx
import json
import pytz
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator


def main():
    """
    Takes the Poetry foundation daily poem link,
    gets an updated link if a new poem is posted
    and then creates an rss feed file.
    """
    poempage = "https://www.poetryfoundation.org/poems/poem-of-the-day"
    reply = get_page_from_pf(poempage)
    if reply:
        create_rss_feed(reply)


def get_page_from_pf(link):
    """
    Parses the PF daily poem link page.
    If it is updated,
    then it goes and fetches the link to the actual poem page and returns it

    :param link: url
    :type link: string
    :return: url
    :rtype: string
    """
    # Passing Mozilla as the useragent,
    # because Cloudflare sometimes blocks the script.
    # Remember to update this every once in a while

    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0'}
    rawhtml = httpx.get(link, headers=headers)
    soup = BeautifulSoup(rawhtml.text, "html.parser")

    # Get the full poem at its url
    look_full_poem_url = soup.find_all("a", string="Read More")
    get_first_element_from_poem_url = look_full_poem_url[0]
    full_poem_url = get_first_element_from_poem_url.attrs["href"]
    full_poem_url = "https://www.poetryfoundation.org" + full_poem_url

    # Get date from the poem-a-day page to see if the poem is new
    ## Old way
    # date_of_poem_str = soup.find("meta", {"name": "dcterms.Date"}).get(
    #     "content")
    # date_of_poem = datetime.strptime(date_of_poem_str, "%Y-%m-%d")

    ## New woy since the site’s moved to some new fangled js framework
    some_raw_blob = soup.find_all(id="__NUXT_DATA__")[0].text
    json_blob = json.loads(some_raw_blob)
    date_of_poem_str = json_blob[616]
    # How did I find that it was 616? by looking like this for date
    # `[i for i,x in enumerate(json_cleaned_up) if x == '2024-09-21T00:00:00-05:00']`
    date_of_poem = datetime.fromisoformat(date_of_poem_str)

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
    Takes the link that we fetched
    and then writes it to an xml file for a feed reader to fetch

    :param poemlink: url
    :type poemlink: string
    """

    # Create a feedgen feed instance and populate it with my details
    poemfeed = FeedGenerator()
    poemfeed.title("Jason's PF feed")
    poemfeed.link(href=poemlink)
    poemfeed.description("Poem of the day")
    poemfeed.lastBuildDate(datetime.now(pytz.timezone('Asia/Kolkata')))

    # Create an rss entry with the url we scraped and parsed
    pf_current_entry = poemfeed.add_entry()
    pf_current_entry.title(f"Poem for {date.today()}")
    pf_current_entry.link(href=poemlink)
    pf_current_entry.guid(f"Poem for {date.today()}")
    pf_current_entry.pubDate(datetime.now(pytz.timezone('Asia/Kolkata')))

    # Write the feed
    poemfeed.rss_file('poem.xml')


#   create and write_to_rss_feed
if __name__ == "__main__":
    main()
