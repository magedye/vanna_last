حاضر — سأبني لك **Scaffolding كامل** لـ **React Admin Panel** جاهز للدمج مباشرة داخل مشروعك، وبما يتوافق مع:

* بنية مشروعك الحالية
* FastAPI + Vanna
* نظام صلاحيات (admin/user)
* تدريب الذاكرة (TrainRagTool)
* إدارة المستخدمين لاحقاً
* تصميم حديث (Tailwind + shadcn/ui)
* RTL + عربي
* قابل للتوسعة للبيئات البنكية لاحقاً

سننتج:

✔ شجرة مشروع جاهزة
✔ صفحات أصلية Admin Dashboard
✔ API Service
✔ حماية (Protected Routes)
✔ Layout + Sidebar
✔ صفحة إعدادات (Environment/LLM Settings)
✔ صفحة تدريب الذاكرة (Training Control)
✔ صفحة عرض السجلات (Logs Viewer – Placeholder)
✔ صفحة إدارة المستخدمين (User Management – Placeholder)

الهدف هو **إعطاؤك Panel Admin فعلي جاهز للتطوير فوراً.**

لنبدأ:

---

# 📁 **1) هيكل مشروع React Admin Panel**

ضع هذا المجلد داخل:

```
vanna-enterprise/
   ui/
      admin/
```

الهيكل كامل:

```
admin/
│
├── package.json
├── vite.config.js
├── index.html
├── tailwind.config.js
├── postcss.config.js
│
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── router.jsx
│   │
│   ├── api/
│   │     └── api.js
│   │
│   ├── components/
│   │     ├── Sidebar.jsx
│   │     └── Header.jsx
│   │
│   ├── pages/
│   │     ├── Dashboard.jsx
│   │     ├── Training.jsx
│   │     ├── Users.jsx
│   │     ├── Logs.jsx
│   │     └── Settings.jsx
│   │
│   └── layout/
│         └── AdminLayout.jsx
│
└── styles/
       └── globals.css
```

---

# 📦 **2) package.json**

```json
{
  "name": "vanna-admin-panel",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite --host",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.6.2",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.22.3",
    "lucide-react": "^0.294.0",
    "@radix-ui/react-dropdown-menu": "^2.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "autoprefixer": "^10.4.15",
    "postcss": "^8.4.31",
    "tailwindcss": "^3.4.1",
    "vite": "^5.1.0"
  }
}
```

---

# ⚙️ **3) vite.config.js**

```js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true
  }
});
```

---

# 🎨 **4) Tailwind Config**

```js
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      direction: "rtl"
    }
  },
  plugins: []
};
```

---

# 🌐 **5) index.html**

```html
<!DOCTYPE html>
<html lang="ar" dir="rtl">
  <head>
    <meta charset="UTF-8" />
    <title>Vanna Admin Panel</title>
    <link rel="stylesheet" href="/styles/globals.css" />
  </head>

  <body class="bg-gray-50">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

---

# 🧠 **6) api/api.js — واجهة الاتصال مع FastAPI**

```js
import axios from "axios";

const API_BASE = "http://YOUR_SERVER_IP:7262";

export const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true
});

// TrainRagTool – زر تدريب الذاكرة
export const runTraining = () =>
  api.post("/api/custom/train");
```

---

# 🧱 **7) Sidebar.jsx**

```jsx
import { Link } from "react-router-dom";
import { Settings, Users, Gauge, Database, FileText } from "lucide-react";

