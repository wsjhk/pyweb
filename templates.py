# -*- coding: utf-8 -*-

import traceback
import sys
import re

def getTraceStackMsg():
    tb = sys.exc_info()[2]
    msg = ''
    for i in traceback.format_tb(tb):
        msg += i
    return msg

# 模板类，拼接html代码
class PyTpl():
    def __init__(self, filepath = None, content = None):
        if filepath != None:
            content = open(filepath, "r").read()
        if content == None:
            raise Exception("template content can not be null")
        indent_count = 0
        self.py_code = "__html_code__ = ''"
        self.param_dic = {}
        text_list = content.split("<%")
        for text in text_list:
            right = text.find("%>")
            if right == -1:
                self.py_code += "\n%s__html_code__ += '''%s'''" % (indent_count*"\t", text)
                continue
            elif text[0] == '=':
                self.py_code += "\n%s__html_code__ += str(%s)" % (indent_count*"\t", text[1:right])
            else:
                replace_reg = re.compile(r'\s*{\s*')
                py_text = replace_reg.sub("{", text[0:right].replace("\r","").replace("\n", "").strip())
                self.py_code += "\n" + indent_count*"\t"
                for sub in py_text:
                    if sub == '}':
                        self.py_code += '\n'
                        indent_count -= 1
                    elif sub == '{':
                        indent_count += 1
                        self.py_code += ":\n" + indent_count*"\t"
                    else:
                        self.py_code += sub
            self.py_code += "\n%s__html_code__ += '''%s'''\n" % (indent_count*"\t", text[right+2:])

    def assign(self, key, value):
        self.param_dic[key] = value

    def render(self):
        try:
            for k,v in self.param_dic.items():
                exec("%s=v" % k)
            exec(self.py_code)
            return __html_code__
        except Exception, e:
            return str(e)+ getTraceStackMsg()

# use example
# tpl = PyTpl(filepath="./test.html")
# data = []
# data.append({"id": 1, "abc": "name1", "arr1": [2,4,6,8,10]})
# data.append({"id": 2, "bcd": "name2", "arr2": [1,3,5,7,9]})
#
# tpl.assign("title", name)
# tpl.assign("data", data)
#
# tpl.render()

