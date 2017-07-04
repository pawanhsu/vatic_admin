from admin_server import db
from sqlalchemy.dialects.postgresql import JSON



class error_checkbox(db.Model):
    __tablename__ = 'error_checkbox'
    id = db.Column(db.Integer,primary_key = True)
    video_name      = db.Column(db.String())
    box_owner       = db.Column(db.String())
    box_reference   = db.Column(db.String())
    error_type      = db.Column(db.String())
    error_begin     = db.Column(db.Integer)
    error_end       = db. Column(db.Integer)

    def __init__(self, video_name,box_owner,box_reference, error_type, error_begin, error_end):
        self.video_name     = video_name
        self.box_owner      = box_owner
        self.box_reference  = box_reference
        self.error_type     = error_type
        self.error_begin    = error_begin
        self.error_end      = error_end





class segment_checkbox(db.Model):
    __tablename__ = 'segment_checkbox'
    id = db.Column(db.Integer,primary_key = True)
    video_name = db.Column(db.String())
    segment_id = db.Column(db.Integer)


    def __init__(self, video_name, segment_id):
        self.video_name = video_name
        self.segment_id = segment_id
