#!/usr/bin/env python3

from contextlib import closing
from requests import get
from datetime import datetime


from requests.exceptions import RequestException
from bs4 import BeautifulSoup

ROOTER_SCOOPS_URL = 'https://rotter.net/scoopscache.html'


def _verify_response(resp):
    """
    Returns true if the response seems to be HTML, false otherwise
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def _simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if _verify_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def _get_scoop_creation_time(scoop):
    creator_tag = scoop.find_all(size='1')[0]
    raw_time = creator_tag.text.split('\n')[0]
    time = datetime.strptime(raw_time, '%d.%m.%y %H:%M')
    return time


def _get_scoop_view_count(scoop):
    try:
        views = scoop.find_all(size='-1')[0].text
        return int(views)
    except ValueError:
        return 0


def _get_scoop_link(scoop):
    a = scoop.find_all(width='55%')[0].find_all('a')[0]
    return a.get('href')


def _is_scoop_known(scoop):
    return False


def _is_trendy(scoop):
    scoop_creation_time = _get_scoop_creation_time(scoop)
    scoop_age = (datetime.now() - scoop_creation_time).seconds
    scoop_views = _get_scoop_view_count(scoop)
    ratio = scoop_views / scoop_age
    if ratio > 3:
        print(ratio)
    return ratio > 5


def get_all_scoops():
    """
    Get all Rooter's first page scoops (excl. pinned scoops).
    :return: ResultSet of all the matching bs4 Tag(s).
    """

    def _is_valid_scoop(tag):
        """
        Given a bs4 tag, check whether a bs4 tag is a valid scoop tag.
        :param tag: bs4 tag
        :return: True if the bs4 tag is in accordance to a valid Rooter's scoop, False otherwise.
        """
        valid_bgcolors = ['#FDFDFD', '#eeeeee']

        # Check if the tag has a matching background color to a scoop tag, and exclude ad scoops
        if tag.has_attr('bgcolor'):
            return tag['bgcolor'] in valid_bgcolors \
                   and 'googletag' not in tag.text \
                   and tag.text != '\n\n'
        else:
            return False

    raw_html = _simple_get(ROOTER_SCOOPS_URL)

    if raw_html is None:
        print('Could not get url')
        return None

    soup = BeautifulSoup(raw_html, 'html.parser')
    scoops = soup.find_all(_is_valid_scoop)
    return scoops


def filter_trendy_scoops(scoops):
    trendy_scoops = []
    for scoop in scoops:
        try:
            if _is_trendy(scoop):
                trendy_scoops.append(_get_scoop_link(scoop))
        except Exception as e:
            try:
                print(e)
                print(f"Couldn't parse this scoop: {scoop.text}")
                print(f"view: {_get_scoop_view_count(scoop)}")
                print(f"creation: {_get_scoop_creation_time()}")
            except:
                pass
    return trendy_scoops


if __name__ == '__main__':
    scoops = get_all_scoops()
    print(filter_trendy_scoops(scoops))
