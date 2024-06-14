import sys
import re
from os import error
from time import sleep
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
import random
from fake_useragent import UserAgent
from playwright._impl._errors import TimeoutError

def handle_response(response):
    if response.status != 200:
        print(f"非200状态码: {response.status}，URL: {response.url}")
        # 这里可以根据需要抛出异常或执行其他逻辑
        raise Exception(f"请求失败，状态码：{response.status},程序退出！")
        sys.exit()

def print_request_headers(request):
    #print(f"Request URL: {request.url}")
    #print("Request Headers:")
    for key, value in request.headers.items():
        #print(f"  {key}: {value}")
        pass


def check_string_in_file(file_path, search_string):
    try:
        # 打开文件并读取全部内容
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        # 检查字符串是否在文件内容中
        return search_string in file_content
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
     # 使用 'w' 模式打开文件，如果文件不存在则创建
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("\n")
        print(f"文件 '{file_path}' 已成功创建并写入内容。")
        file.close()
        return False
    except Exception as e:
        print(f"读取文件时发生错误：{e}")
        file.close()
        return False

def indexPage():
    with  sync_playwright() as p:
        # 使用fake_useragent库生成随机User-Agent
        ua = UserAgent()
        user_agent = ua.random
        allDetailPages = []
        # 启动Chromium浏览器
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_extra_http_headers({
            "User-Agent": user_agent,
            "Accept-Language": "en-US,en;q=0.9",
        })
        page.on("response",handle_response)
        # 导航到目标网址
        try:
            url = "https://www.shuangliusc.com/html/629151/"
            page.goto(url)

            # 等待section-list出现
            page.wait_for_selector('#section-list')

            # 获取section-list下的所有li元素
            li_elements = page.query_selector_all('#section-list > li')

         # 遍历每个li元素
            for li in li_elements:
                # 在每个li中获取所有的a元素
                a_elements = li.query_selector_all('a')

                # 遍历每个a元素并获取其href属性
                for a in a_elements:
                    href = a.get_attribute('href')
                    #print(href)  # 打印每个a元素的href属性值
                    detailPage = urljoin(url,href)
                    print(detailPage)
                    allDetailPages.append(detailPage)
            print(allDetailPages)
        except error as e:
            print(f"发生错误:{e}")
            sys.exit()
        # 关闭浏览器
        browser.close()
        return allDetailPages

def detailPage(allDetailPages,file_name):
    print("准备爬取详情页")
    tmpFile = "tmpUrl.txt"
    with sync_playwright() as p:
        for singlePage in allDetailPages:
            if check_string_in_file(tmpFile, singlePage):
                print(f"网址'{singlePage}' 在文件 {tmpFile} 中找到了。已忽略")
                continue
            else:
                print(f"网址'{singlePage}' 在文件 {tmpFile} 中没有找到。继续执行")
            # 使用fake_useragent库生成随机User-Agent
            ua = UserAgent()
            user_agent = ua.random
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_extra_http_headers({
                "User-Agent": user_agent,
                "Accept-Language": "en-US,en;q=0.9",
            })
            page.on("request", print_request_headers)
            page.on("response", handle_response)
            print("*"*100)
            print("当前爬取的网页为：%s" % singlePage)
            try:
                # 导航到目标网址
                page.goto(singlePage,timeout=60000)
                title_element = page.wait_for_selector('.title')
                title_text = title_element.text_content()
                # 检查并打印结果
                if check_string_in_file(file_name, title_text):
                    print(f"'{title_text}' 在文件 {file_name} 中找到了。已忽略")
                else:
                    print(f"'{title_text}' 在文件 {file_name} 中没有找到。,准备已写入")
                print(f"当前爬取的网页标题为： {title_text}")
                content = page.wait_for_selector('.content')
                content_text = content.text_content()
                pattern_to_remove = r'本页地址.*下一页继续阅读'
                singlePageContent = re.sub(r'&[\da-fA-F]{0,5}[;]?', '', content_text)
                # 使用replace方法将NBSP替换为普通空格
                singlePageContent = singlePageContent.replace('\u00A0', ' ')
                singlePageContent = re.sub(pattern_to_remove, '', singlePageContent)
                print(singlePageContent)
                # 打开文件以写入模式 ('w' 表示写入，如果文件已存在会被覆盖；'a' 表示追加，会在文件末尾添加内容)
                with open(file_name, 'a', encoding='utf-8') as file:
                    # 写入字符串内容
                    file.write(title_text)
                    file.write(singlePageContent + "\n")
                    file.close()
                with open(tmpFile, 'a', encoding='utf-8') as file:
                    file.write(singlePage + "\n")
                    file.close()
                sleep(6)
            except TimeoutError as e:
                print(f"发生错误:{e}")
                sys.exit()
        # 关闭浏览器
        browser.close()


if __name__=='__main__':
    # 文件名和路径
    file_name = "我在惊悚游戏里封神.txt"
    detailPage(indexPage(),file_name)
