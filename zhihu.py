import os
import re
import sys
import json
import time
import random
import pickle
from attr import has
import requests
import platform
import termcolor
import html2text
from bs4 import BeautifulSoup

# --- #

header = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
}

# --- #

class Obj:
    def properties(self, name, cmd):
        if not hasattr(self, f'__{name}'):
            value = eval(cmd)
            setattr(self, f'__{name}', value)
        else:
            value = getattr(self, f'__{name}')
        
        return value

class User(Obj):
    def __init__(self, id = None):
        if id == None:
            self.id = None # Anonymous User
        else:
            matchobj = re.compile('www.zhihu.com/people/([^/]*)/?').search(id)
            if matchobj:
                self.id = matchobj.group(1)
            else:    
                matchobj = re.compile('^[^/]*$').search(id)
                if matchobj:
                    self.id = matchobj.group()
                else:
                    raise ValueError(f'{termcolor.colored("ERROR", "red")}: unrecognized id for User: {id}')

        self.url = f'https://www.zhihu.com/people/{self.id}'

    def __bool__(self):
        return self.id != None
    
    @property
    def soup(self):
        return self.properties(__name__, "BeautifulSoup(requests.get(self.url, headers = header).content, 'lxml')")
    
    # --- #

    # meta

    @property
    def gender(self):
        return self.properties(__name__, "self.soup.find('meta', itemprop = 'gender')['content']")
    @property
    def avatar_url(self):
        return self.properties(__name__, "self.soup.find('meta', itemprop = 'image')['content']")
    @property
    def voteupCount(self):
        return self.properties(__name__, "int(self.soup.find('meta', itemprop = 'zhihu:voteupCount')['content'])")
    @property
    def thankedCount(self):
        return self.properties(__name__, "int(self.soup.find('meta', itemprop = 'zhihu:thankedCount')['content'])")
    @property
    def followerCount(self):
        return self.properties(__name__, "int(self.soup.find('meta', itemprop = 'zhihu:followerCount')['content'])")
    @property
    def answerCount(self):
        return self.properties(__name__, "int(self.soup.find('meta', itemprop = 'zhihu:answerCount')['content'])")
    @property
    def articleCount(self):
        return self.properties(__name__, "int(self.soup.find('meta', itemprop = 'zhihu:articlesCount')['content'])")

    # --- #

    # ProfileHeader

    @property
    def name(self):
        return self.properties(__name__, "self.soup.find('span', class_='ProfileHeader-name').text")
    @property
    def intro(self):
        return self.properties(__name__, "self.soup.find('span', class_='ztext ProfileHeader-headline').text")

    # --- #

    # Profile-sideColumn - achievement

    @property
    def collectedCount(self):
        if not hasattr(self, 'collectedCount'):
            matchobj = re.compile('(\d*) 次收藏').search(self.soup.find('div', class_ = 'Profile-sideColumn').text)
            setattr(self, 'collectedCount', matchobj.group(1) if matchobj else None)
        return getattr(self, 'collectedCount')
    @property
    def editCount(self):
        if not hasattr(self, 'editCount'):
            matchobj = re.compile('(\d*) 次公共编辑').search(self.soup.find('div', class_ = 'Profile-sideColumn').text)
            setattr(self, 'editCount', matchobj.group(1) if matchobj else None)
        return getattr(self, 'editCount')
    
    # --- #

    # Profile-sideColumn - FollowshipCard
    
    @property
    def followingCount(self):
        return self.properties(__name__, "self.soup.find('div', class_ = 'Card FollowshipCard').find_all('strong')[0]['title']")

    # --- #

    # Profile-sideColumn - Profile-lightList

    @property
    def followingtopicsCount(self):
        return self.properties(__name__, "int(self.soup.find('div', class_ = 'Profile-lightList').find_all('span', 'Profile-lightItemValue')[0].text)")
    @property
    def followingcolumnsCount(self):
        return self.properties(__name__, "int(self.soup.find('div', class_ = 'Profile-lightList').find_all('span', 'Profile-lightItemValue')[0].text)")
    @property
    def followingquestionsCount(self):
        return self.properties(__name__, "int(self.soup.find('div', class_ = 'Profile-lightList').find_all('span', 'Profile-lightItemValue')[0].text)")
    @property
    def followingcollectionsCount(self):
        return self.properties(__name__, "int(self.soup.find('div', class_ = 'Profile-lightList').find_all('span', 'Profile-lightItemValue')[0].text)")

    # --- #

    # Profile-mainColumn - ProfileMain-header

    @property
    def videoCount(self):
        return self.properties(__name__, "int(self.soup.find('div', class_ = 'Profile-mainColumn').find('ul', class_ = 'Tabs ProfileMain-tabs').find_all('span')[1].text)")
    @property
    def askCount(self):
        return self.properties(__name__, "int(self.soup.find('div', class_ = 'Profile-mainColumn').find('ul', class_ = 'Tabs ProfileMain-tabs').find_all('span')[2].text)")
    @property
    def columnCount(self):
        return self.properties(__name__, "int(self.soup.find('div', class_ = 'Profile-mainColumn').find('ul', class_ = 'Tabs ProfileMain-tabs').find_all('span')[4].text)")
    @property
    def pinCount(self):
        return self.properties(__name__, "int(self.soup.find('div', class_ = 'Profile-mainColumn').find('ul', class_ = 'Tabs ProfileMain-tabs').find_all('span')[5].text)")
    @property
    def favlistCount(self):
        return self.properties(__name__, "int(self.soup.find('div', class_ = 'Profile-mainColumn').find('ul', class_ = 'Tabs ProfileMain-tabs').find_all('span')[6].text)")

