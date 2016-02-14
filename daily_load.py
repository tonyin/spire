#!/usr/bin/env python

import requests
import json
from datetime import datetime, timedelta
from keen.client import KeenClient
from config import spire, keen

DAYS_AGO = 2

def main():
    print '[INFO] Getting raw spire data...'
    date = (datetime.today()-timedelta(days=DAYS_AGO)).strftime('%Y-%m-%d')
    breaths = get_spire(spire['breath'], date)
    print '[INFO] Uploading raw spire data...'
    client = KeenClient(
        project_id = keen['project_id'],
        read_key = keen['read_key'],
        write_key = keen['write_key']
    )
    data = {}
    data['breaths'] = [{'timestamp': b['timestamp'], 'value':b['value']} for b in breaths['data']]
    data['metadata'] = breaths['metadata']
    data['metadata']['min'] = min([b['value'] for b in breaths['data']])
    data['metadata']['max'] = max([b['value'] for b in breaths['data']])
    client.add_event('sessions': data)
    print '[INFO] Uploaded raw spire data for ' + str(timestamp)

def get_spire(what, date):
    url = spire['url'] + what + date
    token = spire['token']
    headers = {'Authorization': 'Bearer ' + token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = None
    try:
        data = response.json()
    except ValueError as e:
        print '[ERROR] ' + e
    return data

if __name__ == '__main__':
    main()
