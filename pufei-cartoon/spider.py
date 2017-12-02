#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from contextlib import closing
from bs4 import BeautifulSoup
import requests, json, time, re, os, sys, types
from datetime import datetime
from common import utils
import execjs

class Spider(object):
   
    HEADERS = {
        "Origin": "http://www.pufei.net",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0_2 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A421 Safari/604.1",
        "Referer": "http://www.pufei.net",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
    }   
    regex = re.compile(r'[\s\S]*cp="([^"]+)"');
    chapter_id_regx= re.compile(r'[\s\S]*\/(\d+)\.html');


    def __init__(self):
        pass
    
    def get_chapter_list(self,book_id):
        chapter_list_page_url = 'http://www.pufei.net/manhua/%s/' %(book_id);
        response = requests.get(chapter_list_page_url,headers=self.HEADERS);
        response.encoding='gb2312'
        #print(response.content);
        soup = BeautifulSoup(response.text,"html.parser");
        links = soup.select('.plist li a');
        result=[]
        for link in links[::-1]:
           href=link['href'];
           chapter_id = self.chapter_id_regx.search(href).group(1);
           result.append((chapter_id,link['title'],link['href']))
        return result

    def read_chapter_list_from_disk(self,book_id):
        file = os.path.abspath(os.curdir)+"/data/"+book_id+"/chapters.txt";
        result=[];
        if os.path.exists(file)==False:
            return result;
        with open(file) as f:
            for chapter in f:
                result.append(tuple(chapter.split(",")));
        return result;
    
    def do_process(self,book_id,chapters):
        progress = 0;
        length = len(chapters);
        for chapter in chapters:
            self.do_process_sigle_chapter(book_id,chapter)
            progress = progress+1;
            print("Progress:%s/%s name=%s"%(progress,length,chapter[1]))
         
    def do_process_sigle_chapter(self,book_id,chapter):
        chapter_url = 'http://m.pufei.net'+chapter[2];
        repsonse = requests.get(chapter_url,headers=self.HEADERS);
        repsonse.encoding='gb2312'
        # print(repsonse.text);
        ma = self.regex.match(repsonse.text);
        if ma:
            data = self.decrypt_img_data(ma.group(1));
            result={
                "book_id":book_id,
                "chapter_id":chapter[0],
                "chapter_name":chapter[1],
                "chapter_url":chapter[2],
                "pictures":data,
                "count":len(data)
             }
            self.save_result(result)
        else:
            print('process chapter[id=%s],url=%s fail!'%(chapter[0],chapter_url));

    
     
    def save_result(self,result):
        #保存结果 和 章节列表
        dataPath = os.path.abspath(os.curdir)+"/data/"+result['book_id']+"/"+result['chapter_id'];
        if os.path.exists(dataPath)==False:
            os.makedirs(dataPath);
        file = dataPath+"/chapter_info.json"
        with open(file,"w+") as f:
            f.write(json.dumps(result))
        file = os.path.abspath(os.curdir)+"/data/"+result['book_id']+"/chapters.txt";
        with open(file,"a+") as f:
            chapter_info = "%s,%s,%s\n" %(result["chapter_id"],result["chapter_name"],result["chapter_url"])
            f.write(chapter_info);

    # http://pf.yueri.net/
    def decrypt_img_data(self,base64str):
        script = utils.base64Decode(base64str)
        return execjs.eval(script);

    def save_chapters(self,book_id,book_name,chapters):
        data = []
        for chapther in chapters:
            data.append({
                "chapter_id":chapther[0],
                "chapter_name":chapther[1]
            })
        last = len(data)-1;
        data[last]["is_new"]=True;
        file = os.path.abspath(os.curdir)+"/data/"+str(book_id)+"/chapters.json";
        result={
            "book_id":book_id,
            "book_name":book_name,
            "chapters":data[::-1]
        };
        with open(file,"w+") as f:
            f.write(json.dumps(result))


    def update_time(self,book_id):
       file = os.path.abspath(os.curdir)+"/data/books.json";
       with open(file) as f:
            books = json.load(f);
            for book in books:
                if book['book_id']==book_id:
                    book['update_time'] = int(round(time.time() * 1000));
       with open(file,"w+") as f:
            f.write(json.dumps(books))


    def run(self,book_id,book_name):
        chapters = self.get_chapter_list(book_id);
        length = len(chapters);
        if length>0 :
            disk_chapters = self.read_chapter_list_from_disk(book_id);
            disk_chapters_len = len(disk_chapters);
            if length > disk_chapters_len:
                d1 = {};
                for c1 in chapters:
                    d1[c1[0]]=c1;

                for c2 in disk_chapters:
                    del d1[c2[0]];
                    
                self.do_process(book_id,d1.values());
                self.save_chapters(book_id,book_name,chapters);
                self.update_time(book_id);
            else:
                print("There is not any update of  book[id=%s] "% (book_id));
        else:
             print("There is not chapters for the book which id=",book_id); 
    

if __name__ == '__main__':
    spider = Spider();
    # print(spider.get_chapter_list(292));
    # spider.do_process_sigle_chapter('292',('91843','第二百八十四章', '/manhua/292/91843.html'))
    spider.run("292","\u4ece\u524d\u6709\u5ea7\u7075\u5251\u5c71");
    #spider.get_chapter_list(292)
    #spider.update_time(292);
