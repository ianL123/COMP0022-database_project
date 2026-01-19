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

# Getting Started

1. **启动服务** 在项目根目录下运行以下命令来构建并启动所有容器：
```bash
docker compose up --build

```

2. **进入 MySQL 数据库** 等待容器启动完成后，运行以下命令进入 MySQL 交互界面：
```bash
docker exec -it mysql_server mysql -u root -p

```


3. **输入密码** 当提示 `Enter password:` 时，输入：
`password123`
4. **退出** 操作完成后，输入以下命令退出 MySQL 终端：
```sql
exit
```

# Nginx
### 1. 重新启动容器

在终端运行以下命令。Docker 会检测到配置变化，自动下载 Nginx 镜像并启动新容器

```bash
docker compose up -d

```

### 2. 验证结果

打开你的浏览器，在地址栏输入：

http://localhost

**预期结果**：
一个写着 **"Welcome to nginx!"** 的页面。
