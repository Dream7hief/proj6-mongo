import flask_main
from pymongo import MongoClient
import arrow
def test_store():
	test_text = "These are some words."
	test_date = arrow.get('1995-23-03')

	collection_start = len(flask_main.get_memos())

	flask_main.store_document(test_date, test_text)
	
	collection_end = len(flask_main.get_memos())

	assert(collection_start + 1 == collection_end)

def test_remove():
	test_text = "These are some words."
	test_date = arrow.get('1995-23-03')

	collection_start = len(flask_main.get_memos())

	flask_main.store_document(test_date, test_text)
	flask_main.remove_document(['0'])

	collection_end = len(flask_main.get_memos())

	assert(collection_start==collection_end)
