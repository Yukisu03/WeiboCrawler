#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 23:23:47 2020

@author: Yokimsu
"""

#!/usr/bin/env python
# coding: utf-8

# In[7]:


# -*- coding: utf-8 -*-

import csv
from bs4 import BeautifulSoup
import time
import re
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
import datetime
import pandas as pd
import os

def spiderweibo(keywords,timepara,province,city,district,locpara,resultfile):
    # 设置浏览器自动登陆微博
    option = ChromeOptions()
    prefs = {'profile.default_content_setting_values': {'images': 2,'javascript': 1}}#禁止加载图片与JS
    option.add_experimental_option('prefs', prefs)
    #option.add_argument('--headless')#不显示浏览器窗口
    #options.headless = True
    #option.add_argument('--disable-gpu') #for windows not for macos
    option.add_argument(r"user-data-dir=/Users/Yokimsu/Library/Caches/Google/Chrome/User Data/Profile 1")  # 浏览器缓存位置
    browser = Chrome("/Users/YokimSu/chromedriver", 0, options=option)
    
    url0="https://s.weibo.com/weibo?q=" + keywords + locpara + "&typeall=1&suball=1&timescope=custom:" + timepara

    #browser.minimize_window()#最小化窗口
    browser.get(url0)
    time.sleep(3)
    
    soup = BeautifulSoup(browser.page_source, 'lxml')
    loginYN=""
    try:
        loginYN=soup.find('div', {'class': 'm-hint'}).find('a',{'action-type':'login'})
        loginYN="N"
        print("未登录，程序终止，请重新登录后在操作！")
    except:
        pass

    try:
        pagenum = len(soup.find('ul', {'class': 's-scroll'}).find_all('li'))
        #print(pagenum)
        print("-------------------------")
        print("总页数%d" %pagenum)
        # 如果等于50页，有可能超出微博显示数量，后期加上省份选项，重新爬取
        if pagenum == 50:
            with open('超过50页.csv', 'a', encoding='utf8', newline='') as f:
                current = time.time()
                current = time.localtime(current)
                timestr = "" + str(current.tm_year) + "/" + str(current.tm_mon) + "/" + str(current.tm_mday) + " " + str(current.tm_hour) + ":" + str(current.tm_min) + ":" + str(current.tm_sec)
                writer = csv.writer(f)
                writer.writerow((timestr,pagenum,url0,keywords,timepara,province,city,district,locpara))
    except:     # 只有一页是会报错
        pagenum = 1
        print("-------------------------")
        print("总页数%d" %pagenum)

    #判断是否有相关内容
    yn=""
    try:
        yn=soup.find('div',{'class':'card card-no-result s-pt20b40'}).find('p').get_text().strip()
        pagenum=1
        #此段是将没有搜索结果的参数也写入csv结果文件中，方便查看哪些字段信息搜索无结果
        """
        with open(resultfile, 'a', encoding='utf8', newline='') as f:
            current = time.time()
            current = time.localtime(current)
            timestr = "" + str(current.tm_year) + "/" + str(current.tm_mon) + "/" + str(current.tm_mday) + " " + str(current.tm_hour) + ":" + str(current.tm_min) + ":" + str(current.tm_sec)
            writer = csv.writer(f)
            writer.writerow((timestr, url0,timepara, province,city,district,yn,"", "","","", "", "", "",
                             "","","", "","","","","","","","","","",""))
        """
        print(url0+"----此页无结果！")
    except:
        yn=""
        if pagenum <= 50:
            for page in range(0, pagenum):
                try:
                    # 用浏览器打开微博话题页面
                    url=url0+"&Refer=g&page=" + str(page + 1)
                    browser.get(url)
                    #只有时间筛选项的url
                    """
                    browser.get(
                        "https://s.weibo.com/weibo?q=" + keywords + "&typeall=1&suball=1&timescope=custom:" + timepara
                        + "&Refer=g&page=" + str(page + 1))
                    """
                    time.sleep(1)
                    # 调到网页内容
                    browser.switch_to_default_content()
                    # 读取浏览器网页内容
                    soup = BeautifulSoup(browser.page_source, 'lxml')
                    # 每个用户的信息及评论存放在此列表里的每个元素里
                    allinfo = soup.find_all('div', {'class': 'card'})

                    for eachitem in allinfo:
                        if eachitem.find('a', {'class': 'name'}):
                            # 用户名信息
                            try:
                                username = eachitem.find('a', {'class': 'name'}).get_text().strip()  # username
                            except:
                                username = "None"

                            # 用户主页
                            try:
                                userlink = "https://www." + eachitem.find('a', {'class': 'name'}).get('href').replace("/member/","").replace("//","").strip()  # 用户主页
                            except:
                                userlink = ("None")
                            # 微博内容
                            try:
                                contents = eachitem.find('p', {'class': 'txt'}).get_text().strip()  # 微博内容
                            except:
                                contents = "None"
                            try:
                                location_temp=len(eachitem.find('p', {'class': 'txt'}).find_all('a'))
                            except:
                                location_temp=1
                            try:
                                location = eachitem.find('p', {'class': 'txt'}).find_all('a')[location_temp-1].get_text().replace("2","").strip()  # 定位
                                location_link=eachitem.find('p', {'class': 'txt'}).find_all('a')[location_temp-1].get('href').strip()  # 定位
                            except:
                                location = "None"
                                location_link="None"
                            #print(location,location_link)
                            # 判断转发来源,此段暂时不需要
                            """
                            try:
                                pattern = re.compile(r'//@.*?:', re.I)
                                resulttemp = pattern.findall(contents)
                                source = resulttemp[0]
                                source = source.replace("//@", "").replace(":", "")
                                #print(source)
                            except:
                                source = "None"
                            if source == "None":
                                try:
                                    source = eachitem.find('div', {'class': 'card-comment'}).find('div', {
                                        'node-type': 'feed_list_forwardContent'}).find('a').get_text().strip()  # 转发来源
                                except:
                                    pass
                            """
                            # 发表时间
                            try:
                                tempnum=len(eachitem.find_all('p', {'class': 'from'}))
                            except:
                                tempnum=1
                            if tempnum>1:
                                try:
                                    post_date = eachitem.find_all('p', {'class': 'from'})[1].find_all("a")[0].get_text().strip()  # 时间
                                    contents_link = "https://www."+eachitem.find_all('p', {'class': 'from'})[1].find_all("a")[0].get('href').strip().replace("//","")
                                    try:
                                        post_date_date=post_date.split(" ",1 )[0].replace("年","/").replace("月","/").replace("日","")
                                        post_date_time=post_date.split(" ",1 )[1]
                                    except:
                                        post_date_date="None"
                                        post_date_time="None"
                                except:
                                    post_date = "None"
                                    contents_link="None"
                                    post_date_date="None"
                                    post_date_time="None"
                            else:
                                try:
                                    post_date = eachitem.find_all('p', {'class': 'from'})[0].find_all("a")[0].get_text().strip()  # 时间
                                    contents_link = "https://www."+eachitem.find_all('p', {'class': 'from'})[0].find_all("a")[0].get('href').strip().replace("//","")
                                    try:
                                        post_date_date=post_date.split(" ",1 )[0].replace("年","/").replace("月","/").replace("日","")
                                        post_date_time=post_date.split(" ",1 )[1]
                                    except:
                                        post_date_date="None"
                                        post_date_time="None"
                                except:
                                    post_date = "None"
                                    contents_link="None"
                                    post_date_date="None"
                                    post_date_time="None"

                            if post_date.find("今天")>-1:
                                continue
                            # 发布来源
                            try:
                                pingtai = "【来自】" + eachitem.find('p', {'class': 'from'}).find_all("a")[1].get_text().strip()  # 来自
                            except:
                                pingtai = "None"

                            # 收藏数
                            try:
                                favorite_num = eachitem.find('div', {'class': 'card-act'}).find_all("a")[0].get_text().replace("收藏","").strip()
                            except:
                                favorite_num = "None"
                            # 转发数
                            try:
                                repost_num = eachitem.find('div', {'class': 'card-act'}).find_all("a")[1].get_text().replace("转发","").strip()
                            except:
                                repost_num = "None"
                            # 评论数
                            try:
                                comments_num = eachitem.find('div', {'class': 'card-act'}).find_all("a")[2].get_text().replace("评论","").strip()
                            except:
                                comments_num = "None"
                            # 点赞数
                            try:
                                reward_num = eachitem.find('div', {'class': 'card-act'}).find_all("a")[3].get_text().strip()
                            except:
                                reward_num = "None"

                            #解析转发的原微博内容
                            try:
                                username2=eachitem.find('div',{'class':'card-comment'}).find('a').get('nick-name').strip()#用户名
                            except:
                                username2="None"
                            try:
                                userlink2="https://www."+eachitem.find('div',{'class':'card-comment'}).find('a').get('href').strip().replace("//","")#用户主页链接
                            except:
                                userlink2="None"
                            #print(username2,userlink2)
                            try:
                                contents2=eachitem.find('div',{'class':'card-comment'}).find('p',{'class':'txt'}).get_text().strip()#微博内容
                            except:
                                contents2="None"
                            try:
                                post_date2=eachitem.find('div',{'class':'card-comment'}).find('p', {'class': 'from'}).find_all("a")[0].get_text().strip() #发布时间
                            except:
                                post_date2="None"
                            try:
                                contents2_link = "https://www."+eachitem.find('div',{'class':'card-comment'}).find('p', {'class': 'from'}).find_all("a")[0].get('href').strip().replace("//","")
                            except:
                                contents2_link="None"
                            try:
                                pingtai2 = "【来自】" + eachitem.find('div',{'class':'card-comment'}).find('p', {'class': 'from'}).find_all("a")[1].get_text().strip()  # 来自
                            except:
                                pingtai2="None"
                            try:
                                tempinfo2=eachitem.find('div',{'class':'card-comment'}).find('div',{'class':'func'}).find('ul',{'class':'act s-fr'}).find_all('li')
                            except:
                                tempinfo2="None"
                            try:
                                repost_num2=tempinfo2[0].get_text().replace("转发","").strip()
                            except:
                                repost_num2="None"
                            try:
                                comments_num2=tempinfo2[1].get_text().replace("评论","").strip()
                            except:
                                comments_num2="None"
                            try:
                                reward_num2=tempinfo2[2].get_text().strip()
                            except:
                                reward_num2="None"

                            with open(resultfile, 'a', encoding='utf8', newline='') as f:
                                current = time.time()
                                current = time.localtime(current)
                                timestr = "" + str(current.tm_year) + "/" + str(current.tm_mon) + "/" + str(current.tm_mday) + " " + str(current.tm_hour) + ":" + str(current.tm_min) + ":" + str(current.tm_sec)
                                writer = csv.writer(f)
                                writer.writerow((timestr, url,timepara, province,city,district,yn,username, userlink, contents,location,location_link, post_date,post_date_date,post_date_time,pingtai,
                                                 favorite_num, repost_num,comments_num, reward_num,contents_link,username2,userlink2,contents2,post_date2,pingtai2,repost_num2,comments_num2,reward_num2,contents2_link))


                except Exception as e:
                    print("error", str(e))
                print("----------")
                #print(page+1,pagenum,timepara)
                print("第%d/%d页爬取完成！时间参数：%s" % ((page + 1),pagenum,timepara))

               
    browser.quit()
    return loginYN


if __name__ == '__main__':
    time_start = time.time()# 计时开始
    resultfile='COVID-19 weibo_9 Feb.csv'
    if os.path.exists(resultfile):
        df=pd.read_csv(resultfile,header=None)
        temp=df.iloc[0,0]
        #print(temp)
        if temp!="爬取时间":
            with open(resultfile, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(("爬取时间","搜索地址","搜索时间参数", "省","市","地区","搜索结果","用户名", "用户主页链接","微博内容","微博定位","定位地址链接","发布日期","发布日期1","发布日期2", "发布渠道",
                                 "收藏数", "转发数","评论数","点赞数","微博原文链接","转发微博原文用户名","转发微博原文用户主页链接","转发微博原文内容","转发微博原文发布日期","转发微博原文发布渠道","转发微博原文转发数","转发微博原文评论数","转发微博原文点赞数","转发微博原文链接"))
    else:
        with open(resultfile, 'a', encoding='utf8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(("爬取时间","搜索地址","搜索时间参数", "省","市","地区","搜索结果","用户名", "用户主页链接","微博内容","微博定位","定位地址链接","发布日期","发布日期1","发布日期2", "发布渠道",
                                 "收藏数", "转发数","评论数","点赞数","微博原文链接","转发微博原文用户名","转发微博原文用户主页链接","转发微博原文内容","转发微博原文发布日期","转发微博原文发布渠道","转发微博原文转发数","转发微博原文评论数","转发微博原文点赞数","转发微博原文链接"))
    
    
    province_list = ["11", "50", "35", "62", "31", "44", "45", "52", "46", "13", "23", "41", "42", "43", "15", "32", "36", "22", "21", "64", "63", "14", "37", "31", "51", "12", "54", "65", "53", "33", "61", "71", "81", "82", "400", "100"]
    
    for province in province_list:
        locpara = "&region=custom:"+province+":1000"
        keywords = "肺炎" 
        province=""
        city=""
        district=""
       
        d1 = datetime.datetime(2020, 2, 9, 0)         # 开始时间
        d2 = datetime.datetime(2020, 2, 10, 0)         # 结束时间

        td = d2 - d1
        hours = int(td.days * 24 + td.seconds / 3600)
        end = (str(d1)[0:13])
        
        for i in range(hours):
            temp = d1 + datetime.timedelta(hours = i + 1)
            start = end
            end = str(temp)[0:13]

            # 每次检索一个小时的内容 时间设置
            # 开始时间
            startdate = str(start[0:10])
            starttime = str(start[11:13])
            # 结束时间
            enddate = str(end[0:10])
            endtime = str(end[11:13])
            timepara = startdate + "-" + starttime + ":" + enddate + "-" + endtime

            # 记录当前时间
            current = time.time()
            current = time.localtime(current)
            # 文件名后加上确切当前时间避免重名
            filestr = "_" + str(current.tm_year) + "-" + str(current.tm_mon) + "-" + str(current.tm_mday) + "_" + str(
                        current.tm_hour) + "-" + str(current.tm_min) + "-" + str(current.tm_sec)
            loginYN=spiderweibo(keywords,timepara,province,city,district,locpara,resultfile)
            url0 = "https://s.weibo.com/weibo?q=" + keywords + locpara + "&typeall=1&suball=1&timescope=custom:" + timepara
            #print(loginYN)
            if loginYN=="N":
                print("未登录，程序终止，请重新登录后操作！")
                print(url0)
                break
            

    time_end = time.time()# 计时结束
    print("数据爬取并已保存！耗时%d秒！" % (time_end - time_start))# 打印爬取总耗时
    