class Question(Obj):
    def __init__(self, id):
        # https://www.zhihu.com/question/546178692
        matchobj = re.compile('www.zhihu.com/question/(\d*)/?').search(id)
        if matchobj:
            self.id = matchobj.group(1)
        else:    
            matchobj = re.compile('^\d*$').search(id)
            if matchobj:
                self.id = matchobj.group()
            else:
                raise ValueError(f'{termcolor.colored("ERROR", "red")}: unrecognized id for Question: {id}')

        self.url = f'https://www.zhihu.com/question/{self.id}'

    @property
    def soup(self):
        return self.properties(__name__, "BeautifulSoup(requests.get(self.url, headers = header).content, 'lxml')")
    
    # --- #

    # meta

    @property
    def title(self):
        return self.properties(__name__, "self.soup.find('meta', itemprop = 'name')['content']")
    @property
    def answerCount(self):
        return self.properties(__name__, "self.soup.find('meta', itemprop = 'answerCount')['content']")
    @property
    def commentCount(self):
        return self.properties(__name__, "self.soup.find('meta', itemprop = 'commentCount')['content']")
    @property
    def dateCreated(self):
        return self.properties(__name__, "self.soup.find('meta', itemprop = 'dateCreated')['content']")
    @property
    def dateCreated(self):
        return self.properties(__name__, "self.soup.find('meta', itemprop = 'dateCreated')['content']")
    @property
    def followerCount(self):
        return self.properties(__name__, "self.soup.find('meta', itemprop = 'zhihu:followerCount')['content']")

    # --- #

    # data-zop-question

    @property
    def topics(self):
        if not hasattr(self, '__topics'):
            topics = json.loads(self.soup.find('div', class_ = 'QuestionPage').find('div')['data-zop-question'])['topics']
            topics = [[t['name'], int(t['id'])] for t in topics]
            setattr(self, '__topics', topics)
        return getattr(self, '__topics')

    # --- #

    # js-initialData
    
    @property
    def detail(self):
        if not hasattr(self, '__detail'):
            detail = json.loads(self.soup.find('script', id = 'js-initialData').text)['initialState']['entities']['questions'][self.id]['detail']
            
            detail = detail[3:-4]
            detail = re.compile('</p><p>').sub('\n', detail)
            
            # convert math expressions into tex style
            imgs = [img.group() for img in re.compile('<img.*?/>').finditer(detail)]
            exps = ['$' + re.compile('alt="(.*?)"').search(img).group(1) + '$' for img in imgs]
            for img, exp in zip(imgs, exps):
                detail = detail.replace(img, exp)

            setattr(self, '__detail', detail)
        return getattr(self, '__detail')

    # --- #

    def answeriter(self):
        url = f'https://www.zhihu.com/api/v4/questions/{self.id}/feeds?&limit=5&offset=0&order=default&platform=desktop'
        while True:
            data = json.loads(requests.get(url, headers = header).text)
            
            for answerid in [d['target']['id'] for d in data['data']]:
                yield answerid
            
            if data['paging']['is_end']:
                return

            url = data['paging']['next']

