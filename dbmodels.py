# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, LargeBinary, String, Table, Text, text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import vision

Base = declarative_base()
metadata = Base.metadata


class AttributeAnnotation(Base):
    __tablename__ = 'attribute_annotations'

    id = Column(Integer, primary_key=True)
    pathid = Column(ForeignKey(u'paths.id'), index=True)
    attributeid = Column(ForeignKey(u'attributes.id'), index=True)
    frame = Column(Integer)
    value = Column(Integer)

    attribute = relationship(u'Attribute')
    path = relationship(u'Path')


class Attribute(Base):
    __tablename__ = 'attributes'

    id = Column(Integer, primary_key=True)
    text = Column(String(250))
    labelid = Column(ForeignKey(u'labels.id'), index=True)

    label = relationship(u'Label')
    boxs = relationship(u'Box', secondary='boxes2attributes')


class Box(Base):
    __tablename__ = 'boxes'

    id = Column(Integer, primary_key=True)
    pathid = Column(ForeignKey(u'paths.id'), index=True)
    xtl = Column(Integer)
    ytl = Column(Integer)
    xbr = Column(Integer)
    ybr = Column(Integer)
    frame = Column(Integer)
    occluded = Column(Integer)
    outside = Column(Integer)

    path = relationship(u'Path', backref = "boxes")

    def getbox(self):
        return vision.Box(self.xtl, self.ytl, self.xbr, self.ybr,
                          self.frame, self.outside, self.occluded, 0)


t_boxes2attributes = Table(
    'boxes2attributes', metadata,
    Column('box_id', ForeignKey(u'boxes.id'), index=True),
    Column('attribute_id', ForeignKey(u'attributes.id'), index=True)
)


class Label(Base):
    __tablename__ = 'labels'

    id = Column(Integer, primary_key=True)
    text = Column(String(250))
    videoid = Column(ForeignKey(u'videos.id'), index=True)

    video = relationship(u'Video', backref = 'labels')


class Path(Base):
    __tablename__ = 'paths'

    id = Column(Integer, primary_key=True)
    jobid = Column(ForeignKey(u'jobs.id'), index=True)
    labelid = Column(ForeignKey(u'labels.id'), index=True)

    job = relationship(u'Job', backref = 'paths')
    label = relationship(u'Label', backref = 'paths')

    interpolatecache = None

    def getboxes(self, interpolate = False, bind = False, label = False):
        result = [x.getbox() for x in self.boxes]
        result.sort(key = lambda x: x.frame)
        if interpolate:
            if not self.interpolatecache:
                self.interpolatecache = LinearFill(result)
            result = self.interpolatecache

        if bind:
            result = Path.bindattributes(self.attributes, result)

        if label:
            for box in result:
                box.attributes.insert(0, self.label.text)

        return result

    @classmethod
    def bindattributes(cls, attributes, boxes):
        attributes = sorted(attributes, key = lambda x: x.frame)

        byid = {}
        for attribute in attributes:
            if attribute.attributeid not in byid:
                byid[attribute.attributeid] = []
            byid[attribute.attributeid].append(attribute)

        for attributes in byid.values():
            for prev, cur in zip(attributes, attributes[1:]):
                if prev.value:
                    for box in boxes:
                        if prev.frame <= box.frame < cur.frame:
                            if prev.attribute not in box.attributes:
                                box.attributes.append(prev.attribute)
            last = attributes[-1]
            if last.value:
                for box in boxes:
                    if last.frame <= box.frame:
                        if last.attribute not in box.attributes:
                            box.attributes.append(last.attribute)

        return boxes

    def __repr__(self):
        return "<Path {0}>".format(self.id)



class Segment(Base):
    __tablename__ = 'segments'

    id = Column(Integer, primary_key=True)
    videoid = Column(ForeignKey(u'videos.id'), index=True)
    start = Column(Integer)
    stop = Column(Integer)

    video = relationship(u'Video', backref = 'segments')

    @property
    def paths(self):
        paths = []
        for job in self.jobs:
            if job.useful:
                paths.extend(job.paths)
        return paths


class TurkicBonusSchedule(Base):
    __tablename__ = 'turkic_bonus_schedules'

    id = Column(Integer, primary_key=True)
    groupid = Column(ForeignKey(u'turkic_hit_groups.id'), index=True)
    type = Column(String(250))

    turkic_hit_group = relationship(u'TurkicHitGroup')


class CompletionBonus(TurkicBonusSchedule):
    __tablename__ = 'completion_bonuses'

    id = Column(ForeignKey(u'turkic_bonus_schedules.id'), primary_key=True)
    amount = Column(Float, nullable=False)


class PerObjectBonus(TurkicBonusSchedule):
    __tablename__ = 'per_object_bonuses'

    id = Column(ForeignKey(u'turkic_bonus_schedules.id'), primary_key=True)
    amount = Column(Float, nullable=False)


