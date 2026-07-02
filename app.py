import os
from flask import Flask, send_from_directory
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# ===== মেইন অ্যাপ (HTML কার্ড দেখাবে) =====
main_app = Flask(__name__, static_folder='.', static_url_path='')

@main_app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# ===== সার্ভার ১ (bomber.py) লোড =====
try:
    from bomber import app as server1_app
    print("✅ Server 1 (bomber.py) loaded successfully.")
except Exception as e:
    print(f"❌ Server 1 load error: {e}")
    server1_app = Flask(__name__)
    @server1_app.route('/')
    def err1():
        return f"<h3>❌ Server 1 Error</h3><pre>{e}</pre>"

# ===== সার্ভার ২ (hard_bomber.py) লোড =====
try:
    from hard_bomber import app as server2_app
    print("✅ Server 2 (hard_bomber.py) loaded successfully.")
except Exception as e:
    print(f"❌ Server 2 load error: {e}")
    server2_app = Flask(__name__)
    @server2_app.route('/')
    def err2():
        return f"<h3>❌ Server 2 Error</h3><pre>{e}</pre>"

# ===== তিনটি অ্যাপকে একত্রিত করা =====
application = DispatcherMiddleware(main_app, {
    '/server1': server1_app,
    '/server2': server2_app,
})

# ===== লোকাল বা Render-এ চালানোর জন্য =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', port, application)
