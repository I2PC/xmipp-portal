# XMIPP-Portal

**Website:** [https://xmipp.i2pc.es](https://xmipp.i2pc.es)

## Overview
XMIPP-Portal is a web-based application designed for ahving a main portal for xmipp, link to the full documentation and visualzie the metrics of installations of Xmipp.

---

## Local Development Setup

### 1. Clone the Repository
```bash
git clone git@github.com:I2PC/xmipp-portal.git
cd xmipp-portal
```

### 2. Configure Environment
- Copy the `.env` file provided (refer to the documentation for details).

### 3. Create Environment
- Use the provided `xmipp-portal.yml` file to set up the Conda environment:
  ```bash
  conda env create -f xmipp-portal.yml
  ```

### 4. Install Database
Install MariaDB server and client:
```bash
sudo apt install mariadb-client-core-10.6
sudo apt-get install mariadb-server
```

### 5. Apply Database Migrations
Activate the environment and run migrations:
```bash
conda activate xmipp-portal
python manage.py makemigrations
python manage.py migrate
```

### 6. Start Development Server
Run the local server:
```bash
python manage.py runserver
```

---

## Service Management

### Restarting the Service
To restart the service:
```bash
su root
sudo systemctl restart xmipp-portal
```

---

## Hosting Information
The application is hosted on the **Asimov** server.

---

## Updating the Application
1. Push changes to the `devel` branch.
2. If there are changes in MySQL tables:
   - Restart Asimov to reload the application:
     ```bash
     su root
     sudo systemctl restart xmipp-portal
     ```
   - A service will automatically relaunch the page.

---

## Code Structure

- **`api/`**: Contains the API logic, including views and serializers for handling server-side requests and responses. Uses Django's REST framework.
- **`main/`**: Main directory with essential Django configuration and core files.
- **`web/`**: Frontend assets including HTML templates, CSS, and JavaScript files for the user interface.

### Key Configuration Files
- **`.gitignore`**: Specifies files and directories to exclude from Git.
- **`LICENSE`**: Contains the project license (GPL-3.0).
- **`Procfile`**: Defines commands for running the application in deployment environments (e.g., Heroku).
- **`README.md`**: Documentation for setting up and running the project.
- **`manage.py`**: Django CLI tool for administrative tasks.
- **`requirements.txt`**: List of Python dependencies for the project.

---

## Documentation
Full documentation is available [here](https://docs.google.com/document/d/1Regp4Wb0g5n7C2DWs3JnJH080hI0VOOv2HagwbOE758/edit?tab=t.0).

---

## License
This project is licensed under GPL-3.0.
