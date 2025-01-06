import json
import time
import tkinter as tk
import urllib.parse
from tkinter import ttk, messagebox

import ddddocr
import requests
import wcwidth
from PIL import Image

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_session():
    return requests.Session()


def align_text(text, width):
    text_width = wcwidth.wcswidth(text)
    return text + ' ' * (width - text_width) if text_width < width else text


def get_headers(referer):
    return {
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '""',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'https://jxgl.gdufs.edu.cn',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.141 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': referer,
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'close'
    }


def perform_login(session, url, username, password):
    password = urllib.parse.quote(password)
    session.get(url + '/xk/LoginToXkLdap')
    response = session.get(url + '/verifycode.servlet')
    time.sleep(1)
    i = 0
    if response.status_code == 200:
        while i < 30:
            try:
                response = session.get(url + '/verifycode.servlet')
                time.sleep(1)
                i += 1
                with open("./captcha.png", "wb") as f:
                    f.write(response.content)
                img = Image.open("./captcha.png")
                captcha = ddddocr.DdddOcr(show_ad=False).classification(img)
                login_body = f"USERNAME={username}&PASSWORD={password}&RANDOMCODE={captcha}"
                login_response = session.post(
                    url + '/xk/LoginToXkLdap',
                    headers=get_headers(url + '/xk/LoginToXkLdap'),
                    data=login_body
                )
                if "<font color=\"red\">" in login_response.text:
                    error_message = login_response.text.split("<font color=\"red\">")[1].split("</font>")[0]
                    #return None, error_message
            except Exception:
                pass
            else:
                break

        title = login_response.text.split('<title>')[1].split('</title>')[0]
        if i==29:
            return None, error_message
        else:
            return login_response.cookies, title

    return None, "Failed to retrieve captcha"


def perform_out_login(session, url, username, password):
    chrome_options = webdriver.EdgeOptions()
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    service = Service("./edgedriver_win64/msedgedriver.exe")  # 替换为你的chromedriver路径
    browser = webdriver.Edge(service=service)
    login_url = "https://authserver-443.webvpn.gdufs.edu.cn/authserver/login"

    browser.get(login_url)
    username_field = WebDriverWait(browser, timeout=9999999).until(
        EC.presence_of_element_located((By.XPATH, """//*[@id="username"]""")))  # 替换为实际的用户名输入框ID
    password_field = WebDriverWait(browser, timeout=9999999).until(
        EC.presence_of_element_located((By.XPATH, """//*[@id="password"]""")))  # 替换为实际的密码输入框ID
    username_field.send_keys("20231003082")
    password_field.send_keys("123456aA@")
    login_button = WebDriverWait(browser, timeout=9999999).until(
        EC.element_to_be_clickable((By.XPATH, """//*[@id="login_submit"]""")))  # 替换为实际的登录按钮ID
    login_button.click()

    WebDriverWait(browser, timeout=9999999).until(EC.presence_of_element_located((By.XPATH,"""//*[@id="app"]/div/div[2]/div/div/div/div/div/div/div[1]/div[3]/div[1]/div/div/div[1]/div[2]/div""")))
    browser.get("""https://jxgl-443.webvpn.gdufs.edu.cn/jsxsd/""")
    cookies = browser.get_cookies()
    print(cookies)
    browser.close()
    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
    session.cookies.update(cookies_dict)
    for key, value in cookies_dict.items():
        session.cookies.set(key, value)
    response=requests.get("""https://jxgl-443.webvpn.gdufs.edu.cn/jsxsd/""", cookies=cookies_dict)
    print(response.text)
    password = urllib.parse.quote(password)
    session.get(url + '/xk/LoginToXkLdap', cookies=cookies_dict)
    response = session.get(url + '/verifycode.servlet', cookies=cookies_dict)
    time.sleep(1)
    i = 0
    if response.status_code == 200:
        while i < 30:
            try:
                response = session.get(url + '/verifycode.servlet', cookies=cookies_dict)
                time.sleep(1)
                i += 1
                with open("./captcha.png", "wb") as f:
                    f.write(response.content)
                img = Image.open("./captcha.png")
                captcha = ddddocr.DdddOcr(show_ad=False).classification(img)
                login_body = f"USERNAME={username}&PASSWORD={password}&RANDOMCODE={captcha}"
                login_response = session.post(
                    url + '/xk/LoginToXkLdap',
                    headers=get_headers(url + '/xk/LoginToXkLdap'),
                    data=login_body
                )
                if "<font color=\"red\">" in login_response.text:
                    error_message = login_response.text.split("<font color=\"red\">")[1].split("</font>")[0]
                    #return None, error_message
            except Exception:
                pass
            else:
                break

        title = login_response.text.split('<title>')[1].split('</title>')[0]
        if i==29:
            return None, error_message
        else:
            return login_response.cookies, title

    return None, "Failed to retrieve captcha"


