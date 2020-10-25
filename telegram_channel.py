#!/usr/bin/env python

import telegram_send

from spy import get_all_scoops, filter_trendy_scoops

if __name__ == '__main__':
    scoops = get_all_scoops()
    trendy_scoops = filter_trendy_scoops(scoops)
    if trendy_scoops:
        print(trendy_scoops)
    telegram_send.send(messages=trendy_scoops)
