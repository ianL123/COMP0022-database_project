# 数据

我已经将最基本的数据集下载在ml-latest-small文件夹中。
**这些数据可能需要重新清洗然后放入新文件中**
本作业需求的其余数据也可以这个网址下载：
https://files.grouplens.org/datasets/movielens/。

注意：按照作业要求，我们“可以去 Rotten Tomatoes, IMDB or other sites 下载任何我们想要的数据”，
数据爬取属于本课程的考察范围。

# Docker

安装https://www.docker.com/products/docker-desktop/
然后你的电脑里就有所有docker相关的环境了。

# 架构

这里有两个选择，一是我们等第二周的两节课结束之后，根据课程内容自行选择构建架构。

二是github上有一堆COMP0022的作业，我们拿一个回来魔改。

# MySQL

1. **启动服务** 在项目根目录下运行以下命令来构建并启动所有容器：
```bash
docker compose up --build -d

```

2. **进入 MySQL 数据库** 等待容器启动完成后，运行以下命令进入 MySQL 交互界面：
```bash
docker exec -it mysql_server mysql -u root -ppassword123 my_project_db

```

3. **检查 MySQL 数据库内容**
```bash
SELECT COUNT(*) from links; # should be 9742
SELECT COUNT(*) from movies; # should be 9742
SELECT COUNT(*) from ratings; # should be 100836
SELECT COUNT(*) from tags; # should be 3683
SELECT COUNT(*) from average_ratings; # shoule be 9724

SELECT * FROM init_run_log ORDER BY id;
```

最后一行的输出应该是三条你的启动时间，你可以检查时间是否正确。
如果出现任何错误可能是你上一次docker退出方式不对，请完整执行第4步，然后重新开始。


4. **退出** 操作完成后，输入以下命令退出 MySQL 终端：
```sql
exit
```
输入以下命令关闭Docker镜像：
```bash
docker compose down -v
```

# Getting Started
### 1. 重新启动容器

在终端运行以下命令。Docker 会检测到配置变化，自动下载 Nginx 镜像并启动新容器

```bash
docker compose up --build -d

```

### 2. 验证结果

打开你的浏览器，在地址栏输入：

http://localhost:5001

**预期结果**：
一个可以搜索电影均分的页面

# 网页风格

在页面中加入了两个指定页面风格的内容。
```html
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <!-- others -->
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
```
其中后者在static\css\style.css中，可以对前面的样式进行个性化修改。注意由于书写顺序我们自定义的样式会覆盖前面的样式。