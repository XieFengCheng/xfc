# -*- coding: utf-8 -*-

"""
------------------------------------------------
describe:
    the db interact services of enterprise

usage:
    

------------------------------------------------
"""
from deploy.bo.bo_base import BOBase
from deploy.models.enterprise import EnterpriseModel
from sqlalchemy import or_, func


class EnterpriseBo(BOBase):

    def __init__(self):
        super(EnterpriseBo, self).__init__()

    def new_mode(self):
        return EnterpriseModel()

    def get_count(self, status=None):
        if not status:
            q = self.session.query(func.count(EnterpriseModel.id)).scalar()
            return q

        q = self.session.query(EnterpriseModel)
        q = q.filter(EnterpriseModel.status == status)
        return q.count()

    def get_by_code(self, code):
        if not code:
            return {}

        q = self.session.query(
            EnterpriseModel
        )
        q = q.filter(EnterpriseModel.credit_code == code)
        q = q.first()
        return q if q else {}
