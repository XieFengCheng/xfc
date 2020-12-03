# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from fastapi import requests
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message


class My_RetryMiddleware(RetryMiddleware):
    """ 代理重试 """

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response

        if (response.status in self.retry_http_codes) or (response.status != 200):
            reason = response_status_message(response.status)
            try:
                xdaili_url = spider.settings.get('XDAILI_URL')

                r = requests.get(xdaili_url)
                proxy_ip_port = ''.join(r.text).strip()
                print(proxy_ip_port, '*'*80)
                request.meta['proxy'] = 'https://' + proxy_ip_port
            except requests.exceptions.RequestException:
                print('获取讯代理ip失败！')
                spider.logger.error('获取讯代理ip失败！')

            return self._retry(request, reason, spider) or response
        return response


    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) and not request.meta.get('dont_retry', False):
            try:
                xdaili_url = spider.settings.get('XDAILI_URL')

                r = requests.get(xdaili_url)
                proxy_ip_port = ''.join(r.text).strip()
                request.meta['proxy'] = 'https://' + proxy_ip_port
            except requests.exceptions.RequestException:
                print('获取讯代理ip失败！')
                spider.logger.error('获取讯代理ip失败！')

            return self._retry(request, exception, spider)