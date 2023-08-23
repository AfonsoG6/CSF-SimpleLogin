# Web App Example with Simple Login Page

## Requirements

Install the python packages listed in the requirements.txt file.

```bash
pip install -r requirements.txt
```

## Deployment

### WSGI

To deploy the app using WSGI, run the following command:

```bash
gunicorn app:app --bind 0.0.0.0:8000
```

### Local

To run the app locally for testing purposes, run the following command:

```bash
python app.py --port 8000
```
