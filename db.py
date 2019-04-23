from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

association_table1 = db.Table('association1', db.metadata,
                              db.Column('job', db.Integer,
                                        db.ForeignKey('job.id')),
                              db.Column('user', db.Integer,
                                        db.ForeignKey('user.id'))
                              )


def serialize(iter):
    return [i.serialize() for i in iter]


def part_serialize(iter):
    return [i.serialize_part() for i in iter]


class Job(db.Model):
    __tablename__ = 'job'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    starttime = db.Column(db.String, nullable=False)  # can change to UNIXtime
    deadline = db.Column(db.String, nullable=False)  # can change to UNIXtime
    startloc = db.Column(db.String, nullable=False)
    endloc = db.Column(db.String, nullable=False)
    # job poster
    boss = db.relationship(  # confirm if this is correct
        "User", secondary=association_table1, back_populates='job')
    worker = db.relationship(
        "User", secondary=association_table1, back_populates='job')

    def __init__(self, **kwargs):
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.category = kwargs.get('category', '')
        self.starttime = kwargs.get('starttime', '')
        self.deadline = kwargs.get('deadline', '')
        self.startloc = kwargs.get('startloc', '')
        self.endloc = kwargs.get('endloc', '')
        self.boss = kwargs.get('boss', '')
        self.worker = kwargs.get('worker', '')

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'starttime': self.starttime,
            'deadline': self.deadline,
            'startloc': self.startloc,
            'endloc': self.endloc,
            'category': self.name,
            'boss': serialize(self.boss),
            'worker': serialize(self.boss)
        }

    def serialize_part(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
        }


'''class Assignment(db.Model):
    __tablename__ = 'assignment'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Integer, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    classes = db.relationship("Class", back_populates="assignments")

    def __init__(self, **kwargs):
        self.description = kwargs.get('description', '')
        self.due_date = kwargs.get('due_date', '')
        self.class_id = kwargs.get('class_id', '')

    def serialize(self):
        return {
            'id': self.id,
            'description': self.description,
            'due_date': self.due_date,
            'class': self.classes.serialize_part()  # unsure

        }'''


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)
    phone_num = db.Column(db.String, nullable=False)
    rating = db.Column(db.String, nullable=False)
    jobs_completed = db.Column(db.Integer, nullable=False)
    jobs_requested = db.Column(db.Integer, nullable=False)
    # class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    jobs = db.relationship(
        "Job", secondary=association_table1, back_populates="boss")
    # Should it be back populating students or instructors?

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '')
        self.netid = kwargs.get('netid', '')
        self.phone_num = kwargs.get('phone_num', '')
        self.rating = kwargs.get('rating', '')
        self.jobs_completed = kwargs.get('jobs_completed', '')
        self.jobs_requested = kwargs.get('jobs_requested', '')
        self.jobs = kwargs.get('jobs', '')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'netid': self.netid,
            'phone_num': self.phone_num,
            'rating': self.rating,
            'jobs_completed': self.jobs_completed,
            'jobs_requested': self.jobs_requested,
            'jobs': part_serialize(self.jobs)
            # 'classes': self.classes.serialize_part()  # unsure about this line

        }
