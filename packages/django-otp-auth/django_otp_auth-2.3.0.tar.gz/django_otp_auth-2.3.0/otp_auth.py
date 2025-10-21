import os
import json
import requests
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# -------------------------------
# Configuration (JSON file)
# -------------------------------
BASE_DIR = os.getcwd()  # or use settings.BASE_DIR in Django
OTP_CONFIG_FILE = os.path.join(BASE_DIR, "otp_config.json")

def load_otp_config():
    """Load OTP config from JSON file."""
    if os.path.exists(OTP_CONFIG_FILE):
        with open(OTP_CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        config = {"OTP_API_BASE": "", "OTP_API_KEY": ""}
        save_otp_config(config)
        return config

def save_otp_config(config):
    """Save OTP config to JSON file safely."""
    with open(OTP_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Load current config
otp_config = load_otp_config()
OTP_API_BASE = otp_config.get("OTP_API_BASE")
OTP_API_KEY = otp_config.get("OTP_API_KEY")

def update_otp_config(api_base=None, api_key=None):
    global OTP_API_BASE, OTP_API_KEY, otp_config
    if api_base:
        otp_config["OTP_API_BASE"] = api_base
        OTP_API_BASE = api_base
    if api_key:
        otp_config["OTP_API_KEY"] = api_key
        OTP_API_KEY = api_key
    save_otp_config(otp_config)

# -------------------------------
# Rate Limiter & Sessions
# -------------------------------
OTP_RATE_LIMIT = {}  # mobile -> last_sent_time
OTP_SESSIONS = {}    # mobile -> session_id

def can_send_otp(mobile, limit_seconds=60):
    """Check rate limiting per mobile."""
    last_sent = OTP_RATE_LIMIT.get(mobile)
    now = timezone.now()
    if last_sent and (now - last_sent).total_seconds() < limit_seconds:
        return False, int(limit_seconds - (now - last_sent).total_seconds())
    return True, 0

# -------------------------------
# Client IP
# -------------------------------
def get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")

# -------------------------------
# Send OTP
# -------------------------------
def send_otp(request, mobile_field="mobile"):
    mobile = request.POST.get(mobile_field)
    if not mobile:
        return {"success": False, "message": "Enter a valid mobile number"}

    allowed, wait = can_send_otp(mobile)
    if not allowed:
        return {"success": False, "message": f"Wait {wait}s before requesting OTP again."}

    if not OTP_API_BASE or not OTP_API_KEY:
        return {"success": False, "message": "OTP API configuration missing."}

    try:
        payload = {"mobile_number": mobile}
        headers = {"X-API-KEY": OTP_API_KEY}
        response = requests.post(f"{OTP_API_BASE}/generate/", json=payload, headers=headers, timeout=10)
        data = response.json()

        if response.status_code == 201:
            session_id = data.get("session_id")
            request.session["mobile"] = mobile
            request.session["session_id"] = session_id
            request.session["otp_sent_time"] = timezone.now().timestamp()
            OTP_RATE_LIMIT[mobile] = timezone.now()
            OTP_SESSIONS[mobile] = session_id
            return {"success": True, "message": "OTP sent successfully!"}
        else:
            return {"success": False, "message": data.get("detail", "Failed to send OTP")}

    except Exception as e:
        return {"success": False, "message": f"API request failed: {e}"}

# -------------------------------
# Verify OTP
# -------------------------------
def verify_otp(request, otp_field="otp"):
    mobile = request.session.get("mobile")
    session_id = request.session.get("session_id")
    if not mobile or not session_id:
        return {"success": False, "message": "Session expired. Please request OTP again."}

    otp_code = request.POST.get(otp_field)
    if not otp_code:
        return {"success": False, "message": "Enter the OTP"}

    if not OTP_API_BASE or not OTP_API_KEY:
        return {"success": False, "message": "OTP API configuration missing."}

    try:
        payload = {"session_id": session_id, "otp_code": otp_code}
        headers = {"X-API-KEY": OTP_API_KEY}
        response = requests.post(f"{OTP_API_BASE}/verify/", json=payload, headers=headers, timeout=10)
        data = response.json()

        client_ip = get_client_ip(request)
        print(f"[OTP VERIFY] Mobile: {mobile} | IP: {client_ip} | Status: {data.get('detail')}")

        if response.status_code == 200 and data.get("detail") == "OTP verified successfully":
            return {"success": True, "message": "OTP verified successfully!"}
        else:
            return {"success": False, "message": data.get("detail", "Invalid OTP")}

    except Exception as e:
        return {"success": False, "message": f"Verification failed: {e}"}

# -------------------------------
# API Endpoints
# -------------------------------
@csrf_exempt
def api_send_otp(request):
    if request.method == "POST":
        api_base = request.POST.get("api_base")
        api_key = request.POST.get("api_key")
        if api_base and api_key:
            update_otp_config(api_base, api_key)

        result = send_otp(request)
        return JsonResponse(result)
    return JsonResponse({"success": False, "message": "Only POST allowed"})

@csrf_exempt
def api_verify_otp(request):
    if request.method == "POST":
        result = verify_otp(request)
        return JsonResponse(result)
    return JsonResponse({"success": False, "message": "Only POST allowed"})
import os
import json
import requests
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# -------------------------------
# Configuration (JSON file)
# -------------------------------
BASE_DIR = os.getcwd()  # or use settings.BASE_DIR in Django
OTP_CONFIG_FILE = os.path.join(BASE_DIR, "otp_config.json")

def load_otp_config():
    """Load OTP config from JSON file."""
    if os.path.exists(OTP_CONFIG_FILE):
        with open(OTP_CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        config = {"OTP_API_BASE": "", "OTP_API_KEY": ""}
        save_otp_config(config)
        return config

def save_otp_config(config):
    """Save OTP config to JSON file safely."""
    with open(OTP_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Load current config
otp_config = load_otp_config()
OTP_API_BASE = otp_config.get("OTP_API_BASE")
OTP_API_KEY = otp_config.get("OTP_API_KEY")

def update_otp_config(api_base=None, api_key=None):
    global OTP_API_BASE, OTP_API_KEY, otp_config
    if api_base:
        otp_config["OTP_API_BASE"] = api_base
        OTP_API_BASE = api_base
    if api_key:
        otp_config["OTP_API_KEY"] = api_key
        OTP_API_KEY = api_key
    save_otp_config(otp_config)

# -------------------------------
# Rate Limiter & Sessions
# -------------------------------
OTP_RATE_LIMIT = {}  # mobile -> last_sent_time
OTP_SESSIONS = {}    # mobile -> session_id

def can_send_otp(mobile, limit_seconds=60):
    """Check rate limiting per mobile."""
    last_sent = OTP_RATE_LIMIT.get(mobile)
    now = timezone.now()
    if last_sent and (now - last_sent).total_seconds() < limit_seconds:
        return False, int(limit_seconds - (now - last_sent).total_seconds())
    return True, 0

# -------------------------------
# Client IP
# -------------------------------
def get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")

# -------------------------------
# Send OTP
# -------------------------------
def send_otp(request, mobile_field="mobile"):
    mobile = request.POST.get(mobile_field)
    if not mobile:
        return {"success": False, "message": "Enter a valid mobile number"}

    allowed, wait = can_send_otp(mobile)
    if not allowed:
        return {"success": False, "message": f"Wait {wait}s before requesting OTP again."}

    if not OTP_API_BASE or not OTP_API_KEY:
        return {"success": False, "message": "OTP API configuration missing."}

    try:
        payload = {"mobile_number": mobile}
        headers = {"X-API-KEY": OTP_API_KEY}
        response = requests.post(f"{OTP_API_BASE}/generate/", json=payload, headers=headers, timeout=10)
        data = response.json()

        if response.status_code == 201:
            session_id = data.get("session_id")
            request.session["mobile"] = mobile
            request.session["session_id"] = session_id
            request.session["otp_sent_time"] = timezone.now().timestamp()
            OTP_RATE_LIMIT[mobile] = timezone.now()
            OTP_SESSIONS[mobile] = session_id
            return {"success": True, "message": "OTP sent successfully!"}
        else:
            return {"success": False, "message": data.get("detail", "Failed to send OTP")}

    except Exception as e:
        return {"success": False, "message": f"API request failed: {e}"}

# -------------------------------
# Verify OTP
# -------------------------------
def verify_otp(request, otp_field="otp"):
    mobile = request.session.get("mobile")
    session_id = request.session.get("session_id")
    if not mobile or not session_id:
        return {"success": False, "message": "Session expired. Please request OTP again."}

    otp_code = request.POST.get(otp_field)
    if not otp_code:
        return {"success": False, "message": "Enter the OTP"}

    if not OTP_API_BASE or not OTP_API_KEY:
        return {"success": False, "message": "OTP API configuration missing."}

    try:
        payload = {"session_id": session_id, "otp_code": otp_code}
        headers = {"X-API-KEY": OTP_API_KEY}
        response = requests.post(f"{OTP_API_BASE}/verify/", json=payload, headers=headers, timeout=10)
        data = response.json()

        client_ip = get_client_ip(request)
        print(f"[OTP VERIFY] Mobile: {mobile} | IP: {client_ip} | Status: {data.get('detail')}")

        if response.status_code == 200 and data.get("detail") == "OTP verified successfully":
            return {"success": True, "message": "OTP verified successfully!"}
        else:
            return {"success": False, "message": data.get("detail", "Invalid OTP")}

    except Exception as e:
        return {"success": False, "message": f"Verification failed: {e}"}

# -------------------------------
# API Endpoints
# -------------------------------
@csrf_exempt
def api_send_otp(request):
    if request.method == "POST":
        api_base = request.POST.get("api_base")
        api_key = request.POST.get("api_key")
        if api_base and api_key:
            update_otp_config(api_base, api_key)

        result = send_otp(request)
        return JsonResponse(result)
    return JsonResponse({"success": False, "message": "Only POST allowed"})

@csrf_exempt
def api_verify_otp(request):
    if request.method == "POST":
        result = verify_otp(request)
        return JsonResponse(result)
    return JsonResponse({"success": False, "message": "Only POST allowed"})
import os
import json
import requests
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# -------------------------------
# Configuration (JSON file)
# -------------------------------
BASE_DIR = os.getcwd()  # or use settings.BASE_DIR in Django
OTP_CONFIG_FILE = os.path.join(BASE_DIR, "otp_config.json")

def load_otp_config():
    """Load OTP config from JSON file."""
    if os.path.exists(OTP_CONFIG_FILE):
        with open(OTP_CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        config = {"OTP_API_BASE": "", "OTP_API_KEY": ""}
        save_otp_config(config)
        return config

def save_otp_config(config):
    """Save OTP config to JSON file safely."""
    with open(OTP_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Load current config
otp_config = load_otp_config()
OTP_API_BASE = otp_config.get("OTP_API_BASE")
OTP_API_KEY = otp_config.get("OTP_API_KEY")

def update_otp_config(api_base=None, api_key=None):
    global OTP_API_BASE, OTP_API_KEY, otp_config
    if api_base:
        otp_config["OTP_API_BASE"] = api_base
        OTP_API_BASE = api_base
    if api_key:
        otp_config["OTP_API_KEY"] = api_key
        OTP_API_KEY = api_key
    save_otp_config(otp_config)

# -------------------------------
# Rate Limiter & Sessions
# -------------------------------
OTP_RATE_LIMIT = {}  # mobile -> last_sent_time
OTP_SESSIONS = {}    # mobile -> session_id

def can_send_otp(mobile, limit_seconds=60):
    """Check rate limiting per mobile."""
    last_sent = OTP_RATE_LIMIT.get(mobile)
    now = timezone.now()
    if last_sent and (now - last_sent).total_seconds() < limit_seconds:
        return False, int(limit_seconds - (now - last_sent).total_seconds())
    return True, 0

# -------------------------------
# Client IP
# -------------------------------
def get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")

# -------------------------------
# Send OTP
# -------------------------------
def send_otp(request, mobile_field="mobile"):
    mobile = request.POST.get(mobile_field)
    if not mobile:
        return {"success": False, "message": "Enter a valid mobile number"}

    allowed, wait = can_send_otp(mobile)
    if not allowed:
        return {"success": False, "message": f"Wait {wait}s before requesting OTP again."}

    if not OTP_API_BASE or not OTP_API_KEY:
        return {"success": False, "message": "OTP API configuration missing."}

    try:
        payload = {"mobile_number": mobile}
        headers = {"X-API-KEY": OTP_API_KEY}
        response = requests.post(f"{OTP_API_BASE}/generate/", json=payload, headers=headers, timeout=10)
        data = response.json()

        if response.status_code == 201:
            session_id = data.get("session_id")
            request.session["mobile"] = mobile
            request.session["session_id"] = session_id
            request.session["otp_sent_time"] = timezone.now().timestamp()
            OTP_RATE_LIMIT[mobile] = timezone.now()
            OTP_SESSIONS[mobile] = session_id
            return {"success": True, "message": "OTP sent successfully!"}
        else:
            return {"success": False, "message": data.get("detail", "Failed to send OTP")}

    except Exception as e:
        return {"success": False, "message": f"API request failed: {e}"}

# -------------------------------
# Verify OTP
# -------------------------------
def verify_otp(request, otp_field="otp"):
    mobile = request.session.get("mobile")
    session_id = request.session.get("session_id")
    if not mobile or not session_id:
        return {"success": False, "message": "Session expired. Please request OTP again."}

    otp_code = request.POST.get(otp_field)
    if not otp_code:
        return {"success": False, "message": "Enter the OTP"}

    if not OTP_API_BASE or not OTP_API_KEY:
        return {"success": False, "message": "OTP API configuration missing."}

    try:
        payload = {"session_id": session_id, "otp_code": otp_code}
        headers = {"X-API-KEY": OTP_API_KEY}
        response = requests.post(f"{OTP_API_BASE}/verify/", json=payload, headers=headers, timeout=10)
        data = response.json()

        client_ip = get_client_ip(request)
        print(f"[OTP VERIFY] Mobile: {mobile} | IP: {client_ip} | Status: {data.get('detail')}")

        if response.status_code == 200 and data.get("detail") == "OTP verified successfully":
            return {"success": True, "message": "OTP verified successfully!"}
        else:
            return {"success": False, "message": data.get("detail", "Invalid OTP")}

    except Exception as e:
        return {"success": False, "message": f"Verification failed: {e}"}

# -------------------------------
# API Endpoints
# -------------------------------
@csrf_exempt
def api_send_otp(request):
    if request.method == "POST":
        api_base = request.POST.get("api_base")
        api_key = request.POST.get("api_key")
        if api_base and api_key:
            update_otp_config(api_base, api_key)

        result = send_otp(request)
        return JsonResponse(result)
    return JsonResponse({"success": False, "message": "Only POST allowed"})

@csrf_exempt
def api_verify_otp(request):
    if request.method == "POST":
        result = verify_otp(request)
        return JsonResponse(result)
    return JsonResponse({"success": False, "message": "Only POST allowed"})
import os
import json
import requests
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# -------------------------------
# Configuration (JSON file)
# -------------------------------
BASE_DIR = os.getcwd()  # or use settings.BASE_DIR in Django
OTP_CONFIG_FILE = os.path.join(BASE_DIR, "otp_config.json")

def load_otp_config():
    """Load OTP config from JSON file."""
    if os.path.exists(OTP_CONFIG_FILE):
        with open(OTP_CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        config = {"OTP_API_BASE": "", "OTP_API_KEY": ""}
        save_otp_config(config)
        return config

def save_otp_config(config):
    """Save OTP config to JSON file safely."""
    with open(OTP_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Load current config
otp_config = load_otp_config()
OTP_API_BASE = otp_config.get("OTP_API_BASE")
OTP_API_KEY = otp_config.get("OTP_API_KEY")

def update_otp_config(api_base=None, api_key=None):
    global OTP_API_BASE, OTP_API_KEY, otp_config
    if api_base:
        otp_config["OTP_API_BASE"] = api_base
        OTP_API_BASE = api_base
    if api_key:
        otp_config["OTP_API_KEY"] = api_key
        OTP_API_KEY = api_key
    save_otp_config(otp_config)

# -------------------------------
# Rate Limiter & Sessions
# -------------------------------
OTP_RATE_LIMIT = {}  # mobile -> last_sent_time
OTP_SESSIONS = {}    # mobile -> session_id

def can_send_otp(mobile, limit_seconds=60):
    """Check rate limiting per mobile."""
    last_sent = OTP_RATE_LIMIT.get(mobile)
    now = timezone.now()
    if last_sent and (now - last_sent).total_seconds() < limit_seconds:
        return False, int(limit_seconds - (now - last_sent).total_seconds())
    return True, 0

# -------------------------------
# Client IP
# -------------------------------
def get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")

# -------------------------------
# Send OTP
# -------------------------------
def send_otp(request, mobile_field="mobile"):
    mobile = request.POST.get(mobile_field)
    if not mobile:
        return {"success": False, "message": "Enter a valid mobile number"}

    allowed, wait = can_send_otp(mobile)
    if not allowed:
        return {"success": False, "message": f"Wait {wait}s before requesting OTP again."}

    if not OTP_API_BASE or not OTP_API_KEY:
        return {"success": False, "message": "OTP API configuration missing."}

    try:
        payload = {"mobile_number": mobile}
        headers = {"X-API-KEY": OTP_API_KEY}
        response = requests.post(f"{OTP_API_BASE}/generate/", json=payload, headers=headers, timeout=10)
        data = response.json()

        if response.status_code == 201:
            session_id = data.get("session_id")
            request.session["mobile"] = mobile
            request.session["session_id"] = session_id
            request.session["otp_sent_time"] = timezone.now().timestamp()
            OTP_RATE_LIMIT[mobile] = timezone.now()
            OTP_SESSIONS[mobile] = session_id
            return {"success": True, "message": "OTP sent successfully!"}
        else:
            return {"success": False, "message": data.get("detail", "Failed to send OTP")}

    except Exception as e:
        return {"success": False, "message": f"API request failed: {e}"}

# -------------------------------
# Verify OTP
# -------------------------------
def verify_otp(request, otp_field="otp"):
    mobile = request.session.get("mobile")
    session_id = request.session.get("session_id")
    if not mobile or not session_id:
        return {"success": False, "message": "Session expired. Please request OTP again."}

    otp_code = request.POST.get(otp_field)
    if not otp_code:
        return {"success": False, "message": "Enter the OTP"}

    if not OTP_API_BASE or not OTP_API_KEY:
        return {"success": False, "message": "OTP API configuration missing."}

    try:
        payload = {"session_id": session_id, "otp_code": otp_code}
        headers = {"X-API-KEY": OTP_API_KEY}
        response = requests.post(f"{OTP_API_BASE}/verify/", json=payload, headers=headers, timeout=10)
        data = response.json()

        client_ip = get_client_ip(request)
        print(f"[OTP VERIFY] Mobile: {mobile} | IP: {client_ip} | Status: {data.get('detail')}")

        if response.status_code == 200 and data.get("detail") == "OTP verified successfully":
            return {"success": True, "message": "OTP verified successfully!"}
        else:
            return {"success": False, "message": data.get("detail", "Invalid OTP")}

    except Exception as e:
        return {"success": False, "message": f"Verification failed: {e}"}

# -------------------------------
# API Endpoints
# -------------------------------
@csrf_exempt
def api_send_otp(request):
    if request.method == "POST":
        api_base = request.POST.get("api_base")
        api_key = request.POST.get("api_key")
        if api_base and api_key:
            update_otp_config(api_base, api_key)

        result = send_otp(request)
        return JsonResponse(result)
    return JsonResponse({"success": False, "message": "Only POST allowed"})

@csrf_exempt
def api_verify_otp(request):
    if request.method == "POST":
        result = verify_otp(request)
        return JsonResponse(result)
    return JsonResponse({"success": False, "message": "Only POST allowed"})
import os
import json
import requests
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# -------------------------------
# Configuration (JSON file)
# -------------------------------
BASE_DIR = os.getcwd()  # or use settings.BASE_DIR in Django
OTP_CONFIG_FILE = os.path.join(BASE_DIR, "otp_config.json")

def load_otp_config():
    """Load OTP config from JSON file."""
    if os.path.exists(OTP_CONFIG_FILE):
        with open(OTP_CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        config = {"OTP_API_BASE": "", "OTP_API_KEY": ""}
        save_otp_config(config)
        return config

def save_otp_config(config):
    """Save OTP config to JSON file safely."""
    with open(OTP_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Load current config
otp_config = load_otp_config()
OTP_API_BASE = otp_config.get("OTP_API_BASE")
OTP_API_KEY = otp_config.get("OTP_API_KEY")

def update_otp_config(api_base=None, api_key=None):
    global OTP_API_BASE, OTP_API_KEY, otp_config
    if api_base:
        otp_config["OTP_API_BASE"] = api_base
        OTP_API_BASE = api_base
    if api_key:
        otp_config["OTP_API_KEY"] = api_key
        OTP_API_KEY = api_key
    save_otp_config(otp_config)

# -------------------------------
# Rate Limiter & Sessions
# -------------------------------
OTP_RATE_LIMIT = {}  # mobile -> last_sent_time
OTP_SESSIONS = {}    # mobile -> session_id

def can_send_otp(mobile, limit_seconds=60):
    """Check rate limiting per mobile."""
    last_sent = OTP_RATE_LIMIT.get(mobile)
    now = timezone.now()
    if last_sent and (now - last_sent).total_seconds() < limit_seconds:
        return False, int(limit_seconds - (now - last_sent).total_seconds())
    return True, 0

# -------------------------------
# Client IP
# -------------------------------
def get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")

# -------------------------------
# Send OTP
# -------------------------------
def send_otp(request, mobile_field="mobile"):
    mobile = request.POST.get(mobile_field)
    if not mobile:
        return {"success": False, "message": "Enter a valid mobile number"}

    allowed, wait = can_send_otp(mobile)
    if not allowed:
        return {"success": False, "message": f"Wait {wait}s before requesting OTP again."}

    if not OTP_API_BASE or not OTP_API_KEY:
        return {"success": False, "message": "OTP API configuration missing."}

    try:
        payload = {"mobile_number": mobile}
        headers = {"X-API-KEY": OTP_API_KEY}
        response = requests.post(f"{OTP_API_BASE}/generate/", json=payload, headers=headers, timeout=10)
        data = response.json()

        if response.status_code == 201:
            session_id = data.get("session_id")
            request.session["mobile"] = mobile
            request.session["session_id"] = session_id
            request.session["otp_sent_time"] = timezone.now().timestamp()
            OTP_RATE_LIMIT[mobile] = timezone.now()
            OTP_SESSIONS[mobile] = session_id
            return {"success": True, "message": "OTP sent successfully!"}
        else:
            return {"success": False, "message": data.get("detail", "Failed to send OTP")}

    except Exception as e:
        return {"success": False, "message": f"API request failed: {e}"}

# -------------------------------
# Verify OTP
# -------------------------------
def verify_otp(request, otp_field="otp"):
    mobile = request.session.get("mobile")
    session_id = request.session.get("session_id")
    if not mobile or not session_id:
        return {"success": False, "message": "Session expired. Please request OTP again."}

    otp_code = request.POST.get(otp_field)
    if not otp_code:
        return {"success": False, "message": "Enter the OTP"}

    if not OTP_API_BASE or not OTP_API_KEY:
        return {"success": False, "message": "OTP API configuration missing."}

    try:
        payload = {"session_id": session_id, "otp_code": otp_code}
        headers = {"X-API-KEY": OTP_API_KEY}
        response = requests.post(f"{OTP_API_BASE}/verify/", json=payload, headers=headers, timeout=10)
        data = response.json()

        client_ip = get_client_ip(request)
        print(f"[OTP VERIFY] Mobile: {mobile} | IP: {client_ip} | Status: {data.get('detail')}")

        if response.status_code == 200 and data.get("detail") == "OTP verified successfully":
            return {"success": True, "message": "OTP verified successfully!"}
        else:
            return {"success": False, "message": data.get("detail", "Invalid OTP")}

    except Exception as e:
        return {"success": False, "message": f"Verification failed: {e}"}

# -------------------------------
# API Endpoints
# -------------------------------
@csrf_exempt
def api_send_otp(request):
    if request.method == "POST":
        api_base = request.POST.get("api_base")
        api_key = request.POST.get("api_key")
        if api_base and api_key:
            update_otp_config(api_base, api_key)

        result = send_otp(request)
        return JsonResponse(result)
    return JsonResponse({"success": False, "message": "Only POST allowed"})

@csrf_exempt
def api_verify_otp(request):
    if request.method == "POST":
        result = verify_otp(request)
        return JsonResponse(result)
    return JsonResponse({"success": False, "message": "Only POST allowed"})
