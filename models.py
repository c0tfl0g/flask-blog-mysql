
from exts import db
from datetime import datetime

class  Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    title = db.Column(db.String(100),nullable=False)
    content = db.Column(db.Text,nullable=False)
    create_time = db.Column(db.DateTime,default=datetime.now)
    # now()获取的是服务器第一次运行的时间
    # now就是每次创建一个模型的时候，都获取当前的时间
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    author = db.relationship('User',backref=db.backref('questions'))
    #follow = db.relationship('Follow',backref=db.backref('follows'))

class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    content = db.Column(db.Text,nullable=False)
    question_id = db.Column(db.Integer,db.ForeignKey('question.id'))
    create_time = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    question = db.relationship('Question',backref=db.backref('answers'),order_by=create_time.desc())
    author = db.relationship('User',backref=db.backref('answers'))
    __mapper_args__ = {
    "order_by": create_time.desc()
    }


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    telephone = db.Column(db.String(11),nullable=False)
    username = db.Column(db.String(50),nullable=False)
    password = db.Column(db.String(100),nullable=False)

class Follow(db.Model):
    __tablename__ = 'follow'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # addtime = db.Column(db.DATETIME, default=datetime.now)







# 字段中lazy=joined模式，可以直接从数据库中取出所有事例，无需一次次查询。
#
# lazy=dynamic，返回的是一个query对象，可以进行后续过滤操作。
#
# delete-orphan,可以监控删除情况，当一方删除后，这个指向也会被消除，all是为了删除没有指向的孤儿记录。
# * relationship的order_by参数：在指定relationship的时候，传递order_by参数来指定排序的字段。
# * 在模型定义中，添加以下代码：
#
# __mapper_args__ = {
# "order_by": title
# }
#
# 即可让文章使用标题来进行排序。