import time
import requests

ss_request = requests.session()
def timestamp_to_strftime(timestamp, format='%Y-%m-%d %H:%M:%S'):
    """
    时间戳转日期
    timestamp：要转换的时间戳
    format：日期格式化字符串

    :return 返回日期格式字符串
    """
    ltime = time.localtime(timestamp)
    time_str = time.strftime(format, ltime)
    return time_str


def request_doing(url: str = None, headers: dict = dict, Method: int = 1, data: dict = dict,
                  params: dict = dict):
    is_su = False
    for tes in range(6):
        if Method == 1:
            industry_list = ss_request.get(
                url=url,
                headers=headers,
                params=params,
                verify=False,
                timeout=10
            )
        else:
            industry_list = ss_request.post(
                url=url,
                headers=headers,
                data=data,
                verify=False,
                timeout=5
            )
        if industry_list.status_code == 200:
            is_su = True
            break

    if not is_su:
        return False
    return industry_list.text