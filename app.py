import os
import traceback
from flask import Flask, send_from_directory
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# ===== মেইন অ্যাপ (HTML কার্ড) =====
main_app = Flask(__name__, static_folder='.', static_url_path='')

@main_app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# ===== সার্ভার ১ (bomber.py) লোড =====
try:
    from bomber import app as server1_app
    print("✅ Server 1 loaded")
except Exception as e:
    # Exception-এর সম্পূর্ণ ট্রেস লুপ সংরক্ষণ করি
    error_trace1 = traceback.format_exc()
    server1_app = Flask(__name__)
    @server1_app.route('/')
    @server1_app.route('/<path:path>')
    def err1(path=''):
        return f"<pre style='color:#ff6b6b;font-size:14px;'>❌ SERVER 1 ERROR (import failed):\n{error_trace1}</pre>"

# ===== সার্ভার ২ (hard_bomber.py) লোড =====
try:
    from hard_bomber import app as server2_app
    print("✅ Server 2 loaded")
except Exception as e:
    error_trace2 = traceback.format_exc()
    server2_app = Flask(__name__)
    @server2_app.route('/')
    @server2_app.route('/<path:path>')
    def err2(path=''):
        return f"<pre style='color:#ff6b6b;font-size:14px;'>❌ SERVER 2 ERROR (import failed):\n{error_trace2}</pre>"

# ===== ডিসপ্যাচার =====
application = DispatcherMiddleware(main_app, {
    '/server1': server1_app,
    '/server2': server2_app,
})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', port, application)
