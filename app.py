from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb://test:test@localhost', 27017)
# client = MongoClient('localhost', 27017)
db = client.dbsparta_plus_week4


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        all_users_info = list(db.users.find({}, {'_id': False}))

        return render_template('index.html', user_info=user_info, all_users_info=all_users_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="濡쒓렇???쒓컙??留뚮즺?섏뿀?듬땲??"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="濡쒓렇???뺣낫媛 議댁옱?섏? ?딆뒿?덈떎."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/post/김선아/운동')
def otherpage():
    msg = request.args.get("msg")
    return render_template('otherpage.html', msg=msg)


@app.route('/user/<username>')
def user(username):
    # 媛??ъ슜?먯쓽 ?꾨줈?꾧낵 湲??紐⑥븘蹂????덈뒗 怨듦컙
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # ???꾨줈?꾩씠硫?True, ?ㅻⅨ ?щ엺 ?꾨줈???섏씠吏硫?False

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 濡쒓렇??
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 濡쒓렇??24?쒓컙 ?좎?
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 李얠? 紐삵븯硫?
    else:
        return jsonify({'result': 'fail', 'msg': '?꾩씠??鍮꾨?踰덊샇媛 ?쇱튂?섏? ?딆뒿?덈떎.'})



@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    username1_receive = request.form['username1_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username1": username1_receive,                             # ?대쫫
        "username": username_receive,                               # ?꾩씠??
        "password": password_hash,                                  # 鍮꾨?踰덊샇
        "profile_name": username_receive,                           # ?꾨줈???대쫫 湲곕낯媛믪? ?꾩씠??
        "profile_pic": "",                                          # ?꾨줈???ъ쭊 ?뚯씪 ?대쫫
        "profile_pic_real": "profile_pics/profile_placeholder.png", # ?꾨줈???ъ쭊 湲곕낯 ?대?吏
        "profile_info": ""                                          # ?꾨줈????留덈뵒
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/sign_up/save', methods=['GET'])
def users_get():
    users_list = list(db.users.find({}, {'_id': False}))
    return jsonify({'users':users_list})




@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # ?꾨줈???낅뜲?댄듃
        return jsonify({"result": "success", 'msg': '?꾨줈?꾩쓣 ?낅뜲?댄듃?덉뒿?덈떎.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/posting/<username>')
def user_post(username):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('posting.html', user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/posting/save', methods=['GET'])
def get_post():
    posts_list = list(db.posts.find({}, {'_id': False}))
    return jsonify({'posts':posts_list})


@app.route('/posting/save', methods=['POST'])
def posting():
    username_receive = request.form['username_give']
    username1_receive = request.form['username1_give']
    title_receive = request.form['title_give']
    datepicker_receive = request.form['datepicker_give']
    time_receive = request.form['time_give']
    kind_receive = request.form['kind_give']
    comment_receive = request.form['comment_give']

    file = request.files["file_give"]
    extension = file.filename.split('.')[-1]
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    filename = f'file-{mytime}'
    save_to = f'static/{filename}.{extension}'
    file.save(save_to)

    post = list(db.posts.find({}, {'_id': False}))
    count = len(post) + 1

    doc = {
        'num': count,
        "username": username_receive,
        "username1": username1_receive,
        "title": title_receive,
        "datepicker": datepicker_receive,
        "time": time_receive,
        "kind": kind_receive,
        "comment": comment_receive,
        'file': f'{filename}.{extension}'
    }
    db.posts.insert_one(doc)
    return jsonify({'result': 'success'})

# @app.route('/sign_up/save', methods=['POST'])
# def sign_up():
#     username_receive = request.form['username_give']
#     username1_receive = request.form['username1_give']
#     password_receive = request.form['password_give']
#     password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
#     doc = {
#         "username1": username1_receive,                             # ?대쫫
#         "username": username_receive,                               # ?꾩씠??
#         "password": password_hash,                                  # 鍮꾨?踰덊샇
#         "profile_name": username_receive,                           # ?꾨줈???대쫫 湲곕낯媛믪? ?꾩씠??
#         "profile_pic": "",                                          # ?꾨줈???ъ쭊 ?뚯씪 ?대쫫
#         "profile_pic_real": "profile_pics/profile_placeholder.png", # ?꾨줈???ъ쭊 湲곕낯 ?대?吏
#         "profile_info": ""                                          # ?꾨줈????留덈뵒
#     }
#     db.users.insert_one(doc)
#     return jsonify({'result': 'success'})
#
# @app.route('/sign_up/save', methods=['GET'])
# def users_get():
#     users_list = list(db.users.find({}, {'_id': False}))
#     return jsonify({'users':users_list})

@app.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # ?ъ뒪??紐⑸줉 諛쏆븘?ㅺ린
        return jsonify({"result": "success", "msg": "?ъ뒪?낆쓣 媛?몄솕?듬땲??"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 醫뗭븘????蹂寃?
        return jsonify({"result": "success", 'msg': 'updated'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

    @app.route("/feedback", methods=["POST"])
    def feedback_post():
        feedback_name_receive = request.form['feedback_name_give']
        feedback_receive = request.form['feedback_give']

        doc = {
            'feedback_name': feedback_name_receive,
            'feedback': feedback_receive
        }
        db.feedback.insert_one(doc)
        return jsonify({'msg': '댓글 완료!'})


    @app.route("/feedback", methods=["GET"])
    def feedback_get():
        feedback_list = list(db.feedback.find({}, {'_id': False}))
        return jsonify({'feedbacks': feedback_list})




if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)