import json
from db import db, Jobs_in_Progress, Job_History, User
from flask import Flask, request
import users_dao

app = Flask(__name__)
db_filename = 'todo.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
with app.app_context():
    db.create_all()


############################ Helper Functions ##################################


def serialize(iter):
    """ Shortcut for serializing into a list. """
    return [i.serialize() for i in iter]


def get_query_by_id(q, id):
    """ Shortcut for filtering query of given id. """
    return q.query.filter_by(id=id).first()


def extract_token(request):
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return False, json.dumps({'error': 'Missing authorization header.'})

    bearer_token = auth_header.replace('Bearer ', '').strip()
    if not bearer_token:
        return False, json.dumps({'error': 'Invalid authorization header.'})

    return True, bearer_token


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


@app.route('/api/job/<int:job_id>/edit/', methods=['POST'])
def update_job(job_id):
    job = get_query_by_id(Jobs_in_Progress, job_id)

    if job is not None:
        job_body = json.loads(request.data)
        job.description = job_body.get('description', job.description)
        job.title = job_body.get('title', job.title)
        job.cost = job_body.get('cost', job.cost)
        job.category = job_body.get('category', job.category)
        job.start_time = job_body.get('start_time', job.start_time)
        job.end_time = job_body.get('end_time', job.end_time)
        job.first_Add = job_body.get('first_Add', job.first_Add)
        job.last_Add = job_body.get('last_Add', job.last_Add)
        job.date = job_body.get('date', job.date)
        job.amountpaidtoworker = job_body.get(
            'amountpaidtoworker', job.amountpaidtoworker)
        job.profit = job_body.get('profit', job.profit)

        db.session.commit()
        return json.dumps({'success': True, 'data': job.serialize()}), 200
    return json.dumps({'success': False, 'error': 'Post not found'}), 404


@app.route('/api/signup/', methods=['POST'])
def create_user():
    """ Create a new user. """
    try:
        body = json.loads(request.data)
        email = body.get('email')
        password = body.get('password')
        name = body.get('name')
        phone_num = body.get('phone_num')
    except KeyError:
        return json.dumps({'success': False, 'error': 'No json provided!'}), 400

    if email is None or password is None:
        return json.dumps({'error': 'Invalid email or password'})

    created, user = users_dao.create_user(name, phone_num, email, password)

    if not created:
        return json.dumps({'error': 'User already exists'})

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


@app.route('/api/login/', methods=['POST'])
def login():
    post_body = json.loads(request.data)
    email = post_body.get('email')
    password = post_body.get('password')

    if email is None or password is None:
        return json.dumps({'error': 'Invalid email or password'})

    success, user = users_dao.verify_credentials(email, password)

    if not success:
        return json.dumps({'error': 'Incorrect email or password'})

    return json.dumps({
        'session_token': user.session_token,
        'session_expiration': str(user.session_expiration),
        'update_token': user.update_token
    })


@app.route('/api/update/session/', methods=['POST'])
def update_session():
    success, update_token = extract_token(request)

    if not success:
        return update_token

    try:
        user = users_dao.renew_session(update_token)
    except:
        return json.dumps({'error': 'Invalid update token'})

    return json.dumps({
        'session_token': user.session_token,
        'session_expiration': str(user.session_expiration),
        'update_token': user.update_token
    })



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
