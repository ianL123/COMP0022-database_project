# Movie Database Project

This project is a movie search and management system. Currently, no manual data preprocessing is required; you can start the system directly using the containers.

## 1. Getting Started

### Launching the Containers
Run the following command in your terminal to build and start the services:

```bash
docker compose up --build -d
```

If you haven't changed any code logic and just want to restart the app, you can use:

```bash
docker compose up -d
```

### Important: Asynchronous Initialization

Please note that the database starts **asynchronously**. The application will only be fully functional once the MySQL server has finished its internal setup. To verify the status, run:

```bash
docker logs -f mysql_server
```

The app is **only ready** to start if you see lines similar to these:

```plaintext
> `[System] [MY-010931] [Server] /usr/sbin/mysqld: ready for connections. Version: '9.6.0' ...`
```

This should take a few minutes to load. However, the program only need to do so once, precisely at the first docker compose.

### Shutting Down

To stop the services:

```bash
docker compose down
```

If you also wish to detach the volume (which is the databse), use:

```bash
docker compose down -v
```

---

## 2. Verifying Results

After your finished waiting on the asynchronous initialization, open your browser and navigate to: [http://localhost](http://localhost)

**Expected Result**: Access to all interfaces for Tasks 1-6.

---

## 3. UI and Styling

The project utilizes two external style sources and one local stylesheet:

```html
<link href="[https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css](https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css)" rel="stylesheet">
<link rel="stylesheet" href="[https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css](https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css)">
<link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
```

Our custom styles are located in `static/css/style.css`. Due to the CSS cascade, our custom definitions will override Bootstrap's defaults, allowing for personalized modifications.

## 4. Project Layout

```plaintext
COMP0022-database_project
├── app.py                # Main Flask application (Routes & Core Logic)
├── docker-compose.yml    # Docker services configuration
├── Dockerfile            # Python environment setup
├── init.sql              # Database schema & data import
├── user_system.py        # Auth & Folder management
├── ml-latest/            # Core Movie Datasets (CSV)
├── static/               # CSS & JavaScript (Charts/Maps)
└── templates/            # HTML Views (Jinja2)
```