# class Answer:
#     answer_url = None
#     # session = None
#     soup = None

#     def __init__(self, answer_url, question=None, author=None, upvote=None, content=None):

#         self.answer_url = answer_url
#         if question != None:
#             self.question = question
#         if author != None:
#             self.author = author
#         if upvote != None:
#             self.upvote = upvote
#         if content != None:
#             self.content = content

#     def parser(self):
#         headers = {
#             'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
#             'Host': "www.zhihu.com",
#             'Origin': "http://www.zhihu.com",
#             'Pragma': "no-cache",
#             'Referer': "http://www.zhihu.com/"
#         }
#         r = requests.get(self.answer_url, headers=headers, verify=False)
#         soup = BeautifulSoup(r.content, "lxml")
#         self.soup = soup

#     def get_question(self):
#         if hasattr(self, "question"):
#             return self.question
#         else:
#             if self.soup == None:
#                 self.parser()
#             soup = self.soup
#             question_link = soup.find("h2", class_="zm-item-title zm-editable-content").a
#             url = "http://www.zhihu.com" + question_link["href"]
#             title = question_link.string.encode("utf-8")
#             question = Question(url, title)
#             return question

#     def get_author(self):
#         if hasattr(self, "author"):
#             return self.author
#         else:
#             if self.soup == None:
#                 self.parser()
#             soup = self.soup
#             if soup.find("div", class_="zm-item-answer-author-info").get_text(strip='\n') == u"匿名用户":
#                 author_url = None
#                 author = User(author_url)
#             else:
#                 author_tag = soup.find("div", class_="zm-item-answer-author-info").find_all("a")[1]
#                 author_id = author_tag.string.encode("utf-8")
#                 author_url = "http://www.zhihu.com" + author_tag["href"]
#                 author = User(author_url, author_id)
#             return author

#     def get_upvote(self):
#         if hasattr(self, "upvote"):
#             return self.upvote
#         else:
#             if self.soup == None:
#                 self.parser()
#             soup = self.soup
#             count = soup.find("span", class_="count").string
#             if count[-1] == "K":
#                 upvote = int(count[0:(len(count) - 1)]) * 1000
#             elif count[-1] == "W":
#                 upvote = int(count[0:(len(count) - 1)]) * 10000
#             else:
#                 upvote = int(count)
#             return upvote

#     def get_content(self):
#         if hasattr(self, "content"):
#             return self.content
#         else:
#             if self.soup == None:
#                 self.parser()
#             soup = BeautifulSoup(self.soup.encode("utf-8"), "lxml")
#             answer = soup.find("div", class_="zm-editable-content clearfix")
#             soup.body.extract()
#             soup.head.insert_after(soup.new_tag("body", **{'class': 'zhi'}))
#             soup.body.append(answer)
#             img_list = soup.find_all("img", class_="content_image lazy")
#             for img in img_list:
#                 img["src"] = img["data-actualsrc"]
#             img_list = soup.find_all("img", class_="origin_image zh-lightbox-thumb lazy")
#             for img in img_list:
#                 img["src"] = img["data-actualsrc"]
#             noscript_list = soup.find_all("noscript")
#             for noscript in noscript_list:
#                 noscript.extract()
#             content = soup
#             self.content = content
#             return content

#     def to_txt(self):

#         content = self.get_content()
#         body = content.find("body")
#         br_list = body.find_all("br")
#         for br in br_list:
#             br.insert_after(content.new_string("\n"))
#         li_list = body.find_all("li")
#         for li in li_list:
#             li.insert_before(content.new_string("\n"))

