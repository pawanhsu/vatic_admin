from subprocess import call
from config import *
CONTAINER_NAME = "VATIC"
def create_admin_video_entry(video_name,labels):

    ADMIN_NAME = 'Max'
    userid = 'max.hsu@ironyun.com'
    ANNOTATEDFRAMEPATH= "/root/vatic/data/frames_in/" + video_name
    slug = ADMIN_NAME + '_' + video_name


    TURKOPS="--offline --title Hello!"
    vatic_path = "/root/vatic"

    delete_cmd = "cd {}; turkic delete {}".format(vatic_path,slug)
    create_cmd = "cd {}; turkic load {} {} {} {} {}".format(vatic_path,slug, userid ,ANNOTATEDFRAMEPATH, labels, TURKOPS)
    cmd = ['docker', 'exec', CONTAINER_NAME, "/bin/bash", '-c', delete_cmd]
    call(cmd)
    cmd = ['docker', 'exec', CONTAINER_NAME, "/bin/bash", '-c', create_cmd]
    print(" ".join(cmd))
    call(cmd)
