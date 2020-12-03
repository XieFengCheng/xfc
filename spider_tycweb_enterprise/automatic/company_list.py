# -*- coding: utf-8 -*-
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
from libs.login_admin import login_proxy, login_admin
from db.client_db import tyc_cookies


class CompanyList(object):
    def __init__(self):
        chrome_option = webdriver.ChromeOptions()
        # chrome_option.set_headless()
        # chrome_option.add_argument('User-Agent: "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 ('
        #                            'KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"')
        chrome_option.add_argument('--proxy-server=http://{}'.format(login_proxy()))
        self.driver = webdriver.Chrome(executable_path=r"C:\chromedriver.exe", options=chrome_option)
        self.driver.maximize_window()
        self.login_user = login_admin()[0]
        self.login_password = login_admin()[1]

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

        time.sleep(1.5)
        # find_vals = self.driver.find_element_by_xpath('//form[@onsubmit="return header.stopSubmit(event,true,"#home-main-search"'
        #                                   ');"]/div[@class="live-search-wrap -index"]/input[@click-selected="header.suggestToCompany"]').click()
        # find_vals = self.driver.find_element_by_xpath('//*[@id="web-content"]/div/div[1]/div[2]/div/div/div[2]/div[2]/div[1]/form/div/ul').click()
        # find_vals.send_keys('金融行业')
        # self.driver.find_element_by_xpath('//*[@id="web-content"]/div/div[1]/div[2]/div/div/div[2]/div[2]/div[1]/div/[@onclick="header.search(true,"#home-main-search")"]').click()

        for cks in self.driver.get_cookies():
            self.driver.add_cookie(cks)
        self.driver.get('https://www.tianyancha.com/search/p40?key=游戏')
        ps = self.driver.page_source
        with open('list.html', 'w', encoding='utf-8') as wf:
            wf.write(ps)

        self.driver.quit()


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
            print(e)
            pass

    def visit_index(self):
        self.driver.delete_all_cookies()
        self.driver.get("https://www.tianyancha.com/login")

        time.sleep(2)
        pwd_login = self.driver.find_element_by_xpath("//div[@tyc-event-ch='Login.PasswordLogin']")
        pwd_login.click()
        time.sleep(3)
        phone = self.driver.find_element_by_xpath(
            "//div[@class='modulein modulein1 mobile_box  f-base collapse in']"
            "/div[@class='pb24 position-rel']/div[@class='live-search-wrap']"
            "/input[@class='input contactphone js-live-search-phone']")
        if self.login_user and self.login_password:
            print(f'登录账号：{self.login_user}, 密码：{self.login_password}')
            # phone.send_keys("18665821384")
            phone.send_keys(self.login_user)
            time.sleep(1)
            pwd = self.driver.find_element_by_xpath("//div[@class='modulein modulein1 mobile_box  f-base collapse in']"
                                                    "/div[@class='input-warp -block']/input"
                                                    "[@class='input contactword input-pwd']")
            # pwd.send_keys("tl123456")
            pwd.send_keys(self.login_password)
            login_click = self.driver.find_element_by_xpath("//div[@onclick='loginByPhone(event);']")
            login_click.click()

            WebDriverWait(self.driver, 10, 0.5).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="gt_slider_knob gt_show"]')))

            # 进入模拟拖动流程
            self.analog_drag()



if __name__ == "__main__":
    # h = CompanyList()
    # h.visit_index()
    while True:
        h = CompanyList()
        try:
            h.visit_index()
        except:
            h.visit_index()