import functools
import time
import os
from datetime import date
from typing import List, Tuple

import requests

from wahl_p_aka import database as db

start_time = time.time()
last_time = start_time

period = 111  # Bundestag 2017 -- 2021

aw_domain = 'a-watch.dont-break.it'

# api_base_url = 'https://www.abgeordnetenwatch.de/api/v2'
api_base_url = 'https://a-watch.dont-break.it/api/v2'

polls = {}


def fix_api_url(url: str, target: str = None,
                source: str = 'www.abgeordnetenwatch.de') -> str:
    """
    Ensure the urls from the API use our cache

    :param url: The original api
    :param target: Where the requests should be going
    :param source: What should be replaced
    :return: The fixed url
    """
    if target is None and aw_domain:
        target = aw_domain
    return url.replace(source, target)


def get_api_url(endpoint) -> str:
    return f'{api_base_url}/{endpoint}'


def get_poll(poll) -> db.Poll:
    poll_id = poll['id']
    _poll = db.Poll()
    _poll.aw_id = poll_id
    _poll.title = poll['label']
    _poll.abstract = poll['field_intro']
    _poll.date = date.fromisoformat(poll['field_poll_date'])

    for v in get_votes(_poll):
        _poll.politician_votes.append(v)

    db.db.session.add(_poll)

    return _poll


def get_votes(poll: db.Poll) -> List[db.PartyVote]:
    scrape_limit = int(os.getenv('SCRAPE_SHORT', False))
    api_votes = requests.get(
        get_api_url(f'polls/{poll.aw_id}'),
        {
            'related_data': 'votes',
        }
    )

    votes = []
    _api_votes = api_votes.json()
    for _v in api_votes.json()['data']['related_data']['votes']:
        vote = db.PoliticianVote()
        vote.vote = _v['vote']
        mandate_id = int(_v['mandate']['id'])
        politician, party = get_politician_by_mandate_id(mandate_id)
        vote.party = party
        vote.politician = politician
        vote.poll = poll
        db.db.session.add(vote)
        votes.append(vote)

        if scrape_limit and len(votes) > scrape_limit:
            break

    return votes


@functools.lru_cache(maxsize=None)
def get_politician_by_mandate_id(mandate_id) -> Tuple[db.Politician, db.Party]:
    api_mandate = requests.get(
        get_api_url(f'candidacies-mandates/{mandate_id}'),
        {
            'related_data': 'politician',
        }
    )

    mandate = api_mandate.json()['data']
    _politician_data = mandate['related_data']['politician']
    _party_data = _politician_data['party']

    party = create_party(int(_party_data['id']))

    politician = db.Politician()
    politician.aw_id = _politician_data['id']
    politician.first_name = _politician_data['first_name']
    politician.last_name = _politician_data['last_name']
    politician.party = party

    db.db.session.add(politician)

    return politician, party


@functools.lru_cache(maxsize=None)
def create_party(party_id: int) -> db.Party:
    api_party = requests.get(
        get_api_url(f'parties/{party_id}')
    )
    party_data = api_party.json()['data']
    party = db.Party()
    party.short_name = party_data['label']
    party.full_name = party_data['full_name']
    party.aw_id = party_data['id']
    db.db.session.add(party)
    return party


if __name__ == '__main__':
    r = requests.get(
        get_api_url('polls'),
        {
            'field_legislature[entity.id]': period,
            'pager_limit': 10,
            'page': 0,
        }
    )

    data = r.json()['data']

    polls = []
    for poll in data:
        polls.append(get_poll(poll))

    db.db.session.commit()
