import os
from subprocess import check_output, call
from flask import Flask, render_template, make_response, request, render_template_string, jsonify, redirect
from scipy.misc import imread
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import uuid
import cStringIO
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import requests
from urllib import urlencode
import json
from operator import itemgetter
from itertools import groupby
from collections import OrderedDict
from tinydb import TinyDB, Query
from PIL import Image
from annotation import Annotation
from config import *
from branch_dependent_utils import *
from dbio_Inf import *




#OLD functions thar are goging to deprecate












parse_ID = lambda new_ID: new_ID.split("_")




def frame_to_path(video_name, frame_num, img_path="vatic-docker/data/frames_in"):
    dir_A = str(int(frame_num / 10000))
    dir_B = str(int(frame_num / 100))
    path = os.path.join(img_path, video_name,  dir_A, dir_B, "{}.jpg".format(frame_num))
    print(path)
    return path

def get_color_map(workers):
    colors = ["red", "green", "blue", "yellow", "white", "pink", "orange"]
    color_map = {}

    for i, worker in enumerate(sorted(workers)):
        color_map[worker] = colors[i]

    return color_map




def get_img_url(video_name, frame_num, base_url = "/image"):
    return "{}?video_name={}&frame_num={}".format(base_url, video_name, frame_num)



app = Flask(__name__)
app.debug = False
import os
from flask import send_from_directory






@app.route("/alert_boxes")
def get_alert_boxes():



    video = request.args['video']
    frame = int(request.args['frame'])

    annotation = annotations[video]
    alert = annotation.alerts.get(frame, {})


    isolations = alert.get("isolated", {})
    unmatchings = alert.get("label-distinct", [])


    alert_boxes_dict = {}

    for path_ID in isolations:
        box = annotation.paths[path_ID][frame]
        alert_boxes_dict[path_ID] = box


    for path_ID_A,  path_ID_B in unmatchings:
        box_A = annotation.paths[path_ID_A][frame]
        box_B = annotation.paths[path_ID_B][frame]
        alert_boxes_dict[path_ID_A] = box_A
        alert_boxes_dict[path_ID_B] = box_B
    alert_boxes = []

    for path_ID, box in alert_boxes_dict.items():
        worker, box_id = parse_ID(path_ID)
        box["source"] = worker
        box["id"] = box_id
        alert_boxes.append(box)


    return jsonify(alert_boxes)





#Create Static_root for Statistic files
@app.route('/frames/<frame_number>/<video_name>')
def video_frame(frame_number,video_name):
    filename = frame_number + '.jpg'
    last_folder = int(frame_number)/100
    root = os.getcwd()
    path = root + '/vatic-docker/data/frames_in/' + video_name + '/0/' + str(last_folder)
    print(path)
    return send_from_directory(path,filename)


def get_next_frame(video_name, old_frame):
    #A bug of overflowing lies in here
    return old_frame +1


def get_previous_frame(video_name, old_frame):
    if old_frame > 0:
        return old_frame - 1
    else:
        return 0



@app.route('/seek')
def seek_frame():
    if request.method == 'GET':
        video_name = request.args['video']
        target_frame = int(request.args['frame'])
        img_url = get_img_url(video_name, target_frame)
        target_links = get_target_links(video_name, target_frame)
    return jsonify(img_url=img_url, frame_num=target_frame, target_links=target_links)



@app.route('/previous')
def go_previous():
    if request.method == 'GET':
        video_name = request.args['video']
        current_frame = int(request.args['frame'])
        previous_frame = get_previous_frame(video_name, current_frame)


        img_url = get_img_url(video_name, previous_frame)
        target_links = get_target_links(video_name, previous_frame)
    return jsonify(img_url=img_url, frame_num=previous_frame, target_links=target_links)


@app.route('/next')
def go_next():
    if request.method == 'GET':
        video_name = request.args['video']
        print(video_name)
        current_frame = int(request.args['frame'])
        next_frame = get_next_frame(video_name, current_frame)
        img_url = get_img_url(video_name, next_frame)
        target_links = get_target_links(video_name, next_frame)
    return jsonify(img_url=img_url, frame_num=next_frame, target_links=target_links)



@app.route('/update')
def update():
    video = request.args['video_name']
    global annotations
    annotations[video].update()
    return redirect("./?video_name={}".format(video))


