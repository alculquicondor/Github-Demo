from flask import Flask, jsonify, abort
from neo4j.v1.exceptions import ResultError

from utils import neo4j_session

app = Flask(__name__)


def not_found():
    return jsonify({'message': 'Not Found'}), 404


@app.route('/<owner>/<name>')
def repo_info(owner, name):
    repo = owner + '/' + name

    with neo4j_session() as session:

        result = session.run(
            'MATCH (r:Repository{name:"%s"}) '
            'RETURN r' % repo
        )
        try:
            result.single()
        except ResultError:
            return not_found()

        result = session.run(
            'MATCH (:Repository{name:"%s"})<-[:CREATED]-(u:User) '
            'RETURN u.username' % repo
        )
        try:
            creator = result.single()[0]
        except ResultError:
            creator = None

        result = session.run(
            'MATCH (:Repository{name:"%s"})<-[:FORKS]-(r:Repository) '
            'RETURN r.name LIMIT 20' % repo
        )
        forks = [r[0] for r in result]

        result = session.run(
            'MATCH (:Repository{name:"%s"})<-[c:PUSHED|PULL_REQUEST|MEMBER]'
            '-(u:User) '
            'RETURN DISTINCT u.username, collect(type(c)) '
            'LIMIT 20' % repo
        )
        contributed = [
            {'contributor': u[0], 'what': u[1]} for u in result
        ]

        result = session.run(
            'MATCH (r1:Repository{name:"%s"})'
            '<-[:PUSHED|PULL_REQUEST|MEMBER|CREATED|STARRED]-(u:User)'
            '-[:PUSHED|PULL_REQUEST|MEMBER|CREATED|STARRED]->(r2:Repository) '
            'WHERE r1 <> r2 AND NOT (r2)-[:FORKS]->(r1) '
            'WITH r2, count(distinct u) AS people '
            'RETURN r2.name, people '
            'ORDER BY people DESC LIMIT 10' % repo
        )

        similar = [{'repo': r[0], 'count': r[1]} for r in result]

        result = session.run(
            'MATCH (:Repository{name:"%s"})<-[:STARRED]-(u:User) '
            'RETURN count(u)' % repo
        )

        stars = result.single()[0]

    return jsonify({
        'creator': creator,
        'forks': forks,
        'contributed': contributed,
        'similar': similar,
        'stars': stars
    })


@app.route('/<username>')
def user_info(username):
    with neo4j_session() as session:

        result = session.run(
            'MATCH (u:User{username:"%s"}) '
            'RETURN u' % username
        )
        try:
            result.single()
        except ResultError:
            return not_found()

        result = session.run(
            'MATCH (:User{username:"%s"})-[:FOLLOW]->(u:User) '
            'RETURN u.username LIMIT 20' % username
        )
        follows = [u[0] for u in result]

        result = session.run(
            'MATCH (:User{username:"%s"})-[:CREATED]->(r:Repository) '
            'RETURN r.name LIMIT 20' % username
        )
        created = [r[0] for r in result]

        result = session.run(
            'MATCH (:User{username:"%s"})-[c:PUSHED|PULL_REQUEST|MEMBER]->'
            '(r:Repository) '
            'RETURN DISTINCT r.name, collect(type(c)) LIMIT 20' % username
        )
        contributes = [{'repo': r[0], 'what': r[1]} for r in result]

        result = session.run(
            'MATCH (u1:User{username:"%s"})'
            '-[:PUSHED|PULL_REQUEST|MEMBER|CREATED|STARRED]->(r1:Repository)'
            '<-[:PUSHED|PULL_REQUEST|MEMBER|CREATED|STARRED]-(u2:User)'
            '-[:PUSHED|PULL_REQUEST|MEMBER|CREATED|STARRED]->(r2:Repository) '
            'WHERE u1 <> u2 AND r1 <> r2 AND NOT (r2)-[:FORKS]->(r1)'
            'WITH r2, count(distinct u2) AS people '
            'RETURN r2.name, people '
            'ORDER BY people DESC LIMIT 10' % username
        )
        recommended = [{'repo': r[0], 'count': r[1]} for r in result]

    return jsonify({
        'follows': follows,
        'created': created,
        'contributes_to': contributes,
        'recommended': recommended
    })
