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
from flask_cors import CORS


import zipfile
import plistlib
import subprocess
import json
import datetime
import sys,os,re

app = Flask(__name__)
CORS(app)


APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
ipaPath = os.path.join(APP_ROOT, 'static/hello_world.ipa') #设置一个专门的类似全局变量的东西

# 文件上传目录
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
# 支持的文件格式
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif','txt','ipa'}  # 集合类型
app.config['UPLOAD_PATH'] = 'uploads'

#@app.route('/')
#def hello_world():
#   return 'Hello World!'

# 判断文件名是否是我们支持的格式
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


# 解压ipa获取并信息
def unzip_ipa(path):
    ipa_file = zipfile.ZipFile(path)
    plist_path = find_path(ipa_file, 'Payload/[^/]*.app/Info.plist')
    # 读取plist内容
    plist_data = ipa_file.read(plist_path)
    # 解析plist内容
    plist_info = plistlib.loads(plist_data)
    
    # 获取mobileprovision文件路径
    provision_path = find_path(ipa_file, 'Payload/[^/]*.app/embedded.mobileprovision')
    provision_data = ipa_file.read(provision_path)
    mobileprovision_info=get_mobileprovision(provision_data)
    
    fsize = os.path.getsize(path)
    f_M = fsize/float(1024*1024)
    plist_info["filesize"]=str(format(f_M,'.2f'))
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
    print("99999999999999")
    print("request.args:"+str(request.args))
    print(request.files)
    appDict={'BuildMachineOSBuild': '20E232', 'CFBundleDevelopmentRegion': 'en', 'CFBundleDisplayName': '乐牛SDK', 'CFBundleExecutable': 'XianGongZhanJiSDK_Demo', 'CFBundleIcons': {'CFBundlePrimaryIcon': {'CFBundleIconFiles': ['AppIcon20x20', 'AppIcon29x29', 'AppIcon40x40', 'AppIcon60x60'], 'CFBundleIconName': 'AppIcon'}}, 'CFBundleIcons~ipad': {'CFBundlePrimaryIcon': {'CFBundleIconFiles': ['AppIcon20x20', 'AppIcon29x29', 'AppIcon40x40', 'AppIcon60x60', 'AppIcon76x76', 'AppIcon83.5x83.5'], 'CFBundleIconName': 'AppIcon'}}, 'CFBundleIdentifier': 'com.kyren.LNGame', 'CFBundleInfoDictionaryVersion': '6.0', 'CFBundleName': 'XianGongZhanJiSDK_Demo', 'CFBundlePackageType': 'APPL', 'CFBundleShortVersionString': '1.0', 'CFBundleSupportedPlatforms': ['iPhoneOS'], 'CFBundleVersion': '1', 'DTCompiler': 'com.apple.compilers.llvm.clang.1_0', 'DTPlatformBuild': '19C51', 'DTPlatformName': 'iphoneos', 'DTPlatformVersion': '15.2', 'DTSDKBuild': '19C51', 'DTSDKName': 'iphoneos15.2', 'DTXcode': '1321', 'DTXcodeBuild': '13C100', 'LSRequiresIPhoneOS': True, 'MinimumOSVersion': '10.0', 'NSAppTransportSecurity': {'NSAllowsArbitraryLoads': True}, 'NSAppleMusicUsageDescription': '应用通过访问您的照片权限来使用头像上传功能', 'NSCameraUsageDescription': '应用通过访问您的摄像头权限来使用头像拍摄功能', 'NSLocationWhenInUseUsageDescription': '应用希望通过获得您的位置定位权限来使用附近的人的功能', 'NSMicrophoneUsageDescription': '应用希望通过获得您的麦克风权限来使用语音功能', 'NSPhotoLibraryAddUsageDescription': '应用希望通过访问您的照片权限来为您保存游客账号信息', 'NSPhotoLibraryUsageDescription': '应用通过访问您的照片权限来使用头像上传功能', 'NSSpeechRecognitionUsageDescription': '应用希望通过获得您的麦克风权限来使用语音功能', 'NSUserTrackingUsageDescription': '应用希望通过访问您的广告标识符权限来追踪广告和推送您喜欢的内容', 'UIApplicationSupportsIndirectInputEvents': True, 'UIDeviceFamily': [1, 2], 'UILaunchStoryboardName': 'LaunchScreen', 'UIMainStoryboardFile': 'Main', 'UIRequiredDeviceCapabilities': ['armv7'], 'UISupportedInterfaceOrientations': ['UIInterfaceOrientationLandscapeLeft', 'UIInterfaceOrientationLandscapeRight'], 'UISupportedInterfaceOrientations~ipad': ['UIInterfaceOrientationPortrait', 'UIInterfaceOrientationPortraitUpsideDown', 'UIInterfaceOrientationLandscapeLeft', 'UIInterfaceOrientationLandscapeRight'], 'filesize': '3.96'}
    return json.dumps(appDict)
    
#   for item in request.files:
#       print(item)
#       
#   plist_info=None
#   if request.files:
#       uploaded_file = request.files['file']
#       if uploaded_file:
#           (plist_info,mobileprovision_info)=unzip_ipa(ipaPath)
#           print(plist_info)
#   return make_response(plist_info)


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
    
    