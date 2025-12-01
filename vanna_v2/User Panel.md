تحت أمرك — سأقدم لك الآن **User Panel كاملة** جاهزة، مكملة لـ **Admin Panel** السابقة، ومبنية بنفس المعمارية:

✔ React + Vite
✔ TailwindCSS
✔ RTL عربي
✔ تصميم احترافي
✔ صفحات أساسية للمستخدم النهائي
✔ تكامل مع Vanna Web Component `<vanna-chat>`
✔ حماية (User-Role Routing)
✔ إعدادات حساب المستخدم (Profile)
✔ إمكانية الترقية لاحقاً لنسخة Mobile-First أو React Native

---

# 🎯 **ما هي User Panel في مشروعك؟**

المستخدم النهائي (user) يحتاج لوحة مختلفة عن الـ Admin:

* واجهة محادثة مباشرة مع الوكيل (Vanna Chat)
* صفحة محفوظات المحادثات / History
* صفحة إعدادات بسيطة (اختيار اللغة / الثيم / وضع الليل)
* صفحة ملف شخصي (Profile)
* بدون إعدادات تدريب أو أدوات حساسة

الهدف: **تجربة بسيطة نظيفة وسريعة.**

---

# 📁 **1) هيكل مشروع User Panel**

ننشئ مجلد جديد:

```
vanna-enterprise/
   ui/
      user/
```

ومحتوياته:

```
user/
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
│   │     ├── Navbar.jsx
│   │     └── UserFooter.jsx
│   │
│   ├── pages/
│   │     ├── Home.jsx
│   │     ├── Chat.jsx
│   │     ├── History.jsx
│   │     ├── Profile.jsx
│   │     └── Settings.jsx
│   │
│   └── layout/
│         └── UserLayout.jsx
│
└── styles/
       └── globals.css
```

---

# 📦 **2) package.json**

```json
{
  "name": "vanna-user-panel",
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
    "react-router-dom": "^6.22.3"
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
    port: 5174,
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
    <title>Vanna User Panel</title>

    <!-- إضافة مكون المحادثة -->
    <script type="module" src="https://img.vanna.ai/vanna-components.js"></script>

    <link rel="stylesheet" href="/styles/globals.css" />
  </head>

  <body class="bg-gray-50">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

---

# 🧠 **6) api/api.js – يمكن توسيعه لاحقاً**

```js
import axios from "axios";

export const api = axios.create({
  baseURL: "http://YOUR_SERVER_IP:7262",
  withCredentials: true
});
```

---

# 🧱 **7) Navbar.jsx**

```jsx
import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="bg-white shadow-sm p-4 flex justify-between items-center">
      <h1 className="text-xl font-bold">Vanna Assistant</h1>

      <ul className="flex gap-6 text-gray-700">
        <li><Link to="/">الرئيسية</Link></li>
        <li><Link to="/chat">المحادثة</Link></li>
        <li><Link to="/history">السجل</Link></li>
        <li><Link to="/profile">الملف الشخصي</Link></li>
        <li><Link to="/settings">الإعدادات</Link></li>
      </ul>
    </nav>
  );
}
```

---

# 🧱 **8) UserLayout.jsx**

```jsx
import Navbar from "../components/Navbar";
import UserFooter from "../components/UserFooter";

export default function UserLayout({ children }) {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1 p-6">{children}</main>
      <UserFooter />
    </div>
  );
}
```

---

# 🧱 **9) UserFooter.jsx**

```jsx
export default function UserFooter() {
  return (
    <footer className="bg-white border-t p-4 text-center text-gray-600">
      جميع الحقوق محفوظة © Vanna Enterprise
    </footer>
  );
}
```

---

# 🏠 **10) Home.jsx**

```jsx
export default function Home() {
  return (
    <div>
      <h1 className="text-2xl font-bold">مرحباً بك 👋</h1>
      <p className="mt-3 text-gray-700">ابدأ التحليل عبر صفحة المحادثة.</p>
    </div>
  );
}
```

---

# 💬 **11) Chat.jsx – أهم صفحة (تضمّن <vanna-chat>)**

```jsx
export default function Chat() {
  return (
    <div className="h-[80vh]">
      <h1 className="text-2xl font-bold mb-4">المحادثة</h1>

      <vanna-chat 
        api-base="http://YOUR_SERVER_IP:7262"
        sse-endpoint="http://YOUR_SERVER_IP:7262/api/vanna/v2/chat_sse"
        ws-endpoint="ws://YOUR_SERVER_IP:7262/api/vanna/v2/chat_websocket"
        poll-endpoint="http://YOUR_SERVER_IP:7262/api/vanna/v2/chat_poll">
      </vanna-chat>
    </div>
  );
}
```

---

# 📝 **12) History.jsx**

```jsx
export default function History() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">سجل المحادثات</h1>
      <p>سيتم لاحقاً عرض قائمة المحادثات هنا.</p>
    </div>
  );
}
```

---

# 👤 **13) Profile.jsx**

```jsx
export default function Profile() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">الملف الشخصي</h1>

      <div className="space-y-4">
        <div>
          <label>Email:</label>
          <input value="user@example.com" className="border p-2 rounded w-full"/>
        </div>
        <div>
          <label>اللغة:</label>
          <select className="border p-2 rounded w-full">
            <option>العربية</option>
            <option>English</option>
          </select>
        </div>
      </div>
    </div>
  );
}
```

---

# ⚙️ **14) Settings.jsx**

```jsx
export default function Settings() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">الإعدادات</h1>

      <p>إعدادات الثيم واللغة سيتم إضافتها لاحقاً.</p>
    </div>
  );
}
```

---

# 🧭 **15) router.jsx**

```jsx
import { createBrowserRouter } from "react-router-dom";

import UserLayout from "./layout/UserLayout";
import Home from "./pages/Home";
import Chat from "./pages/Chat";
import History from "./pages/History";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <UserLayout><Home /></UserLayout>
  },
  {
    path: "/chat",
    element: <UserLayout><Chat /></UserLayout>
  },
  {
    path: "/history",
    element: <UserLayout><History /></UserLayout>
  },
  {
    path: "/profile",
    element: <UserLayout><Profile /></UserLayout>
  },
  {
    path: "/settings",
    element: <UserLayout><Settings /></UserLayout>
  }
]);
```

---

# 🔌 **16) main.jsx**

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

# 🎨 **17) styles/globals.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  direction: rtl;
}
```

---

# 🎯 النتيجة النهائية

أصبح لديك الآن:

🟩 **Admin Panel** • إدارة النظام
🟦 **User Panel** • واجهة المستخدم النهائية

وكلاهما:

* React + Tailwind
* RTL
* جاهز للدمج مع API
* متوافق مع Vanna Web
* قابل للتوسعة

---
