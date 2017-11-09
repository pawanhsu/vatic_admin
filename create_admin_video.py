from dbconnect import *
from dbmodels import *
from sqlalchemy.orm.session import make_transient
from tinydb import TinyDB, Query
from branch_dependent_utils import *
from admin_server import *
from sqlalchemy.sql import func
from subprocess import call
import time
from config import *


def load_admin_video(video_name,labels):

    ANNOTATEDFRAMEPATH= "/root/vatic/data/frames_in/" + video_name
    slug = ADMIN_NAME + '_' + video_name

    TURKOPS="--offline --title Hello!"
    vatic_path = "/root/vatic"

    delete_cmd = "cd {}; turkic delete {}".format(vatic_path,slug)
    create_cmd = "cd {}; turkic load {} {} {} {} {}".format(vatic_path,slug, ADMIN_ID,ANNOTATEDFRAMEPATH, labels, TURKOPS)
    cmd = ['docker', 'exec', CONTAINER_NAME, "/bin/bash", '-c', delete_cmd]
    call(cmd)
    cmd = ['docker', 'exec', CONTAINER_NAME, "/bin/bash", '-c', create_cmd]
    print(" ".join(cmd))
    call(cmd)



def create_admin_video(admin_name = "Max",video_name="jacksonhole.mp4"):

    check_box_DB_segment = TinyDB("check_box_db_segment.json")

    #get annotation info
    annotations = get_annotations()
    annotation = annotations[video_name]
    #get admin info
    admin = session.query(User).filter(User.username == admin_name).first()
    admin_id = admin.id
    admin_name = admin.username
    #max id: primary key duplication issue
    max_video_id = session.query(func.max(Video.id).label("max_id")).one()

    #create video object for admin
    sample_video = session.query(Video).filter(Video.slug == annotation.workers[0] + '_' + video_name).first()
    sample_labels = session.query(Label).filter(Label.videoid == sample_video.id).all()
    labels = ""
    for sample_label in sample_labels:
        labels = labels + sample_label.text + " "
    load_admin_video(video_name,labels)
    session.commit()


    target_video = session.query(Video).filter(Video.slug == admin_name + '_' + video_name).first()

    query = Query()

    segments = check_box_DB_segment.search(query.videoname == video_name)
    #create segment object for admin
    for segment in segments:
        #print(1)
        sample_segment = session.query(Segment).filter(Segment.id == segment["segment_id"]).first()
        target_segment = session.query(Segment).filter(Segment.videoid == target_video.id, Segment.start == sample_segment.start).first()

        jobs = session.query(Job).filter(Job.segmentid == segment["segment_id"]).all()
        for job in jobs:
            target_job = session.query(Job).filter(Job.segmentid == target_segment.id).first()

            paths = session.query(Path).filter(Path.jobid == job.id).all()
            #print("job")
            #print(temp_jobid)
            for path in paths:

                temp_pathid = path.id
                session.expunge(path)
                make_transient(path)
                max_path_id = session.query(func.max(Path.id).label("max_id")).one()
                path.id = max_path_id.max_id + 1
                path.jobid = target_job.id
                label_text = session.query(Label).filter(Label.id == path.labelid).first().text
                label = session.query(Label).filter(Label.videoid == target_video.id, Label.text == label_text).first().id
                path.labelid = label

                new_path = Path(id = max_path_id.max_id + 1, jobid = target_job.id, labelid = label)

                session.add(new_path)
                session.commit()

                boxes = session.query(Box).filter(Box.pathid == temp_pathid).all()

                for box in boxes:
                    print(box.frame)
                    session.expunge(box)
                    make_transient(box)
                    max_box_id = session.query(func.max(Box.id).label("max_id")).one()
                    box.id = max_box_id.max_id + 1
                    box.pathid = path.id
                    #print(path.id)
                    session.add(box)
                    session.commit()

def create_admin_video_entry(video_name,labels):

    ADMIN_NAME = 'Max'
    userid = 'max.hsu@ironyun.com'
    ANNOTATEDFRAMEPATH= "/root/vatic/data/frames_in/" + video_name
    slug = ADMIN_NAME + '_' + video_name


    TURKOPS="--offline --title Hello!"
    vatic_path = "/root/vatic"

    delete_cmd = "cd {}; turkic delete {}".format(vatic_path,slug)
    create_cmd = "cd {}; turkic load {} {} {} {} {}".format(vatic_path,slug, user_id ,ANNOTATEDFRAMEPATH, labels, TURKOPS)
    cmd = ['docker', 'exec', CONTAINER_NAME, "/bin/bash", '-c', delete_cmd]
    call(cmd)
    cmd = ['docker', 'exec', CONTAINER_NAME, "/bin/bash", '-c', create_cmd]
    print(" ".join(cmd))
    call(cmd)



if __name__ == "__main__":
    create_admin_video()
