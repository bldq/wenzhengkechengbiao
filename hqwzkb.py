from bs4 import BeautifulSoup
import re
import requests
import datetime
from datetime import datetime, timedelta
from PIL import Image

def cap(captcha_data):
    """创建一个处理验证码的方法，主要逻辑就是请求验证码的url，然后把验证码图片下载到本地，人工识别后输入"""
    with open("captcha.gif", "wb") as f:
        f.write(captcha_data)
    # 手动输入验证码
    img = Image.open('captcha.gif')
    img.show()
    img.close()
    text = input("输入验证码：")
    return text

def wzjwlogin():
    """先创建一个方法"""
    xuehao = input('你的学号')
    jiaowumima = input('你的教务网密码')
    login_url = "http://wzjw.sdwz.cn/"
    # 实例化一个session对象，用来保存cookie信息
    session = requests.Session()
    # 创建headers
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}
    # 先发送一个get请求，用来获取需要的captcha-id
    # 获得html页面信息
    html = session.get(login_url, headers=headers).content.decode()
    # 使用etree方法把html转化为xpath可解析对象
    # html_e = etree.HTML(html)
    # 提取动态的信息
    data = {'txtuserid': xuehao, 'txtpwd': jiaowumima}
    soup = BeautifulSoup(html, features='lxml')
    tag_root = soup.div.find_all('input')
    for i in tag_root:
        info = BeautifulSoup(str(i), 'html.parser')
        try:
            id = info.input['id']
            value = info.input['value']
            data[id] = value
        except (KeyError):
            pass
    # 构建完整的验证码地址
    captcha_url = "http://wzjw.sdwz.cn/ImageValidate.ashx?temp=aaaaaaaa"
    # 请求验证码地址获得验证码图片的数据
    captcha_data = session.get(captcha_url, headers=headers).content
    # 调用函数处理验证码数据
    text = cap(captcha_data)
    # 构建post请求需要的data数据
    data ['txtjym'] = str(text)
    # 发送post请求，获取登陆成功页面，到这一步就获得了登陆账号的cookie信息
    session.post(login_url, headers=headers, data=data)
    # 获得了cookie，就可以再发送get请求，获取个人主页信息
    response = session.get("http://wzjw.sdwz.cn/student/xk_jg_chaxun.aspx", headers=headers)
    with open("xkjg.html", "w", encoding="utf-8") as f:
        f.write(response.content.decode())

def xxzh(info):
    info = info.replace('一', '1')
    info = info.replace('二', '2')
    info = info.replace('三', '3')
    info = info.replace('四', '4')
    info = info.replace('五', '5')
    info = info.replace('六', '6')
    info = info.replace('日', '7')
    info = info.replace('周星期', ';')
    info = info.replace('星期', ';')
    info = info.replace('--', '-')
    info = info.replace('第', ';')
    info = info.replace('节', ';')
    return info


def rgWeek(startWeek, endWeek):
    return list(range(startWeek, endWeek + 1))


def oeWeek(startWeek, endWeek, mode):
    allWeek = range(startWeek, endWeek + 1)
    oddWeek = []
    evenWeek = []
    for w in allWeek:
        if w % 2 == 0:
            evenWeek.append(w)
        else:
            oddWeek.append(w)
    if mode:
        return oddWeek
    else:
        return evenWeek


def fanwei(fanweishu):
    is_fanwei = re.match(r'(\d*)-(\d*)', fanweishu)
    if is_fanwei:
        fanweishu = rgWeek(int(is_fanwei.group(1)), int(is_fanwei.group(2)))
    elif fanweishu == '':
        fanweishu = rgWeek(1, 17)
    elif fanweishu == '双':
        fanweishu = oeWeek(1, 17, 0)
    elif fanweishu == '单':
        fanweishu = oeWeek(1, 17, 1)
    return fanweishu


