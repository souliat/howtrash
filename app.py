from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/content_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb+srv://test:sparta@cluster0.dmyon.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        status = True
        return render_template('index.html', user_info=user_info, status=status)

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        status = False
        return render_template('index.html', status=status)

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest() # Hash함수를 이용해서 패스워드를 암호화
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        status = True

        return jsonify({'result': 'success', 'token': token, 'status': status})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png", # 프로필 사진 기본 이미지
        "profile_info": ""                                          # 프로필 한 마디
    }

    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

# 중분류 아이템들 다 가져와서 던져주는 것.
@app.route("/get_posts", methods=['GET'])
def get_posts():
    item_list = list(db.items.find({}, {'_id': False}))
    return jsonify({'item_list': item_list, "result": "success"})


# admin 에서 저장하는 것.
@app.route("/save_posts", methods=["POST"])
def save_posts():
    category_receive = request.form['category_give']
    item_num_receive = request.form['item_num_give']
    img_path_receive = request.form['img_path_give']
    content_txt_receive = request.form['content_txt_give']

    doc = {
        'category': category_receive,
        'item_num': item_num_receive,
        'img_path': img_path_receive,
        'content_txt': content_txt_receive
    }

    db.items.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})

@app.route('/items/<item_num>')
def item(item_num):
    token_receive = request.cookies.get('mytoken')
    print("토큰 리시브", token_receive is not None)
    try:
        if token_receive is not None:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.users.find_one({"username": payload["id"]})
            # status = request.args.get("status")
            status = True

            item_info = db.items.find_one({"num": item_num}, {"_id": False})
            return render_template('detail.html', user_info=user_info, item_info=item_info, status=status)
        else:
            status = False

            item_info = db.items.find_one({"num": item_num}, {"_id": False})
            return render_template('detail.html', item_info=item_info, status=status)

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# 댓글 저장하기
@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        user_info = db.users.find_one({"username": payload["id"]})
        comment_receive = request.form["comment_give"]
        date_receive = request.form["date_give"]
        num_receive = request.form["num_give"]

        doc = {
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            "comment": comment_receive,
            "date": date_receive,
            "item_num": num_receive
        }

        db.posts.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 댓글 가져오기 + 상세페이지는 특정 댓글만 가져오기
@app.route("/get_comments", methods=['GET'])
def get_comments():
    token_receive = request.cookies.get('mytoken')
    try:
        if token_receive is not None:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

            num_receive = request.args.get("num_give") # 해당 상세페이지에 해당하는 num이 get방식으로 전달되었으므로 args.get 사용

            if num_receive == "":
                posts = list(db.posts.find({}).sort("date", -1).limit(20))
            else: # num_receive가 있다면 detail.html에서 불렸다는 소리.
                posts = list(db.posts.find({"item_num": num_receive}).sort("date", -1).limit(20))

            for post in posts:
                post["_id"] = str(post["_id"]) # 좋아요를 눌렀는지 안눌렀는지를 확인할 고유 식별자를 id값으로 하며 이를 str타입으로 변경하여 사용.
                post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
                post["heart_by_me"] = bool(db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload['id']}))

            return jsonify({"result": "success", "status": "login", "posts": posts, "msg": "포스팅을 가져왔습니다."})
        else:
            posts = list(db.posts.find({}).sort("date", -1).limit(20))
            for post in posts:
                post["_id"] = str(post["_id"])
                post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})

            return jsonify({"result": "success", "status": "logout", "posts": posts, "msg": "포스팅을 가져왔습니다."})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 좋아요 수 변경
        user_info = db.users.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]

        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive
        }

        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)

        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)