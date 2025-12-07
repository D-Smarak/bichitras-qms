# Bichitras Quality Management System (QMS)

A comprehensive Quality Management System for lab testing operations, product management, and quality compliance.

## Features

- **User Management**: Role-based access control (Admin & Controller)
- **Product Management**: Master data for products, categories, suppliers, and units
- **Quality Configuration**: Test parameters, methods, and product specifications
- **Testing Pipeline**: Multi-step testing process with progress tracking
- **Analytics Dashboard**: Comprehensive analytics with charts and visualizations
- **Reporting**: PDF and CSV export capabilities

## Tech Stack

- **Backend**: Django 5.x
- **Frontend**: Jinja2 templates with TailwindCSS
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Deployment**: Render

## Setup Instructions

### Local Development

1. Clone the repository:
```bash
git clone <your-repo-url>
cd QMS
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

### Deployment on Render (Simple SQLite Setup)

1. Push your code to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Configure environment variables:
   - `SECRET_KEY`: Generate a secure secret key (Render can auto-generate)
   - `DEBUG`: Set to `False`
   - `ALLOWED_HOSTS`: Your Render domain (e.g., `qms-web.onrender.com`)
5. Set build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
6. Set start command: `gunicorn qms.wsgi:application`
7. Deploy!

**Note**: SQLite is used for this demo. For production with multiple users, consider PostgreSQL.

## User Roles

- **Admin**: Full access to master data, analytics, and user management
- **Controller**: Access to testing pipeline and result entry

## Project Structure

```
QMS/
├── apps/
│   ├── core/          # Base models and utilities
│   ├── users/          # User management and authentication
│   ├── products/       # Product master data
│   ├── quality/        # Quality configuration
│   ├── testing/        # Testing pipeline
│   └── analytics/      # Analytics and reporting
├── qms/                # Project settings
├── services/           # Export services (PDF, CSV)
├── templates/          # Jinja2 templates
├── static/             # Static files
└── requirements.txt    # Python dependencies
```

## License

Proprietary - Bichitras Group Pvt. Ltd.

