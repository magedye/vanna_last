## 📘 **Vanna Enterprise – دليل النشر الكامل في بيئة الإنتاج (Production Deployment Guide)**

**FastAPI + Vanna 2.0 + SQLite/Oracle + React Admin/User Panels + ChromaDB**
نسخة Enterprise مستقرة، مبنية على الملفات التي صممناها معاً.

---

# 🎯 **مقدمة**

هذا الدليل يمثل **المرجع الرسمي الوحيد** لتشغيل مشروعك في بيئة إنتاج فعلية (Production-Grade).
يغطي كل شيء:
✔ إعداد السيرفر
✔ تركيب المتطلبات
✔ تجهيز قواعد البيانات
✔ نشر FastAPI كخدمة systemd
✔ نشر واجهات React
✔ أمن النظام
✔ مراقبة النظام
✔ النسخ الاحتياطي
✔ صيانة النظام

هذا الدليل مكتوب على نمط المؤسسات البنكية التي تعتمد Oracle في الإنتاج.

---

# 🔶 القسم 1 — متطلبات بيئة الإنتاج (Production Requirements)

## 🧰 **1.1 الأجهزة (Hardware Requirements)**

**الحد الأدنى (Pilot / PoC):**

* CPU: 2 cores
* RAM: 4 GB
* Disk: 20 GB

**البيئة المؤسسية (Enterprise Banking):**

* CPU: 4–8 cores
* RAM: 16+ GB
* Disk: NVMe 200 GB
* Network: 1 Gbps

---

## 🧰 **1.2 البرامج (Software Requirements)**

| البرنامج      | النسخة المقترحة   |
| ------------- | ----------------- |
| Ubuntu Server | **22.04 LTS**     |
| Python        | **3.10–3.12**     |
| Node.js       | **18 أو 20 LTS**  |
| Oracle DB     | إنتاجي            |
| SQLite        | للتطوير           |
| ChromaDB      | مدمج داخل المشروع |
| Uvicorn       | مع systemd        |

---

# 🔶 القسم 2 — تجهيز السيرفر (Server Preparation)

## 📌 2.1 تحديث النظام

```bash
sudo apt update && sudo apt upgrade -y
```

## 📌 2.2 تثبيت Python + أدواته

```bash
sudo apt install -y python3 python3-pip python3-venv build-essential
```

## 📌 2.3 تثبيت Node.js (للواجهات)

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

## 📌 2.4 إنشاء مجلد المشروع

```bash
sudo mkdir -p /opt/vanna-enterprise
sudo chown $USER:$USER /opt/vanna-enterprise
cd /opt/vanna-enterprise
```

---

# 🔶 القسم 3 — إعداد مشروع الباكند (FastAPI Backend)

## 📌 3.1 إنشاء بيئة Python

```bash
python3 -m venv venv
source venv/bin/activate
```

## 📌 3.2 تثبيت المتطلبات

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 📌 3.3 تجهيز مجلدات البيانات

```bash
mkdir -p data chroma_db logs backups
cp mydb.db data/mydb.db   # عند الحاجة
```

## 📌 3.4 ضبط ملف البيئة `.env`

ضع الملف النهائي الذي أنشأناه سابقاً:

```
ENV=PROD
DB_TYPE=oracle
...
```

---

# 🔶 القسم 4 — نشر الباكند كخدمة (systemd Service)

## 📌 4.1 إنشاء الخدمة:

```bash
sudo nano /etc/systemd/system/vanna.service
```

انسخ التالي:

```
[Unit]
Description=Vanna Enterprise Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/vanna-enterprise
Environment="ENV=PROD"
EnvironmentFile=/opt/vanna-enterprise/.env
ExecStart=/opt/vanna-enterprise/venv/bin/uvicorn app:app --host 0.0.0.0 --port 7262
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## 📌 4.2 تفعيل الخدمة:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vanna
sudo systemctl start vanna
```

## 📌 4.3 التحقق:

```bash
sudo systemctl status vanna
```

---

# 🔶 القسم 5 — نشر واجهات React (Admin & User Panels)

## 📌 5.1 بناء لوحة الآدمن

```bash
cd ui/admin
npm install
npm run build
```

يتم إنشاء مجلد `dist/`.

## 📌 5.2 نشرها عبر Nginx

