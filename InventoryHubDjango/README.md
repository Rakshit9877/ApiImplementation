# InventoryHub - Django Inventory Management System

InventoryHub is a comprehensive inventory management system built with Django. This application helps businesses manage and track their inventory, organize items into groups, and monitor inventory statistics.

## Features

- User authentication and authorization
- Dashboard with inventory statistics and insights
- Item management (add, edit, delete items)
- Item group organization
- Admin dashboard for user management and system monitoring
- Responsive design for desktop and mobile devices

## Prerequisites

- Python 3.8 or higher
- Django 4.2 or higher
- SQLite (default) or other database supported by Django

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/inventory_hub.git
cd inventory_hub
```

2. Create and activate a virtual environment:
```
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Apply migrations:
```
python manage.py migrate
```

5. Create a superuser:
```
python manage.py createsuperuser
```
   Or use the existing superuser credentials:
   - Username: admin
   - Email: jindalrakshit3@gmail.com
   - Password: admin123

6. Run the development server:
```
python manage.py runserver
```

7. Access the application at http://127.0.0.1:8000/

## Project Structure

- `accounts/` - User authentication and profile management
- `inventory/` - Core inventory functionality (items, groups, dashboard)
- `admin_dashboard/` - Administrative functions and analytics
- `templates/` - HTML templates for all apps
- `static/` - CSS, JavaScript, and image files

## Usage

1. **Login/Register**: Create an account or use the admin account
2. **Dashboard**: View inventory statistics and insights
3. **Items**: Manage your inventory items
4. **Groups**: Organize items into groups by type
5. **Admin Dashboard**: Monitor system activity and manage users (admin only)

## Security

- Django's built-in authentication system secures user accounts
- Role-based access control restricts sensitive features to administrators
- CSRF protection on all forms

## Credits

This project was migrated from a Flask-based implementation to Django.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 