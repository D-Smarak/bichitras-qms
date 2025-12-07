# User Setup Instructions

## Creating the First Admin User

To create the first admin user, you need to use Django's management command:

```bash
python manage.py createsuperuser
```

This will prompt you for:
- Username
- Email (optional)
- Password

After creating the superuser, you can:
1. Log in to the system
2. Go to "User Management" in the admin sidebar
3. Create additional users (Admin or Controller roles) from the web interface

## Creating Users via Web Interface (Admin Only)

Once logged in as an admin:
1. Navigate to **User Management** in the sidebar
2. Click **Add User** button
3. Fill in the form:
   - Username (required)
   - Email (optional)
   - First Name / Last Name (optional)
   - Role: Select either "Admin" or "Controller"
   - Password: Enter a secure password
   - Confirm Password: Re-enter the same password
   - Is Active: Check to make user active immediately
   - Is Staff: Check if user should have staff privileges
4. Click **Save**

## Default Credentials

**Note:** There are no default credentials. You must create the first admin user using the `createsuperuser` command.

## User Roles

- **Admin**: Full access to master data management, user management, and analytics
- **Controller**: Access to testing pipeline and result entry

## Password Requirements

- Passwords should be secure (minimum 8 characters recommended)
- Passwords are hashed and stored securely
- Admins can reset user passwords from the User Management interface

Quick reference
Role	         Username	         Password
Admin	         admin	            admin123
Controller	   controller1	      controller123
Controller	   controller2	      controller123
Controller	   controller3	      controller123