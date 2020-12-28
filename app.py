#encoding:utf-8
from flask import Flask,render_template,request,redirect,url_for,session,g
import config
from models import User,Question,Answer,Follow
from exts import db
from decorators import login_required
from sqlalchemy import or_
from wtforms import Form
from wtforms.fields import simple
from wtforms import validators
from wtforms import widgets
import hashlib
def md5(str1):
    return hashlib.md5(str(str1).encode()).hexdigest()

class LoginForm(Form):
    telephone = simple.StringField(
        label = '用户名',
        validators=[
            validators.DataRequired(message='用户名不能为空'),
            validators.Length(min=3,max=18,message='用户名长度必须大于%(min)d且小于%(max)d')
        ],
        widget = widgets.TextInput(),
        render_kw={'class': 'form-control','placeholder':"手机号码"}

    )
    password = simple.PasswordField(
        label='密码',
        validators = [
            validators.DataRequired(message='密码不能为空.'),
            validators.Length(min=3,message='密码长度必须大于%(min)d')
        ],
        widget = widgets.PasswordInput(),
        render_kw={'class': 'form-control',"placeholder":'密码'}
    )

class RegisterForm(Form):
    telephone =simple.StringField(
        label = '手机号',
        validators=[
            validators.DataRequired(message='用户电话不能为空'),
            validators.Length(min=11,max=11,message='手机号长度必须为%(min)d')
        ],
        widget = widgets.TextInput(),
        render_kw={'class': 'form-control','placeholder':"手机号码"}

    )
    username = simple.StringField(
        label='用户名',
        validators=[
            validators.DataRequired(message='用户名不能为空'),
            validators.Length(min=3, max=18, message='用户名长度必须大于%(min)d且小于%(max)d')
        ],
        widget=widgets.TextInput(),
        render_kw={'class': 'form-control', 'placeholder': "用户名"}

    )
    password1 = simple.PasswordField(
        label='密码1',
        validators = [
            validators.DataRequired(message='密码不能为空.'),
            validators.Length(min=3,message='密码长度必须大于%(min)d')
        ],
        widget = widgets.PasswordInput(),
        render_kw={'class': 'form-control',"placeholder":'密码'}
    )
    password2 = simple.PasswordField(
        label='密码2',
        validators=[
            validators.DataRequired(message='确认密码不能为空.'),
            validators.EqualTo('password1', message="两次密码输入不一致")
        ],
        widget=widgets.PasswordInput(),
        render_kw={'class': 'form-control', "placeholder": '确认密码'}
    )

app = Flask(__name__)
app.config.from_object(config)
#app.config['SERVER_NAME'] = 'zut.cn:5000'
db.init_app(app)



@app.route('/')
def index():
    context = {
        'questions':Question.query.order_by(Question.create_time.desc()).all()
    }
    return render_template('index.html',**context)

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        form = LoginForm()
        return render_template('login.html',form=form)
    else:
        form = LoginForm(formdata = request.form)
        # print(form.telephone)
        # print(form.password)
        if form.validate():
            telephone = request.form.get('telephone')
            password = request.form.get('password')
            user = User.query.filter(User.telephone == telephone,User.password == md5(password)).first()
            if user:
                session['user_id'] = user.id
                # 如果想在31天内都不需要登录
                session.permanent = True
                return redirect(url_for('index'))
            else:

                #return render_template('login.html',form=form)
                return render_template('login.html',form=form,flag=1)
        else:
            return render_template('login.html',form=form)


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        form = RegisterForm()
        return render_template('register.html',form=form)
    else:
        form = RegisterForm(formdata=request.form)
        if form.validate():

            telephone = request.form.get('telephone')
            username = request.form.get('username')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            # 收集号码验证，如果被注册了，就不能再注册了
            # if password1 != password2:
            #     # return u'两次密码不相等，请核对后再填写!'
            #     return render_template('register.html', form=form,flag=1)
            # else:
            user = User.query.filter(User.telephone == telephone).first()
            if user:
                # return u'该手机号已被注册，请更换手机号码'
                return render_template('register.html', form=form, flag=2)
            else:
                user = User(telephone=telephone, username=username, password=md5(password1))
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))
        else:
            return render_template('register.html',form=form)




@app.route('/search/')
def search():
    q = request.args.get('q')
    questions = Question.query.filter(or_(Question.title.contains(q),Question.content.contains(q)))
    context = {
        'questions': questions
    }
    return render_template('index.html',**context)

@app.route('/logout/')
def logout():
    #session.pop('user_id')
    #del_session['user_id']
    session.clear()
    return redirect(url_for('login'))

@app.route('/question/',methods=['GET','POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title,content=content)
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        question.author = user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/detail/<question_id>',methods=['GET','POST'])
def detail(question_id):
    if request.method == 'GET':
        question_model = Question.query.filter(Question.id == question_id).first()
        return render_template('detail.html', question=question_model)
    else:
        if session.get('user_id'):
            question_model = Question.query.filter(Question.id == question_id).first()
            #followed = User.query.filter(User.id == request.form.get('followed_id')).first()  # 查询被关注者的id
            # followed_id = followed.id

            follow = Follow()

            follow.follower_id = int(session.get('user_id'))  # 关注者的id
            follow.followed_id = int(request.form.get('followed_id'))
            #print(follow.follower_id)
            #print(follow.followed_id)
            db.session.add(follow)
            db.session.commit()
            followed_id = request.form.get('followed_id')  # 接收文章作者的id
            follow_id = session.get('user_id')
            #print(followed_id)
            #print(follow_id)
            follow_flag = Follow.query.filter(Follow.followed_id == question_model.author.id,Follow.follower_id == session.get('user_id')).first()
            # if follow_flag!=None:
            #     follow_flag = 1
            #     print(follow_flag)
            #     return render_template('detail.html', question=question_model,follow_flag=follow_flag)
            # else:
            return redirect(url_for('detail', question_id=question_id))

            #follow_model = Follow.query.filter(Follow.follower_id == session.get('user_id')).first()
            #return render_template('detail.html',question=question_model,follow=follow_model)
        else:
            return redirect(url_for('login'))


@app.route('/add_answer/',methods=['POST'])
def add_answer():

    content = request.form.get('answer_content')
    question_id = request.form.get('question_id')
    answer = Answer(content=content)
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        answer.author = user
        question = Question.query.filter(Question.id == question_id).first()
        answer.question = question
        db.session.add(answer)
        db.session.commit()

        return redirect(url_for('detail',question_id=question_id))
    else:
        return redirect(url_for('login'))


@app.route('/person_info/',methods=['GET','POST'])
def person_info():
    user_id = session.get('user_id')
    user = User.query.filter(User.id == user_id).first()
    followers_id = Follow.query.filter(Follow.followed_id == user_id).all()
    # for follower in followers_id:
    #     print(follower)
    #followers = User.query.filter(User.id == followers_id.follower_id).all()

    return render_template('persion_info.html',user=user,followers_num=len(followers_id))
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'),404


@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user_id = user_id
            return {'user':user}

    return {}


if __name__ == '__main__':
    app.run()
