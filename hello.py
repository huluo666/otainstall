from flask import Flask
from flask import render_template, make_response, send_file

app = Flask(__name__)

#@app.route('/')
#def hello_world():
#   return 'Hello World!'


#首页
@app.route('/')
def index():
    return render_template('ipa_install.html')


#手机访问的下载包路径
@app.route('/ipa.html')
def ipa_install():
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
    app.run()
    