# Inventory Hub API Integration Project

This project demonstrates the integration between a Flask backend API and a Django frontend application. The system allows managing inventory items and groups, with data storage in both Django and Flask databases.

## Project Structure

- **InventoryHub-Flask**: Flask API backend providing RESTful endpoints
- **InventoryHubDjango**: Django frontend consuming Flask APIs

## Manual Startup Instructions

### Starting the Flask API Server

```bash
# Activate the Flask virtual environment
source flask_env/bin/activate

# Navigate to the Flask project directory
cd InventoryHub-Flask

# Start the Flask server
python app.py

# The Flask API will be available at: http://localhost:5001/api
```

### Starting the Django Server

```bash
# In a new terminal, activate the Django virtual environment
source django_env/bin/activate

# Navigate to the Django project directory
cd InventoryHubDjango

# Start the Django server
python manage.py runserver

# The Django application will be available at: http://127.0.0.1:8000/
```

## Workflow

1. **User Registration**: Users sign up in the Django application, with data stored in the Django database.
2. **Item/Group Management**: 
   - When adding items/groups in Django, data is stored in both Django and Flask databases.
   - The Django app consumes Flask APIs to synchronize data.
3. **Data Display**: 
   - Item list, group list, and dashboard data in Django are retrieved from the Flask API.
   - All data is displayed through the Django frontend.

## API Endpoints (Flask)

- **GET /api/items**: Get all inventory items
- **GET /api/items/<id>**: Get a specific item
- **POST /api/items**: Create a new item
- **PUT /api/items/<id>**: Update an existing item
- **DELETE /api/items/<id>**: Delete an item

- **GET /api/groups**: Get all groups
- **GET /api/groups/<id>**: Get a specific group
- **POST /api/groups**: Create a new group
- **PUT /api/groups/<id>**: Update an existing group
- **DELETE /api/groups/<id>**: Delete a group

- **GET /api/dashboard**: Get dashboard statistics

## Setup and Installation

1. Install required packages for both projects:

```bash
# For Flask project
cd InventoryHub-Flask
pip install -r requirements.txt

# For Django project
cd ../InventoryHubDjango
pip install -r requirements.txt
```

2. Run both applications:

```bash
# Run using the provided script
./run_apps.sh

# Or manually:
# Terminal 1 - Flask app
cd InventoryHub-Flask
python app.py

# Terminal 2 - Django app
cd InventoryHubDjango
python manage.py runserver
```

3. Access the applications:
   - Flask API: http://localhost:5000
   - Django frontend: http://localhost:8000

## Implementation Details

- Flask API uses SQLAlchemy for database management.
- Django consumes Flask APIs using the requests library.
- Mock data is automatically generated in the Flask application.
- Django application stores user data locally and syncs item/group data with Flask.

## Notes

- The Flask API has CORS enabled to allow cross-origin requests from Django.
- Both applications have their own databases, but the Django app shows all data from the Flask API.
- Error handling is in place to gracefully degrade to using local data if the Flask API is unavailable. 