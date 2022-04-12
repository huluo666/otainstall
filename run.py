#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2022/3/20
# @Author  : jenkins
# @Version : V1.0
# @Features: OTA分发下载

from flask import Flask
from flask import render_template, make_response, send_file
from flask import request, redirect, url_for,session
from flask import make_response
import zipfile
import plistlib
import subprocess
import json
import datetime
import sys,os,re
import io

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
defaultIpaPath = os.path.join(APP_ROOT, 'static/hello_world.ipa') #设置一个专门的类似全局变量的东西
# 文件上传目录
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
# 支持的文件格式
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif','txt','ipa'}  # 集合类型
app.config['UPLOAD_PATH'] = 'uploads'


print(APP_ROOT)
#@app.route('/')
#def hello_world():
#   return 'Hello World!'

# 判断文件名是否是我们支持的格式
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def get_size(fobj):
    if fobj.content_length:
        return fobj.content_length
    try:
        pos = fobj.tell()
        fobj.seek(0, 2)  #seek to end
        size = fobj.tell()
        fobj.seek(pos)  # back to original position
        return size
    except (AttributeError, IOError):
        pass
        
    # in-memory file object that doesn't support seeking or tell
    return 0  #assume small enough

# 解压ipa获取并信息
def unzip_ipa(file):
    ipa_file = zipfile.ZipFile(file, 'r')
#   ipa_file = zipfile.ZipFile(file)    
    plist_path = find_path(ipa_file, 'Payload/[^/]*.app/Info.plist')
    # 读取plist内容
    plist_data = ipa_file.read(plist_path)
    # 解析plist内容
    plist_info = plistlib.loads(plist_data)
    
    # 获取mobileprovision文件路径
    provision_path = find_path(ipa_file, 'Payload/[^/]*.app/embedded.mobileprovision')
    provision_data = ipa_file.read(provision_path)
    mobileprovision_info=get_mobileprovision(provision_data)
##   file.seek(0, os.SEEK_END)
##   size = file.tell()
##   zip_M = float(size) / float(1000*1000)  # MB
#   plist_info["filesize"]=str(format(zip_M,'.2f'))
    return (plist_info,mobileprovision_info)


def get_mobileprovision(content):
        provision_xml_rx = re.compile(br'<\?xml.+</plist>', re.DOTALL)
        match = provision_xml_rx.search(content)
        if match:
            xml_content = match.group()
            data = plistlib.loads(xml_content)
            #移除无用信息（影响阅读~）          
            data.setdefault("DeveloperCertificates","")
            data.setdefault("DER-Encoded-Profile","")
            del data["DeveloperCertificates"]
            del data["DER-Encoded-Profile"]
            return data
        else:
            return None 
    
# 获取plist路径
def find_path(zip_file, pattern_str):
    name_list = zip_file.namelist()
    pattern = re.compile(pattern_str)
    for path in name_list:
        m = pattern.match(path)
        if m is not None:
            return m.group()
        

#首页
@app.route("/", methods=["GET", "POST"])
def index():
    print("request.args:"+str(request.args))
    (plist_info,mobileprovision_info)=(None,None)
    return render_template('ipa_install.html',data=plist_info)


@app.route("/upload_file", methods=["GET", "POST"])
def upload_file():
    print("upload_fileAction")
    plist_info={};
    if request.files:
        print(request.files)
        print("======request.files========")
        file = request.files['file']
        print(file)
        if file:
            #保存文件           
            filename = file.filename        
#           file_like_object=io.BytesIO(file.read())
#           unzip_ipa(file)
#           (plist_info,mobileprovision_info)=unzip_ipa(file_like_object)
#           print(plist_info)
            
            upload_filePath=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(upload_filePath)            
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ipaPath= os.path.join(APP_ROOT,upload_filePath) #设置一个专门的类似全局变量的东西
            print(f"ipaPath:{ipaPath}")  
            (plist_info,mobileprovision_info)=unzip_ipa(ipaPath)
            print(plist_info)            
            return json.dumps(plist_info)
    else:
        return json.dumps(plist_info)


#手机访问的下载包路径
@app.route('/ipa')
def ipa_install():
    print("request.argsipa:"+str(request))
    print("session:"+session.get('name'))
    return render_template('ipa_install.html')

#分发机制文件的路径
@app.route('/manifest.plist')
def manifest_plist():
    return render_template('manifest.plist')

#分发文件内ipa包的路径
@app.route('/hello_world.ipa')
def download():
    response = make_response(send_file(hello_world.ipa))    #send_file内填写ipa包路径
    response.headers["Content-Disposition"] = "attachment; filename=hello_world.ipa;"
    return response

    
if __name__ == '__main__':
    app.run(debug=True)
    
    