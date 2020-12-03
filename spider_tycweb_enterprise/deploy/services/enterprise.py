# -*- coding: utf-8 -*-

"""
------------------------------------------------
describe:
    the services of employee

usage:
    

------------------------------------------------
"""
from deploy.bo.enterprise import EnterpriseBo
from deploy.utils.logger import logger as LOG


class EnterpriseService(object):

    attrs = [
        'id',
        'name',
        'email',
        'phone',
        'tyt_url',
        'company_url',
        'address',
        'register_funds'
        'paidin_funds',
        'establish_date',
        'status',
        'credit_code',
        'registration_number',
        'identification_number',
        'organization_code',
        'company_type',
        'industry',
        'business_term',
        'taxpayer_qualification',
        'personnel_size',
        'insured_num'
        'resume',
        'registered_address',
        'business_scope'
    ]

    def __init__(self):
        super(EnterpriseService, self).__init__()
        self.enterprise_bo = EnterpriseBo()

    def get_count(self, status=None):
        count = self.enterprise_bo.get_count(status)
        return count if count else 0

    def adds(self, datas):
        if not datas:
            LOG.error('DB: data is null.')

        failure_list = list()
        success_list = list()
        for data in datas:
            if not data:
                continue

            credit_code = data.get('credit_code')
            name = data.get('name')
            model = self.enterprise_bo.get_by_code(credit_code)
            if model:
                failure_list.append(name)
                continue

            new_model = self.enterprise_bo.new_mode()
            new_model.name = name
            new_model.phone = data.get('phone')
            new_model.email = data.get('email')
            new_model.tyt_url = data.get('tyt_url')
            new_model.company_url = data.get('company_url')
            new_model.address = data.get('address')
            new_model.register_funds = data.get('register_funds')
            new_model.paidin_funds = data.get('paidin_funds')
            new_model.establish_date = data.get('establish_date')
            new_model.status = data.get('status')
            new_model.credit_code = credit_code
            new_model.registration_number = data.get('registration_number')
            new_model.identification_number = data.get('identification_number')
            new_model.organization_code = data.get('organization_code')
            new_model.company_type = data.get('company_type')
            new_model.industry = data.get('industry')
            new_model.business_term = data.get('business_term')
            new_model.taxpayer_qualification = data.get('taxpayer_qualification')
            new_model.personnel_size = data.get('personnel_size')
            new_model.insured_num = data.get('insured_num')
            new_model.resume = data.get('resume')
            new_model.registered_address = data.get('registered_address')
            new_model.business_scope = data.get('business_scope')
            self.enterprise_bo.add_model(new_model)
            success_list.append(name)
        else:
            print('success list【%s】:%s' % (len(success_list), ','.join(success_list)))
            print('failure list【%s】:%s' % (len(failure_list), ','.join(failure_list)))
