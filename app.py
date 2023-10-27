from flask import *
from flask_paginate import Pagination
#导入数据库模块
import pymysql
import re
from urllib.parse import quote
import traceback
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'xyzgjl'  # 设置一个安全的密钥来启用会话


# 路由访问静态文件
# 默认路径访问首页界面
@app.route('/index')
def index():
    username = session.get('user_name', '')  # 获取用户名
    recipes = []   # 需要返回的食谱数据
    foods = []  # 需要返回的食谱数据
    news = []  # 需要返回的食谱数据
    userworks = []  # 需要返回的食谱数据

    # 查询语句
    recipes_sql = """SELECT * FROM recipes"""
    foods_sql = """SELECT * FROM foods"""
    news_sql = """SELECT * FROM news"""
    userworks_sql = """SELECT * FROM userworks"""

    # 食谱
    cursor.execute(recipes_sql)
    result = cursor.fetchall()
    # 取八个食谱数据进行返回
    for i in range(8):
        # recipe = {"id": result[i][0], "name": result[i][1], "type": result[i][2], "img": result[i][3], "info": result[i][4], "material": result[i][5], "make": result[i][6]}
        recipe = {"id": result[i][0], "name": result[i][1], "type": result[i][2], "img": result[i][3]}
        recipes.append(recipe)

    # 食材
    cursor.execute(foods_sql)
    result = cursor.fetchall()
    for i in range(12):
        food = {"id": result[i][0], "name": result[i][1], "img": result[i][2]}
        foods.append(food)

    # 饮食新闻
    cursor.execute(news_sql)
    result = cursor.fetchall()
    for i in range(4):
        new = {"id": result[i][0], "name": result[i][1], "author": result[i][2], "time": result[i][3], "source": result[i][4], "img": result[i][5]}
        news.append(new)

    # 用户作品
    cursor.execute(userworks_sql)
    result = cursor.fetchall()
    for i in range(6):
        userwork = {"id": result[i][0], "name": result[i][1], "author": result[i][2], "time": result[i][3], "img": result[i][4]}
        userworks.append(userwork)

    return render_template("index.html", username=username, recipes=recipes, foods=foods, news=news, userworks=userworks)

# 默认路径访问食谱界面
@app.route('/recipe')
def recipe():
    username = session.get('user_name', '')  # 获取用户名
    recipes = []  # 需要返回的食谱数据
    types = []
    limit = 15
    # 查询语句
    recipes_sql = """SELECT * FROM recipes"""
    cursor.execute(recipes_sql)
    result = cursor.fetchall()
    # 取所有食谱数据进行返回
    for i in range(len(result)):
        # recipe = {"id": result[i][0], "name": result[i][1], "type": result[i][2], "img": result[i][3], "info": result[i][4], "material": result[i][5], "make": result[i][6]}
        recipe = {"id": result[i][0], "name": result[i][1], "type": result[i][2], "img": result[i][3]}
        recipes.append(recipe)
        if result[i][2] not in types:
            types.append(result[i][2])

    page = int(request.args.get("page", 1))
    start = (page - 1) * limit
    end = page * limit if len(recipes) > page * limit else len(recipes)
    paginate = Pagination(page=page, total=len(recipes), per_page=limit)
    ret = recipes[start:end]

    current_url = request.path
    return render_template("recipe.html", username=username, types=types, recipes=ret, paginate=paginate, current_url=current_url)

