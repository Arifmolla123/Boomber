services:
  - type: web
    name: otp-bomber                   # Render-এ সার্ভিসের নাম
    runtime: python
    rootDir: backend                   # 👈 ফোল্ডারের নাম দিন
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app     # এখানে startCommand পরিবর্তন করতে পারেন

  - type: web
    name: phishing-tool
    runtime: python
    rootDir: phishing
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn phis:app

  - type: web
    name: my-static-site
    runtime: static
    rootDir: frontend
    publish: ./                        # স্ট্যাটিক ফাইল যেখানে আছে