#         if platform.system() == 'Windows':
#             anon_user_id = "匿名用户".decode('utf-8').encode('gbk')
#         else:
#             anon_user_id = "匿名用户"
#         if self.get_author().get_user_id() == anon_user_id:
#             if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "text"))):
#                 os.makedirs(os.path.join(os.path.join(os.getcwd(), "text")))
#             if platform.system() == 'Windows':
#                 file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt".decode(
#                     'utf-8').encode('gbk')
#             else:
#                 file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt"
#             print file_name
#             # if platform.system() == 'Windows':
#             # file_name = file_name.decode('utf-8').encode('gbk')
#             # print file_name
#             # else:
#             # print file_name
#             file_name = file_name.replace("/", "'SLASH'")
#             if os.path.exists(os.path.join(os.path.join(os.getcwd(), "text"), file_name)):
#                 f = open(os.path.join(os.path.join(os.getcwd(), "text"), file_name), "a")
#                 f.write("\n\n")
#             else:
#                 f = open(os.path.join(os.path.join(os.getcwd(), "text"), file_name), "a")
#                 f.write(self.get_question().get_title() + "\n\n")
#         else:
#             if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "text"))):
#                 os.makedirs(os.path.join(os.path.join(os.getcwd(), "text")))
#             if platform.system() == 'Windows':
#                 file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt".decode(
#                     'utf-8').encode('gbk')
#             else:
#                 file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt"
#             print file_name
#             # if platform.system() == 'Windows':
#             # file_name = file_name.decode('utf-8').encode('gbk')
#             # print file_name
#             # else:
#             # print file_name
#             file_name = file_name.replace("/", "'SLASH'")
#             f = open(os.path.join(os.path.join(os.getcwd(), "text"), file_name), "wt")
#             f.write(self.get_question().get_title() + "\n\n")
#         if platform.system() == 'Windows':
#             f.write("作者: ".decode('utf-8').encode('gbk') + self.get_author().get_user_id() + "  赞同: ".decode(
#                 'utf-8').encode('gbk') + str(self.get_upvote()) + "\n\n")
#             f.write(body.get_text().encode("gbk"))
#             link_str = "原链接: ".decode('utf-8').encode('gbk')
#             f.write("\n" + link_str + self.answer_url.decode('utf-8').encode('gbk'))
#         else:
#             f.write("作者: " + self.get_author().get_user_id() + "  赞同: " + str(self.get_upvote()) + "\n\n")
#             f.write(body.get_text().encode("utf-8"))
#             f.write("\n" + "原链接: " + self.answer_url)
#         f.close()

#     # def to_html(self):
#     # content = self.get_content()
#     # if self.get_author().get_user_id() == "匿名用户":
#     # file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.html"
#     # f = open(file_name, "wt")
#     # print file_name
#     # else:
#     # file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.html"
#     # f = open(file_name, "wt")
#     # print file_name
#     # f.write(str(content))
#     # f.close()

#     def to_md(self):
#         content = self.get_content()
#         if platform.system() == 'Windows':
#             anon_user_id = "匿名用户".decode('utf-8').encode('gbk')
#         else:
#             anon_user_id = "匿名用户"
#         if self.get_author().get_user_id() == anon_user_id:
#             if platform.system() == 'Windows':
#                 file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md".decode(
#                     'utf-8').encode('gbk')
#             else:
#                 file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md"
#             print file_name
#             # if platform.system() == 'Windows':
#             # file_name = file_name.decode('utf-8').encode('gbk')
#             # print file_name
#             # else:
#             # print file_name
#             file_name = file_name.replace("/", "'SLASH'")
#             if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "markdown"))):
#                 os.makedirs(os.path.join(os.path.join(os.getcwd(), "markdown")))
#             if os.path.exists(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name)):
#                 f = open(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name), "a")
#                 f.write("\n")
#             else:
#                 f = open(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name), "a")
#                 f.write("# " + self.get_question().get_title() + "\n")
#         else:
#             if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "markdown"))):
#                 os.makedirs(os.path.join(os.path.join(os.getcwd(), "markdown")))
#             if platform.system() == 'Windows':
#                 file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md".decode(
#                     'utf-8').encode('gbk')
#             else:
#                 file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md"
#             print file_name
#             # file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md"
#             # if platform.system() == 'Windows':
#             # file_name = file_name.decode('utf-8').encode('gbk')
#             # print file_name
#             # else:
#             # print file_name
#             file_name = file_name.replace("/", "'SLASH'")
#             f = open(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name), "wt")
#             f.write("# " + self.get_question().get_title() + "\n")
#         if platform.system() == 'Windows':
#             f.write("### 作者: ".decode('utf-8').encode('gbk') + self.get_author().get_user_id() + "  赞同: ".decode(
#                 'utf-8').encode('gbk') + str(self.get_upvote()) + "\n")
#         else:
#             f.write("### 作者: " + self.get_author().get_user_id() + "  赞同: " + str(self.get_upvote()) + "\n")
#         text = html2text.html2text(content.decode('utf-8')).encode("utf-8")

#         r = re.findall(r'\*\*(.*?)\*\*', text)
#         for i in r:
#             if i != " ":
#                 text = text.replace(i, i.strip())

