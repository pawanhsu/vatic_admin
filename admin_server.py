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
from create_admin_video import *
from sqlalchemy import desc
from mail import sendmail
from hashlib import sha1
from time import gmtime, strftime
import datetime




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
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:1111@localhost/boxcheck"

db = SQLAlchemy(app)




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

    if request.args.has_key("video_name"):
        video = request.args['video_name']
        #print("hahahaha: {}".format(video))
        videos.remove(video)
        videos.insert(0, video)
        #user_name = session.query(User).first().username
    else:
        video = videos[0]
        #user_name = session.query(User).first().username

    segments = []
    frame_num = 0
    img_url = get_img_url(video, frame_num)
    annotation = annotations[video]

    for worker in annotation.workers:
        worker_video = session.query(Video).filter(Video.slug == worker + '_' + video).first()
        segment = session.query(Segment).filter(Segment.videoid == worker_video.id)
        segments.append({'worker': worker, "segment": segment})
        video_obj = session.query(Video).filter(Video.slug == worker + '_' + video).first()
        video_res = {'height':video_obj.height,'width':video_obj.width}

    #target_links = get_target_links(video, frame_num)
    target = {}
    check_boxes = {}
    checkbox_errors = error_checkbox.query.all()

    for checkbox in checkbox_errors:
        error = checkbox.video_name + '\t' + checkbox.box_owner + '\t' + \
                checkbox.box_reference + '\t\t' + checkbox.error_type + '\t' + \
                str(checkbox.error_begin) + '\t' + str(checkbox.error_end)
        check_boxes[error] = 1

    print(check_boxes)
    #{u'A2Streetnight.mp4\tSponge\tSpooky\tsurplus\t0\t66': 1, u'A2Streetnight.mp4\tSponge\tSpooky\tsurplus\t0\t59': 1, u'A2Streetnight.mp4\tSponge\tpwan\tsurplus\t0\t59': 1}
    check_boxes_segment = {}
    for error_data in check_box_DB_segment.all():
        segment_id = error_data["segment_id"]
        check_boxes_segment[segment_id] = 1


    admin_video = session.query(Video).filter(Video.user_id == 'max.hsu@ironyun.com', Video.slug == 'Max_'+video).order_by(desc(Video.id)).first()

    if admin_video != None:
        admin_segment = session.query(Segment).filter(Segment.videoid == admin_video.id).order_by(Segment.start)
    else:
        admin_segment = []
    #label = session.query(Label).distinct(Label.text).group_by(Label.text)
    #label = ['car' , 'person']
    return render_template('index.html', checkbox_errors=checkbox_errors,label=LABELS, img_url=img_url, videos=videos, frame_num=frame_num,
        target_links=target_links, errors=annotation.errors, vatic=VATIC_ADDRESS, \
        video_name=video, check_boxes=check_boxes, check_boxes_segment=check_boxes_segment,color_map=color_map, users=annotation.workers,video_res = video_res, \
        segments = segments, admin_segment = admin_segment)



@app.route('/users')
def user_manage():

    users = session.query(User).all()

    return render_template('user.html', users=users, vatic=VATIC_ADDRESS)

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







from checkbox_models import error_checkbox,segment_checkbox

@app.route('/box_check')
def box_check():
    global check_box_DB
    global check_box_DB_segment
    if request.method == 'GET':
        op_type = request.args['type']
        if(op_type == 'error'):
            error_id = request.args['id']
            action = request.args['action']

            #segment_id = request.args['segmentid']
            if action == "insert":
                #checkbox = checkbox()

                #check_box_DB.insert({"error_id":error_id})
                error_arr = error_id.split()
                error = error_checkbox(error_arr[0],error_arr[1],error_arr[2],error_arr[3],error_arr[4],error_arr[5])
                db.session.add(error)
                db.session.commit()


                print("Insert {} into DB".format(error_id))
                return jsonify(condition="successfully insert")

            elif action == "remove":
                error_arr = error_id.split()
                if(len(error_arr) == 7):
                    error = error_checkbox.query.filter_by(video_name = error_arr[0],box_owner = error_arr[1],\
                    box_reference = error_arr[2], error_type = error_arr[3], error_begin = error_arr[4],\
                    error_end = error_arr[5]).delete()
                else:
                    error = error_checkbox.query.filter_by(video_name = error_arr[0],box_owner = error_arr[1],\
                    box_reference = error_arr[2], error_type = error_arr[3], error_begin = error_arr[4],\
                    error_end = error_arr[5]).delete()
                db.session.commit()
                db.session.close()

                print("Remove {} from DB".format(error_id))
                return jsonify(condition="successfully remove")


        elif(op_type == 'segment'):
            segment_id = request.args['segmentid']
            action = request.args['action']
            video_name = request.args['videoname']

            if action == "insert":
                check_box_DB_segment.insert({"segment_id":segment_id,"videoname":video_name})
                print("Insert {} into DB".format(segment_id))
                return jsonify(condition="successfully insert")
            elif action == "remove":
                query = Query()
                check_box_DB_segment.remove(query.segment_id==segment_id)
                print("Remove {} from DB".format(segment_id))
                return jsonify(condition="successfully remove")


@app.route('/dump_segment')
def dump_segment():
    if request.method == 'GET':
        video = request.args['video_name']
        create_admin_video(video_name=video)

        return jsonify(condition="successfully dump segments")





def get_annotations():
    user_map = get_user_map()
    assignments = get_assignments(user_map)

    annotations = {video: Annotation(assignment, video) for video, assignment in assignments.items()}

    return annotations