# 默认路径访问食谱分类界面
@app.route('/recipe/<recipe_type>')
def recipe_type(recipe_type='全部'):
    limit = 15
    username = session.get('user_name', '')  # 获取用户名
    recipes = []  # 需要返回的食谱数据
    # 食谱的类型
    types = []
    recipes_sql = """SELECT * FROM recipes"""
    cursor.execute(recipes_sql)
    result = cursor.fetchall()
    # 取所有食谱数据进行返回
    for i in range(len(result)):
        if result[i][2] not in types:
            types.append(result[i][2])
    # 查询语句
    recipes_sql = """SELECT * FROM recipes WHERE recipe_type = %s"""
    cursor.execute(recipes_sql, (recipe_type))
    result = cursor.fetchall()
    # 取所有食谱数据进行返回
    for i in range(len(result)):
        # recipe = {"id": result[i][0], "name": result[i][1], "type": result[i][2], "img": result[i][3], "info": result[i][4], "material": result[i][5], "make": result[i][6]}
        recipe = {"id": result[i][0], "name": result[i][1], "type": result[i][2], "img": result[i][3]}
        recipes.append(recipe)
    # 分页
    page = int(request.args.get("page", 1))
    start = (page - 1) * limit
    end = page * limit if len(recipes) > page * limit else len(recipes)
    paginate = Pagination(page=page, total=len(recipes), per_page=limit)
    ret = recipes[start:end]
    # 获取当前路由
    current_url = quote(request.path)
    return render_template("recipe.html", username=username, types=types, recipes=ret, paginate=paginate, current_url=current_url)


# 默认路径访问食材界面
@app.route('/food')
def food():
    username = session.get('user_name', '')  # 获取用户名
    # 每页数据条数
    limit = 15
    foods = []  # 需要返回的食材数据
    # 查询语句
    foods_sql = """SELECT * FROM foods"""
    cursor.execute(foods_sql)
    result = cursor.fetchall()
    # 取所有食材数据进行返回
    for i in range(len(result)):
        food = {"id": result[i][0], "name": result[i][1], "img": result[i][2]}
        foods.append(food)

    # 分页实现
    page = int(request.args.get("page", 1))
    start = (page - 1) * limit
    end = page * limit if len(foods) > page * limit else len(foods)
    paginate = Pagination(page=page, total=len(foods), per_page=limit)
    ret = foods[start:end]
    return render_template("food.html", username=username, foods=ret, paginate=paginate)


# 默认路径访问饮食新闻界面
@app.route('/news')
def news():
    username = session.get('user_name', '')  # 获取用户名

    # 每页数据条数
    limit = 20
    news = []  # 需要返回的作品数据
    # 查询语句
    news_sql = """SELECT * FROM news"""
    cursor.execute(news_sql)
    result = cursor.fetchall()
    # 取所有作品数据进行返回
    for i in range(len(result)):
        new = {"id": result[i][0], "name": result[i][1], "author": result[i][2], "time": result[i][3],
               "source": result[i][4], "img": result[i][5]}
        news.append(new)

    # 分页实现
    page = int(request.args.get("page", 1))
    start = (page - 1) * limit
    end = page * limit if len(news) > page * limit else len(news)
    paginate = Pagination(page=page, total=len(news), per_page=limit)
    ret = news[start:end]

    return render_template("news.html", username=username, news=ret, paginate=paginate)

    # return render_template("news.html", username=username)

# 默认路径访问用户作品界面
@app.route('/userwork')
def userwork():
    username = session.get('user_name', '')  # 获取用户名
    # 每页数据条数
    limit = 20
    userworks = []  # 需要返回的作品数据
    # 查询语句
    userworks_sql = """SELECT * FROM userworks"""
    cursor.execute(userworks_sql)
    result = cursor.fetchall()
    # 取所有作品数据进行返回
    for i in range(len(result)):
        userwork = {"id": result[i][0], "name": result[i][1], "author": result[i][2], "time": result[i][3], "img": result[i][4]}
        userworks.append(userwork)
    # 分页实现
    page = int(request.args.get("page", 1))
    start = (page - 1) * limit
    end = page * limit if len(userworks) > page * limit else len(userworks)
    paginate = Pagination(page=page, total=len(userworks), per_page=limit)
    ret = userworks[start:end]
    return render_template("userwork.html", username=username, userworks=ret, paginate=paginate)


