#!/usr/bin/env python

import re
from datetime import datetime
import logging

from contextlib import closing
from requests import get

from requests.exceptions import RequestException
from bs4 import BeautifulSoup

ROOTER_SCOOPS_URL = 'https://rotter.net/scoopscache.html'
INTEREST_THRESHOLD = 10


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
        logging.error('Error during requests to {0} : {1}'.format(url, str(e)))
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


def _is_scoop_known(link):
    try:
        with open(".known_scoops.txt", 'r') as file:
            known = link in file.read()
            file.close()
            return known
    except FileNotFoundError:
        open(".known_scoops.txt", 'w+')


def _acknowledge_scoop(link):
    with open(".known_scoops.txt", 'a+') as file:
        file.write(f"{link}\n")
        file.close()


def _how_trendy(scoop):
    scoop_creation_time = _get_scoop_creation_time(scoop)
    scoop_age = int((datetime.now() - scoop_creation_time).total_seconds())
    assert scoop_age, f"scoop age is {scoop_age}, cannot calculate how trendy it is."

    scoop_views = _get_scoop_view_count(scoop)

    ratio = scoop_views / scoop_age
    if ratio > INTEREST_THRESHOLD:
        return ratio
    return 0


def _is_valid_scoop(tag):
    """
    Given a bs4 tag, check whether a bs4 tag is a valid scoop tag.
    :param tag: bs4 tag
    :return: True if the bs4 tag is in accordance to a valid Rooter's scoop, False otherwise.
    """
    valid_bgcolors = ['#FDFDFD', '#eeeeee']
    # Check if the tag has a matching background color to a scoop tag, and exclude ad scoops
    if tag.has_attr('bgcolor'):
        return (tag['bgcolor'] in valid_bgcolors) and ('googletag' not in tag.text) and (not bool(re.fullmatch(r"\n+", tag.text)))
    else:
        pass


def get_all_scoops():
    """
    Get all Rooter's first page scoops (excl. pinned scoops).
    :return: ResultSet of all the matching bs4 Tag(s).
    """

    raw_html = _simple_get(ROOTER_SCOOPS_URL)

    if raw_html is None:
        logging.error('Could not get url')
        return None

    soup = BeautifulSoup(raw_html, 'html.parser')
    scoops = soup.find_all(_is_valid_scoop)
    return scoops


def filter_trendy_scoops(scoops):
    trendy_scoops = []
    for scoop in scoops:
        try:
            if not _is_scoop_known(_get_scoop_link(scoop)):
                score = _how_trendy(scoop)
                if score:
                    _acknowledge_scoop(_get_scoop_link(scoop))
                    trendy_scoops.append(f"Found this scoop to be interesting with score of: {score:.2f}\n"
                                         f"{_get_scoop_link(scoop)}")
        except Exception as e:
            try:
                logging.error(_is_valid_scoop(scoop))
                logging.error(e)
                logging.error(f"Could'nt parse this scoop: {scoop.text}")
                logging.error(f"View: {_get_scoop_view_count(scoop)}")
                logging.error(f"Creation: {_get_scoop_creation_time()}")
            except:
                pass
    return trendy_scoops


if __name__ == '__main__':
    scoops = get_all_scoops()
    logging.info(filter_trendy_scoops(scoops))
