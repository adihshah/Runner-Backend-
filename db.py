from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

boss_association_table = db.Table(
    'bosses',
    db.Model.metadata,
    db.Column('boss_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('job_id', db.Integer, db.ForeignKey('job.id'))
)

worker_association_table = db.Table(
    'workers',
    db.Model.metadata,
    db.Column('worker_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('job_id', db.Integer, db.ForeignKey('job.id'))
)


def serialize(iter):
    return [i.serialize() for i in iter]


def part_serialize(iter):
    return [i.part_serialize() for i in iter]


class Job(db.Model):
    __tablename__ = 'job'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    starttime = db.Column(db.String, nullable=False)
    deadline = db.Column(db.String, nullable=False)
    startloc = db.Column(db.String, nullable=False)
    endloc = db.Column(db.String, nullable=False)
    bosses = db.relationship(
        "User", secondary=boss_association_table, back_populates="boss_jobs")
    workers = db.relationship(
        "User", secondary=worker_association_table, back_populates="worker_jobs")

    def __init__(self, **kwargs):
        self.title = kwargs.get('title', '')
        self.category = kwargs.get('category', '')
        self.description = kwargs.get('description', '')
        self.starttime = kwargs.get('starttime', '')
        self.deadline = kwargs.get('deadline', '')
        self.startloc = kwargs.get('startloc', '')
        self.endloc = kwargs.get('endloc', '')

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'starttime': self.starttime,
            'deadline': self.deadline,
            'startloc': self.startloc,
            'endloc': self.endloc,
            'bosses': serialize(self.bosses),
            'workers': serialize(self.workers)
        }

    def part_serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
        }


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)
    phone_num = db.Column(db.String, nullable=False)
    rating = db.Column(db.String, nullable=False)
    jobs_completed = db.Column(db.Integer, nullable=False)
    jobs_requested = db.Column(db.Integer, nullable=False)
    boss_jobs = db.relationship(
        "Job", secondary=boss_association_table, back_populates="bosses")
    worker_jobs = db.relationship(
        "Job", secondary=worker_association_table, back_populates="workers")

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '')
        self.netid = kwargs.get('netid', '')
        self.phone_num = kwargs.get('phone_num', '')
        self.rating = kwargs.get('rating', '')
        self.jobs_completed = kwargs.get('jobs_completed', '')
        self.jobs_requested = kwargs.get('jobs_requested', '')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'netid': self.netid,
            'phone_num': self.phone_num,
            'rating': self.rating,
            'jobs_completed': self.jobs_completed,
            'jobs_requested': self.jobs_requested,
            'boss_jobs': part_serialize(self.boss_jobs),
            'worker_jobs': part_serialize(self.worker_jobs),
        }
