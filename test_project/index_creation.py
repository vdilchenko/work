from elasticsearch import Elasticsearch
from datetime import datetime
from sqlalchemy import create_engine


def main():
    engine = create_engine(
        'postgresql://ilchenkoslava@localhost:5432/postgres')
    es = Elasticsearch()

    con = engine.connect()

    result = con.execute(
        """
        SELECT id, text from posts;
        """)

    for _id, text in result.fetchall():
        body = {'iD': _id, 'text': text}
        es.index(index='documents', id=_id, body=body)


if __name__ == '__main__':
    main()