@app.route('/verify_email')
def verify_email():
    print("verify mail")

    from mail import sendmail
    from hashlib import sha1
    from time import gmtime, strftime


    mail = request.args.get('mail')
    if mail == None or mail == "":
        return render_template("verify_resend.html")

    registered_users = session.query(User).filter(User.priority==0)
    user = None
    for current_user in registered_users:
        if current_user.id == mail:
            user = current_user
            break

    if user==None:
        message = "user not found."
        return render_template("verify.html", info=message)

    if user.verification == True:
        message = "your email address has already been verified."
        return render_template("verify.html", info=message)

    now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    token = sha1(now + "user " + user.id + "auth").hexdigest()

    update_user = session.query(User).filter(User.id == mail).\
            update({'token': token})
    session.commit()

    token_url = "http://"+EXT_ADDR+":"+str(PORT)+"/verify_email_input?token=" + token

    receivers = mail
    receiver_name = "vatic user"
    subject = 'Vatic - email confirm'

    content = render_template("mail_confirm.html", token_url = token_url)
    content_type = 'html'

    if sendmail(receivers, receiver_name, subject, content, content_type):
        message = "check out your mail inbox to verify the email address."
        return render_template("verify.html", info=message)

    else:
        message = "unable to send mail."
        return render_template("verify.html", info=message)

@app.route('/verify_email_input')
def verify_email_input():
    token = request.args.get('token')
    if token == None or token == "":
        message = "No required auth token input."
        return render_template("verify.html", info=message)

    user = list(session.query(User).filter(User.token == token))

    if len(user) == 0:

        message = "Token invalid. Go to <a href='/verify_email'>re-send page</a> to resend verification mail."
        return render_template("verify.html", info=message, vatic=VATIC_ADDRESS)

    if user[0].verification == True:
        message = "You has already verified your email address."
        return render_template("verify.html", info=message)

    user = session.query(User).filter(User.token == token).\
            update({'verification': True})
    session.commit()
    message = "email verification is succeed."
    return render_template("verify.html", info=message)

@app.route('/reset')
def reset_password():
    if not request.remote_addr in ALLOW_IP or "*" in ALLOW_IP:
        message = "not allow to use this function"
        return render_template("forget_message.html", info=message)
    mail = request.args.get('mail')
    if mail == None or mail == "":
        return render_template("forget_find.html")

    registered_users = session.query(User).filter(User.priority==0)
    user = None
    for current_user in registered_users:
        if current_user.id == mail:
            user = current_user
            break

    if user==None:
        message = "user not found."
        return render_template("forget_message.html", info=message)

    now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    token = sha1(now + "user" + user.id + "reset").hexdigest()

    expire_time = datetime.datetime.now() + datetime.timedelta(minutes = 30)
    update_user = session.query(User).filter(User.id == mail).\
            update({'forgetPasswordToken': token })
    update_user = session.query(User).filter(User.id == mail).\
            update({'forgetPasswordTokenExpireTime': expire_time})
    session.commit()

    token_url = "http://"+EXT_ADDR+":"+str(PORT)+"/reset_input?token=" + token

    receivers = mail
    receiver_name = "vatic user"
    subject = 'Vatic - password reset'

    content = render_template("mail_reset.html", token_url = token_url)
    content_type = 'html'

    if sendmail(receivers, receiver_name, subject, content, content_type):
        message = "check out your mail inbox to reset your password."
        return render_template("forget_message.html", info=message)

    else:
        message = "unable to send mail."
        return render_template("forget_message.html", info=message)

@app.route('/reset_input', methods=['GET', 'POST'])
def reset_input():
    token = request.args.get('token')
    if token == None or token == "":
        message = "No required reset token input."
        return render_template("forget_message.html", info=message)

    user = list(session.query(User) \
            .filter(User.forgetPasswordToken == token) \
            .filter(User.forgetPasswordTokenExpireTime >= datetime.datetime.now()))

    if len(user) == 0:
        message = "Token invalid. Go to <a href='/reset'>re-send page</a> to resend verification mail."
        return render_template("forget_message.html", info=message)

    new_pass = request.form.get('password')
    if new_pass== None or new_pass == "":
        return render_template("forget_set.html", token=token, username=user[0].username)

    user = session.query(User) \
            .filter(User.forgetPasswordToken == token) \
            .filter(User.forgetPasswordTokenExpireTime >= datetime.datetime.now()) \
            .update({'password': new_pass, 'forgetPasswordToken': None, 'forgetPasswordTokenExpireTime': None})
    session.commit()
    message = "password update successful."
    return render_template("forget_message.html", info=message)



if __name__ == "__main__":
    #dump_user_map()
    EXT_ADDR = os.environ.get('EXTERNAL_ADDRESS')
    if EXT_ADDR == None:
        EXT_ADDR = "172.16.22.51"
    VATIC_ADDRESS = "http://"+EXT_ADDR+":8892"
    DUMP_TXT_DATA()
    user_map = get_user_map()
    assignments = get_assignments(user_map)

    annotations = {video: Annotation(assignment, video) for video, assignment in assignments.items()}
    workers = get_workers(user_map)
    color_map = get_color_map(workers)
    check_box_DB =  TinyDB("check_box_db.json")
    check_box_DB_segment = TinyDB("check_box_db_segment.json")
    app.run(host='0.0.0.0',debug=DEBUG,threaded=False, port=PORT)
