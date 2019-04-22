from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

association_table1 = db.Table('association1', db.metadata,
                              db.Column('class', db.Integer,
                                        db.ForeignKey('class.id')),
                              db.Column('user', db.Integer,
                                        db.ForeignKey('user.id'))
                              )


class Class(db.Model):
    __tablename__ = 'class'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    assignments = db.relationship(
        'Assignment', back_populates='classes', cascade='delete')
    students = db.relationship(
        "User", secondary=association_table1, back_populates="classes")
    instructors = db.relationship(
        "User", secondary=association_table1, back_populates="classes")

    def __init__(self, **kwargs):
        self.code = kwargs.get('code', '')
        self.name = kwargs.get('name', '')
        self.assignments = kwargs.get('assignments', '')
        self.students = kwargs.get('students', '')
        self.instructors = kwargs.get('instructors', '')

    def serialize(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'assignments': [a.serialize() for a in self.assignments],
            'students': [a.serialize() for a in self.students],
            'instructors': [a.serialize() for a in self.instructors]
        }

    def serialize_part(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
        }


class Assignment(db.Model):
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

        }


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)
    #class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    classes = db.relationship(
        "Class", secondary=association_table1, back_populates="instructors")
    # Should it be back populating students or instructors?

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '')
        self.netid = kwargs.get('netid', '')
        self.classes = kwargs.get('classes', '')
        #self.class_id = kwargs.get('class_id', '')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'netid': self.netid,
            'classes': [clas.serialize_part() for clas in self.classes]
            # 'classes': self.classes.serialize_part()  # unsure about this line

        }
