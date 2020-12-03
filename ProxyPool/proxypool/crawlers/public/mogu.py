from proxypool.schemas.proxy import Proxy
from proxypool.crawlers.base import BaseCrawler


class Mogu(BaseCrawler):
    urls = ['http://mvip.piping.mogumiao.com/proxy/api/get_ip_bs?'
            'appKey=b43805c715694b9d8395d0de5895e805&count=15'
            '&expiryDate=0&format=2&newLine=3']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko'
                      ') Chrome/83.0.4103.97 Safari/537.36'
    }

    def parse(self, html):
        for ip in str(html).split(' '):
            host = ip.split(':')[0]
            port = ip.split(':')[1]
            yield Proxy(host=host, port=port)


if __name__ == '__main__':
    crawler = Mogu()
    for proxy in crawler.crawl():
        print(proxy)