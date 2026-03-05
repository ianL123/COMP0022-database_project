# 数据

本作业需求的数据可以这个网址下载：
https://files.grouplens.org/datasets/movielens/

注意：按照作业要求，我们“可以去 Rotten Tomatoes, IMDB or other sites 下载任何我们想要的数据”，
数据爬取属于本课程的考察范围。

# Getting Started
目前版本无需预处理数据，直接启动容器即可。

### 1. 启动容器

在终端运行以下命令

```bash
docker compose up --build -d

```

如果没有改变代码逻辑，则运行
```bash
docker compose up -d

```

### 2. 验证结果

打开你的浏览器，在地址栏输入：

http://localhost:5001

注：现在在网站后台没有启动完成（数据库初次读取）之前，会出现一个错误，这个错误来页面强调样式需求的对正在
使用的页面信息的读取。

**预期结果**：
Task 1-4的所有界面

输入以下命令关闭Docker镜像：
```bash
docker compose down
```
如果数据库内容有变化，就需要以下命令让docker重启时重新加载数据库：
```bash
docker compose down -v
```

# 网页风格

在页面中加入了两个指定页面风格的内容。
```html
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <!-- others -->
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
```
其中后者在static\css\style.css中，可以对前面的样式进行个性化修改。注意由于书写顺序我们自定义的样式会覆盖前面的样式。

## 标签拆分

目前已经写了`.genre`类的样式，可以对电影类型标签进行个性化修改。似乎tag也应该做对应调整。

目前的配色仅仅是功能展示，未来可以改地更好看一些。

# MySQL

1. **进入 MySQL 数据库** 等待容器启动完成后，运行以下命令进入 MySQL 交互界面：
```bash
docker exec -it mysql_server mysql -u root -ppassword123 my_project_db

```

2. **检查 MySQL 数据库内容**
```bash
SELECT * from init_run_log;
```
等到最后一行变成finished即可启动网页。


3. **退出** 操作完成后，输入以下命令退出 MySQL 终端：
```sql
exit
```