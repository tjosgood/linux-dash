#!/usr/bin/env python

from __future__ import print_function
import os
import sys
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer, test as _test
import subprocess
from SocketServer import ThreadingMixIn
import argparse
import json
import time

map = {
    "gpu_temp" : lambda: get_nvidia_smi("gpu_temp"),
    "gpu_util" : lambda: get_nvidia_smi("gpu_util"),
    "gpu_mem" : lambda: get_nvidia_smi("gpu_mem"),
    "gpu_power" : lambda: get_nvidia_smi("gpu_power"),
    "gpu_all" : lambda: get_nvidia_smi("gpu_all"),
    "all_stats": lambda: all_stats(),
}

parser = argparse.ArgumentParser(description='Simple Threaded HTTP server to run linux-dash.')
parser.add_argument('--port', metavar='PORT', type=int, nargs='?', default=80,
                    help='Port to run the server on.')

modulesSubPath = '/server/linux_json_api.sh'
appRootPath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class MainHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            data = ''
            contentType = 'text/html'
            if self.path.startswith("/server/"):
                module = self.path.split('=')[1]
                if module in map.keys():
                    data = json.dumps(map[module]())
                else:
                    data = call_bash(module,"text")
            else:
                if self.path == '/':
                    self.path = 'index.html'
                f = open(appRootPath + os.sep + self.path)
                data = f.read()
                if self.path.startswith('/linuxDash.min.css'):
                    contentType = 'text/css'
                f.close()
            self.send_response(200)
            self.send_header('Content-type', contentType)
            self.end_headers()
            self.wfile.write(data)

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

def call_bash(module,format="json"):
    output = subprocess.Popen(
        appRootPath + modulesSubPath + " " + module,
        shell=True,
        stdout=subprocess.PIPE)

    if format=="json":
        return json.loads(output.communicate()[0])
    else:
        return output.communicate()[0]

def all_stats():

    res = get_nvidia_smi("gpu_all")

    info = call_bash("load_avg")
    for k,v in info.items():
        res["cpu_"+k] = v

    info = call_bash("load_avg")
    for k, v in info.items():
        res["cpu_load_" + k.lower()] = v

    info = call_bash("cpu_temp")
    for k, v in info.items():
        res["cpu_temp_" + k.lower()] = v

    info = call_bash("current_ram")
    for k, v in info.items():
        res["ram_" + k.lower()] = v

    return res


def get_nvidia_smi(type):
    cachelife = 1

    if not hasattr(get_nvidia_smi, '_cache'):
        get_nvidia_smi._cache = {}

    if (time.time() - get_nvidia_smi._cache.get("time", 0)) > cachelife:
        res = subprocess.check_output(["nvidia-smi",
                                       "--query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw,power.limit",
                                       "--format=csv,noheader"])
        res = res.replace(" W", "").replace(" %", "").replace(" MiB", "").strip()
        res = [x.split(",") for x in res.split("\n")]
        keys = [x[1][:15].strip() + " " + x[0] for x in res]

        data = {
            "gpu_temp": {keys[i]: float(res[i][2]) for i in range(len(keys))},
            "gpu_util": {keys[i]: float(res[i][3]) for i in range(len(keys))},
            "gpu_mem": {keys[i]: float(res[i][4]) / float(res[i][5]) * 100 for i in range(len(keys))},
            "gpu_power": {keys[i]: float(res[i][6]) for i in range(len(keys))}
        }

        measures = data.keys()
        data["gpu_all"] = {}

        for k in measures:
            data["gpu_all"][k + "_max"] = max(data[k].values())
            data["gpu_all"][k + "_avg"] = sum(data[k].values()) / len(keys)

        get_nvidia_smi._cache = {"time": time.time(), "data": data}
    else:
        data = get_nvidia_smi._cache["data"]

    return data[type]

if __name__ == '__main__':
    args = parser.parse_args()
    server = ThreadedHTTPServer(('0.0.0.0', args.port), MainHandler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()
