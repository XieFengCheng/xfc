import copy

from db.mongo_set import bixiao_list
from pymongo.errors import DuplicateKeyError

default_des = {
    'tyt_url': '公司列表地址',
    'name': '公司名称',
    'company_id': '公司ID',
    'label_index': '索引',
    'rquest_url': '详情信息地址',
    'source': '来源',
    'created_time': '创建时间',
}

default_vals = {
    'tyt_url': '',
    'name': '',
    'company_id': '',
    'label_index': '',
    'rquest_url': '',
    'source': '',
    'created_time': '',
}


def _insert(data):
    add_dict = copy.copy(default_vals)
    for key in default_vals:
        if key in data:
            _values = data.get(key)
            if isinstance(_values, str):
                _values = _values.strip()
            add_dict.update({key: _values})
    try:
        bixiao_list.find_one_and_update({'company_id': add_dict.get('company_id')}, {'$set': add_dict})
    except DuplicateKeyError:
        return {'status': False, 'msg': u'已存在'}
    return {'status': True, '_id': add_dict.get('_id'), 'company_id': add_dict.get('company_id')}