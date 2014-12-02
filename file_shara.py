#!/usr/local/bin/python3.3
from flask import Flask, url_for, render_template, request
from flask import redirect
from werkzeug.contrib.fixers import ProxyFix

from API import API_yDISK

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)


###############################################################################
# error's
###############################################################################
@app.errorhandler(404)
def err_not_found(error):
    return 'WTF 404, %s, спробуй ще' % error


@app.errorhandler(500)
def err_server(error):
    return 'WTF 500, %s' % error


###############################################################################
# main
###############################################################################
api = API_yDISK()


@app.route('/', methods=['POST', 'GET'])
def APIgetList():
    # send file to yandex disk
    if request.method == 'POST':
        ufile = request.files['file']
        api.upload_file(ufile)
        return redirect(url_for('APIgetList'))
    # GET list
    pLIST = api.get_list()
    return render_template('downloadAPI_fs.html',
                           files=pLIST,
                           diskSIZE=api.get_disk_size())


@app.route('/download/<filename>')
def APIdownload(filename):
    download_link = api.get_download_link(filename)
    return redirect(download_link)


@app.route('/delete/<filename>', methods=['GET', 'DELETE'])
def APIdelete(filename):
    api.delete_file(filename)
    return redirect(url_for('APIgetList'))

#-----------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)