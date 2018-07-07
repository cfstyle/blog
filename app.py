#coding=utf-8
#chenfei 20180706

from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from datetime import timedelta
from data import get_articles
from config import MYSQL_CONFIG
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

# mysql config
app.config['MYSQL_HOST'] = MYSQL_CONFIG['host']
app.config['MYSQL_USER'] = MYSQL_CONFIG['username']
app.config['MYSQL_PASSWORD'] = MYSQL_CONFIG['password']
app.config['MYSQL_DB'] = MYSQL_CONFIG['db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' # 结果是字典格式

# init mysql
mysql = MySQL(app)


# 设置静态文件缓存过期时间
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
#也可以这样写：
#app.send_file_max_age_default = timedelta(seconds=1)

@app.route("/")
def index():
    results = {
        'page': 'index',
    }
    return render_template('home.html', results=results)

@app.route("/about/")
def about():
    results = {
        'page': 'about',
    }
    return render_template('about.html', results=results)


class RegisterForm(Form):
    username = StringField(u'用户名', validators=[validators.input_required(), validators.Length(min=4, max=25, message=u"用户名长度必须大于4，小于25")])
    email  = StringField(u'邮箱', validators=[validators.Length(min=6, max=50, message=u"邮箱地址长度必须大于6，小于50")])
    password = PasswordField(u'密码', validators=[
            validators.DataRequired(),
            validators.EqualTo('confirm', message=u'两次输入密码不一致！')
        ])
    confirm = PasswordField(u'确认密码')

@app.route("/user/register/", methods=['GET', 'POST'])
def register():
    results = {
        'page': 'user_register',
    }
    form = RegisterForm(request.form)
    results['form'] = form
    
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # create mysql cursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO user(username, password, email, is_superuser) VALUES(%s, %s, %s, 0)",   (username, email, password))

        # commit to mysql
        mysql.connection.commit()

        # close the connection
        cur.close()

        flash(u'您已经注册成功！', 'success')

        return redirect(url_for('index', results={'page': 'index'}))

    return render_template('user/register.html', results=results)

@app.route("/blog/<id>/")
def blog_detail(id):
    results = {
        'page': 'blog_detail',
        'blog': {}
    }
    for each in get_articles():
        if each.get('id') == int(id):
            results['blog'] = each
            break
    return render_template('blog/detail.html', results=results)

@app.route("/blog/recent/")
def blog_recent():
    results = {
        'page': 'blog_recent',
        'articles': []
    }
    results['articles'] = get_articles()
    return render_template('blog/recent.html', results=results)

@app.route("/blog/archive/")
def blog_archive():
    results = {
        'page': 'blog_archive',
    }
    return render_template('blog/archive.html', results=results)

if __name__ == '__main__':
    app.secret_key = 'secret_chenfei'
    app.run(debug=True)