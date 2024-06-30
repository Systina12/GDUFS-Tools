import urllib.parse
import requests
from PIL import Image
import wcwidth

url="https://jxgl.gdufs.edu.cn/jsxsd"
session=requests.Session()
urls = []
names = []


def align_text(text, width):
    text_width = wcwidth.wcswidth(text)
    if text_width < width:
        return text + ' ' * (width - text_width)
    else:
        return text

def login(username,password):
    loginHeader = {
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '\"\"',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'https://jxgl.gdufs.edu.cn',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.141 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://jxgl.gdufs.edu.cn/jsxsd/xk/LoginToXkLdap',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'close'
    }
    password=urllib.parse.quote(password)
    #print(password)
    session.get(url+'/xk/LoginToXkLdap')
    response=session.get(url+'/verifycode.servlet')
    if response.status_code==200:
        with open("./captcha.png","wb") as f:
            f.write(response.content)
        img = Image.open("./captcha.png")
        img.show()
        captcha=input("请输入验证码:")
        body = f"USERNAME={username}&PASSWORD={password}&RANDOMCODE={captcha}"
        response=session.post(url+'/xk/LoginToXkLdap',headers=loginHeader,data=body)
        titles=response.text.split('<title>')[1].split('</title>')[0]
        return response.cookies,titles

def check():
    checkHeader={
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '\"\"',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'https://jxgl.gdufs.edu.cn',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.141 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://jxgl.gdufs.edu.cn/jsxsd/kscj/cjcx_query',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'close'
    }
    body="""kksj=&kcxz=&kcmc=&fxkc=0&xsfs=all"""
    response=session.post(url+'/kscj/cjcx_list',headers=checkHeader,data=body)
    #print(response.text)
    text=response.text
    lines=text.split('\n')

    i=0
    for line in lines:
        if """/jsxsd/kscj/pscj_list.do""" in line:
            name=lines[i-2].split('<td align="left">')[1].split("</td>")[0]
            url1=line.split("JsMod('")[1].split("'")[0].split("/jsxsd")[1].strip()
            print(align_text(name,15),url+url1)
            names.append(name)
            urls.append(url1)
        i+=1
    # for i in urls:
    #     print(i)
    contents=[]
    for elem in urls:
        response=session.get(url+elem,headers=checkHeader)
        #print(response.text)
        lines=response.text.split('\n')
        for line in lines:
            if "<td>" in line:
                content=line.split("<td>")[1].split("</td>")[0]
                #print(content)
                contents.append(content)

    print(
        align_text("课程名",40), align_text("序号",10), align_text("平时成绩",10),
        align_text("平时成绩比例",20), align_text("期中成绩",10),align_text("期中成绩比例",20),
        align_text("期末成绩",10), align_text("期末成绩比例",20), align_text("总成绩",10)
    )

    # 打印每行内容
    for i in range(int(len(contents) / 8)):
        print(
            align_text(names[i],40), align_text(contents[i * 8],10), align_text(contents[i * 8 + 1],10),
            align_text(contents[i * 8 + 2],20), align_text(contents[i * 8 + 3],10),align_text(contents[i * 8 + 4],20),
            align_text(contents[i * 8 + 5],10), align_text(contents[i * 8 + 6],20), align_text(contents[i * 8 + 7],10)
        )


if __name__ == '__main__':
    print("程序基于requests实现了查询成绩组成的功能,用于解决学校教务系统仅可用ie浏览器查询平时成绩的问题")
    print("在该可执行文件所在目录下会产生captcha.png用于暂存验证码,在程序使用结束后可以删除")
    print("注意:目前仅在校园网内可用")
    while True:
        username=input("请输入账号:")
        password=input("请输入密码:")
        cookies,title=login(username,password)
        if str(cookies)=='None':
            print(f"cookies={cookies};登录失败,请重试")
            continue
        elif "学生个人中心" not in title:
            result=input(f"登录后界面标题为:{title},可能登录失败,是否重试? Y/N")
            if str(result) in "yY1yes":
                continue
            check()
        else:
            print(f"cookies={cookies}")
            check()
