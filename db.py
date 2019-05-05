from flask_sqlalchemy import SQLAlchemy
import bcrypt
import datetime
import hashlib
import os

db = SQLAlchemy()

boss_association_table = db.Table(
    'bosses',
    db.Model.metadata,
    db.Column('boss_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('job_id', db.Integer, db.ForeignKey('jobs_in_progress.id'))
)

worker_association_table = db.Table(
    'workers',
    db.Model.metadata,
    db.Column('worker_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('job_id', db.Integer, db.ForeignKey('jobs_in_progress.id'))
)


def serialize(iter):
    return [i.serialize() for i in iter]


def part_serialize(iter):
    return [i.part_serialize() for i in iter]


class Job(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    profit = db.Column(db.Integer, nullable=False)
    amountpaidtoworker = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String, nullable=False)
    first_Add = db.Column(db.String, nullable=False)
    last_Add = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    start_time = db.Column(db.String, nullable=False)
    end_time = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    def __init__(self, **kwargs):
        self.title = kwargs.get('title', '')
        self.category = kwargs.get('category', '')
        self.description = kwargs.get('description', '')
        self.start_time = kwargs.get('start_time', '')
        self.end_time = kwargs.get('end_time', '')
        self.first_Add = kwargs.get('first_Add', '')
        self.last_Add = kwargs.get('last_Add', '')
        self.date = kwargs.get('date', '')
        self.cost = kwargs.get('cost', '')
        self.amountpaidtoworker = kwargs.get('amountpaidtoworker', '')
        self.profit = kwargs.get('profit', '')

    def serialize(self):
        return {
            'job_id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'first_Add': self.first_Add,
            'last_Add': self.last_Add,
            'date': self.date,
            'cost': self.cost,
            'profit': self.profit,
            'amountpaidtoworker': self.amountpaidtoworker,
        }

    def part_serialize(self):
        return {
            'job_id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
        }


class Jobs_in_Progress(Job):
    __tablename__ = 'jobs_in_progress'
    bosses = db.relationship(
        "User", secondary=boss_association_table, back_populates="boss_jobs")
    workers = db.relationship(
        "User", secondary=worker_association_table, back_populates="worker_jobs")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def serialize(self):
        body = super().serialize()
        body.update({
            'bosses': part_serialize(self.bosses),
            'workers': part_serialize(self.workers)
        })
        return body


class Job_History(Job):
    __tablename__ = 'job_history'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref="job_history")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def serialize(self):
        body = super().serialize()
        body.update({
            'user_id': self.user_id,
        })
        return body


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone_num = db.Column(db.String, nullable=False)
    rating = db.Column(db.String, nullable=False)
    jobs_created = db.Column(db.Integer, nullable=False)
    jobs_done = db.Column(db.Integer, nullable=False)
    money_earned = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String, nullable=False)
    password_digest = db.Column(db.String, nullable=False)
    boss_jobs = db.relationship(
        "Jobs_in_Progress", secondary=boss_association_table, back_populates="bosses")
    worker_jobs = db.relationship(
        "Jobs_in_Progress", secondary=worker_association_table, back_populates="workers")
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '')
        self.phone_num = kwargs.get('phone_num', '')
        self.rating = kwargs.get('rating', '')
        self.jobs_created = kwargs.get('jobs_created', '')
        self.jobs_done = kwargs.get('jobs_done', '')
        self.money_earned = kwargs.get('money_earned', '')
        self.email = kwargs.get('email', '')
        self.password_digest = bcrypt.hashpw(kwargs.get('password', '').encode('utf8'),
                                            bcrypt.gensalt(rounds=13))
        self.renew_session()

    def serialize(self):
        return {
            'user_id': self.id,
            'name': self.name,
            'phone_num': self.phone_num,
            'rating': self.rating,
            'jobs_created': self.jobs_created,
            'jobs_done': self.jobs_done,
            'money_earned': self.money_earned,
            'boss_jobs': part_serialize(self.boss_jobs),
            'worker_jobs': part_serialize(self.worker_jobs),
            'job_history': part_serialize(self.job_history),
            'email': self.email,
        }

    def part_serialize(self):
        return {
            'user_id': self.id,
            'name': self.name,
        }

    # Used to randomly generate session/update tokens
    def _urlsafe_base_64(self):
        return hashlib.sha1(os.urandom(64)).hexdigest()

    # Generates new tokens, and resets expiration time
    def renew_session(self):
        self.session_token = self._urlsafe_base_64()
        self.session_expiration = datetime.datetime.now() + \
                                datetime.timedelta(days=1)
        self.update_token = self._urlsafe_base_64()

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf8'),
                              self.password_digest)

    # Checks if session token is valid and hasn't expired
    def verify_session_token(self, session_token):
        return session_token == self.session_token and \
            datetime.datetime.now() < self.session_expiration

    def verify_update_token(self, update_token):
        return update_token == self.update_token