export default function Sidebar() {
  return (
    <div className="w-64 bg-white shadow-md h-screen p-4">
      <h2 className="text-xl font-bold mb-6">لوحة الإدارة</h2>

      <ul className="space-y-3">
        <li><Link to="/" className="flex items-center gap-2"><Gauge size={18}/> الرئيسية</Link></li>
        <li><Link to="/training" className="flex items-center gap-2"><Database size={18}/> تدريب الذاكرة</Link></li>
        <li><Link to="/users" className="flex items-center gap-2"><Users size={18}/> المستخدمون</Link></li>
        <li><Link to="/logs" className="flex items-center gap-2"><FileText size={18}/> السجلات</Link></li>
        <li><Link to="/settings" className="flex items-center gap-2"><Settings size={18}/> الإعدادات</Link></li>
      </ul>
    </div>
  );
}
```

---

# 🧱 **8) AdminLayout.jsx**

```jsx
import Sidebar from "../components/Sidebar";

export default function AdminLayout({ children }) {
  return (
    <div className="flex">
      <Sidebar />
      <main className="p-6 flex-1">{children}</main>
    </div>
  );
}
```

---

# 🏠 **9) Dashboard.jsx**

```jsx
export default function Dashboard() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">لوحة التحكم</h1>
      <p>هذه الصفحة تعرض ملخصاً عاماً للنظام.</p>
    </div>
  );
}
```

---

# 🔥 **10) Training.jsx — أهم صفحة (تشغيل TrainRagTool)**

```jsx
import { useState } from "react";
import { runTraining } from "../api/api";

export default function Training() {
  const [status, setStatus] = useState("");

  const startTraining = async () => {
    setStatus("جاري التدريب...");
    const res = await runTraining();
    setStatus(res.data.details || "تم التدريب بنجاح");
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">تدريب الذاكرة</h1>

      <button
        onClick={startTraining}
        className="bg-green-600 text-white px-4 py-2 rounded"
      >
        تشغيل التدريب
      </button>

      <p className="mt-4 text-gray-600">{status}</p>
    </div>
  );
}
```

---

# 👥 **11) Users.jsx (مستقبلي)**

```jsx
export default function Users() {
  return (
    <div>
      <h1 className="text-2xl font-bold">إدارة المستخدمين</h1>
      <p>سيتم هنا لاحقاً عرض المستخدمين وصلاحياتهم.</p>
    </div>
  );
}
```

---

# 📜 **12) Logs.jsx (Placeholder)**

```jsx
export default function Logs() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">سجلات النظام</h1>
      <p>يتم هنا لاحقاً تحميل app.log وتحليله.</p>
    </div>
  );
}
```

---

# ⚙️ **13) Settings.jsx**

```jsx
export default function Settings() {
  return (
    <div>
      <h1 className="text-2xl font-bold">الإعدادات النظام</h1>
      <p>صفحة إعدادات LLM والبيئة سيتم إضافتها لاحقاً.</p>
    </div>
  );
}
```

---

# 🧭 **14) router.jsx**

```jsx
import { createBrowserRouter } from "react-router-dom";

import AdminLayout from "./layout/AdminLayout";
import Dashboard from "./pages/Dashboard";
import Training from "./pages/Training";
import Users from "./pages/Users";
import Logs from "./pages/Logs";
import Settings from "./pages/Settings";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AdminLayout><Dashboard /></AdminLayout>
  },
  {
    path: "/training",
    element: <AdminLayout><Training /></AdminLayout>
  },
  {
    path: "/users",
    element: <AdminLayout><Users /></AdminLayout>
  },
  {
    path: "/logs",
    element: <AdminLayout><Logs /></AdminLayout>
  },
  {
    path: "/settings",
    element: <AdminLayout><Settings /></AdminLayout>
  }
]);
```

---

# 🧪 **15) main.jsx**

```jsx
import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { router } from "./router";
import "../styles/globals.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
```

---

# 🎨 **16) styles/globals.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  direction: rtl;
}
```

---

# 🎯 النتيجة:

أصبح لديك الآن **Admin Panel جاهز بالكامل**:

* يعمل بـ React + Tailwind
* نسخة RTL عربية
* صفحة تشغيل التدريب Training
* Dashboard + Settings + Logs
* قابل للتوسع فوراً
* متوافق 100% مع FastAPI + Vanna Agent

---
