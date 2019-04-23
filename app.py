import json
from db import db, Job, User
from flask import Flask, request

app = Flask(__name__)
db_filename = 'todo.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
with app.app_context():
    db.create_all()

# Jason
# /api/jobs GET
# ASSIGN USER i TO JOB /api/user/i/job POST
# CREATE A JOB i /api/job/i POST
# GET JOB GIVEN id /api/job/id GET

# Aditya
# DELETE /
# UPDATE ^
# CREATE NEW USER /api/users POST
# GET USER /api/user/i GET


# OAuth (Google)

# Later
# Connect to frontend
# Deployment


@app.route('/api/jobs/')
def getjobs():
    classes = Class.query.all()
    res = {'success': True, 'data': [clas.serialize() for clas in classes]}
    return json.dumps(res), 200


@app.route('/api/classes/', methods=['POST'])
def create_class():
    class_body = json.loads(request.data)

    clas = Class(code=class_body.get('code'),
                 name=(class_body.get('name')),
                 assignments=[],
                 students=[],
                 instructors=[]
                 )

    db.session.add(clas)
    db.session.commit()

    return json.dumps({'success': True, 'data': clas.serialize()}), 201


@app.route('/api/class/<int:class_id>/')
def get_class(class_id):
    clas = Class.query.filter_by(id=class_id).first()
    if clas is not None:
        return json.dumps({'success': True, 'data': clas.serialize()}), 200
    return json.dumps({'success': False, 'error': 'Class not found'}), 404


@app.route('/api/class/<int:class_id>/', methods=['DELETE'])
def delete_class(class_id):
    clas = Class.query.filter_by(id=class_id).first()
    if clas is not None:
        db.session.delete(clas)
        db.session.commit()
        return json.dumps({'success': True, 'data': clas.serialize()}), 200
    return json.dumps({'success': False, 'error': 'Class not found'}), 404


'''
@app.route('/api/post/<int:post_id>/', methods=['POST'])
def update_post(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if post is not None:
        post_body = json.loads(request.data)
        post.text = post_body.get('text', post.text)
        db.session.commit()
        return json.dumps({'success': True, 'data': post.serialize()}), 200
    return json.dumps({'success': False, 'error': 'Post not found'}), 404'''


@app.route('/api/class/<int:class_id>/assignment/', methods=['POST'])
def create_assignment(class_id):
    clas = Class.query.filter_by(id=class_id).first()

    if clas is not None:
        clas_body = json.loads(request.data)
        assignment = Assignment(
            description=clas_body.get('description'),
            due_date=clas_body.get('due_date'),
            class_id=class_id
        )
        clas.assignments.append(assignment)
        db.session.add(assignment)
        db.session.commit()
        return json.dumps({'success': True, 'data': assignment.serialize()}), 200
    return json.dumps({'success': False, 'error': 'Post not found'}), 404


@app.route('/api/users/', methods=['POST'])
def create_user():
    user_body = json.loads(request.data)

    user = User(
        name=(user_body.get('name')),
        netid=(user_body.get('netid')),
        classes=[]
    )

    db.session.add(user)
    db.session.commit()

    return json.dumps({'success': True, 'data': user.serialize()}), 201


@app.route('/api/user/<int:user_id>/', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is not None:
        return json.dumps({'success': True, 'data': user.serialize()}), 200
    return json.dumps({'success': False, 'error': 'User not found'}), 404


@app.route('/api/class/<int:class_id>/add/', methods=['POST'])
def add_user_to_class(class_id):
    clas = Class.query.filter_by(id=class_id).first()

    if clas is not None:
        input_body = json.loads(request.data)
        typ = input_body.get('type')
        user_id = input_body.get('user_id')
        #user = get_user(user_id)
        user = User.query.filter_by(id=user_id).first()
        if typ == 'student':
            clas.students.append(user)
        else:
            clas.instructors.append(user)

        db.session.commit()
        return json.dumps({'success': True, 'data': clas.serialize()}), 200
    return json.dumps({'success': False, 'error': 'Class not found'}), 404


'''@app.route('/api/post/<int:post_id>/comment/', methods=['POST'])
def post_comment(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if post is not None:
        post_body = json.loads(request.data)

        comment = Comment(

            text=(post_body.get('text')),
            username=post_body.get('username')
            score=0,
            post_id=post.id,

        )

        post.comments.append(comment)
        db.session.add(comment)
        db.session.commit()
        return json.dumps({'success': True, 'data': comment.serialize()}), 200
    return json.dumps({'success': False, 'error': 'Post not found'}), 404'''


'''@app.route('/api/post/<int:post_id>/comments/')
def get_comments(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post is not None:
        comments = [comment.serialize() for comment in post.comments]
        return json.dumps({'success': True, 'data': comments}), 200
    return json.dumps({'success': False, 'error': 'Post not found'}), 404'''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
