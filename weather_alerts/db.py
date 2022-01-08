from sqlalchemy import create_engine

class Database:
    def create(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)