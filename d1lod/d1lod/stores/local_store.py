import logging
import RDF

logger = logging.getLogger(__name__)


class LocalStore:
    def __init__(self):
        self.storage = RDF.MemoryStorage()
        self.model = RDF.Model(storage=self.storage)

    def query(self, query_text):
        q = RDF.Query(query_text)

        return [r for r in q.execute(self.model)]

    def insert_model(self, model):
        for statement in model:
            self.model.add_statement(statement)

        return True
