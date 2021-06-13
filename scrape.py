import functools
import os
import time
from datetime import date
from hashlib import scrypt
from typing import List

import requests

from wahl_p_aka import database as db
from sqlalchemy import func

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


def get_or_create_poll(poll) -> db.Poll:
    poll_id = int(poll['id'])

    db_obj = db.db.session.query(db.Poll) \
        .filter(db.Poll.aw_id == poll_id).first()
    if db_obj is not None:
        return db_obj

    _poll = db.Poll()
    _poll.aw_id = poll_id
    _poll.title = poll['label']
    _poll.abstract = poll['field_intro']
    _poll.date = date.fromisoformat(poll['field_poll_date'])

    if poll['field_topics'] is not None:
        for topic in poll['field_topics']:
            _poll.topic = get_or_create_topic_from_api(topic['id'])

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
        politician = get_or_create_politician_by_mandate_id(mandate_id)
        vote.party = politician.party
        vote.politician = politician
        vote.poll = poll
        db.db.session.add(vote)
        votes.append(vote)

        if scrape_limit and len(votes) > scrape_limit:
            break

    return votes


@functools.lru_cache(maxsize=None)
def get_or_create_politician_by_mandate_id(mandate_id) -> db.Politician:
    db_obj = db.db.session.query(db.Politician) \
        .filter(db.Politician.aw_id == mandate_id).first()
    if db_obj is not None:
        return db_obj

    api_mandate = requests.get(
        get_api_url(f'candidacies-mandates/{mandate_id}'),
        {
            'related_data': 'politician',
        }
    )

    mandate = api_mandate.json()['data']
    _politician_data = mandate['related_data']['politician']
    _party_data = _politician_data['party']

    party = get_or_create_party(int(_party_data['id']))

    politician = db.Politician()
    politician.aw_id = _politician_data['id']
    politician.first_name = _politician_data['first_name']
    politician.last_name = _politician_data['last_name']
    politician.party = party

    db.db.session.add(politician)

    return politician


@functools.lru_cache(maxsize=None)
def get_or_create_party(party_id: int) -> db.Party:
    db_obj = db.db.session.query(db.Party) \
        .filter(db.Party.aw_id == party_id).first()
    if db_obj is not None:
        return db_obj

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


@functools.lru_cache(maxsize=None)
def get_or_create_topic_from_api(topic_id: int) -> db.PollTopic():
    db_obj = db.db.session.query(db.PollTopic) \
        .filter(db.PollTopic.aw_id == topic_id).first()
    if db_obj is not None:
        return db_obj

    api_topic = requests.get(
        get_api_url(f'topics/{topic_id}')
    )

    topic_data = api_topic.json()['data']

    topic = db.PollTopic()
    topic.aw_id = topic_id
    topic.name = topic_data['label']

    if topic_data['parent'] is not None:
        topic.parents.append(
            get_or_create_topic_from_api(
                int(topic_data['parent'][0]['id'])
            )
        )

    db.db.session.add(topic)

    return topic


if __name__ == '__main__':
    scraper_polls_count = int(os.getenv('SCRAPE_POLLS_COUNT', 100))
    if scraper_polls_count > 100:
        scraper_polls_count = 100  # 100 is the limit of the aw api
    scraper_paginate = os.getenv('SCRAPE_PAGINATE', str(scraper_polls_count >= 100))
    scraper_paginate = scraper_paginate.lower() in ('true', '1', 't')
    next_page = True
    page = 0
    _polls = []
    polls = []

    while next_page:
        r = requests.get(
            get_api_url('polls'),
            {
                'field_legislature[entity.id]': period,
                'pager_limit': scraper_polls_count,
                'page': page,
            }
        )

        api_polls = r.json()['data']
        _polls += api_polls
        next_page = (
            (len(api_polls) >= scraper_polls_count) and
            scraper_paginate
         )
        page += 1

    for _p in _polls:
        polls.append(get_or_create_poll(_p))

    db.db.session.commit()

    for poll in db.Poll.query.all():
        parties = {}
        for vote in poll.politician_votes:
            party = vote.politician.party
            if party.id not in parties:
                parties[party.id] = {}
            if vote.vote not in parties[party.id]:
                parties[party.id][vote.vote] = 0
            parties[party.id][vote.vote] += 1

        print(parties)
