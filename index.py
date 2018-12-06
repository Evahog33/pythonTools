
import re
import json
from urllib import request
from urllib.parse import quote
import string


class Spider():
    url = 'https://www.douguo.com/caipu'
    # 网站的目录
    # mune_list = ['下饭菜', '甜品', '肉类', '主食', '私家菜', '凉菜', '烘焙', '豆制品', '煲汤',
    #              '海鲜', '蛋类'] 
    
    # 测试用的第一个数据
    mune_list = ['下饭菜']

    # 过滤器
    root_pattern = '<div class="cp_box">([\s\S]*?)</div>'
    name_pattern = 'alt="([\s\S]*?)">'
    href_pattern = '<a href="([\s\S]*?)" class="cp_pic" target="_blank"'
    img_pattern = '<img src="([\s\S]*?)" alt="'
    # 子页面
    # 食材
    Ingredients_html_pattern = '<tr>([\s\S]*?)</tr>' 
    # 具体食材
    # Ingredients_pattern = '>([\u4e00-\u9fa5]*?)<'
    Ingredients_pattern = '>([\u4e00-\u9fa5a-zA-Z0-9]*?)<'

    # 步骤整体
    step_box_pattern = '<span class="fwb">([\s\S]*?)</p>'   
    # 步骤
    step_pattern = '</span>([\s\S]*)'

    # 整体网站
    def __fetch_content(self, menu_name):
        _url = Spider.url + '/' + menu_name
        _url = quote(_url, safe=string.printable)
        r = request.urlopen(_url)
        htmls = r.read()
        htmls = str(htmls, encoding='utf-8')
        return htmls

    # 获取菜单的 name img
    def __analysis(self, htmls,):
        root_html = re.findall(Spider.root_pattern, htmls)
        anchors = []
        for html in root_html:
            name = re.findall(Spider.name_pattern, html)
            href = re.findall(Spider.href_pattern, html)
            img = re.findall(Spider.img_pattern, html)
            menu = self.__get_menu(href)
            anchor = {'name': name[0], 'menu': menu, 'img': img[0]}
            anchors.append(anchor)
        return anchors

    # 获取菜单的步骤
    def __get_menu(self, href):
        r1 = request.urlopen(href[0])
        menu_htmls = r1.read()
        menu_htmls = str(menu_htmls, encoding='utf-8')
        ing_box = re.findall(Spider.Ingredients_html_pattern, menu_htmls)
        Ingredients = []
        for Ing_item in ing_box:
            ing = re.findall(Spider.Ingredients_pattern, Ing_item)
            for i in ing:
                if(i != ''):
                    Ingredients.append(i)

        steps_box = re.findall(Spider.step_box_pattern, menu_htmls)
        steps = []
        for inx, item in enumerate(steps_box):
            _pattern = 'span class="fwb">' + str(inx + 1) + '.' + Spider.step_pattern
            step = re.findall(_pattern, item)
            if(len(step) == 0):
                _pattern = str(inx + 1) + '.' + Spider.step_pattern
                step = re.findall(_pattern, item)
            steps.append(step[0])
        menu_item = {'Ingredients': Ingredients, 'steps': steps}
        return menu_item

    # 入口方法
    def go(self):
        for item in self.mune_list:
            anchors_box = []
            # 循环了5次 因为没个种类下面都是5页
            # 可以查出具体的数字 然后再判断是否循环 不过我比较懒就没那么写
            for i in range(5):
                htmls = self.__fetch_content(item + '/' + str(i*30))
                anchors = self.__analysis(htmls)
                # 把查询到的数据写到数组中
                anchors_box += anchors
                print('往数组中添加第 ' + str(i + 1) + ' 次')
            data = {'list': anchors_box}
            # 处理数据（为了方便我就直接写成json了）
            with open('./json/' + item + '.json', 'w', encoding='utf-8') as file_obj:
                json.dump(data, file_obj, ensure_ascii=False)
                print('写入json')
        

spider = Spider()
spider.go()
