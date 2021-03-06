#!/usr/bin/env python

import requests
import json
from datetime import datetime, timedelta
from keen.client import KeenClient
from config import spire, keen

DAYS_AGO = 2
USER = 'tyin'

def main():
    print '[INFO] Getting raw spire data...'
    date = (datetime.today()-timedelta(days=DAYS_AGO)).strftime('%Y-%m-%d')

    # Breath
    breath_client = KeenClient(
        project_id = keen['breath']['project_id'],
        read_key = keen['breath']['read_key'],
        write_key = keen['breath']['write_key']
    )

    if len(breath_client.extraction('sessions', timeframe='this_' + str(DAYS_AGO) + '_days')) > 0:
        print '[INFO] Already uploaded breath data for ' + date + '.'
    else:
        breaths = get_spire(spire['breath'], date)
        
        if len(breaths['data']) > 0:
            print '[INFO] Uploading breath data...'

            keen_breaths = {}
            keen_breaths['breaths'] = [{'timestamp': b['timestamp'], 'value':b['value']} for b in breaths['data']]
            keen_breaths['metadata'] = breaths['metadata']

            keen_breaths['metadata']['min'] = min([b['value'] for b in breaths['data']])
            keen_breaths['metadata']['max'] = max([b['value'] for b in breaths['data']])
            keen_breaths['id'] = USER + date
            breath_client.add_event('sessions', keen_breaths)
            print '[INFO] Uploaded breath data for ' + date + '.'
        else:
            print '[INFO] No breath data found for ' + date + '.'
    
    # Steps
    steps_client = KeenClient(
        project_id = keen['steps']['project_id'],
        read_key = keen['steps']['read_key'],
        write_key = keen['steps']['write_key']
    )

    if len(steps_client.extraction('sessions', timeframe='this_' + str(DAYS_AGO) + '_days')) > 0:
        print '[INFO] Already uploaded steps data for ' + date + '.'
    else:
        steps = get_spire(spire['step'], date)

        if len(steps['data']) > 0:
            print '[INFO] Uploading steps data...'
            
            keen_steps = {}
            keen_steps['steps'] = [{'timestamp': s['timestamp'], 'value':s['value']} for s in steps['data']]
            keen_steps['metadata'] = steps['metadata']
            keen_steps['id'] = USER + date
            steps_client.add_event('sessions', keen_steps)
            print '[INFO] Uploaded steps data for ' + date + '.'
        else:
            print '[INFO] No steps data found for ' + date + '.'    

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
