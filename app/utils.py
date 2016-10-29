from contextlib import contextmanager

from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://neo4j",
                              auth=basic_auth("neo4j", "githubdemo"))


@contextmanager
def neo4j_session():
    session = driver.session()
    yield session
    session.close()