#         r = re.findall(r'_(.*)_', text)
#         for i in r:
#             if i != " ":
#                 text = text.replace(i, i.strip())

#         r = re.findall(r'!\[\]\((?:.*?)\)', text)
#         for i in r:
#             text = text.replace(i, i + "\n\n")

#         if platform.system() == 'Windows':
#             f.write(text.decode('utf-8').encode('gbk'))
#             link_str = "\n---\n#### 原链接: ".decode('utf-8').encode('gbk')
#             f.write(link_str + self.answer_url.decode('utf-8').encode('gbk'))
#         else:
#             f.write(text)
#             f.write("\n---\n#### 原链接: " + self.answer_url)
#         f.close()

#     def get_visit_times(self):
#         if self.soup == None:
#             self.parser()
#         soup = self.soup
#         for tag_p in soup.find_all("p"):
#             if "所属问题被浏览" in tag_p.contents[0].encode('utf-8'):
#                 return int(tag_p.contents[1].contents[0])

#     def get_voters(self):
#         if self.soup == None:
#             self.parser()
#         soup = self.soup
#         data_aid = soup.find("div", class_="zm-item-answer  zm-item-expanded")["data-aid"]
#         request_url = 'http://www.zhihu.com/node/AnswerFullVoteInfoV2'
#         # if session == None:
#         #     create_session()
#         # s = session
#         # r = s.get(request_url, params={"params": "{\"answer_id\":\"%d\"}" % int(data_aid)})
#         headers = {
#             'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
#             'Host': "www.zhihu.com",
#             'Origin': "http://www.zhihu.com",
#             'Pragma': "no-cache",
#             'Referer': "http://www.zhihu.com/"
#         }
#         r = requests.get(request_url, params={"params": "{\"answer_id\":\"%d\"}" % int(data_aid)}, headers=headers, verify=False)
#         soup = BeautifulSoup(r.content, "lxml")
#         voters_info = soup.find_all("span")[1:-1]
#         if len(voters_info) == 0:
#             return
#             yield
#         else:
#             for voter_info in voters_info:
#                 if voter_info.string == u"匿名用户、" or voter_info.string == u"匿名用户":
#                     voter_url = None
#                     yield User(voter_url)
#                 else:
#                     voter_url = "http://www.zhihu.com" + str(voter_info.a["href"])
#                     voter_id = voter_info.a["title"].encode("utf-8")
#                     yield User(voter_url, voter_id)

# class Post:
#     url = None
#     meta = None
#     slug = None

#     def __init__(self, url, ):
#         if not re.compile(r"(http|https)://zhuanlan.zhihu.com/p/\d{8}").match(url):
#             raise ValueError("\"" + url + "\"" + " : it isn't a question url.")
#         else:
#             self.url = url
#             self.slug = re.compile(r"(http|https)://zhuanlan.zhihu.com/p/(\d{8})").match(url).group(2)

#     def parser(self):
#         headers = {
#             'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
#             'Host': "zhuanlan.zhihu.com",
#             'Accept': "application/json, text/plain, */*"
#         }
#         r = requests.get('https://zhuanlan.zhihu.com/api/posts/' + self.slug, headers=headers, verify=False)
#         self.meta = r.json()

#     def get_title(self):
#         if hasattr(self, "title"):
#             if platform.system() == 'Windows':
#                 title = self.title.decode('utf-8').encode('gbk')
#                 return title
#             else:
#                 return self.title
#         else:
#             if self.meta == None:
#                 self.parser()
#             meta = self.meta
#             title = meta['title']
#             self.title = title
#             if platform.system() == 'Windows':
#                 title = title.decode('utf-8').encode('gbk')
#                 return title
#             else:
#                 return title

#     def get_content(self):
#         if self.meta == None:
#             self.parser()
#         meta = self.meta
#         content = meta['content']
#         if platform.system() == 'Windows':
#             content = content.decode('utf-8').encode('gbk')
#             return content
#         else:
#             return content
    
#     def get_author(self):
#         if hasattr(self, "author"):
#             return self.author
#         else:
#             if self.meta == None:
#                 self.parser()
#             meta = self.meta
#             author_tag = meta['author']
#             author = User(author_tag['profileUrl'],author_tag['slug'])
#             return author

