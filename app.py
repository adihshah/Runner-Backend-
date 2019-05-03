import json
from db import db, Jobs_in_Progress, Job_History, User
from flask import Flask, request
# from google.oauth2 import id_token
# from google.auth.transport import requests

app = Flask(__name__)
db_filename = 'todo.db'
# request = requests.Request()
# CLIENT_ID = "ABCDE12345"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
with app.app_context():
    db.create_all()


'''
Jason
/api/jobs/ GET
/api/job/<int:id>/ GET
/api/job/ POST
/api/job/<int:id>/ DELETE
/api/user/ POST
/api/user/<int:user_id>/ GET
/api/user/<int:user_id>/job/<int:job_id>/ POST (assign user u to job j)
'''
# Aditya
# DELETE /
# UPDATE ^
# CREATE NEW USER /api/users POST
# GET USER /api/user/i GET


# OAuth (Google)

# Later
# Connect to frontend
# Deployment

############################ Helper Functions ##################################


def serialize(iter):
    """ Shortcut for serializing into a list. """
    return [i.serialize() for i in iter]


def get_query_by_id(q, id):
    """ Shortcut for filtering query of given id. """
    return q.query.filter_by(id=id).first()


################################## Routes ######################################


@app.route('/api/jobs/')
def get_jobs():
    """ Returns all jobs. """
    jobs = Jobs_in_Progress.query.all()
    res = {'Success': True, 'Data': serialize(jobs)}
    return json.dumps(res), 200
@app.route('/api/jobss/')
def get_jobss():
    """ Returns all jobs. """
    jobs = Job_History.query.all()
    res = {'Success': True, 'Data': serialize(jobs)}
    return json.dumps(res), 200

# creates a job under a user with a specified ID
@app.route('/api/job/<int:user_id>/', methods=['POST'])
def create_job(user_id):
    """ Creates a new job. """
    try:
        body = json.loads(request.data)
    except KeyError:
        return json.dumps({'Success': False, 'Error': 'No json provided!'}), 400

    job = Jobs_in_Progress(
        title=body.get('title'),
        cost=body.get('cost'),
        profit=body.get('profit'),
        amountpaidtoworker=body.get('amountpaidtoworker'),
        category=body.get('category'),
        first_Add=body.get('first_Add'),
        last_Add=body.get('last_Add'),
        start_time=body.get('start_time'),
        end_time=body.get('end_time'),
        description=body.get('description'),
        date=body.get('date'),
    )
    user = get_query_by_id(User, user_id)
    user.jobs_created += 1
    job.bosses.append(user)
    db.session.add(job)
    db.session.commit()
    return json.dumps({'Success': True, 'Data': job.serialize()}), 201


@app.route('/api/job/<int:id>/')
def get_job_by_id(id):
    """ Returns specific job with the given job id. """
    job = get_query_by_id(Jobs_in_Progress, id)

    if job is not None:
        return json.dumps({'Success': True, 'Data': job.serialize()}), 200
    return json.dumps({'Success': False, 'Error': 'Job not found!'}), 404


@app.route('/api/job/delete/<int:job_id>/', methods=['DELETE'])
def delete_job_early(job_id):
    """ Deletes and returns job with job id. """
    job = get_query_by_id(Jobs_in_Progress, job_id)
    user = get_query_by_id(User, job.bosses[0].id)
    user.jobs_created -= 1

    if job is not None:
        db.session.delete(job)
        db.session.commit()
        return json.dumps({'Success': True, 'Data': job.serialize()}), 200
    return json.dumps({'Success': False, 'Error': 'Job not found!'}), 404


@app.route('/api/job/finished/<int:job_id>/', methods=['DELETE'])
def complete_job(job_id):
    """ Deletes and returns job with job id. """
    job = get_query_by_id(Jobs_in_Progress, job_id)
    if job is None:
        return json.dumps({'Success': False, 'Error': 'Job not found!'}), 
    body = job.serialize()
    job_done = Job_History(
        title=body.get('title'),
        cost=body.get('cost'),
        profit=body.get('profit'),
        amountpaidtoworker=body.get('amountpaidtoworker'),
        category=body.get('category'),
        first_Add=body.get('first_Add'),
        last_Add=body.get('last_Add'),
        start_time=body.get('start_time'),
        end_time=body.get('end_time'),
        description=body.get('description'),
        date=body.get('date'),
    )
    if job is not None:
        user = get_query_by_id(User, job.bosses[0].id)
        user2 = get_query_by_id(User, job.workers[0].id)
        user2.jobs_done += 1
        user.job_history.append(job_done)
        db.session.delete(job)
        db.session.add(job_done)
        db.session.commit()
        return json.dumps({'Success': True, 'Data': job_done.serialize()}), 200
    return json.dumps({'Success': False, 'Error': 'Job not found!'}), 404


