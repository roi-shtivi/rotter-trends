#!/usr/bin/env python

import logging
import re

import telegram_send

from spy import get_all_scoops, filter_trendy_scoops

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filename='telegram_channel.log',
                        level=logging.INFO)

    scoops = get_all_scoops()
    trendy_scoops = filter_trendy_scoops(scoops)
    if trendy_scoops:
        logging.info(trendy_scoops)

    messages = []
    for link, score in trendy_scoops.items():
        scoop_id = re.search(r'om=(\d+)', link).group(1)
        messages.append(f"[link]({link}), (rating: {score:.2f})")

    telegram_send.send(messages=messages, parse_mode="markdown")
