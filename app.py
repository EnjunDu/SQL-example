from flask import Flask, request, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.sql import text
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zheshiyigeanquanmiyaoo~'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///signin.db'
db = SQLAlchemy(app)

# 用户模块
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    sign_ins = db.relationship('SignIn', backref='user', lazy=True)

# 签到记录模块
class SignIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sign_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# 创建数据库表格
@app.before_request
def create_tables():
    db.create_all()

# 登录检查装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 管理员权限检查装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('admin') != True:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# 主页
@app.route('/')
def index():
    return render_template('index.html')

# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return '用户名和密码不能为空'

        if not User.query.filter_by(username=username).first():
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html')

# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return '用户名和密码不能为空'

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['admin'] = False
            return redirect(url_for('signin'))
        else:
            return '登录失败'

    return render_template('login.html')

# 签到
@app.route('/signin', methods=['GET', 'POST'])
@login_required
def signin():
    if request.method == 'POST':
        new_sign_in = SignIn(user_id=session['user_id'])
        db.session.add(new_sign_in)
        db.session.commit()
        return ('签到成功！'
                'LFXXKIDNMF4SA3TFMVSCA5DPEB2XGZJAM5ZG65LQEBSW4Y3SPFYHI2LPNYQQ===='
                '86,106,74,87,99,49,107,121,79,88,82,97,85,49,86,53,84,85,104,83,100,107,112,85,83,88,100,107,82,50,104,119,89,51,108,86,101,85,49,70,98,70,82,82,77,69,49,115,84,87,112,67,77,49,112,88,83,87,120,78,97,107,74,52,90,70,100,87,101,109,82,72,98,72,90,105,97,86,85,122,85,108,86,79,100,109,74,116,90,72,108,90,87,70,73,120,89,107,100,71,77,71,70,88,79,88,86,106,101,86,86,53,84,85,99,53,100,85,112,85,83,88,100,107,82,48,90,121,89,86,99,49,98,107,112,85,83,88,100,90,86,122,86,50,90,69,100,111,98,71,78,112,86,88,108,78,83,69,52,119,87,108,104,66,98,69,49,113,81,106,66,105,77,50,82,111,89,50,49,83,101,107,112,85,83,88,100,90,98,107,112,115,87,86,100,48,99,71,74,116,89,50,120,78,97,107,73,119,89,85,104,75,100,109,82,88,90,71,57,75,86,69,108,52,83,108,82,74,100,49,82,116,79,84,78,75,86,69,108,51,87,86,78,86,101,85,49,73,85,109,120,105,87,69,74,50,89,50,49,71,101,87,86,84,86,88,108,78,83,69,74,53,89,106,73,120,100,50,82,68,86,88,108,78,82,50,120,54,83,108,82,74,100,49,111,121,98,68,74,97,86,122,82,115,84,87,112,66,100,69,112,85,83,88,100,107,82,50,104,115,83,108,82,74,100,49,108,88,85,110,82,104,86,122,86,119,89,122,78,83,101,86,108,89,85,110,90,106,97,86,86,53,84,106,78,78,98,69,49,113,81,109,104,90,77,107,53,50,90,70,99,49,77,69,112,85,83,88,100,104,87,69,49,115,84,87,112,66,98,69,52,119,83,107,112,86,77,69,53,69,87,72,112,74,100,48,49,113,85,109,90,106,77,110,81,49,87,68,66,119,97,70,107,121,100,71,90,83,83,70,86,115,84,106,66,82,100,85,112,85,83,88,100,87,82,50,104,119,89,51,108,86,101,85,49,72,77,87,104,108,85,49,86,53,84,85,100,75,98,69,112,85,83,88,100,107,98,86,90,53,90,86,78,86,101,85,49,73,86,110,112,97,86,49,111,120,89,107,77,49,81,50,82,89,85,87,120,78,97,107,73,119,89,85,100,86,98,69,49,113,81,109,104,97,82,122,70,119,89,109,49,115,101,109,82,73,83,109,104,107,82,122,108,53,83,108,82,74,100,50,78,72,82,110,112,106,77,50,82,50,89,50,49,82,98,69,49,113,81,109,112,90,86,122,86,49,89,106,78,82,98,69,49,113,81,109,108,97,85,49,86,53,84,85,100,87,97,71,77,121,98,72,78,108,85,49,86,53,84,85,104,83,100,109,74,72,85,87,120,78,97,107,73,119,89,110,108,86,101,85,49,73,98,72,90,107,85,49,86,53,85,88,108,86,101,85,49,72,84,110,90,105,98,108,74,119,89,109,53,87,98,69,112,85,83,88,100,97,87,71,104,51,89,107,99,53,101,87,70,88,78,87,53,75,86,69,108,52')
    else:
        return render_template('signin.html')

# 管理员登录
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 设置一个专门的管理员账号密码
        admin_username = 'ISCC_2024_sky_Jack_Du'
        admin_password = 'sky_1s_S0_h@NdsOme~_1234678910'

        # 检查是否是特定管理员
        if username == admin_username:
            # 允许使用 SQL 注入，仅当用户名为 "sky"
            query = text(f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'")
            result = db.session.execute(query).fetchone()
            if result:
                session['admin'] = True
                session['user_id'] = result.id
                return redirect(url_for('admin_dashboard'))
            else:
                return '登录失败'
        else:
            # 对于其他用户, 使用普通的安全验证
            user = User.query.filter_by(admin_username=username,admin_password=password).first()
            if user:
                session['admin'] = True
                session['user_id'] = user.id
                return redirect(url_for('admin_dashboard'))
            else:
                return '登录失败'

    return render_template('admin_login.html')

# 后台面板
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    sign_ins = SignIn.query.all()
    return render_template('admin_dashboard.html', sign_ins=sign_ins)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8848)