def query_scores(session, url,cookie):
    response = session.post(
        url + '/kscj/cjcx_list',
        headers=get_headers(url + '/kscj/cjcx_query'),
        data="kksj=&kcxz=&kcmc=&fxkc=0&xsfs=all"
        , cookies=cookie
    )

    text = response.text
    lines = text.split('\n')
    names, urls = [], []

    for i, line in enumerate(lines):
        if "/jsxsd/kscj/pscj_list.do" in line:
            name = lines[i - 2].split('<td align="left">')[1].split("</td>")[0]
            url_fragment = line.split("JsMod('")[1].split("'")[0].split("/jsxsd")[1].strip()
            names.append(name)
            urls.append(url_fragment)

    return names, urls


def fetch_scores_details(session, url, urls,cookie):
    contents = []
    for elem in urls:
        response = session.get(url + elem, headers=get_headers(url), cookies=cookie)
        lines = response.text.split('\n')
        for line in lines:
            if "<td>" in line:
                content = line.split("<td>")[1].split("</td>")[0]
                contents.append(content)
    return contents


def display_scores_gui(names, contents, on_refresh, gpa_message):
    root = tk.Tk()
    root.title("成绩查询结果")
    root.iconbitmap('./GDUFS.ico')

    frame = ttk.Frame(root, padding="10")
    frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    gpa_label = ttk.Label(frame, text=gpa_message, font=("Arial", 12))
    gpa_label.grid(column=0, row=0, columnspan=2, pady=1)

    columns = ["行数", "课程名", "序号", "平时成绩", "平时成绩比例", "期中成绩", "期中成绩比例", "期末成绩",
               "期末成绩比例", "总成绩"]
    tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    for i in range(int(len(contents) / 8)):
        tree.insert("", tk.END, values=(
            i + 1, names[i], contents[i * 8], contents[i * 8 + 1], contents[i * 8 + 2],
            contents[i * 8 + 3], contents[i * 8 + 4], contents[i * 8 + 5], contents[i * 8 + 6], contents[i * 8 + 7]
        ))

    tree.grid(column=0, row=1, sticky=(tk.W, tk.E, tk.N, tk.S))
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(column=1, row=1, sticky=(tk.N, tk.S))

    button_frame = ttk.Frame(root, padding="5")
    button_frame.grid(column=0, row=2, sticky=(tk.W, tk.E))

    refresh_button = ttk.Button(button_frame, text="重新查询", command=on_refresh)
    refresh_button.grid(column=0, row=0, padx=5, pady=5)
    root.mainloop()