@app.route('/multiclass_filter')
def multiclass_filter():
    global annotations
    selected_class = request.args['selected_class']
    video = request.args['video']
    selected_list = selected_class.split(",")
    annotations[video].filter(selected_list)
    return redirect("./?video_name={}".format(video))


@app.route('/')
def index():

    global check_box_DB
    global annotations
    videos = get_videos(user_map)
    print(request.args)
    if request.args.has_key("video_name"):
        print(videos)
        video = request.args['video_name']
        print("hahahaha: {}".format(video))
        videos.remove(video)
        videos.insert(0, video)
        user_name = session.query(User).first().username
        video_res = session.query(Video).filter(Video.slug == user_name + '_' + video).first()
        video_res = {'height':video_res.height,'width':video_res.width}
        print(1111)
        print(video_res)

    else:
        video = videos[0]
        user_name = session.query(User).first().username
        print(video)
        video_res = session.query(Video).filter(Video.slug == user_name + '_' + video).first()
        video_res = {'height':video_res.height,'width':video_res.width}
        print(22222)
        print(video_res)

    frame_num = 0
    img_url = get_img_url(video, frame_num)
    annotation = annotations[video]
    print(annotation.video)



    target_links = get_target_links(video, frame_num)
    check_boxes = {}
    for error_data in check_box_DB.all():
        error_id = error_data["error_id"]
        check_boxes[error_id] = 1

    #label = session.query(Label).distinct(Label.text).group_by(Label.text)
    #label = ['car' , 'person']




    return render_template('index.html', label=LABELS, img_url=img_url, videos=videos, frame_num=frame_num,
        target_links=target_links, errors=annotation.errors, \
        video_name=video, check_boxes=check_boxes, color_map=color_map, users=annotation.workers,video_res = video_res)


@app.route('/frames', methods=['GET'])
def get_frame():

    video_name = request.args.get('video')
    if video_name == None:
        return jsonify(success=False, message="no video name input")

    frames = {}


    for frame_key in annotations[video_name].alerts:
    #frame_key = 0
    #while True:
        frames[frame_key] = {}
        frame = frames[frame_key]

        #frame["alert"] = alert_frames[frame_key]
        #What is this?
        frame["alert"] = []
        frame["frame_num"] = frame_key
        frame["img_url"] = get_img_url(video_name, frame_key)
        frame["target_links"] = get_target_links(video_name, frame_key)
        #  break;
        frame_key = 0
        frames[frame_key] = {}
        frame = frames[frame_key]

        frame["alert"] = {}
        frame["frame_num"] = frame_key
        frame["img_url"] = get_img_url(video_name, frame_key)
        frame["target_links"] = get_target_links(video_name, frame_key)
    if len(frames)==0:
        frame_key = 0
        frames[frame_key] = {}
        frame = frames[frame_key]

        frame["alert"] = {}
        frame["frame_num"] = frame_key
        frame["img_url"] = get_img_url(video_name, frame_key)
        frame["target_links"] = get_target_links(video_name, frame_key)


    response_data = {"success": True, "data": frames}
    return jsonify(response_data)








@app.route('/box_check')
def box_check():
    global check_box_DB
    if request.method == 'GET':
        error_id = request.args['id']
        action = request.args['action']

        if action == "insert":
            check_box_DB.insert({"error_id":error_id})
            print("Insert {} into DB".format(error_id))
            return jsonify(condition="successfully insert")

        elif action == "remove":
            query = Query()
            check_box_DB.remove(query.error_id==error_id)
            print("Remove {} from DB".format(error_id))

            return jsonify(condition="successfully remove")




if __name__ == "__main__":
    #dump_user_map()
    EXT_ADDR = os.environ.get('EXTERNAL_ADDRESS')
    if EXT_ADDR == None:
        EXT_ADDR = "172.16.12.91"
    VATIC_ADDRESS = "http://"+EXT_ADDR+":8892"
    DUMP_TXT_DATA()
    user_map = get_user_map()
    assignments = get_assignments(user_map)

    annotations = {video: Annotation(assignment, video) for video, assignment in assignments.items()}
    workers = get_workers(user_map)
    color_map = get_color_map(workers)
    check_box_DB =  TinyDB("check_box_db.json")
    app.run(host='0.0.0.0',debug=DEBUG,threaded=True, port=PORT)
