import datetime
import gc
import gzip
from io import BytesIO
import json

import requests

from utils import neo4j_session


GITHUB_ARCHIVE_URL = 'http://data.githubarchive.org/%s-%d.json.gz'


def add_user_to_repo(session, username, repository, relationship):
    session.run('MERGE (u:User{username: "%s"}) '
                'MERGE (r:Repository{name: "%s"}) '
                'MERGE (u)-[:%s]->(r)' % (username, repository, relationship))


def add_user_to_user(session, username1, username2, relationship):
    session.run('MERGE (u1:User{username: "%s"}) '
                'MERGE (u2:User{username: "%s"}) '
                'MERGE (u1)-[:%s]->(u2)' % (username1, username2, relationship))


def process_create_event(session, event):
    if event['payload']['ref_type'] == 'repository':
        add_user_to_repo(session, event['actor']['login'],
                         event['repo']['name'], 'CREATED')


def process_follow_event(session, event):
    add_user_to_user(session, event['actor']['login'],
                     event['payload']['target']['login'], 'FOLLOW')


def process_fork_event(session, event):
    add_user_to_repo(session, event['actor']['login'],
                     event['repo']['name'], 'FORKED')
    add_user_to_repo(session, event['actor']['login'],
                     event['payload']['forkee']['full_name'], 'CREATED')


def process_member_event(session, event):
    add_user_to_repo(session, event['payload']['member']['login'],
                     event['repo']['name'], 'MEMBER')


def process_pull_request_event(session, event):
    if event['payload']['action'] == 'opened':
        add_user_to_repo(session, event['actor']['login'],
                         event['repo']['name'], 'PULL_REQUEST')


def process_push_event(session, event):
    add_user_to_repo(session, event['actor']['login'],
                     event['repo']['name'], 'PUSHED')


def process_watch_event(session, event):
    add_user_to_repo(session, event['actor']['login'],
                     event['repo']['name'], 'STARRED')


EVENT_MAPPER = {
    'CreateEvent': process_create_event,
    'FollowEvent': process_follow_event,
    'ForkEvent': process_fork_event,
    'MemberEvent': process_member_event,
    'PullRequestEvent': process_pull_request_event,
    'PushEvent': process_push_event,
}


def fill_up(date=None):
    if isinstance(date, str):
        date_str = date
    else:
        if not date:
            date = datetime.date.today()
        date_str = date.strftime('%Y-%m-%d')
    with neo4j_session() as session:
        for hour in range(24):
            gc.collect()
            url = GITHUB_ARCHIVE_URL % (date_str, hour)
            print(url)
            response = BytesIO(requests.get(url).content)
            with gzip.GzipFile(fileobj=response, mode='r') as content_f:
                for line in content_f:
                    line = line.decode('utf8').strip()
                    if not line:
                        continue
                    event = json.loads(line)
                    event_processor = EVENT_MAPPER.get(event['type'])
                    if event_processor:
                        event_processor(session, event)


if __name__ == '__main__':
    import sys
    fill_up(sys.argv[1] if len(sys.argv) > 1 else None)
