import os
from flask import Flask, send_from_directory
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# ===== Server 1 ইমপোর্ট করুন =====
try:
    from bomber import app as server1_app
    print("✅ Server 1 (bomber.py) loaded.")
except Exception as e:
    print(f"⚠️ Server 1 load error: {e}")
    server1_app = Flask(__name__)
    @server1_app.route('/')
    def err1():
        return "Server 1 is not available."

# ===== Server 2 ইমপোর্ট করুন =====
try:
    from hard_bomber import app as server2_app
    print("✅ Server 2 (hard-bomber.py) loaded.")
except Exception as e:
    print(f"⚠️ Server 2 load error: {e}")
    server2_app = Flask(__name__)
    @server2_app.route('/')
    def err2():
        return "Server 2 is not available."

# ===== মূল অ্যাপ (যা HTML দেখাবে) =====
main_app = Flask(__name__, static_folder='.', static_url_path='')

@main_app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# ===== তিনটি অ্যাপকে একত্রিত করা =====
application = DispatcherMiddleware(main_app, {
    '/server1': server1_app,
    '/server2': server2_app,
})

# ===== লোকাল রানে চালানোর জন্য (ঐচ্ছিক) =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', port, application)
