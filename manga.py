import requests
import time
from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import pyautogui


url = "https://www.manhuazhan.com/category/list/2"
headers ={'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                    "refer":"https://www.manhuazhan.com"
}

try:
    n = 0
    page_n = 1
    #获取用户输入的漫画名称
    name = input("请输入漫画名称（可输入关键字，但顺序一定要正确）：")
    found = False #添加变量用于检测是否找到匹配的漫画
    for i in range(50): #可获取前50页的所有漫画
        i = i+1
        url = "https://www.manhuazhan.com/category/list/2"+'/page'+'/'+str(page_n)
        page_n += 1
        resp = requests.get(url, headers=headers)
        main_page = BeautifulSoup(resp.text, 'html.parser')
        main_page.encode('utf-8')
        a_tags = main_page.find("div", attrs={"class": "d-item-list clearfix"}).find_all("a")
        print("正在查询页面：",url)
        #遍历所有的a标签，检查是否有匹配的漫画名称
        for tag in a_tags:  #tag是a标签
            if name in tag['title']:       #判断漫画名是否称在a标签的文本中
                print("找到了匹配的漫画：", tag['title'])
                found = True #标记找到匹配的漫画
                break #跳出内循环
            else:
                n=n+1
        if found: #找到匹配的漫画，跳出外循环
            break
    if not found: 
        print("未找到匹配的漫画  break♫ ♫ ♫")
        exit()    
except requests.exceptions.RequestException as e:
    print(f"请求主页时出错：{e}")
    exit()


url_child = "https://www.manhuazhan.com" + tag['href']
print(url_child)
folder_path1 = 'E:/crawler/test/'+tag['title']

#创建文件夹以保存漫画
# 检查文件夹是否存在
if not os.path.exists(folder_path1):
    # 如果文件夹不存在，则创建文件夹
    os.makedirs(folder_path1)
    print(f"文件夹 {folder_path1} 创建成功。")
else:
    print(f"文件夹 {folder_path1} 已存在。")
#请求漫画所在的子页面
try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            drive = webdriver.Chrome(options =options)
            drive.get(url_child)
            child_response = drive.page_source
            child_response.encode('utf-8')
            child_page = BeautifulSoup(child_response, 'html.parser')
            child_page.encode('utf-8')
            drive.quit()
            print("请求子页面成功")
except requests.exceptions.RequestException as e:
            print(f"请求子页面时出错：{e}")
            exit()
#获得漫画所有章节的a标签
chapter_a= child_page.find("div", attrs={"class": "d-player-list clearfix looplist"}).find_all("a")
all_chapter = len(chapter_a)
print("总章节数：",all_chapter)
start_chapter = int(input("请输入要开始爬取的章节："))
end_chapter = int(input("请输入要结束爬取的章节："))
start_chapter = start_chapter - 1
j = end_chapter - start_chapter
i = -1      #这里的i为计数器，用来控制循环次数
folder_path = 'E:/crawler/test'+'/'+tag['title']
for i in range(j):
    i = i+1
    start_chapter = start_chapter + 1
    folder_name= chapter_a[start_chapter-1].string
    chapter_href = "https://www.manhuazhan.com/"+ chapter_a[start_chapter-1].get("href") #获取章节链接
    print("这是chapter_href：",chapter_href)
    folder_path = os.path.join(f'E:/crawler/test'+'/'+tag['title']+'/'+ f'{folder_name}')#创建文件夹以保存章节漫画
    try:
        os.makedirs(folder_path, exist_ok=True)
        print(f"文件夹 '{folder_path}' 创建成功。")
    except OSError as error:    
        print(f"创建文件夹失败: {error}")
        exit()
    # 最大化窗口启动
    options2 = webdriver.ChromeOptions()
    options2.add_argument('--headless')
    options2.add_argument('--disable-gpu')
    #启动浏览器滚动获取所有图片
    drive2 = webdriver.Chrome(options = options2)
    drive2.get(chapter_href)
    last_height = drive2.execute_script("return document.body.scrollHeight")
    #循环滚动，直到到达页面底部为止
    while True:
        #滚动到页面底部
        drive2.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #等待一段时间，让页面有机会加载新内容
        drive2.implicitly_wait(10)  # 等待最多10秒
        #计算新的页面高度
        new_height = drive2.execute_script("return document.body.scrollHeight")
        #如果页面高度没有变化，说明没有加载新内容，退出循环
        if new_height == last_height:
            break
         # 更新页面高度
        last_height = new_height
    #获取图片链接
    chapter_href_response=drive2.page_source
    chapter_href_response.encode('utf-8')
    chapter_href_response = BeautifulSoup(chapter_href_response, 'html.parser')
    chapter_img= chapter_href_response.find_all('img',attrs={"class": "lazy"})
    drive.quit()  #关闭浏览器
  
    jpg  = str("jpg")
    #下载图片
    max_attempts = 3  # 设置最大尝试次数
    attempts = 0     # 初始化尝试次数
    download_count = 0  # 成功下载图片的计数器
    if chapter_img:
        while attempts < max_attempts and download_count < len(chapter_img):
            try:
                for chapter_img_src in chapter_img:
                    if jpg in chapter_img_src['src']: 
                        chapter_img_src = chapter_img_src['src']  #获取图片url
                        content = requests.get(chapter_img_src).content
                        file_path=os.path.join(folder_path, chapter_img_src.split('/')[-1])
                        download_count += 1
                        #保存图片
                        with open(file_path, "wb") as f: 
                            f.write(content)
                            print(f"图片已保存到：{file_path}")
            except Exception as e:
                print("爬取失败！原因为：",e)
                attempts += 1
                print("正在重试...\n")
                print("重试次数:", attempts)
                if attempts == max_attempts:
                    print("已达到最大尝试次数，退出循环。该错误话数为：",folder_path[folder_name])
        else:
            print("本章节下载完成")
    if i==j:
        print("全部下载完成")
    else:
        left_chapter = j-i
        print(f"剩余{left_chapter}章节未下载")
