# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import logging
from itemadapter import ItemAdapter
from aiqicha_spiderItem2.aiqicha.aiqicha.items import AiqichaItem


class AiqichaPipeline(object):
    def open_spider(self, spider):
        self.file = open('ocu2.json', 'a', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        logging.critical(spider.name, '%' * 80)
        if spider.name == 'SupplySpiders':
            if isinstance(item, AiqichaItem):
                line = json.dumps(ItemAdapter(item).asdict()) + "\n"
                self.file.write(line)
                logging.critical(f'json数据集：{line}**********************************')
                return item

            else:
                logging.debug(f'!!!异常item信息:{item}')

        else:
            logging.error(f'!!!爬虫名称异常：{spider.name}')

