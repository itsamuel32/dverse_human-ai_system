from unittest import TestCase

from vectordb.vector_db import VectorDB


class TestVectorDB(TestCase):
    vector_db = VectorDB()

    def test_query(self):
        print(self.vector_db.search("Pictures over 2.3 million", 3))
