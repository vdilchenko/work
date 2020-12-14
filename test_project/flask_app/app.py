#! /usr/bin/env python3

import argparse

from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
from sqlalchemy import create_engine

from elasticsearch.exceptions import NotFoundError


parser = argparse.ArgumentParser(
    description=u"""Search engine for documents""")
parser.add_argument("dbname", type=str, metavar="DBNAME", help=u"Name of database")
parser.add_argument("user", type=str, metavar="USERNAME", help=u"Username for auth.")
parser.add_argument("--password", type=str, required=False, metavar="PASSWORD", help=u"Password for auth.")
parser.add_argument("--host", type=str, required=False, default="localhost", metavar="HOST", help=u"Database host")
parser.add_argument("--port", type=str, required=False, default=5432, metavar="PORT", help=u"Database port")

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search/results', methods=['GET', 'POST'])
def request_search():
    search_term = request.form['search']
    if len(request.form) > 1:
        if ((len(search_term) > 0) and (len(request.form['delete']) > 0)):
            return 'Choose either search or delete!'

    if len(search_term) == 0:
        id_to_delete = request.form['delete']
        try:
            es.delete(index='documents', id=id_to_delete)
            con.execute(f"""DELETE FROM posts where id = {id_to_delete}""")
        except NotFoundError:
            return f'Document #{id_to_delete} not found!'

        return f'Document #{id_to_delete} is deleted!'
    es_result = es.search(
        index='documents',
        size=20,
        body={'query': {'match': {'text': search_term}}}
    )
    results = {'id': [], 'rubrics': [], 'text': [], 'created_date': []}

    ids = []
    for res in es_result['hits']['hits']:
        ids.append(res['_id'])
    if len(ids) > 0:
        if len(ids) == 1:
            query = con.execute(f"""
                SELECT * from posts where id = {ids[0]} order by created_date;
                """).fetchall()
        else:
            query = con.execute(f"""
                SELECT * from posts where id in {*ids,} order by created_date;
            """).fetchall()
        for que in query:
            results['id'].append(que[0])
            results['rubrics'].append(que[1])
            results['text'].append(que[2])
            results['created_date'].append(que[3])

    return render_template('results.html', results=results)


if __name__ == '__main__':
    es = Elasticsearch()
    args = parser.parse_args()

    host = args.host
    db = args.dbname
    user = args.user
    password = args.password
    port = args.port
    try:
        engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
        con = engine.connect()
    except (Exception) as error:
        print('Error while working with PostgreSQL', error)

    app.run('127.0.0.1', debug=True)