def display_login_gui(on_login,on_out_login):
    login_root = tk.Tk()
    login_root.title("登录")
    login_root.iconbitmap('./GDUFS.ico')

    frame = ttk.Frame(login_root, padding="10")
    frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    ttk.Label(frame, text="用户名:").grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
    username_entry = ttk.Entry(frame)
    username_entry.grid(column=1, row=0, padx=5, pady=5)

    ttk.Label(frame, text="密码:").grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
    password_entry = ttk.Entry(frame, show="*")
    password_entry.grid(column=1, row=1, padx=5, pady=5)

    auto_login_var = tk.BooleanVar()
    auto_login_check = ttk.Checkbutton(frame, text="自动登录", variable=auto_login_var)
    auto_login_check.grid(column=1, row=2, sticky=tk.W, padx=5, pady=5)

    try:
        with open("./config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            username_entry.insert(0, config.get("username", ""))
            password_entry.insert(0, config.get("password", ""))
            auto_login_var.set(bool(config.get("autoLogin", 0)))
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        messagebox.showerror("错误", "配置文件格式错误！")

    def handle_login():
        username = username_entry.get()
        password = password_entry.get()
        auto_login = auto_login_var.get()

        if username and password:
            on_login(username, password, auto_login)
            login_root.destroy()
        else:
            messagebox.showerror("错误", "请输入用户名和密码！")

    def handle_out_login():
        username = username_entry.get()
        password = password_entry.get()

        if username and password:
            on_out_login(username, password, False)
            login_root.destroy()
        else:
            messagebox.showerror("错误", "请输入用户名和密码！")

    login_button = ttk.Button(frame, text="校园网登录", command=handle_login)
    login_button.grid(column=1, row=3, padx=5, pady=5, sticky=tk.E)

    login_button = ttk.Button(frame, text="外网登录", command=handle_out_login)
    login_button.grid(column=2, row=3, padx=5, pady=5, sticky=tk.E)

    login_root.mainloop()


def getGpa(url, session,cookie):
    name="查询失败"
    mainGPA=secGPA=name
    response = session.post(
        url + '/kscj/cjcx_list',
        headers=get_headers(url + '/kscj/cjcx_query'),
        data="kksj=&kcxz=&kcmc=&fxkc=0&xsfs=all"
        , cookies=cookie
    )
    text=response.text
    name = text.split("&nbsp;&nbsp;&nbsp;")[1].split("</div>")[0]
    try:
        mainGPA = text.split("主修课程平均学分绩点<span>")[1].split("</span>")[0]
        secGPA = text.split("辅修课程平均学分绩点<span>")[1].split("</span>")[0]
    except IndexError:
        pass
    return f"{name} ,主修课程平均学分绩点 {mainGPA} ,辅修课程平均学分绩点 {secGPA}"

url = "https://jxgl.gdufs.edu.cn/jsxsd"
def main():

    session = create_session()

    def on_login(username, password, auto_login):
        try:
            global url
            url = "https://jxgl.gdufs.edu.cn/jsxsd"
            cookies, title = perform_login(session, url, username, password)

            if not cookies:
                messagebox.showerror("登录失败", title)
                display_login_gui(on_login,on_out_login)
                return

            if auto_login:
                with open("./config.json", "w", encoding="utf-8") as f:
                    json.dump({"username": username, "password": password, "autoLogin": 1}, f)
            else:
                with open("./config.json", "w", encoding="utf-8") as f:
                    json.dump({"username": username, "password": password, "autoLogin": 0}, f)

            query_and_display(cookies)

        except Exception as e:
            messagebox.showerror("错误", str(e))
            display_login_gui(on_login,on_out_login)

    def on_out_login(username, password, auto_login):
        global url
        url = "https://jxgl-443.webvpn.gdufs.edu.cn/jsxsd"
        try:
            cookies, title = perform_out_login(session, url, username, password)
            if not cookies:
                messagebox.showerror("登录失败", title)
                display_login_gui(on_login,on_out_login)
                return

            if auto_login:
                with open("./config.json", "w", encoding="utf-8") as f:
                    json.dump({"username": username, "password": password, "autoLogin": 1}, f)
            else:
                with open("./config.json", "w", encoding="utf-8") as f:
                    json.dump({"username": username, "password": password, "autoLogin": 0}, f)

            query_and_display(cookies)

        except Exception as e:
            messagebox.showerror("错误", str(e))
            display_login_gui(on_login,on_out_login)

    def query_and_display(cookie):
        try:
            names, urls = query_scores(session, url,cookie)
            contents = fetch_scores_details(session, url, urls,cookie)

            gpa_message = getGpa(url, session,cookie)

            def on_logout():
                main()

            def on_refresh():
                query_and_display(cookie)

            display_scores_gui(names, contents,on_refresh, gpa_message)

        except Exception as e:
            messagebox.showerror("错误", str(e))

    try:
        with open("./config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

            if config.get("autoLogin"):
                on_login(config['username'], config['password'], True)
            else:
                display_login_gui(on_login,on_out_login)

    except FileNotFoundError:
        display_login_gui(on_login,on_out_login)
    except json.JSONDecodeError:
        messagebox.showerror("错误", "配置文件格式错误！")
    except KeyError:
        messagebox.showerror("错误", "配置文件缺少必要字段！")
    except Exception as e:
        messagebox.showerror("错误", str(e))


if __name__ == '__main__':
    main()
