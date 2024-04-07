import os
import random
from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, db
from api.todo.todo import todo_bp

import uuid
import hashlib

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///local_db.sqlite")

app.register_blueprint(todo_bp, url_prefix='/api/v1/todos')
db.init_app(app)

with app.app_context():
    db.create_all()


MAX_SECRET = 30


def get_user(user_token=None, email=None):
    if set(locals().values()) == {None}:
        return None
    
    if user_token:
        select_query = db.select(User).filter_by(session_token=user_token)
    if email:
        select_query = db.select(User).filter_by(email=email)
    return db.session.execute(select_query).scalar()


def get_all_users():
    select_query = db.select(User)
    return db.session.execute(select_query).scalars().all()


@app.route('/', methods=['GET'])
def index():
    user = get_user(user_token=request.cookies.get('token'))
    return render_template('index.html', user=user, max_secret=MAX_SECRET)


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        response = render_template('sign-up.html')
    else:
        name = request.form.get('user-name')
        email = request.form.get('user-email')
        password = str(request.form.get('user-pass'))
        hashed_pass = hashlib.sha256(password.encode()).hexdigest()

        user = get_user(email=email)
        if user:
            return render_template('message.html', message={'text': 'Uporabnik s takšnim e-naslovom že obstaja.', 'type':'danger'})

        # no user found, create new user
        secret = random.randint(1, MAX_SECRET)
        token = str(uuid.uuid4())

        user = User(name=name, email=email, secret_number=secret, passwd=hashed_pass, session_token=token)

        db.session.add(user)
        db.session.commit()

        response = make_response(redirect(url_for('index')))
        response.set_cookie('token', token, httponly=True, samesite='strict')

    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        response = render_template('login.html')
    else:
        email = request.form.get('user-email')
        password = str(request.form.get('user-pass'))
        hashed_pass = hashlib.sha256(password.encode()).hexdigest()

        user = get_user(email=email)
        if not user:
            return render_template('message.html', message={'text': 'Uporabnika ni bilo mogoče najti.', 'type':'warning'})

        if hashed_pass != user.passwd:
            # V realnih aplikacijah je zaradi varnostnih vidikov smiselno združiti ta dva scenarija v eno error sporočilo.
            return render_template('message.html', message={'text': 'Geslo ni pravilno.', 'type':'error'})

        token = str(uuid.uuid4())
        user.session_token = token
        db.session.add(user)
        db.session.commit()

        response = make_response(redirect(url_for('index')))
        response.set_cookie('token', token, httponly=True, samesite='strict')

    return response


@app.route("/result", methods=["POST"])
def result():
    guess = int(request.form.get("guess"))
    user = get_user(user_token=request.cookies.get('token'))
    if not user:
        return redirect(url_for('login'))

    if guess == user.secret_number:
        message = "Pravilno! Skrito število je {0}".format(str(user.secret_number))
        response = make_response(render_template("result.html", finished=True, message=message))
        user.secret_number = random.randint(1, MAX_SECRET)
        db.session.add(user)
        db.session.commit()
        return response
    elif guess > user.secret_number:
        message = "Ta poizkus ni pravilen. Poizkusi z manjšo številko."
        return render_template("result.html", finished=False, message=message)
    elif guess < user.secret_number:
        message = "Ta poizkus ni pravilen. Poizkusi z večjo številko."
        return render_template("result.html", finished=False,  message=message)


@app.route("/user", methods=["GET"])
def profile():
    token = request.cookies.get('token')
    user = get_user(user_token=token)

    if user:
        return redirect(url_for('user_detail', user_id=user.id))
    else:
        return redirect(url_for('login'))


# beremo vrednost parametra user_id iz URL naslova
@app.route("/user/<user_id>")
def user_detail(user_id):
    user = db.get_or_404(User, user_id)
    logged_in_user = get_user(user_token=request.cookies.get('token'))

    return render_template("profile.html", user_data=user, is_my_account=user.id==logged_in_user.id)


@app.route("/user/edit", methods=["GET", "POST"])
def profile_edit():
    token = request.cookies.get('token')
    user = get_user(user_token=token)

    if not user:
        return redirect(url_for('login'))
    else:
        if request.method == "GET":
            return render_template("profile_edit.html", user_data=user)
        else:
            user.email = request.form.get('email')
            db.session.add(user)
            db.session.commit()

            return redirect(url_for('profile'))


@app.route("/user/delete", methods=["GET", "POST"])
def profile_delete():
    token = request.cookies.get('token')
    user = get_user(user_token=token)

    if not user:
        return redirect(url_for('login'))
    else:
        if request.method == "GET":
            return render_template("profile_delete.html")
        else:
            db.session.delete(user)
            db.session.commit()

            return render_template("deleted.html")


@app.route("/users")
def all_users():
    user = get_user(user_token=request.cookies.get('token'))
    if not user:
        return redirect(url_for('login'))
    users_list = get_all_users()

    return render_template("all_users.html", users=users_list)

@app.route("/todo")
def todo():
    return render_template("todo_spa.html")


if __name__ == '__main__':
    app.run(debug=True)
