# -*- coding: utf-8 -*-

"""
------------------------------------------------
describe:
    the model of enterprise

usage:
    

------------------------------------------------
"""
from sqlalchemy import (
        Column,
        String,
        Integer,
        TIMESTAMP,
        Date,
        TEXT
)
from deploy.models import base


__all__ = ("EnterpriseModel")


class EnterpriseModel(base.ModelBase):
    __tablename__ = 'enterprise'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(55))
    phone = Column(String(55))
    tyt_url = Column(String(100))
    company_url = Column(String(100))
    address = Column(String(255))
    register_funds = Column(String(20))
    paidin_funds = Column(String(20))
    establish_date = Column(Date)
    status = Column(String(30))
    credit_code = Column(String(30))
    registration_number = Column(String(120))
    identification_number = Column(String(120))
    organization_code = Column(String(80))
    company_type = Column(String(30))
    industry = Column(String(100))
    business_term = Column(String(55))
    taxpayer_qualification = Column(String(120))
    personnel_size = Column(String(120))
    insured_num = Column(String(30))
    resume = Column(TEXT())
    registered_scope = Column(String(200))
    business_scope = Column(TEXT())