def get_info():
    soup = BeautifulSoup(open("xkjg.html", encoding='utf-8'), features='lxml')
    tag_root = soup.table.tr.find_all('tr')
    lessons = []
    lesson = []
    classes = []
    for tag in tag_root:
        leaves = tag.select('td[class="dxgv"]')
        for leaf in leaves:
            lesson.append(leaf.string)
        lessons.append(lesson)
        lesson = []
    while [] in lessons:
        lessons.remove([])
    lessons.pop()
    for lesson in lessons:
        for i in range(len(lesson)):
            lesson[i] = lesson[i].replace(' ', '')  # 清除空格
        main_info = re.split('\*;', lesson[4])  # 分割时间课程
        del lesson[4:]
        while '' in main_info:
            main_info.remove('')  # 去除空
        for i in range(len(main_info)):
            main_info[i] = xxzh(main_info[i])
            lesson1 = lesson + re.split(';', main_info[i])
            classes.append(lesson1)
    for i in classes:
        i[4] = fanwei(i[4])
        i[5] = int(i[5])
        i[6] = fanwei(i[6])
        if len(i) > 8:
            i.pop()
    return classes




if __name__ == '__main__':

    maxWeek = 20
    classTime = [None, (8, 40), (9, 30), (10, 30), (11, 20), (13, 30), (14, 20), (15, 20), (16, 10), (17, 0), (18, 30),
                 (19, 20), (20, 10)]
    weeks = [None]
    starterDay = datetime(2020, 9, 7)
    for i in range(1, maxWeek):
        singleWeek = [None]
        for d in range(0, 7):
            singleWeek.append(starterDay)
            starterDay = starterDay + timedelta(days=1)
        weeks.append(singleWeek)
    while True:
        try:
            wzjwlogin()
            print('正在获取教务信息')
            classes = get_info()
            print('正在生成课表文件')
            break
        except(AttributeError):
            print('未获取到任何信息，请检查你输入的学号、教务密码、验证码是否正确')
            i = input('键入q结束程序，其他任意键入再试一次')
        if i == 'q':
            exit()
    iCalHeader = \
        '''
BEGIN:VCALENDAR
METHOD:PUBLISH
VERSION:2.0
X-WR-CALNAME:课表
PRODID:-//Apple Inc.//Mac OS X 10.14.6//EN
X-WR-TIMEZONE:Asia/Shanghai
CALSCALE:GREGORIAN
BEGIN:VTIMEZONE
TZID:Asia/Shanghai
END:VTIMEZONE
'''

    createNow = datetime.now() - timedelta(hours=8)
    dtStamp = createNow.strftime('%Y%m%dT%H%M%SZ')
    allvEvent = ""

    for Class in classes:
        [Name, Xuefen, classXingzhi, Classmates, classWeek, classWeekday, classOrder, Location] = Class[:]
        Title = Name + '--' + Location

        if '6号楼' in Location:
            customGEO = '''LOCATION:苏州大学文正学院教学楼6号楼\\n越溪吴山村吴中大道1188号
X-APPLE-STRUCTURED-LOCATION;VALUE=URI;X-ADDRESS="越溪吴山村吴中大道1188号";X-APPLE-MAPKIT
 -HANDLE=;X-APPLE-RADIUS=214.6811596310179;X-APPLE-REFERENCEFRAME=2;X
 -TITLE="苏州大学文正学院教学楼6号楼":geo:31.217280,120.581800'''
        elif '5号楼' in Location:
            customGEO = '''LOCATION:苏州大学文正学院教学楼5号楼\\n吴中大道1188号
X-APPLE-STRUCTURED-LOCATION;VALUE=URI;X-ADDRESS="吴中大道1188号";X-APPLE-MAPKIT
 -HANDLE=;X-APPLE-RADIUS=110.0041262892164;X-APPLE-REFERENCEFRAME=2;X
 -TITLE="苏州大学文正学院教学楼5号楼":geo:31.217313,120.583322'''
        elif '4号楼' in Location:
            customGEO = '''LOCATION:苏州大学文正学院教学楼4号楼\\n吴越路西50米
X-APPLE-STRUCTURED-LOCATION;VALUE=URI;X-ADDRESS="吴越路西50米";X-APPLE-MAPKIT
 -HANDLE=;X-APPLE-RADIUS=219.4448708817638;X-APPLE-REFERENCEFRAME=2;X
 -TITLE="苏州大学文正学院教学楼4号楼":geo:31.219883,120.582396'''
        elif '3号楼' in Location:
            customGEO = '''LOCATION:苏州大学文正学院-3号教学楼\\n越湖路188号
X-APPLE-STRUCTURED-LOCATION;VALUE=URI;X-ADDRESS="越湖路188号";X-APPLE-MAPKIT
 -HANDLE=;X-APPLE-RADIUS=291.941821779832;X-APPLE-REFERENCEFRAME=2;X
 -TITLE="苏州大学文正学院-3号教学楼":geo:31.220223,120.581559'''
        elif '2号楼' in Location:
            customGEO = '''LOCATION:苏州大学文正学院教学楼2号楼\\n吴越路西100米
X-APPLE-STRUCTURED-LOCATION;VALUE=URI;X-ADDRESS="吴越路西100米";X-APPLE-MAPKIT
 -HANDLE=;X-APPLE-RADIUS=271.0389439103238;X-APPLE-REFERENCEFRAME=2;X
 -TITLE="苏州大学文正学院教学楼2号楼":geo:31.219813,120.581494'''
        elif '1号楼' in Location:
            customGEO = '''LOCATION:苏州大学文正学院教学楼1号楼\\n吴越路西100米
X-APPLE-STRUCTURED-LOCATION;VALUE=URI;X-ADDRESS="吴越路西100米";X-APPLE-MAPKIT
 -HANDLE=;X-APPLE-RADIUS=263.2426963767142;X-APPLE-REFERENCEFRAME=2;X
 -TITLE="苏州大学文正学院教学楼1号楼":geo:31.219584,120.581431'''
        elif '数中心' in Location:
            customGEO = '''LOCATION:苏州大学文正学院-数字化中心\\n吴越路与横越路交叉路口往东南约100米
X-APPLE-STRUCTURED-LOCATION;VALUE=URI;X-ADDRESS="吴越路与横越路交叉路口往东南约100米";X-A
 PPLE-MAPKIT-HANDLE=;X-AP
 PLE-RADIUS=48.91477971362795;X-APPLE-REFERENCEFRAME=2;X-TITLE="苏州大学文正学院-
 数字化中心":geo:31.218525,120.583704'''
        elif '实验室' in Location:
            customGEO = '''LOCATION:苏州大学文正学院-综合实验楼\\n越湖路188号苏州大学文正学院
X-APPLE-STRUCTURED-LOCATION;VALUE=URI;X-ADDRESS="越湖路188号苏州大学文正学院";X-APPLE
 -MAPKIT-HANDLE=;X-APPLE-RADIUS=247.7265399647241;X-APPLE-REFERENCEFRAME=
 2;X-TITLE="苏州大学文正学院-综合实验楼":geo:31.216721,120.581720'''
        elif '体育场' in Location:
            customGEO = '''LOCATION:苏州大学文正学院运动场\\n吴中大道1188号苏州大学文正学院内
X-APPLE-STRUCTURED-LOCATION;VALUE=URI;X-ADDRESS="吴中大道1188号苏州大学文正学院内";X-AP
 PLE-MAPKIT-HANDLE=;X-APPLE-RADIUS=100.8007224915657;
 X-APPLE-REFERENCEFRAME=2;X-TITLE="苏州大学文正学院运动场":geo:31.217213,120.584534'''
        else:
            customGEO = ''

        for timeWeek in classWeek:
            classDate = weeks[timeWeek][classWeekday]
            startTime = classTime[classOrder[0]]
            endTime = classTime[classOrder[-1]]
            classStartTime = classDate + timedelta(minutes=startTime[0] * 60 + startTime[1])
            classEndTime = classDate + timedelta(minutes=endTime[0] * 60 + endTime[1] + 40)
            Description = '课程性质:' + classXingzhi + ' ; 学分:' + Xuefen + ';  教学班:' + Classmates + '。'
            vEvent = "\nBEGIN:VEVENT"
            vEvent += "\nDTEND;TZID=Asia/Shanghai:" + classEndTime.strftime('%Y%m%dT%H%M%S')
            vEvent += "\nSUMMARY:" + Title
            vEvent += "\nDTSTART;TZID=Asia/Shanghai:" + classStartTime.strftime('%Y%m%dT%H%M%S')
            vEvent += "\nDESCRIPTION:" + Description
            vEvent += "\n" + customGEO
            vEvent += "\nEND:VEVENT"
            allvEvent += vEvent

    allvEvent += "\nEND:VCALENDAR"
    jWrite = open("kebiao.ics", "w", encoding="utf-8")
    jWrite.write(iCalHeader + allvEvent)
    jWrite.close()
    input('生成课表完成,任意键入退出')