# 默认路径访问上传作品界面
@app.route('/releasework')
def releasework():
    username = session.get('user_name', '')  # 获取用户名
    if username != '':
        return render_template("releasework.html", username=username)
    else:
        flash("请登录后进行作品上传！", 'danger')
        return render_template("login.html", username=username)

# 默认路径上传作品
@app.route('/upload', methods=["POST"])
def upload():
    username = session.get('user_name', '')  # 获取用户名
    workname = request.values.get('workname').strip()  # 获取作品名
    workmaterial = request.values.get('workmaterial').strip()    # 获取作品材料
    workinfo = request.values.get('workinfo').strip()    # 获取作品介绍
    workmake = request.values.get('workmake').strip()    # 获取作品方法
    worktime =datetime.now().strftime("%y-%m-%d")   # 获取作品时间
    # 上传文件
    uploaded_file = request.files.get("workimg")
    if uploaded_file:
        filename = uploaded_file.filename
        file_path = './static/uploads/' + filename
        uploaded_file.save(file_path)
        message = "上传成功！"
    else:
        file_path = ''
        message = "上传失败！"
    # SQL 插入语句
    sql = """INSERT INTO userworks (work_name, work_author, work_time, work_pic, work_info, work_material, work_make) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(sql, (workname, username, '20' + worktime, './.' + file_path, workinfo, workmaterial, workmake))
    # 提交到数据库执行
    db.commit()
    return render_template("releasework.html", username=username, message=message)

# 默认路径访问登录界面
@app.route('/login')
def login():
    username = session.get('user_name', '')  # 获取用户名
    return render_template("login.html", username=username)

# 默认路径访问注册界面
@app.route('/register')
def register():
    username = session.get('user_name', '')  # 获取用户名
    return render_template("register.html", username=username)

# 默认路径访问详情界面
@app.route('/detail/<ID>')
def detail(ID):
    username = session.get('user_name', '')  # 获取用户名
    html_id = int(request.args.get('html_id'))
    # 根据html_id选择不同的表进行查询
    if html_id == 1:  # 查询食谱表
        recipe_sql = """SELECT * FROM recipes WHERE recipe_id = %s"""
        cursor.execute(recipe_sql, (int(ID)))
        result = cursor.fetchall()
        make = result[0][6].replace('\n', '', 1)
        recipe = {"id": result[0][0], "name": result[0][1], "type": result[0][2], "img": result[0][3],
                  "info": Markup(result[0][4].replace('\n·\n', '')), "material": result[0][5],
                  "make": Markup(make.replace('\n', '<br>'))}
        return render_template("detail.html", username=username, data=recipe, html_id=1)
    elif html_id == 2:  # 查询食材表
        food_sql = """SELECT * FROM foods WHERE food_id = %s"""
        cursor.execute(food_sql, (int(ID)))
        result = cursor.fetchall()
        food = {"id": result[0][0], "name": result[0][1], "img": result[0][2],
                  "info": result[0][3], "effect": result[0][4], "adapt": result[0][5]}
        return render_template("detail.html", username=username, data=food, html_id=2)
    elif html_id == 3:  # 查询新闻表
        news_sql = """SELECT * FROM news WHERE news_id = %s"""
        cursor.execute(news_sql, (int(ID)))
        result = cursor.fetchall()
        news = {"id": result[0][0], "name": result[0][1], "author": result[0][2], "time": result[0][3],
               "source": result[0][4], "img": result[0][5], "content": Markup(re.sub(r'\n+', '<br>', result[0][6]))}
        # Markup(result[0][6].replace('\n', ''))
        return render_template("detail.html", username=username, data=news, html_id=3)
    elif html_id == 4:    # 查询作品表
        userwork_sql = """SELECT * FROM userworks WHERE work_id = %s"""
        cursor.execute(userwork_sql, (int(ID)))
        result = cursor.fetchall()
        make = result[0][7].replace('\n', '', 1)
        userwork = {"id": result[0][0], "name": result[0][1], "author": result[0][2], "time": result[0][3], "img": result[0][4],
                  "info": Markup(result[0][5].replace('\n·\n', '')), "material": result[0][6],
                  "make": Markup(make.replace('\n', '<br>'))}
        return render_template("detail.html", username=username, data=userwork, html_id=4)

# 默认路径访问搜索内容界面
@app.route('/search')
def search():
    username = session.get('user_name', '')  # 获取用户名
    inputname = request.args.get('inputname')
    recipes = []
    limit = 15
    # 模糊搜索，通配符%
    recipe_sql = """SELECT * FROM recipes WHERE recipe_name like %s"""
    cursor.execute(recipe_sql, ('%' + inputname + '%'))
    result = cursor.fetchall()
    # 取所有食谱数据进行返回
    for i in range(len(result)):
        recipe = {"id": result[i][0], "name": result[i][1], "type": result[i][2], "img": result[i][3]}
        recipes.append(recipe)

    page = int(request.args.get("page", 1))
    start = (page - 1) * limit
    end = page * limit if len(recipes) > page * limit else len(recipes)
    paginate = Pagination(page=page, total=len(recipes), per_page=limit)
    ret = recipes[start:end]
    return render_template("search.html", username=username, recipes=ret, paginate=paginate)



# 连接数据库,此前在数据库中创建数据库TESTDB
db = pymysql.connect(host="localhost", user="root", password="root", database="recipe_web")
# 使用cursor()方法获取操作游标
cursor = db.cursor()

# 获取注册请求及处理
@app.route('/registuser')
def getRigistRequest():
    # 把用户名和密码注册到数据库中
    username = request.args.get('username')
    password = request.args.get('password')
    again_pwd = request.args.get('again_pwd')

    # SQL 查询语句
    sql_check = """SELECT * FROM users WHERE user_name = %s"""

    # SQL 插入语句
    sql = """INSERT INTO users (user_name, user_pwd) VALUES (%s, %s)"""

    try:
        # 执行查询语句
        cursor.execute(sql_check, (username))
        result = cursor.fetchall()
        if len(result) == 1:
            # 用户已存在
            flash('用户已存在，请重新注册！', 'danger')
            # 使用redirect函数来重定向到新的路由
            return redirect(url_for('register'))
        else:
            if password != again_pwd:
                flash('两次输入密码不一致，请重新注册！', 'danger')
                # 使用redirect函数来重定向到新的路由
                return redirect(url_for('register'))
            else:
                # 执行sql插入语句
                cursor.execute(sql, (username, password))
                # 提交到数据库执行
                db.commit()
                flash('注册成功，请登录！', 'info')
                return redirect(url_for('login'))
    except:
        # 抛出错误信息
        traceback.print_exc()
        # 如果发生错误则回滚
        db.rollback()
        return '注册失败'

# 获取登录参数及处理
@app.route('/loginuser')
def getLoginRequest():
    # 查询用户名及密码是否匹配及存在
    # SQL 查询语句
    username = request.args.get('username')
    password = request.args.get('password')
    sql = """SELECT * FROM users WHERE user_name = %s and user_pwd = %s"""
    try:
        # 执行sql语句
        cursor.execute(sql, (username, password))
        result = cursor.fetchall()
        if len(result) == 1:
            # 在登录成功时设置会话
            session['user_name'] = username
            flash(username, 'success')
            # 登录成功后，重定向用户到首页
            # 使用redirect函数来重定向到新的路由
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误，请重新登录！', 'danger')
            # 登录失败后，重定向用户到登录页面
            # 使用redirect函数来重定向到新的路由
            return redirect(url_for('login'))
        # 提交到数据库执行
        db.commit()
    except Exception as e:
        # 如果发生错误则回滚
        traceback.print_exc()
        db.rollback()
        return '发生错误，请重试'

# 注销登录
@app.route('/logout')
def logout():
    session.pop('user_name', None)
    flash('你已退出登录!', 'warning')
    return redirect(url_for('login'))

#     # # 关闭数据库连接
#     # db.close()

if __name__ == '__main__':
    app.run()
