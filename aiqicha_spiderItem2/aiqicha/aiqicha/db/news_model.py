from pymongo.errors import DuplicateKeyError
from ..settings import bixiao_reports
import copy

default_values = {
    'name': u'',
    'links': u'',
    'content_url': u''
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
        bixiao_reports.insert_one(add_dict)
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, '_id': add_dict.get('_id')}