```bash
sudo apt install nginx -y
```

### ملف Nginx:

```bash
sudo nano /etc/nginx/sites-available/vanna-admin
```

```
server {
   listen 80;
   server_name admin.domain.com;

   root /opt/vanna-enterprise/ui/admin/dist;
   index index.html;

   location / {
       try_files $uri $uri/ /index.html;
   }
}
```

تفعيل:

```bash
sudo ln -s /etc/nginx/sites-available/vanna-admin /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## 📌 5.3 نفس الخطوات للـ User Panel

(مع نطاق مختلف مثل `user.domain.com`)

---

# 🔶 القسم 6 — إعداد Oracle (للإنتاج الحقيقي Banking Mode)

## 📌 6.1 تفعيل Python Thin Mode

لا حاجة لتنزيل Oracle Instant Client.
Runner الخاص بنا يستخدم:

```python
oracledb.init_oracle_client(lib_dir=None)
```

✔ يدعم الاتصال مباشرة عبر TCP
✔ مناسب جداً للسيرفرات الصغيرة
✔ أسهل بكثير في التثبيت

## 📌 6.2 إعداد مستخدم مخصص للوكيل

على DBA تنفيذ:

```sql
CREATE USER V_AI IDENTIFIED BY StrongPass123;

GRANT CREATE SESSION TO V_AI;
GRANT SELECT ON SCHEMA.TABLE TO V_AI;   # حسب الجداول
```

**مهم جداً:**
الوكيل يجب أن يرى **Views فقط** وليس الجداول الخام.

---

# 🔶 القسم 7 — ChromaDB (Vector Memory)

لا يحتاج إعادة تشغيل منفصل.
هو يعمل داخل المشروع:

```
CHROMA_PATH=./chroma_db
COLLECTION_NAME=vanna_memory
```

✔ آمن
✔ محلي
✔ عرضة للنسخ الاحتياطي بسهولة

---

# 🔶 القسم 8 — الأمن (Security)

## ✔ 8.1 User Roles

* Admin: التدريب + إدارة الذاكرة
* User: الاستعلام فقط

## ✔ 8.2 SQL Guardrails

* regex يستبعد: DROP, UPDATE, DELETE
* حصر Views بـ prefix: `V_AI_`

## ✔ 8.3 SECRET_KEY

ضروري للجلسات.

---

# 🔶 القسم 9 — النسخ الاحتياطي (Backup & Recovery)

## 👇 جدول النسخ

يومياً الساعة 2 صباحاً:

```bash
crontab -e
```

أضف:

```
0 2 * * * tar -czf /opt/vanna-enterprise/backups/chroma_$(date +\%Y\%m\%d).tar.gz /opt/vanna-enterprise/chroma_db
```

✔ احتفظ بآخر 7 نسخ
✔ النسخ لا يشمل قواعد Oracle — مسؤولية DBA

---

# 🔶 القسم 10 — المراقبة (Monitoring)

## 10.1 Logs

السجلات في:

```
logs/
systemctl journalctl -u vanna
```

## 10.2 Telemetry (اختياري)

* Sentry
* OpenTelemetry
* ELK stack

---

# 🔶 القسم 11 — الاختبارات (Smoke Tests)

## 🔍 1. اختبار API:

```bash
curl http://SERVER_IP:7262/api/vanna/v2/health
```

## 🔍 2. اختبار SQL:

```bash
curl -X POST http://SERVER_IP:7262/api/vanna/v2/chat_poll \
 -H "Content-Type: application/json" \
 -d '{"message":"what tables do I have?"}'
```

## 🔍 3. اختبار React Panels:

* افتح المتصفح:
  `http://admin.domain.com`
  `http://user.domain.com`

---

# 🎯 **الختام — ماذا سيحدث بعد هذا الدليل؟**

بعد تنفيذ هذه الخطوات:

✔ الباكند يعمل كـ خدمة نظام مستقرة
✔ يعمل على Oracle أو SQLite حسب بيئة التشغيل
✔ الواجهات تعمل عبر Nginx
✔ حماية كاملة من SQL Injection
✔ نظام ذكاء اصطناعي يعمل على قواعد بنكية
✔ تدريب الذاكرة بضغطة زر
✔ قابل للتوسع لأكثر من قاعدة

---

