from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.models import db, Users, Subject, Chapter, Quiz, Question, Score
from werkzeug.security import generate_password_hash,check_password_hash
import os
from datetime import date, datetime, time
import uuid
from functools import wraps

main = Blueprint('main',__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Login to start !!','error')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('user_type') != type:
                flash('Unauthorized access', 'error')
                return redirect(url_for('main.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/login')
def login_page():
    return render_template('login.html')

@main.route('/login', methods=['POST'])
def login():
    email=request.form['username']
    password=request.form['password']
    if email=='' or password=='':
        flash('Empty Fields !!','error')
        return redirect(url_for('main.login_page'))
    user=Users.query.filter_by(user_mail=email).first()
    if user:
        if check_password_hash(user.user_pass,password):
            session['user_id']=user.user_id
            session['email']=user.user_mail
            session['usename']=user.user_name
            session['user_type']=user.user_type
            session['qualification']=user.qualification
            session['dob']=user.dob
            flash('Login Successful !!','success')
            if user.user_type == 'admin':
                return redirect(url_for('main.admin_homepage'))
            else:
                return redirect(url_for('main.customer_homepage'))

        else:
            flash('Invalid Password !!','error')
            return redirect(url_for('main.login_page'))
    else:
        flash('No user exist with this mail id !!','error')
        return redirect(url_for('main.login_page'))

@main.route('/register')
def register_page():
    return render_template('user_reg.html')

@main.route('/register', methods=['POST'])
def register():
    user_email=request.form['email']
    user_name=request.form['fullname']
    user_pass=request.form['password']
    user_cpass=request.form['cpassword']
    user_qualification=request.form['qualification']
    user_dob=request.form['dob']
    dob = datetime.strptime(user_dob, "%Y-%m-%d").date()

    if user_pass==user_cpass:
        if user_email=="" or user_name=="" or user_pass=="" or user_dob=="":
            flash('Empty Field !!','error')
            return redirect(url_for('main.register_page'))
        else:
            if Users.query.filter_by(user_mail=user_email).first():
                flash('Mail already exists !!','error')
                return redirect(url_for('main.register_page'))

            user_id='C'+ str(uuid.uuid4().hex[:8])

            new_user=Users(user_id=user_id, user_mail=user_email, user_name=user_name, user_type='customer', user_pass=generate_password_hash(user_pass),qualification=user_qualification,dob=dob)
            

            db.session.add(new_user)
            db.session.commit()

            flash('Registeration Successful !!','success')
            return render_template('login.html')
    else:
        flash('Password and Confirm Password should be same !!','error')
        return redirect(url_for('main.register_page'))

@main.route('/admin_home')
@login_required
@role_required('admin')
def admin_homepage():
    user=session['user_id']

    subject_list=Subject.query.all()
    chap=Chapter.query.all()
    user_list=Users.query.all()
    return render_template('admin_home.html',subject_list=subject_list,chap=chap,user_list=user_list)

@main.route('/remove_user/<user>',methods=['POST'])
@login_required
@role_required('admin')
def remove_user(user):
    rm_user=Users.query.filter_by(user_id=user).first()

    db.session.delete(rm_user)
    db.session.commit()
    flash('User removed !!',"success")
    return redirect(request.referrer)

@main.route('/add_subject',methods=['POST'])
@login_required
@role_required('admin')
def add_subject():
    subject_name = request.form['subject_name']
    description = request.form['description']
    id = 'S' + str(uuid.uuid4().hex[:8])

    new_subject = Subject(sub_id=id, sub_name=subject_name, sub_desc=description)
    db.session.add(new_subject)
    db.session.commit()
    
    return redirect(url_for('main.admin_homepage'))

@main.route('/add_chapter/<s_id>',methods=['POST'])
@login_required
@role_required('admin')
def add_chapter(s_id):
    chapter_name = request.form['chapter_name']
    description = request.form['description']
    id = 'C' + str(uuid.uuid4().hex[:8])

    new_chapter = Chapter(chp_id=id, chp_name=chapter_name, chp_desc=description, sub_id=s_id)
    db.session.add(new_chapter)
    db.session.commit()
    
    return redirect(request.referrer)

@main.route('/subject_details/<sub_id>')
@login_required
@role_required('admin')
def subject_details(sub_id):
    sub = Subject.query.filter_by(sub_id=sub_id).first()
    chap = Chapter.query.filter_by(sub_id=sub_id).all()
    return render_template('admin_subject.html', sub=sub, chapters=chap)

@main.route('/edit_subject/<s_id>',methods=['POST'])
@login_required
@role_required('admin')
def edit_subject(s_id):
    sub = Subject.query.filter_by(sub_id=s_id).first()
    sub.sub_name=request.form['subject_name']
    sub.sub_desc=request.form['description']

    db.session.commit()
    return redirect(request.referrer)

@main.route('/delete_subject/<s_id>',methods=['POST'])
@login_required
@role_required('admin')
def delete_subject(s_id):
    sub = Subject.query.filter_by(sub_id=s_id).first()
    db.session.delete(sub)
    db.session.commit()
    flash('Subject deleted !!',"success")
    return redirect(request.referrer)

@main.route('/add_question/<sub>/<chapter>/<quiz>',methods=['GET','POST'])
@login_required
@role_required('admin')
def add_question(sub,chapter,quiz):
    statement=request.form['statement']
    option1=request.form['option1']
    option2=request.form['option2']
    option3=request.form['option3']
    option4=request.form['option4']
    answer=request.form['correctAnswer']
    id = 'Q' + str(uuid.uuid4().hex[:8])
    option={'1': option1, '2': option2, '3': option3, '4': option4}

    ques=Question(ques_id=id,sub_id=sub,chp_id=chapter,q_id=quiz,statement=statement,options=option,answer=answer)
    db.session.add(ques)
    db.session.commit()
    return redirect(request.referrer)

@main.route('/quizzes/<subject>/<chap>',methods=['GET','POST'])
@login_required
def quiz_list(subject,chap):
    sub=Subject.query.filter_by(sub_id=subject).first()
    chapter=Chapter.query.get(chap)
    quiz_list=Quiz.query.filter_by(chp_id=chap).all()
    if session.get('user_type') == 'admin':
        return render_template('quiz_list.html',sub=sub,chapter=chapter, quiz_list=quiz_list)
    else:
        return render_template('quiz_list_user.html',sub=sub,chapter=chapter, quiz_list=quiz_list, today_date=date.today())

@main.route('/add_quiz/<sub>/<chapter>', methods=['GET','POST'])
@login_required
@role_required('admin')
def add_quiz(sub,chapter):
    quiz_name=request.form['quiz_name']
    quiz_date_str=request.form['quiz_date']
    quiz_duration_str=request.form['quiz_duration']
    quiz_id = 'Qz' + str(uuid.uuid4().hex[:8])

    try:
        quiz_date = datetime.strptime(quiz_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash("Invalid date format. Use YYYY-MM-DD.")
        return redirect(request.referrer)
    
    minutes = int(quiz_duration_str)
    quiz_duration = time(hour=minutes // 60, minute=minutes % 60)

    quiz=Quiz(q_id=quiz_id, q_name=quiz_name, chp_id=chapter, sub_id=sub, date_of_quiz=quiz_date, time_dur=quiz_duration)

    db.session.add(quiz)
    db.session.commit()
    return redirect(request.referrer)

@main.route('/questions/<subject>/<chap>/<quiz>',methods=['GET','POST'])
@login_required
def questions(subject,chap,quiz):
    ques_list=Question.query.filter_by(q_id=quiz).all()
    sub=Subject.query.filter_by(sub_id=subject).first()
    chapter=Chapter.query.get(chap)
    quiz=Quiz.query.filter_by(q_id=quiz).first()
    if session.get('user_type') == 'admin':
        return render_template('question_list.html',questions=ques_list,sub=sub,chapter=chapter,quiz=quiz)
    else:
        return render_template('question_list_user.html',questions=ques_list,sub=sub,chapter=chapter,quiz=quiz)

@main.route('/delete_chapter/<chap>',methods=['GET','POST'])
@login_required
@role_required('admin')
def delete_chapter(chap):
    chapter=Chapter.query.filter_by(chp_id=chap).first()
    db.session.delete(chapter)
    db.session.commit()
    return redirect(request.referrer)

@main.route('/edit_chapter/<chap>',methods=['GET','POST'])
@login_required
@role_required('admin')
def edit_chapter(chap):
    chapter=Chapter.query.filter_by(chp_id=chap).first()
    chapter.chp_name=request.form['chapter_name']
    chapter.chp_desc=request.form['description']
    db.session.commit()
    return redirect(request.referrer)

@main.route('/delete_ques/<ques>',methods=['GET','POST'])
@login_required
@role_required('admin')
def delete_ques(ques):
    question=Question.query.filter_by(ques_id=ques).first()
    db.session.delete(question)
    db.session.commit()
    return redirect(request.referrer)

@main.route('/edit_ques/<question>',methods=['GET','POST'])
@login_required
@role_required('admin')
def edit_ques(question):
    ques=Question.query.filter_by(ques_id=question).first()
    ques.statement=request.form['statement']
    option1=request.form['option1']
    option2=request.form['option2']
    option3=request.form['option3']
    option4=request.form['option4']
    ques.answer=request.form['correctAnswer']
    ques.options={'1': option1, '2': option2, '3': option3, '4': option4}

    db.session.commit()
    return redirect(request.referrer)

@main.route('/customer_homepage',methods=['GET','POST'])
@login_required
@role_required('customer')
def customer_homepage():
    user=session['user_id']

    scores = db.session.query(
        Score.total_score, 
        Quiz.q_name, 
        Chapter.chp_name, 
        Subject.sub_name, 
        Score.time_stamp
    ).join(Quiz, Score.q_id == Quiz.q_id) \
     .join(Chapter, Quiz.chp_id == Chapter.chp_id) \
     .join(Subject, Quiz.sub_id == Subject.sub_id) \
     .filter(Score.user_id == user) \
     .all()

    subject_list = Subject.query.limit(4).all()
    return render_template('customer_home.html', subjects=subject_list, scores=scores)

@main.route('/subject/<sub_id>')
@login_required
@role_required('customer')
def subject(sub_id):
    sub = Subject.query.filter_by(sub_id=sub_id).first()
    chap = Chapter.query.filter_by(sub_id=sub_id).all()
    return render_template('subject.html', sub=sub, chapters=chap)

@main.route('/subject_list')
@login_required
def subject_list():
    subjects=Subject.query.all()
    chap=Chapter.query.all()
    return render_template('subject_list.html',subjects=subjects,chap=chap)

@main.route('/quiz/<q_id>')
@login_required
def quiz(q_id):
    quiz = Quiz.query.get(q_id)
    chapter = Chapter.query.get(quiz.chp_id)
    subject = Subject.query.get(quiz.sub_id)
    if not quiz:
        flash("Quiz not found!", "error")
        return redirect(request.referrer)

    questions = Question.query.filter_by(q_id=q_id).all()

    time_duration = quiz.time_dur.hour * 60 + quiz.time_dur.minute

    return render_template('quiz.html',quiz=quiz,chapter=chapter,subject=subject,questions=questions,time_duration=time_duration)

@main.route('/submit_quiz/<q_id>', methods=['POST'])
@login_required
def submit_quiz(q_id):
    quiz = Quiz.query.get(q_id)
    
    if not quiz:
        flash("Invalid quiz!", "error")
        return redirect(url_for('home'))

    questions = Question.query.filter_by(q_id=q_id).all()

    answers = request.form.to_dict()

    score = 0
    for question in questions:
        selected_option_num = answers.get(f"q{question.ques_id}")

        if selected_option_num:
            selected_option_text = question.options.get(selected_option_num)
            if selected_option_text and str(selected_option_text) == str(question.answer):
                score += 1

    total_questions = len(questions)
    percentage_score = (score / total_questions) * 100

    new_score = Score(
        score_id='S' + str(uuid.uuid4().hex[:8]),
        q_id=q_id,
        user_id=session.get('user_id', 'guest'),
        time_stamp=datetime.now(),
        total_score=percentage_score
    )

    db.session.add(new_score)
    db.session.commit()

    flash(f"Quiz submitted! You scored {percentage_score:.2f}%", "success")
    return redirect(url_for('main.customer_homepage'))

@main.route('/search')
def search():
    query = request.args.get('query')
    filter_type = request.args.get('filter')

    if not query:
        flash(f"No search query provided!!", "warning")
        return redirect(request.referrer)

    results = []

    if filter_type == 'subject':
        results = Subject.query.filter(Subject.sub_name.ilike(f"%{query}%")).all()
    elif filter_type == 'quiz':
        results = Quiz.query.filter(Quiz.q_name.ilike(f"%{query}%")).all()
    elif filter_type == 'chapter':
        results = Chapter.query.filter(Chapter.chp_name.ilike(f"%{query}%")).all()
    elif filter_type == 'user':
        results = Users.query.filter(Users.user_name.ilike(f"%{query}%")).all()

    print(results)
    return render_template('search_results.html', results=results, query=query, filter_type=filter_type)

@main.route('/admin/summary')
@login_required
@role_required('admin')
def admin_summary():
    quiz_count = Quiz.query.count()
    user_count = Users.query.count()
    chapter_count = Chapter.query.count()

    subject_data = (
        db.session.query(Subject.sub_name, db.func.count(Quiz.q_id))
        .join(Quiz, Subject.sub_id == Quiz.sub_id)
        .group_by(Subject.sub_name)
        .all()
    )
    subject_names = [row[0] for row in subject_data]
    quiz_counts = [row[1] for row in subject_data]

    top_quizzes_data = (
        db.session.query(Quiz.q_name, db.func.count(Score.q_id))
        .join(Score, Quiz.q_id == Score.q_id)
        .group_by(Quiz.q_name)
        .order_by(db.func.count(Score.q_id).desc())
        .limit(5)
        .all()
    )
    quiz_names = [row[0] for row in top_quizzes_data]
    quiz_attempts = [row[1] for row in top_quizzes_data]

    return render_template(
        'admin_summary.html',
        quiz_count=quiz_count,
        user_count=user_count,
        chapter_count=chapter_count,
        subject_names=subject_names,
        quiz_counts=quiz_counts,
        quiz_names=quiz_names,
        quiz_attempts=quiz_attempts
    )

@main.route('/user/summary')
@login_required
def user_summary():
    user_id = session.get('user_id')

    scores_data = (
        db.session.query(Quiz.q_name, Score.total_score, Score.time_stamp)
        .join(Score, Quiz.q_id == Score.q_id)
        .filter(Score.user_id == user_id)
        .order_by(Score.time_stamp)
        .all()
    )
    quiz_names = [row[0] for row in scores_data]
    scores = [row[1] for row in scores_data]

    total_quizzes = Quiz.query.count()
    attempted_quizzes = Score.query.filter_by(user_id=user_id).count()
    unattempted_quizzes = total_quizzes - attempted_quizzes

    subject_performance = (
        db.session.query(Subject.sub_name, db.func.avg(Score.total_score))
        .join(Quiz, Subject.sub_id == Quiz.sub_id)
        .join(Score, Quiz.q_id == Score.q_id)
        .filter(Score.user_id == user_id)
        .group_by(Subject.sub_name)
        .all()
    )
    subject_names = [row[0] for row in subject_performance]
    avg_scores = [row[1] for row in subject_performance]

    return render_template(
        'user_summary.html',
        quiz_names=quiz_names,
        scores=scores,
        attempted_quizzes=attempted_quizzes,
        unattempted_quizzes=unattempted_quizzes,
        subject_names=subject_names,
        avg_scores=avg_scores
    )



@main.route('/logout')
def logout():
    session.clear()
    flash('Logged Out Successfully','success')
    return redirect(url_for('main.login_page'))
