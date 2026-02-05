import requests
from requests.auth import HTTPBasicAuth

API_BASE = "http://127.0.0.1:8000/api"

# Store credentials and user info globally
_credentials = None
_current_user = None

def set_credentials(username, password):
    """Store credentials for API calls"""
    global _credentials, _current_user
    if not username or not password:
        _credentials = None
        _current_user = None
    else:
        _credentials = HTTPBasicAuth(username, password)

def get_auth():
    """Get current authentication"""
    return _credentials

def get_current_user():
    """Get current logged-in user info"""
    return _current_user

def login(username, password):
    """Authenticate user"""
    global _current_user
    try:
        response = requests.post(
            f"{API_BASE}/auth/login/",
            json={'username': username, 'password': password}
        )
        if response.status_code == 200:
            set_credentials(username, password)
            _current_user = response.json()
            return _current_user
        else:
            return None
    except:
        return None

def register(username, password, email=''):
    """Register new user"""
    global _current_user
    try:
        response = requests.post(
            f"{API_BASE}/auth/register/",
            json={'username': username, 'password': password, 'email': email}
        )
        if response.status_code == 201:
            set_credentials(username, password)
            _current_user = response.json()
            return _current_user
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
        return {"error": "Not authenticated."}
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_BASE}/datasets/", files=files, auth=auth)
    try:
        payload = response.json()
    except Exception:
        payload = {}
    if response.status_code in [200, 201]:
        return payload
    return {"error": payload.get("error", "Upload failed.")}

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

def get_records(dataset_id, params=None):
    """Fetch filtered records for a dataset"""
    auth = get_auth()
    if not auth:
        return {"error": "Not authenticated."}
    response = requests.get(
        f"{API_BASE}/datasets/{dataset_id}/records/",
        auth=auth,
        params=params or {}
    )
    try:
        payload = response.json()
    except Exception:
        payload = {}
    if response.status_code == 200:
        return payload
    return {"error": payload.get("error", "Failed to load records.")}

def get_users():
    """Fetch all users (admin only)"""
    auth = get_auth()
    if not auth:
        return []
    response = requests.get(f"{API_BASE}/admin/users/", auth=auth)
    return response.json() if response.status_code == 200 else []

def delete_user(user_id):
    """Delete a user (admin only)"""
    auth = get_auth()
    if not auth:
        return None
    response = requests.delete(f"{API_BASE}/admin/users/{user_id}/", auth=auth)
    return response.status_code
