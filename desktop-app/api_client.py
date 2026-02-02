import requests
from requests.auth import HTTPBasicAuth

API_BASE = "http://127.0.0.1:8000/api"

# Store credentials globally
_credentials = None

def set_credentials(username, password):
    """Store credentials for API calls"""
    global _credentials
    _credentials = HTTPBasicAuth(username, password)

def get_auth():
    """Get current authentication"""
    return _credentials

def login(username, password):
    """Authenticate user"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/login/",
            json={'username': username, 'password': password}
        )
        if response.status_code == 200:
            set_credentials(username, password)
            return response.json()
        else:
            return None
    except:
        return None

def register(username, password, email=''):
    """Register new user"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/register/",
            json={'username': username, 'password': password, 'email': email}
        )
        if response.status_code == 201:
            set_credentials(username, password)
            return response.json()
        else:
            return None
    except:
        return None

def get_datasets():
    """Fetch all datasets"""
    auth = get_auth()
    if not auth:
        return []
    response = requests.get(f"{API_BASE}/datasets/", auth=auth)
    return response.json() if response.status_code == 200 else []

def upload_csv(file_path):
    """Upload CSV file"""
    auth = get_auth()
    if not auth:
        return None
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_BASE}/datasets/", files=files, auth=auth)
    return response.json() if response.status_code in [200, 201] else None

def get_summary(dataset_id):
    """Get dataset summary"""
    auth = get_auth()
    if not auth:
        return None
    try:
        response = requests.get(f"{API_BASE}/datasets/{dataset_id}/summary/", auth=auth)
        if response.status_code != 200:
            return None
        return response.json()
    except requests.exceptions.RequestException:
        return None

def delete_dataset(dataset_id):
    """Delete a dataset"""
    auth = get_auth()
    if not auth:
        return None
    response = requests.delete(f"{API_BASE}/datasets/{dataset_id}/", auth=auth)
    return response.status_code

def download_pdf(dataset_id, save_path):
    """Download PDF report"""
    auth = get_auth()
    if not auth:
        return False
    try:
        response = requests.get(
            f"{API_BASE}/datasets/{dataset_id}/download_pdf/",
            auth=auth
        )
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except:
        return False