import flask
from flask import request, jsonify, render_template
import requests
import tempfile
import webvtt
import time

app = flask.Flask(__name__)
app.config['DEBUG'] = True

@app.route('/', methods=['GET'])
def home():
    return 'use /api/&lt;videoid&gt;/&lt;word&gt; to get timestamps for &lt;word&gt;'
    # return render_template('index.html')

@app.route('/api/<videoid>/<word>', methods=['GET'])
def get_loc(videoid, word):
    d = {}
    d['output'] = []

    vtt = requests.get(f'https://invidio.us/api/v1/captions/{videoid}?label=English')
    if not vtt.text:
        d['status'] = 0
        d['message'] = 'No captions found'
        return jsonify(d)

    f = tempfile.NamedTemporaryFile(mode = 'w')
    # print(vtt.text)
    f.write(vtt.text)
    f.seek(0)
    # print(f.name)
    flag = 0
    #temp_url = f'https://youtube.com/watch?v={videoid}&t={total_secs}' 
    try:
        for caption in webvtt.read(f.name):
            if word in caption.text.lower():
                #d['output'].append(caption.start)
                temp_str = caption.start.split('.')[0] 
                #00:01:29.856
                time_obj = time.strptime(temp_str, '%H:%M:%S')
                total_secs = int(time.strftime("%H", time_obj)) * 3600 + int(time.strftime("%M", time_obj)) * 60 + int(time.strftime("%S", time_obj))
                temp_url = f'https://youtube.com/watch?v={videoid}&t={total_secs}' 
                d['output'].append(temp_url)
                flag = 1
                # print(caption.start)
                # print(caption.end)
                # print(caption.text)
    except Exception as e:
        print(e)
    finally:
        f.close()

    if flag:
        d['status'] = 1
        d['message'] = 'Captions found'
    else:
        d['status'] = 0
        d['message'] = 'Word not found'

    return jsonify(d)

app.run(host='0.0.0.0', port='9001')
# app.run()

# Reference:
# https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
