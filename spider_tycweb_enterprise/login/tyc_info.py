"""
突破天眼查极验验证码
"""
import random
import time, re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import requests
from io import BytesIO
import sys
sys.path.append('/spider_tycweb_enterprise/')
from libs.login_admin import login_proxy, login_user
from db.client_db import tyc_cookies
from libs.get_keys import conn, ck_cli, account_cli
from urllib import parse

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from io import BytesIO
from PIL import Image
import time
from selenium.webdriver import ActionChains
from lxml import etree
from db.mongo_set import (bixiao_business, bixiao_people, bixiao_shareholder,
                          bixiao_news, bixiao_product, bixao_phone_emial,
                          bixiao_recruit, bixiao_record_icp)
from request.get_info import TianYanChaClient

CHAOJIYING_USERNAME = ''
CHAOJIYING_PASSWORD = ''
CHAOJIYING_SOFT_ID = ''
CHAOJIYING_KIND = ''


class HuXiu(object):
    def __init__(self):
        self.chrome_option = webdriver.ChromeOptions()
        # chrome_option.set_headless()
        self.chrome_option.add_argument('User-Agent: "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 ('
                                   'KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"')
        self.proxy = login_proxy()
        # self.chrome_option.add_argument('--proxy-server=http://{}'.format(self.proxy))
        self.driver = webdriver.Chrome(executable_path=r"C:\chromedriver.exe", options=self.chrome_option)
        # self.driver = webdriver.Firefox(executable_path=r'C:\geckodriver.exe', firefox_options=options)
        self.driver.maximize_window()
        self.login_user = login_user()[0]
        self.login_password = login_user()[1]
        self.company_list_url = 'https://www.tianyancha.com/search/p0?key={}'
        self.wait = WebDriverWait(self.driver, 10)

    def close(self):
        import os
        self.driver.quit()
        os.system('taskkill /im chromedriver.exe /F')
        os.system('taskkill /im chrome.exe /F')

    def move_x(self, distance):
        element = self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]')

        # 这里就是根据移动进行调试，计算出来的位置不是百分百正确的，加上一点偏移
        distance -= element.size.get('width') / 2
        distance += 15

        # 按下鼠标左键
        ActionChains(self.driver).click_and_hold(element).perform()
        time.sleep(0.05)

        one = distance + 5


        ActionChains(self.driver).move_by_offset(one, 0).perform()
        time.sleep(0.1)
        ActionChains(self.driver).move_by_offset(-2, 0).perform()
        time.sleep(0.2)
        ActionChains(self.driver).move_by_offset(-4, 0).perform()
        time.sleep(1)
        # ActionChains(self.driver).move_by_offset(4, 0).perform()

        # ActionChains(self.driver).move_by_offset(distance, 1).perform()
        ActionChains(self.driver).release(on_element=element).perform()

        time.sleep(2)
        self.company_list()


    def company_list(self):

        keys_url = conn.rpop('keys_pg_urls')
        # keys = conn.lindex('keywords', 0)
        print(keys_url)
        try:
            self.driver.get(keys_url)
            nowurl = self.driver.current_url
            if 'captcha' not in str(nowurl):
                if nowurl[8:17] == 'antirobot':
                    self.run_verify()
                    company_list = self.driver.page_source
                    re_url = re.compile(r'https://www.tianyancha.com/company/\d+')
                    # 获取公司详细页面链接
                    url = re_url.findall(company_list)
                    print(type(url), url, '#' * 80)
                    print(f'公司列表个数：{len(url)}')
                    if len(url) < 1 or len(url) == 0:
                        conn.lpush('keys_pg_urls', keys_url)
                        self.chrome_option.add_argument('--proxy-server=http://{}'.format(login_proxy()))
                        self.visit_index()

                    else:
                        for num_company in url:
                            conn.lpush('info_sys', num_company)
                            self.company_info(num_company)


                    time.sleep(5)
                else:
                    company_list = self.driver.page_source
                    re_url = re.compile(r'https://www.tianyancha.com/company/\d+')
                    # 获取公司详细页面链接
                    url = re_url.findall(company_list)
                    print(url, '#' * 80)
                    print(f'公司列表个数：{len(url)}')
                    if len(url) < 1 or len(url) == 0:
                        conn.lpush('keys_pg_urls', keys_url)
                        self.chrome_option.add_argument('--proxy-server=http://{}'.format(login_proxy()))
                        self.visit_index()

                    else:
                        for num_company in url:
                            conn.lpush('info_sys', num_company)
                            self.company_info(num_company)

            elif 'login' in str(keys_url):
                print('## 返回登录页面 ##')
                conn.lpush('keys_pg_urls', keys_url)
                self.visit_index()
                print('X'*80)

            else:
                print('!! 验证点击验证码 !!')
                print(keys_url)
                # conn.lpush('keys_pg_urls', keys_url)
                nowurl = self.driver.current_url
                print(nowurl)
                if nowurl[8:17] == 'antirobot':
                    self.run_verify()
                company_list = self.driver.page_source
                re_url = re.compile(r'https://www.tianyancha.com/company/\d+')
                # 获取公司详细页面链接
                url = re_url.findall(company_list)
                print(url, '#' * 80)
                print(f'公司列表个数：{len(url)}')
                if len(url) < 1 or len(url) == 0:
                    conn.lpush('keys_pg_urls', keys_url)
                    self.chrome_option.add_argument('--proxy-server=http://{}'.format(login_proxy()))
                    self.visit_index()

                else:
                    for num_company in url:
                        conn.lpush('info_sys', num_company)
                        self.company_info(num_company)
                time.sleep(2)
            list_vals = self.driver.page_source
            self.write_file('changevals.html', list_vals)
        except Exception as ex:
            print('R'*80, ex)
            conn.lpush('keys_pg_urls', keys_url)
            if 'NoneType' in str(ex):
                self.close()

    def company_info(self, url):
        # info_url = conn.rpop('info_sys')
        print(url, '详情信息地址')
        self.driver.get(url)
        time.sleep(2)
        nowurl = self.driver.current_url
        if nowurl[8:17] == 'antirobot':
            self.run_verify()
            source_txt = self.driver.page_source
        else:
            source_txt = self.driver.page_source
        if not source_txt:
            self.company_info(url)
        obj = TianYanChaClient()
        vals_item = obj.detail_by_url(source_txt)
        if not vals_item:
            conn.lpush('info_sys', url)
            self.company_info(url)



    def run_verify(self):
        from login.chaojiying import Chaojiying
        chaojiying = Chaojiying(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID)
        image = self.get_touch_image()
        bytes_array = BytesIO()
        image.save(bytes_array, format='PNG')
        result = chaojiying.post_pic(bytes_array.getvalue(), CHAOJIYING_KIND)
        locations = self.get_points(result)
        self.click_words(locations)
        self.click_verify()

    def get_touch_image(self, name='captcha.png'):
        top, bottom, left, right = self.get_position()
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        # 截图位置必须为左上右下
        captcha.save(name)
        return captcha

    def get_points(self, captcha_result):
        groups = captcha_result.get('pic_str').split('|')
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations

    def click_words(self, locations):
        for location in locations:
            ActionChains(self.driver).move_to_element_with_offset(self.get_touch_element(), location[0],
                                                             location[1]).click().perform()
            time.sleep(1)

    def click_verify(self):
        button = self.wait.until(EC.element_to_be_clickable((By.ID, 'submitie')))
        button.click()

    def get_position(self):
        element = self.get_touch_element()
        time.sleep(2)
        location = element.location
        size = element.size
        print(location, size)
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size['width']
        return (top, bottom, left, right)

    def get_touch_element(self):
        element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'new-box94')))
        return element

    def get_screenshot(self):
        screenshot = self.driver.get_screenshot_as_png()
        self.driver.get_screenshot_as_file('prdabnormal.png')
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot


    def write_file(self, name_file, info_vals):
        with open(name_file, 'w', encoding='utf-8') as wf:
            wf.write(str(info_vals))


    # 判断颜色是否相近
    def is_similar_color(self, x_pixel, y_pixel):
        for i, pixel in enumerate(x_pixel):
            if abs(y_pixel[i] - pixel) > 50:
                return False
        return True

    def get_offset_distance(self, cut_image, full_image):
        for x in range(cut_image.width):
            for y in range(cut_image.height):
                cpx = cut_image.getpixel((x, y))
                fpx = full_image.getpixel((x, y))
                if not self.is_similar_color(cpx, fpx):
                    img = cut_image.crop((x, y, x + 50, y + 40))
                    # 保存一下计算出来位置图片，看看是不是缺口部分
                    img.save("tyc1.jpg")
                    return x

    # 拼接图片
    def mosaic_image(self, image_url, location):
        resq = requests.get(image_url)
        file = BytesIO(resq.content)
        img = Image.open(file)
        image_upper_lst = []
        image_down_lst = []
        for pos in location:
            if pos[1] == 0:
                # y值==0的图片属于上半部分，高度58
                image_upper_lst.append(img.crop((abs(pos[0]), 0, abs(pos[0]) + 10, 58)))
            else:
                # y值==58的图片属于下半部分
                image_down_lst.append(img.crop((abs(pos[0]), 58, abs(pos[0]) + 10, img.height)))

        x_offset = 0
        # 创建一张画布，x_offset主要为新画布使用
        new_img = Image.new("RGB", (260, img.height))
        for img in image_upper_lst:
            new_img.paste(img, (x_offset, 58))
            x_offset += img.width

        x_offset = 0
        for img in image_down_lst:
            new_img.paste(img, (x_offset, 0))
            x_offset += img.width

        return new_img

    def get_image_url(self, xpath):
        link = re.compile('background-image: url\("(.*?)"\); background-position: (.*?)px (.*?)px;')
        elements = self.driver.find_elements_by_xpath(xpath)
        image_url = None
        location = list()
        for element in elements:
            style = element.get_attribute("style")
            groups = link.search(style)
            url = groups[1]
            x_pos = groups[2]
            y_pos = groups[3]
            location.append((int(x_pos), int(y_pos)))
            image_url = url
        return image_url, location

    def analog_drag(self):
        try:
            # 鼠标移动到拖动按钮，显示出拖动图片
            element = self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]')
            ActionChains(self.driver).move_to_element(element).perform()
            time.sleep(3)

            # 刷新一下极验图片
            element = self.driver.find_element_by_xpath('//a[@class="gt_refresh_button"]')
            element.click()
            time.sleep(1)

            # 获取图片地址和位置坐标列表
            cut_image_url, cut_location = self.get_image_url('//div[@class="gt_cut_bg_slice"]')
            full_image_url, full_location = self.get_image_url('//div[@class="gt_cut_fullbg_slice"]')

            # 根据坐标拼接图片
            cut_image = self.mosaic_image(cut_image_url, cut_location)
            full_image = self.mosaic_image(full_image_url, full_location)

            cut_image.save("tyc_cut.jpg")
            full_image.save("tyc_full.jpg")

            # 根据两个图片计算距离
            distance = self.get_offset_distance(cut_image, full_image)
            self.move_x(distance)

        except Exception as e:
            print(f'im error vals as {e}')


    def visit_index(self):
        # self.driver.delete_all_cookies()
        self.driver.get("https://www.tianyancha.com/login")
        if self.login_user and self.login_password:
            time.sleep(2)
            pwd_login = self.driver.find_element_by_xpath("//div[@tyc-event-ch='Login.PasswordLogin']")
            pwd_login.click()
            time.sleep(3)
            user_num = login_user()[0]
            password = login_user()[1]
            phone = self.driver.find_element_by_xpath("//div[@class='modulein modulein1 mobile_box  f-base collapse in']"
                                                      "/div[@class='pb24 position-rel']/div[@class='live-search-wrap']"
                                                      "/input[@class='input contactphone js-live-search-phone']")
            # phone.send_keys("18665821384")
            phone.send_keys(user_num)
            time.sleep(1)
            pwd = self.driver.find_element_by_xpath("//div[@class='modulein modulein1 mobile_box  f-base collapse in']"
                                                    "/div[@class='input-warp -block']/input"
                                                    "[@class='input contactword input-pwd']")
            # pwd.send_keys("tl123456")
            pwd.send_keys(password)
            login_click = self.driver.find_element_by_xpath("//div[@onclick='loginByPhone(event);']")
            login_click.click()

            WebDriverWait(self.driver, 10, 0.5).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="gt_slider_knob gt_show"]')))

            # 进入模拟拖动流程
            self.analog_drag()

        else:
            pass



if __name__ == "__main__":
    import time
    while True:
        h = HuXiu()
        try:
            h.visit_index()
        except Exception as eo:
            try:
                h.visit_index()
            except:
                pass
        h.close()
        time.sleep(8)