#     def get_column(self):
#         if self.meta == None:
#             self.parser()
#         meta = self.meta
#         column_url = 'https://zhuanlan.zhihu.com/' + meta['column']['slug']
#         return Column(column_url, meta['column']['slug'])

#     def get_likes(self):
#         if self.meta == None:
#             self.parser()
#         meta = self.meta
#         return int(meta["likesCount"])

#     def get_topics(self):
#         if self.meta == None:
#             self.parser()
#         meta = self.meta
#         topic_list = []
#         for topic in meta['topics']:
#             topic_list.append(topic['name'])
#         return topic_list      

# class Column:
#     url = None
#     meta = None

#     def __init__(self, url, slug=None):

#         if not re.compile(r"(http|https)://zhuanlan.zhihu.com/([0-9a-zA-Z]+)").match(url):
#             raise ValueError("\"" + url + "\"" + " : it isn't a question url.")
#         else:
#             self.url = url
#             if slug == None:
#                 self.slug = re.compile(r"(http|https)://zhuanlan.zhihu.com/([0-9a-zA-Z]+)").match(url).group(2)
#             else:
#                 self.slug = slug

#     def parser(self):
#         headers = {
#             'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
#             'Host': "zhuanlan.zhihu.com",
#             'Accept': "application/json, text/plain, */*"
#         }
#         r = requests.get('https://zhuanlan.zhihu.com/api/columns/' + self.slug, headers=headers, verify=False)
#         self.meta = r.json()

#     def get_title(self):
#         if hasattr(self,"title"):
#             if platform.system() == 'Windows':
#                 title =  self.title.decode('utf-8').encode('gbk')
#                 return title
#             else:
#                 return self.title
#         else:
#             if self.meta == None:
#                 self.parser()
#             meta = self.meta
#             title = meta['name']
#             self.title = title
#             if platform.system() == 'Windows':
#                 title = title.decode('utf-8').encode('gbk')
#                 return title
#             else:
#                 return title

#     def get_description(self):
#         if self.meta == None:
#             self.parser()
#         meta = self.meta
#         description = meta['description']
#         if platform.system() == 'Windows':
#             description = description.decode('utf-8').encode('gbk')
#             return description
#         else:
#             return description

#     def get_followers_num(self):
#         if self.meta == None:
#             self.parser()
#         meta = self.meta
#         followers_num = int(meta['followersCount'])
#         return followers_num

#     def get_posts_num(self):
#         if self.meta == None:
#             self.parser()
#         meta = self.meta
#         posts_num = int(meta['postsCount'])
#         return posts_num

#     def get_creator(self):
#         if hasattr(self, "creator"):
#             return self.creator
#         else:
#             if self.meta == None:
#                 self.parser()
#             meta = self.meta
#             creator_tag = meta['creator']
#             creator = User(creator_tag['profileUrl'],creator_tag['slug'])
#             return creator

#     def get_all_posts(self):
#         posts_num = self.get_posts_num()
#         if posts_num == 0:
#             print "No posts."
#             return
#             yield
#         else:
#             for i in xrange((posts_num - 1) / 20 + 1):
#                 parm = {'limit': 20, 'offset': 20*i}
#                 url = 'https://zhuanlan.zhihu.com/api/columns/' + self.slug + '/posts'
#                 headers = {
#                     'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
#                     'Host': "www.zhihu.com",
#                     'Origin': "http://www.zhihu.com",
#                     'Pragma': "no-cache",
#                     'Referer': "http://www.zhihu.com/"
#                 }
#                 r = requests.get(url, params=parm, headers=headers, verify=False)
#                 posts_list = r.json()
#                 for p in posts_list:
#                     post_url = 'https://zhuanlan.zhihu.com/p/' + str(p['slug'])
#                     yield Post(post_url)

# class Collection:
#     url = None
#     # session = None
#     soup = None

#     def __init__(self, url, name=None, creator=None):

#         #if url[0:len(url) - 8] != "http://www.zhihu.com/collection/":
#         if not re.compile(r"(http|https)://www.zhihu.com/collection/\d{8}").match(url):
#             raise ValueError("\"" + url + "\"" + " : it isn't a collection url.")
#         else:
#             self.url = url
#             # print 'collection url',url
#             if name != None:
#                 self.name = name
#             if creator != None:
#                 self.creator = creator
#     def parser(self):
#         headers = {
#             'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
#             'Host': "www.zhihu.com",
#             'Origin': "http://www.zhihu.com",
#             'Pragma': "no-cache",
#             'Referer': "http://www.zhihu.com/"
#         }
#         r = requests.get(self.url, headers=headers, verify=False)
#         soup = BeautifulSoup(r.content, "lxml")
#         self.soup = soup

