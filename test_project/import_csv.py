from sqlalchemy import create_engine, insert, Table, MetaData
from sqlalchemy.dialects import postgresql
import sqlalchemy

import pandas as pd

parser = argparse.ArgumentParser(
    description=u"""DB credentials""")
parser.add_argument("dbname", type=str, metavar="DBNAME", help=u"Name of database")
parser.add_argument("user", type=str, metavar="USERNAME", help=u"Username for auth.")
parser.add_argument("--password", type=str, required=False, metavar="PASSWORD", help=u"Password for auth.")
parser.add_argument("--host", type=str, required=False, default="localhost", metavar="HOST", help=u"Database host")
parser.add_argument("--port", type=str, required=False, default=5432, metavar="PORT", help=u"Database port")


def main(engine):
	df = pd.read_csv('/Users/ilchenkoslava/Downloads/posts.csv')
	df['rubrics'] = df['rubrics'].apply(lambda x: eval(x))

	df.to_sql('posts', engine, if_exists='append', index=False,
		dtype={
			'text': sqlalchemy.types.VARCHAR(),
			'rubrics': postgresql.ARRAY(sqlalchemy.types.TEXT()),
			'created_date': sqlalchemy.types.TIMESTAMP()
		})


if __name__ == '__main__':
	args = parser.parse_args()

    host = args.host
    db = args.dbname
    user = args.user
    password = args.password
    port = args.port

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
	main(engine)
