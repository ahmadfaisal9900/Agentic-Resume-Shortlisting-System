
import lancedb
from langchain_google_genai import GoogleGenerativeAIEmbeddings


class LanceDBManager:
    def __init__(self, uri, api_key, region):
        self.db = lancedb.connect(uri=uri, api_key=api_key, region=region)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001"
        )

    def drop_table(self, table_name):
        if table_name in self.db.table_names():
            self.db.drop_table(table_name)

    def get_embeddings(self):
        return self.embeddings

    def get_connection(self):
        return self.db
