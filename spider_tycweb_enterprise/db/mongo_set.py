
import pymongo

conn = pymongo.MongoClient('mongodb://{0}:{1}@{2}:{3}/'.format({}, {}, {}, {}))
conn_db = conn['tldb']
bixiao_list = conn_db['source_list']
bixiao_business = conn_db['basic_business']
bixiao_people = conn_db['job_people']
bixiao_shareholder = conn_db['structure_shareholder']
bixiao_news = conn_db['opinion_news']
bixiao_product = conn_db['info_product']
bixao_phone_emial = conn_db['phone_email']
bixiao_recruit = conn_db['info_recruit']
bixiao_record_icp = conn_db['record_icp']
bixiao_financing = conn_db['financing']
bixiao_reports = conn_db['reports']