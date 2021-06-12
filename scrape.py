import requests
import json
import time

starttime = time.time()
lasttime = starttime

period = 111  # Bundestag 2017 -- 2021

aw_domain = 'a-watch.dont-break.it'

api_base_url = 'https://www.abgeordnetenwatch.de/api/v2'
api_base_url = 'https://a-watch.dont-break.it/api/v2'

r = requests.get(
    api_base_url +
    f'/polls?field_legislature[entity.id]={period}&pager_limit=100&page=0'
)

response = r.json()
data = response['data']

polls = {}
politicians = {}
partys = {}

known_mandates = {}

for p in data:
    poll_id = p['id']

    poll = {
        'aw_id': poll_id,
        'poll': p['label'],
        'abstract': p['field_intro'],
        'date': p['field_poll_date'],
        'votes': {}
    }

    rv = requests.get(
        f'{api_base_url}/polls/{p["id"]}',
        {'related_data': 'votes'}
    )


    data = rv.json()['data']


    for vote in data['related_data']['votes']:
        mandate_id = int(vote['mandate']['id'])

        if mandate_id in known_mandates:
            pid = known_mandates[mandate_id]
        else:
            api_url = vote['mandate']['api_url'].replace('www.abgeordnetenwatch.de', aw_domain)
            pr  = requests.get(
                api_url,
                'related_data=politician'
            )
            pdata = pr.json()['data']
            predata = pdata['related_data']['politician']
            pid = int(pdata['id'])
            known_mandates[mandate_id] = pid
            party_id = int(predata['party']['id'])

            politician = {
                'first_name': predata['first_name'],
                'last_name': predata['last_name'],
                'display_name': predata['label'],
                'party_id': int(predata['party']['id']),
            }

            politicians[pid] = politician

            party = {
                'name': predata['party']['label'],
            }

            partys[party_id] = party

        poll['votes'][pid] = vote['vote']
    
    polls[poll_id] = poll
    total_time = time.time() - starttime
    exec_time = time.time() - lasttime
    lasttime = time.time()
    print(round(exec_time, 4), round(total_time, 4), len(polls))

with open('polls.json', 'w') as f:
    json.dump(polls, f)
