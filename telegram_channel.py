#!/usr/bin/env python

import logging

import telegram_send

from spy import get_all_scoops, filter_trendy_scoops

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='telegram_channel.log',
                    level=logging.DEBUG)


if __name__ == '__main__':
    scoops = get_all_scoops()
    trendy_scoops = filter_trendy_scoops(scoops)
    if trendy_scoops:
        logging.info(trendy_scoops)
    telegram_send.send(messages=trendy_scoops)