class TurkicBonusScheduleConstant(TurkicBonusSchedule):
    __tablename__ = 'turkic_bonus_schedule_constant'

    id = Column(ForeignKey(u'turkic_bonus_schedules.id'), primary_key=True)
    amount = Column(Float, nullable=False)


class TurkicEventLog(Base):
    __tablename__ = 'turkic_event_log'

    id = Column(Integer, primary_key=True)
    hitid = Column(ForeignKey(u'turkic_hits.id'), index=True)
    domain = Column(Text)
    message = Column(Text)
    timestamp = Column(DateTime)

    turkic_hit = relationship(u'TurkicHit')


class TurkicHitGroup(Base):
    __tablename__ = 'turkic_hit_groups'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    duration = Column(Integer, nullable=False)
    lifetime = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    keywords = Column(String(250), nullable=False)
    height = Column(Integer, nullable=False)
    donation = Column(Integer)
    offline = Column(Integer)
    minapprovedamount = Column(Integer)
    minapprovedpercent = Column(Integer)
    countrycode = Column(String(10))


class TurkicHit(Base):
    __tablename__ = 'turkic_hits'

    id = Column(Integer, primary_key=True)
    hitid = Column(String(30))
    groupid = Column(ForeignKey(u'turkic_hit_groups.id'), index=True)
    assignmentid = Column(String(30))
    workerid = Column(ForeignKey(u'turkic_workers.id'), index=True)
    ready = Column(Integer, index=True)
    published = Column(Integer, index=True)
    completed = Column(Integer, index=True)
    compensated = Column(Integer, index=True)
    accepted = Column(Integer, index=True)
    validated = Column(Integer, index=True)
    reason = Column(Text)
    comments = Column(Text)
    timeaccepted = Column(DateTime)
    timecompleted = Column(DateTime)
    timeonserver = Column(DateTime)
    ipaddress = Column(String(15))
    page = Column(String(250), nullable=False)
    opt2donate = Column(Float)
    donatedamount = Column(Float, nullable=False)
    bonusamount = Column(Float, nullable=False)
    useful = Column(Integer)
    type = Column(String(250))

    turkic_hit_group = relationship(u'TurkicHitGroup')
    turkic_worker = relationship(u'TurkicWorker')


class Job(TurkicHit):
    __tablename__ = 'jobs'

    id = Column(ForeignKey(u'turkic_hits.id'), primary_key=True)
    segmentid = Column(ForeignKey(u'segments.id'), index=True)
    istraining = Column(Integer)

    segment = relationship(u'Segment', backref = 'jobs')


class TurkicWorker(Base):
    __tablename__ = 'turkic_workers'

    id = Column(String(14), primary_key=True)
    numsubmitted = Column(Integer, nullable=False)
    numacceptances = Column(Integer, nullable=False)
    numrejections = Column(Integer, nullable=False)
    blocked = Column(Integer)
    donatedamount = Column(Float, nullable=False)
    bonusamount = Column(Float, nullable=False)
    verified = Column(Integer)

class User(Base):
    __tablename__ = 'users'

    id = Column(String(50), primary_key=True)
    username = Column(String(50))
    password = Column(String(50))
    priority = Column(Integer, nullable=False, default =  0)
    token = Column(String(50), nullable=True, unique = True, default = None)
    verification = Column(Boolean, nullable=False, default = False)
    forgetPasswordToken = Column(String(50), nullable=True, default = None)
    forgetPasswordTokenExpireTime = Column(DateTime, nullable=True, default=None)

    video = relationship('Video')


class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    slug = Column(String(250), index=True)
    width = Column(Integer)
    height = Column(Integer)
    totalframes = Column(Integer)
    location = Column(String(250))
    skip = Column(Integer, nullable=False)
    perobjectbonus = Column(Float)
    completionbonus = Column(Float)
    trainwithid = Column(ForeignKey(u'videos.id'), index=True)
    isfortraining = Column(Integer)
    trainvalidator = Column(LargeBinary)
    blowradius = Column(Integer)
    user_id = Column(ForeignKey(u'users.id'), nullable=False, index=True)

    user = relationship("User", backref = 'videos')

    def __getitem__(self, frame):
        path = Video.getframepath(frame, self.location)
        return Image.open(path)

    @classmethod
    def getframepath(cls, frame, base = None):
        l1 = frame / 10000
        l2 = frame / 100
        path = "{0}/{1}/{2}.jpg".format(l1, l2, frame)
        if base is not None:
            path = "{0}/{1}".format(base, path)
        return path

    @property
    def cost(self):
        cost = 0
        for segment in self.segments:
            cost += segment.cost
        return cost

    @property
    def numjobs(self):
        count = 0
        for segment in self.segments:
            for job in segment.jobs:
                count += 1
        return count

    @property
    def numcompleted(self):
        count = 0
        for segment in self.segments:
            for job in segment.jobs:
                if job.completed:
                    count += 1
        return count
