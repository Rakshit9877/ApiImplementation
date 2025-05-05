from app import app, db, Item, Group, GroupAttribute, User
from datetime import datetime

def add_more_mock_data():
    print("Adding more mock data to the database...")
    
    # Check if we have a user, if not create one
    if User.query.count() == 0:
        admin_user = User(username="admin", email="admin@example.com", role="admin")
        admin_user.generate_password("admin123")
        db.session.add(admin_user)
        db.session.flush()
        user_id = admin_user.id
        print(f"Created admin user with ID: {user_id}")
    else:
        user_id = User.query.first().id
        print(f"Using existing user with ID: {user_id}")
    
    # Add more items
    new_items = [
        Item(name="Monitor", sku="MON-001", unit="piece", returnable=True, 
             selling_price=350.00, cost_price=250.00, tax_rate=18.0, quantity_in_hand=20, reorder_point=5),
        
        Item(name="USB Drive", sku="USB-001", unit="piece", returnable=True, 
             selling_price=25.00, cost_price=10.00, tax_rate=5.0, quantity_in_hand=100, reorder_point=20),
        
        Item(name="External Hard Drive", sku="HDD-001", unit="piece", returnable=True, 
             selling_price=120.00, cost_price=80.00, tax_rate=18.0, quantity_in_hand=15, reorder_point=3),
        
        Item(name="Wireless Router", sku="RTR-001", unit="piece", returnable=True, 
             selling_price=75.00, cost_price=50.00, tax_rate=12.0, quantity_in_hand=12, reorder_point=4),
        
        Item(name="Graphics Card", sku="GFX-001", unit="piece", returnable=True, 
             selling_price=650.00, cost_price=500.00, tax_rate=18.0, quantity_in_hand=8, reorder_point=2),
        
        Item(name="Office Chair", sku="CHR-001", unit="piece", returnable=False, 
             selling_price=200.00, cost_price=120.00, tax_rate=12.0, quantity_in_hand=10, reorder_point=3),
        
        Item(name="Desk Lamp", sku="LMP-001", unit="piece", returnable=True, 
             selling_price=40.00, cost_price=20.00, tax_rate=5.0, quantity_in_hand=25, reorder_point=8)
    ]
    
    for item in new_items:
        db.session.add(item)
    
    print(f"Added {len(new_items)} new items")
    
    # Add more groups
    new_groups = [
        {
            "group": Group(
                type="goods",
                name="Computer Accessories",
                description="Various accessories for computers and laptops",
                returnable=True,
                unit="piece",
                manufacturer="Various",
                brand="Multiple",
                created_by=user_id
            ),
            "attributes": [
                {"name": "Connection Type", "options": "Wired, Wireless, Bluetooth"},
                {"name": "Compatibility", "options": "Windows, Mac, Linux, All"}
            ]
        },
        {
            "group": Group(
                type="goods",
                name="Office Supplies",
                description="Common office supplies and stationery",
                returnable=True,
                unit="piece",
                manufacturer="OfficePro",
                brand="OfficeMate",
                created_by=user_id
            ),
            "attributes": [
                {"name": "Color", "options": "Black, Blue, Red, Green, Assorted"},
                {"name": "Packaging", "options": "Single, Pack of 5, Pack of 10, Box"}
            ]
        },
        {
            "group": Group(
                type="service",
                name="IT Support",
                description="Technical support and IT services",
                returnable=False,
                unit="hour",
                manufacturer="TechSupport Inc",
                brand="TechHelp",
                created_by=user_id
            ),
            "attributes": [
                {"name": "Service Level", "options": "Basic, Standard, Premium"},
                {"name": "Response Time", "options": "24 hours, 12 hours, 4 hours, 1 hour"}
            ]
        }
    ]
    
    for group_data in new_groups:
        group = group_data["group"]
        db.session.add(group)
        db.session.flush()  # Get the group ID
        
        # Add attributes
        for attr in group_data["attributes"]:
            attribute = GroupAttribute(
                group_id=group.id,
                attribute_name=attr["name"],
                options=attr["options"]
            )
            db.session.add(attribute)
    
    print(f"Added {len(new_groups)} new groups")
    
    # Commit all changes
    db.session.commit()
    print("All data committed to database successfully!")

if __name__ == "__main__":
    with app.app_context():
        add_more_mock_data() 