#     def get_name(self):
#         if hasattr(self, 'name'):
#             if platform.system() == 'Windows':
#                 return self.name.decode('utf-8').encode('gbk')
#             else:
#                 return self.name
#         else:
#             if self.soup == None:
#                 self.parser()
#             soup = self.soup
#             self.name = soup.find("h2", id="zh-fav-head-title").string.encode("utf-8").strip()
#             if platform.system() == 'Windows':
#                 return self.name.decode('utf-8').encode('gbk')
#             return self.name

#     def get_creator(self):
#         if hasattr(self, 'creator'):
#             return self.creator
#         else:
#             if self.soup == None:
#                 self.parser()
#             soup = self.soup
#             creator_id = soup.find("h2", class_="zm-list-content-title").a.string.encode("utf-8")
#             creator_url = "http://www.zhihu.com" + soup.find("h2", class_="zm-list-content-title").a["href"]
#             creator = User(creator_url, creator_id)
#             self.creator = creator
#             return creator

#     def get_all_answers(self):
#         if self.soup == None:
#             self.parser()
#         soup = self.soup
#         answer_list = soup.find_all("div", class_="zm-item")
#         if len(answer_list) == 0:
#             print "the collection is empty."
#             return
#             yield
#         else:
#             question_url = None
#             question_title = None
#             for answer in answer_list:
#                 if not answer.find("p", class_="note"):
#                     question_link = answer.find("h2")
#                     if question_link != None:
#                         question_url = "http://www.zhihu.com" + question_link.a["href"]
#                         question_title = question_link.a.string.encode("utf-8")
#                     question = Question(question_url, question_title)
#                     answer_url = "http://www.zhihu.com" + answer.find("span", class_="answer-date-link-wrap").a["href"]
#                     author = None

#                     if answer.find("div", class_="zm-item-answer-author-info").get_text(strip='\n') == u"匿名用户":
#                         author_url = None
#                         author = User(author_url)
#                     else:
#                         author_tag = answer.find("div", class_="zm-item-answer-author-info").find_all("a")[0]
#                         author_id = author_tag.string.encode("utf-8")
#                         author_url = "http://www.zhihu.com" + author_tag["href"]
#                         author = User(author_url, author_id)
#                     yield Answer(answer_url, question, author)
#             i = 2
#             while True:
#                 headers = {
#                     'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
#                     'Host': "www.zhihu.com",
#                     'Origin': "http://www.zhihu.com",
#                     'Pragma': "no-cache",
#                     'Referer': "http://www.zhihu.com/"
#                 }
#                 r = requests.get(self.url + "?page=" + str(i), headers=headers, verify=False)
#                 answer_soup = BeautifulSoup(r.content, "lxml")
#                 answer_list = answer_soup.find_all("div", class_="zm-item")
#                 if len(answer_list) == 0:
#                     break
#                 else:
#                     for answer in answer_list:
#                         if not answer.find("p", class_="note"):
#                             question_link = answer.find("h2")
#                             if question_link != None:
#                                 question_url = "http://www.zhihu.com" + question_link.a["href"]
#                                 question_title = question_link.a.string.encode("utf-8")
#                             question = Question(question_url, question_title)
#                             answer_url = "http://www.zhihu.com" + answer.find("span", class_="answer-date-link-wrap").a[
#                                 "href"]
#                             author = None
#                             if answer.find("div", class_="zm-item-answer-author-info").get_text(strip='\n') == u"匿名用户":
#                                 # author_id = "匿名用户"
#                                 author_url = None
#                                 author = User(author_url)
#                             else:
#                                 author_tag = answer.find("div", class_="zm-item-answer-author-info").find_all("a")[0]
#                                 author_id = author_tag.string.encode("utf-8")
#                                 author_url = "http://www.zhihu.com" + author_tag["href"]
#                                 author = User(author_url, author_id)
#                             yield Answer(answer_url, question, author)
#                 i = i + 1

#     def get_top_i_answers(self, n):
#         j = 0
#         answers = self.get_all_answers()
#         for answer in answers:
#             j = j + 1
#             if j > n:
#                 break
#             yield answer

