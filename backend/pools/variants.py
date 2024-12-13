import os
from backend import utils
from backend.db.connect import PoolV, get_session
from sqlalchemy import select, text, desc, asc, and_
from datetime import datetime
from collections import defaultdict
from backend import utils
from backend import logger



temp_pool = {
    "pool_lid": "lksdfnvcxn",
    "updated_date": datetime.strptime("2000-01-01", "%Y-%m-%d"),
    "project_lids": ["dsfndsfal", "lfdasncv", "dlsfanvc"]
}


class PoolsV:
    def __init__(self):
        self.session = get_session()

    def get_pool(self, pool_lid):
        pool = self.session.query(PoolV).filter(PoolV.pool_lid == pool_lid)
        return pool

    def get_pool_updated_date(self, pool_lid):
        pool = self.session.query(PoolV).filter(PoolV.pool_lid == pool_lid).first()
        return pool.updated_date

    def delete_pool(self, pool_lid):
        pool = self.get_pool(pool_lid)
        pool.delete()
        self.session.commit()

    def delete_all_data(self):
        self.session.query(PoolV).delete()
        self.session.commit()

    def add_pool(self, pool: dict):
        for project in pool["project_lids"]:
            row = PoolV(
                pool_lid=pool["pool_lid"],
                updated_date=pool["updated_date"],
                project_lid=project,
            )
            self.session.add(row)

        self.session.commit()

