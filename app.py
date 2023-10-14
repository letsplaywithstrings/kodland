from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from models import db, User
import copy
import random
from misc import get_weather, questions, day_names

app = Flask(__name__)
app.secret_key = 'PDIHSadpAIDHJasADF66664'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)
with app.app_context():
    db.create_all()


@app.route('/styles/<path:filename>')
def serve_css(filename):
    return send_from_directory('styles', filename)


def init_session():
    session['asked'] = 0
    session['answers'] = {}
    session['questions'] = copy.deepcopy(questions)
    session['last_id'] = 0


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data, processed_weather_data = [], None
    if request.method == 'POST':
        city = request.form['city']

        processed_weather_data, weather_data = get_weather(city)

    return render_template('index.html', logged_in='username' in session, weather_data=weather_data,
                           day_names=day_names, processed_weather_data=processed_weather_data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        flash('Zaten giriş yapıldı!', 'danger')
        return render_template('error.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        nickname = request.form['nickname']
        existing_user = User.query.filter((User.username == username) | (User.nickname == nickname)).first()
        if existing_user:
            flash(
                'Kullanıcı adı veya takma adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı veya takma adı seçin.',
                'danger')
            return render_template('register.html', show_data=False)

        if password != confirm_password:
            flash('Şifreler uyuşmuyor. Lütfen aynı şifreyi girin.', 'danger')
            return render_template('register.html', show_data=False)

        new_user = User(username=username, password=password, nickname=nickname)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        flash('Kayıt başarıyla tamamlandı!', 'success')
        return redirect('/')

    return render_template('register.html', show_data=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        flash('Zaten giriş yapıldı!.','default')
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['username'] = username
            session['nickname'] = user.nickname
            flash('Giriş başarılı!', 'success')
            return redirect("/")
        else:
            flash('Geçersiz kullanıcı adı veya şifre!', 'danger')

    return render_template('login.html', show_data=False)


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'username' not in session:
        flash('Sınavı yapabilmek için giriş yapmalısınız.','danger')
        return render_template('error.html')
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if user and user.score is not None:
        flash('Sınavı tekrar yapamazsınız, skorunuz zaten kaydedilmiştir.','default')
        flash('Skorunuz: ' + str(user.score),'success')
        return render_template('error.html')

    if 'questions' not in session or 'answers' not in session:
        init_session()

    score = 0

    if request.method == 'POST':
        user_answer = request.form.get(f'answer_{session["last_id"]}', '-1')
        user_answer = int(
            user_answer) if user_answer.isdigit() else -1
        session['answers'][str(session['last_id'])] = user_answer
    else:
        session['answers'] = {}
        session['questions'] = copy.deepcopy(questions)
        session['last_id'] = 0
        current_question = random.choice(session['questions'])
        session['last_id'] = current_question['id']
        session["asked"] += 1
        session['questions'].remove(current_question)
        return render_template('quiz.html', show_question=True, score=score, question=current_question, logged_in=True)

    if session['asked'] < len(questions):
        current_question = random.choice(session['questions'])
        session['last_id'] = current_question['id']
        session["asked"] += 1
        session['questions'].remove(current_question)

        return render_template('quiz.html', question=current_question, show_question=True, score=0, logged_in=True)
    else:
        username = session.get('username')
        user = User.query.filter_by(username=username).first()
        if user:
            correct_answers = {str(question['id']): int(question['correct_answer']) for question in questions}
            score = sum(20 if session['answers'][qid] == correct_answers[qid] else 0 for qid in session['answers'])
            if score < 60:
                session['asked'] = 0
                session['answers'] = {}
                session['questions'] = copy.deepcopy(questions)
                session['last_id'] = 0
                current_question = random.choice(session['questions'])
                session['last_id'] = current_question['id']
                session["asked"] += 1
                session['questions'].remove(current_question)
                flash('Sınavı geçmek için en az 60 puan almanız gerekmektedir. Sınava tekrar girebilirsiniz!','danger')
                return render_template('quiz.html' ,show_question=True, score=score, question=current_question, logged_in=True)

            user.score = score
            db.session.commit()

        return render_template('quiz.html', show_question=False, score=score, logged_in=True)


@app.route('/leaderboard')
def leaderboard():
    leaderboard_data = User.query.order_by(User.score.desc()).all()
    return render_template('leaderboard.html', leaderboard_data=leaderboard_data, logged_in='username' in session)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == "POST":
        session.clear()

        return redirect(url_for('index'))
    else:
        return render_template('logout.html')


if __name__ == '__main__':
    app.run(debug=True)
