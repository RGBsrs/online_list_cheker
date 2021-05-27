from ..models import Table


class TableService:
    @staticmethod
    def fetch_all_tables(session):
        return session.query(Table)

    