@app.route('/api/job/<int:job_id>/', methods=['POST'])
def update_job(job_id):
    job = get_query_by_id(Jobs_in_Progress, job_id)

    if job is not None:
        job_body = json.loads(request.data)
        job.description = job_body.get('description', job.description)

        
        db.session.commit()
        return json.dumps({'success': True, 'data': job.serialize()}), 200
    return json.dumps({'success': False, 'error': 'Post not found'}), 404


@app.route('/api/user/', methods=['POST'])
def create_user():
    """ Create a new user. """
    try:
        body = json.loads(request.data)
    except KeyError:
        return json.dumps({'success': False, 'error': 'No json provided!'}), 400

    user = User(
        name=body.get('name'),
        phone_num=body.get('phone_num'),
        rating=0,
        jobs_created=0,
        jobs_done=0,
        money_earned=0,
    )

    db.session.add(user)
    db.session.commit()
    return json.dumps({'success': True, 'data': user.serialize()}), 201


@app.route('/api/user/<int:user_id>/', methods=['POST'])
def update_user_info(user_id):
    """ Update user's name or phone number, if one is not given, nothing happens. """
    user = get_query_by_id(User, user_id)

    if user is not None:
        body = json.loads(request.data)
        user.name = body.get('name', user.phone_num)
        user.phone_num = body.get('phone_num', user.phone_num)
        db.session.commit()
        return json.dumps({'success': True, 'data': user.serialize()}), 200
    return json.dumps({'success': False, 'error': 'Post not found'}), 404


@app.route('/api/user/<int:user_id>/')
def get_user(user_id):
    """ Returns user with given user id. """
    try:
        user = get_query_by_id(User, user_id)
    except KeyError:
        return json.dumps({'success': False, 'error': 'No json Provided!'}), 400
    if user is not None:
        return json.dumps({'Success': True, 'Data': user.serialize()}), 200
    return json.dumps({'Success': False, 'Error': 'User not found'}), 404


@app.route('/api/user/<int:user_id>/job/<int:job_id>/', methods=['POST'])
def assign_worker_to_job(user_id, job_id):
    """ Adds a worker (user_id) to a specific job (job_id). """
    try:
        body = json.loads(request.data)
    except KeyError:
        return json.dumps({'success': False, 'error': 'No json Provided!'}), 400

    optional_job = get_query_by_id(Jobs_in_Progress, job_id)
    if optional_job is None:
        return json.dumps({'success': False, 'error': 'Job not found!'}), 404

    optional_user = get_query_by_id(User, user_id)
    if optional_user is None:
        return json.dumps({'success': False, 'error': 'User not found!'}), 404
    
    optional_job.workers.append(optional_user)
    db.session.add(optional_job)
    db.session.commit()
    return json.dumps({'success': True, 'data': optional_job.serialize()}), 200


# @app.route('/api/user/signin/<token>', methods=['POST'])
# def verify_login(token):
#     try:
#         body = json.loads(request.data)
#     except KeyError:
#         return json.dumps({'success': False, 'error': 'No json Provided!'}), 400

#     try:
#         # Specify the CLIENT_ID of the app that accesses the backend:
#         idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

#         # Or, if multiple clients access the backend server:
#         # idinfo = id_token.verify_oauth2_token(token, requests.Request())
#         # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
#         #     raise ValueError('Could not verify audience.')

#         if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
#             raise ValueError('Wrong issuer.')

#         # If auth request is from a G Suite domain:
#         # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
#         #     raise ValueError('Wrong hosted domain.')

#         # ID token is valid. Get the user's Google Account ID from the decoded token.
#         userid = idinfo['sub']
#     except ValueError:
#         # Invalid token
#         return json.dumps({'success': False, 'error': 'Invalid Token!'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
