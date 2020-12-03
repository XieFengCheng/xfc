from pymongo.errors import DuplicateKeyError
from ..settings import bixiao_aiqicha_list
import copy

default_values = {
    'version': u'',
    'pid': u'',
    'title': u'',
    'info_links': u'',
    'md5_vals': u''
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
        bixiao_aiqicha_list.insert_one(add_dict)
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, '_id': add_dict.get('_id')}