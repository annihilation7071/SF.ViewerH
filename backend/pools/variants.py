# noinspection PyUnresolvedReferences
from backend.db.connect import PoolV, get_session
from datetime import datetime


temp_pool = {
    "updated_date": datetime.strptime("2000-01-01", "%Y-%m-%d"),
    "project_lids": ["dsfndsfal", "lfdasncv", "dlsfanvc"]
}


class PoolsV:
    def __init__(self):
        self.session = get_session()

    def get_pool_by_lid(self, pool_lid):
        pool = self.session.query(PoolV).filter(PoolV.pool_lid == pool_lid)
        return pool

    def get_pool_updated_date_by_lid(self, pool_lid):
        pool = self.session.query(PoolV).filter(PoolV.pool_lid == pool_lid).first()
        return pool.updated_date

    def find_pool_by_project_lid(self, project_lid):
        pool = self.session.query(PoolV).filter(PoolV.project_lid == project_lid).first()
        return pool

    def delete_pool_by_lid(self, pool_lid):
        pool = self.get_pool_by_lid(pool_lid)
        pool.delete()
        self.session.commit()

    def delete_all_data(self):
        self.session.query(PoolV).delete()
        self.session.commit()

    def add_pool(self, pool: dict):

        for project in pool["project_lids"]:
            existing_pool = self.find_pool_by_project_lid(project)
            if len(existing_pool) == 0:
                continue
            else:
                existing_pool = self.get_pool_by_lid(existing_pool[0].pool_lid)
                if existing_pool.updated_date > pool["updated_date"]:
                    return "exist_newer", existing_pool.pool_lid
                else:
                    self.delete_pool_by_lid(existing_pool.pool_lid)

        for project in pool["project_lids"]:
            row = PoolV(
                pool_lid=pool["pool_lid"],
                updated_date=pool["updated_date"],
                project_lid=project,
            )
            self.session.add(row)

        self.session.commit()
