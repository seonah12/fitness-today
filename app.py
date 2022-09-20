
from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb://test:test@localhost', 27017)
# client = MongoClient('localhost', 27017)
db = client.dbsparta


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/fitness', methods=['POST'])
def posting():
    title_receive = request.form['title_give']
    datepicker_receive = request.form['datepicker_give']
    kind_receive = request.form['kind_give']
    time_receive = request.form['time_give']
    comment_receive = request.form['comment_give']

    file = request.files["file_give"]

    save_to = 'static/mypicture.png'
    file.save(save_to)

    doc = {
        'title':title_receive,
        'datepicker':datepicker_receive,
        'kind':kind_receive,
        'time':time_receive,
        'comment':comment_receive
    }

    db.fitness.insert_one(doc)

    return jsonify({'msg': '등록완료'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)