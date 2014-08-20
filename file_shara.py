#!/usr/local/bin/python3.3
from flask import Flask, url_for, render_template, request
from flask import redirect
from werkzeug.contrib.fixers import ProxyFix
import urllib
import urllib.request
import urllib.parse
import os

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
OAuth = " *** "		# http://api.yandex.ru/oauth/doc/dg/tasks/get-oauth-token.xml


@app.errorhandler(404)
def err_not_found(error):
    return 'WTF 404, %s, спробуй ще' % error


@app.errorhandler(500)
def err_server(error):
    return 'WTF 500, %s' % error


#-----------------------------------------------------------------------
#-------------------- API ---------------------

@app.route('/', methods=['POST', 'GET'])
def APIgetList():
    URL_GET_LIST = 'https://cloud-api.yandex.net:443/v1/disk/resources/?path=%2FAPI'
    pLIST = []

    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename

        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)

        # GET LINK
        URL_UPLOAD = 'https://cloud-api.yandex.net:443/v1/disk/resources/upload/?path=%2FAPI%2F'
        URL_UPLOAD += filename

        response = REQUEST(URL_UPLOAD, 'GET')
        STR_resp = str(response.read() )

        link_upload = STR_resp[ STR_resp.find('"https')+1  :  STR_resp.find('","', STR_resp.find('"https')+1) ]

        # PUT
        req = urllib.request.Request(link_upload, data=file)
        req.get_method = lambda: 'PUT'
        req.add_header('Authorization', OAuth)
        req.add_header('Content-Length', file_length)
        response = urllib.request.urlopen(req)

        return redirect(url_for('APIgetList'))


    # GET list
    response = REQUEST(URL_GET_LIST, 'GET')
    STR_resp = str(response.read() )
    parse_list = STR_resp[  STR_resp.find('{')+1  :  STR_resp.find('}]', STR_resp.find('{')+1)  ].split('},{')

    for i in parse_list:
        pLIST.append( PARSE(i) )

    return render_template('downloadAPI.html', files=pLIST, diskSIZE = 'API yDISK' )


@app.route('/download/<filename>')
def APIdownload(filename):
    URL_DOWNLOAD = 'https://cloud-api.yandex.net:443/v1/disk/resources/?path=%2FAPI'

    response = REQUEST(URL_DOWNLOAD, 'GET')
    resp_str = str( response.read() )

    parse_list = resp_str[  resp_str.find('{')+1  :  resp_str.find('}]', resp_str.find('{')+1)  ].split('},{')
    LINK =''
    for i in parse_list:
        NAME = i[  i.find('"name')+1  :  i.find('","', i.find('"name')+1)  ].split('":"')[1]  # "name": "filename"
        if NAME == filename:
            LINK = i[  i.find('"public_url')+1  :  i.find('","', i.find('"public_url')+1)  ].split('":"')[1]

    return redirect( LINK )


@app.route('/delete/<filename>', methods=['GET', 'DELETE'])
def APIdelete(filename):
    URL_DELETE = 'https://cloud-api.yandex.net:443/v1/disk/resources/?path=%2FAPI%2F'
    URL_DELETE += filename

    response = REQUEST(URL_DELETE, 'DELETE')

    return redirect( url_for('APIgetList') )
#---------------- DEF ----------------------------
def REQUEST(url, method):
    req = urllib.request.Request(url)
    req.get_method = lambda: method
    req.add_header('Authorization', OAuth)
    return urllib.request.urlopen(req)


def PARSE(res):
    TYPE = res[  res.find('"type')+1  :  res.find('","', res.find('"type')+1)  ].split('":"')[1]  # "type": "dir"
    if TYPE == 'file':
        NAME = res[  res.find('"name')+1  :  res.find('","', res.find('"name')+1)  ].split('":"')[1].encode('latin-1').decode('utf-8')
        SIZE = res[  res.find('","size')+1  :  res.find('","', res.find('","size')+1)  ].split('":')[1]
        DATE_CREATE = res[  res.find('"created')+1  :  res.find('","', res.find('"created')+1)  ].split('":"')[1]
        DATE_MODIFY = res[  res.find('"modified')+1  :  res.find('","', res.find('"modified')+1)  ].split('":"')[1]

    return NAME, SIZE, DATE_CREATE, DATE_MODIFY

#-----------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)