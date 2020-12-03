# -*- coding: utf8 -*-
import copy
import time
import threading

from pymongo.errors import DuplicateKeyError
from datetime import datetime
from db.mongo_set import bixao_phone_emial

default_values = {
    'company_name': u'',
    'report_year': u'',
    'phone': u'',
    'email': u'',
    'date_time': datetime.now()
}



def _insert(data):
    add_dict = copy.copy(default_values)
    for key in default_values:
        if key in data:
            _values = data.get(key)
            if isinstance(_values, str):
                _values = _values.strip()
            add_dict.update({key: _values})

    try:
        bixao_phone_emial.insert_one(add_dict)
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, '_id': add_dict.get('_id')}