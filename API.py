# -*- coding: utf-8 -*-
###############################################################################
# API for use yandexDISK
###############################################################################
import os
import urllib.request
import urllib.parse


class API_yDISK:
    def __init__(self):
        # http://api.yandex.ru/oauth/doc/dg/tasks/get-oauth-token.xml
        self.OAuth = " *** "

    def get_list(self):
        get_list_url = 'https://cloud-api.yandex.net:443/v1/disk/resources/?path=%2FAPI'
        result = []
        response = self.send_request(get_list_url, 'GET')
        resp_str = str(response.read())
        parse_list = resp_str[resp_str.find('{') + 1:resp_str.find('}]',
                              resp_str.find('{') + 1)].split('},{')
        for i in parse_list:
            result.append(self.PARSE(i))
        return result

    def get_download_link(self, download_file):
        # get public key
        get_public_url = 'https://cloud-api.yandex.net:443/v1/disk/resources/?path=%2FAPI%2F'
        download_file = urllib.parse.quote(download_file)
        resp_str = self.send_request(get_public_url + download_file, 'GET')
        resp_str = str(resp_str.read())
        public_key = resp_str[resp_str.find('"public_key') + 1:
                              resp_str.find('","',
                              resp_str.find('"public_key') + 1)].split('":"')[1]
        public_key = public_key.replace('/', '%2F')
        public_key = public_key.replace('=', '%3D')
        public_key = urllib.parse.quote(public_key)
        # get download link
        download_url = 'https://cloud-api.yandex.net:443/v1/disk/public/resources/download/?public_key='
        resp_str = self.send_request(download_url + public_key, 'GET')
        resp_str = str(resp_str.read())
        LINK = resp_str[resp_str.find('"href') + 1:
                        resp_str.find('","',
                        resp_str.find('"href') + 1)].split('":"')[1]
        return LINK

    def delete_file(self, delete_file):
        delete_url = 'https://cloud-api.yandex.net:443/v1/disk/resources/?path=%2FAPI%2F'
        delete_file = urllib.parse.quote(delete_file)
        self.send_request(delete_url + delete_file, 'DELETE')
        return True

    def upload_file(self, send_file):
        get_upload_url = 'https://cloud-api.yandex.net:443/v1/disk/resources/upload/?path=%2FAPI%2F'
        # get file size and file name
        file_name = urllib.parse.quote(send_file.filename)
        send_file.seek(0, os.SEEK_END)
        file_length = send_file.tell()
        send_file.seek(0)
        # get upload link #
        response = self.send_request(get_upload_url + file_name, 'GET')
        STR_resp = str(response.read())
        upload_url = STR_resp[STR_resp.find('"https') + 1:
                              STR_resp.find('","',
                              STR_resp.find('"https') + 1)]
        # send file
        req = urllib.request.Request(upload_url, data=send_file)
        req.get_method = lambda: 'PUT'
        req.add_header('Authorization', self.OAuth)
        req.add_header('Content-Length', file_length)
        urllib.request.urlopen(req)
        # create public link
        public_url = 'https://cloud-api.yandex.net/v1/disk/resources/publish/?path=%2FAPI%2F'
        self.send_request(public_url + file_name, 'PUT')
        return True

    def get_disk_size(self):
        root_url = 'https://cloud-api.yandex.net:443/v1/disk'
        response = self.send_request(root_url, 'GET')
        resp_str = str(response.read())
        #parse
        total_space = int(resp_str[resp_str.find('"total_space":') + 1:
                          resp_str.find(',"',
                          resp_str.find('"total_space":') + 1)].split(':')[1]
                          )
        used_space = int(resp_str[resp_str.find('"used_space":') + 1:
                         resp_str.find(',"',
                         resp_str.find('"used_space":') + 1)].split(':')[1]
                         )
        return str(self.bytes2human(used_space) + '/' +
                   self.bytes2human(total_space))

    def send_request(self, url, method):
        req = urllib.request.Request(url)
        req.get_method = lambda: method
        req.add_header('Authorization', self.OAuth)
        return urllib.request.urlopen(req)

    def PARSE(self, res):
        TYPE = res[res.find('"type') + 1:
                   res.find('","',
                   res.find('"type') + 1)].split('":"')[1]  # "type": "dir"
        if TYPE == 'file':
            NAME = res[res.find('"name') + 1:
                       res.find('","',
                       res.find('"name') + 1)].split('":"')[1]
            SIZE = res[res.find('","size') + 1:].split('":')[1]
            DATE_CREATE = res[res.find('"created') + 1:
                              res.find('","',
                              res.find('"created') + 1)].split('":"')[1]
            DATE_MODIFY = res[res.find('"modified') + 1:
                              res.find('","',
                              res.find('"modified') + 1)].split('":"')[1]
        return NAME, SIZE, DATE_CREATE, DATE_MODIFY

    def bytes2human(self, n):
        symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i + 1) * 10
        for s in reversed(symbols):
            if n >= prefix[s]:
                value = float(n) / prefix[s]
                return '%.2f%s' % (value, s)
        return "%sB" % n