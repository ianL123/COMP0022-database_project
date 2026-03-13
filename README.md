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

### Database

To log into the database, use:

```bash
docker exec -it mysql_server mysql -u root -ppassword123 my_project_db
```

## 2. Verifying Results

After your finished waiting on the asynchronous initialization, open your browser and navigate to: [http://localhost](http://localhost)

**Expected Result**: Access to all interfaces for Tasks 1-6.

---

## 3. Project Layout

```plaintext
COMP0022-database_project
├── ml-latest/            # Core Movie Datasets (CSV)
├── templates/            # HTML Views (Jinja2)
├── static/               # CSS & JavaScript (Charts/Maps)
├── analytics.py          # Analytical tasks (2, 3, 5)
├── app.py                # Main Flask application (Routes & Core Logic)
├── docker-compose.yml    # Docker services configuration
├── Dockerfile            # Python environment setup
├── extensions.py         # Global constants
├── ER Diagram.png        # ER Diagram
├── init.sql              # Database schema & data import
├── nginx.conf            # nginx configurations
├── predict.py            # Predictive tasks (4)
├── requirements.txt      # Python library requirements
└── user_system.py        # User Authentication & Folder management (Task 6)
```
