# Gym Management System

## Overview
The Gym Management System is a web-based application built using Django that helps gym administrators manage memberships, track member attendance, schedule classes, and maintain records. This system streamlines gym operations by providing an easy-to-use interface for managing day-to-day activities.

## Features
- **Member Management**: Add, update, and delete member information.
- **Attendance Tracking**: Record and monitor member attendance.
- **Class Scheduling**: Schedule classes and manage class enrollments.
- **Payment Management**: Track membership payments and dues.
- **Reporting**: Generate reports for memberships, attendance, and financials.
- **User Authentication**: Secure login for admin and staff.

## Technologies Used
- **Backend**: Django, Django Rest Framework
- **Frontend**: HTML, CSS, JavaScript (optional: React, Vue.js)
- **Database**: SQLite (default), can be configured to use PostgreSQL, MySQL, etc.
- **Other Tools**: Celery for background tasks (optional)

## Installation

### Prerequisites
- Python 3.x
- Django 3.x or higher
- Git
- Virtualenv

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/hasnainAli22/gms.git
   cd gms
   ```

2. **Create and Activate Virtual Environment**:
    ```
    python3 -m venv env
    env\Scripts\activate
    ```

3. **Install Dependencies**:
    ```
    pip install -r requirements.txt
    ```

5. **Setup Database**:
    ```
    python manage.py makemigrations
    python manage.py migrate
    ```

6. **Create Superuser**:
  python manage.py createsuperuser

7. **Run Development Server**:
  python manage.py runserver

8. **Access the Application**:
Open your web browser and go to [http://127.0.0.1:8000](http://127.0.0.1:8000)


## Usage
### Admin Panel
Access the admin panel at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
Use the admin credentials created during the createsuperuser step to log in.
From the admin panel, you can manage members, Subscriptions, Inventory, Trainer, and payments.
### Main Features
- **Members**: Add and manage member information.
- **Trainer**: Add and manage trainer information.
-  **Payments**: Record and manage payments.
## Configuration
### Database
By default, the project uses SQLite. To use a different database, update the DATABASES setting in settings.py with your database configuration.

### Email
To enable email notifications, configure the `EMAIL_BACKEND` and related settings in settings.py.

### Static Files
To serve static files in production, configure the `STATIC_ROOT` and use a web server like Nginx or Apache.

### Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes. Ensure that your code adheres to the project's coding standards and includes appropriate tests.
Things to work on
1. Dockerizing the Project.
2. Adding Celery Support to Support the Chatting between the Trainer and Member.
3. Adding the attandance management.
4. Working on the realtime notification.

### License
This project is licensed under the MIT License. See the LICENSE file for details.

### Contact
For any questions or suggestions, feel free to open an issue or contact me at [our.hasnain22@gmail.com](mailto:our.hasnain22@gmail.com)

Thank you for using the Gym Management System!
