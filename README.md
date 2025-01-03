# Top 50 Songs Website

A modern web application to showcase the top 50 songs, built with Flask and SQLAlchemy.

## Features

- Display top 50 songs with cover images
- Admin panel for content management
- Secure authentication
- Responsive design
- Song details editing
- Cover image upload
- Hero section customization

## Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
flask run
```

4. Access the application at http://127.0.0.1:5000

## Deployment to Render.com

1. Create a [Render.com](https://render.com) account

2. Create a new Web Service:
   - Connect your GitHub repository
   - Choose Python environment
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `gunicorn app:app`

3. Set Environment Variables:
   - `SECRET_KEY`: Your secure secret key
   - `FLASK_ENV`: production
   - `DATABASE_URL`: Your database URL (optional, defaults to SQLite)

4. Deploy the application

## Default Admin Credentials

- Username: `admin`
- Password: `admin123`

**Important**: Change these credentials after first login!

## File Structure

```
top50songs/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── render.yaml         # Render.com configuration
├── gunicorn.conf.py   # Gunicorn configuration
├── static/            # Static files (CSS, uploads)
└── templates/         # HTML templates
```

## Security Notes

- Change the default admin password
- Set a secure SECRET_KEY in production
- Keep your database credentials secure
- Regular security updates
- Monitor application logs

## License

MIT License - feel free to use this project for your own purposes.
