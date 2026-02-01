# Perishable Inventory Risk Engine (P.I.R.E)

**Developer:** Reshma Banu T

**Education:** B.Tech Information Technology

**Project Objective:** A full-stack retail management solution designed to automate inventory tracking and minimize waste through real-time expiration analytics.

---

## 📌 Overview

P.I.R.E is an intelligent inventory management system built to handle time-sensitive retail goods (like dairy and bakery items). Unlike a standard list, this application features a **Risk Assessment Algorithm** that analyzes product shelf-life and provides visual alerts to store managers before items spoil.

## 🚀 Key Features

* **Dynamic Risk Analytics:** The Node.js backend calculates `daysLeft` for every item and categorizes it as **High Risk** (≤3 days), **Medium Risk** (≤7 days), or **Safe**.
* **Secure User Authentication:** Implemented **JWT (JSON Web Tokens)** for session management and **Bcrypt** for industry-standard password hashing.
* **Multilingual Interface:** Fully localized dashboard supporting both **English** and **Tamil** for diverse workplace environments.
* **Full-Stack Architecture:** A decoupled design with a RESTful API and a reactive, state-driven frontend.

## 🛠️ Technical Stack

| Layer | Technologies Used |
| --- | --- |
| **Frontend** | React.js, CSS3, JavaScript (ES6+) |
| **Backend** | Node.js, Express.js |
| **Security** | JWT, Bcrypt |
| **Version Control** | Git & GitHub |

## ⚙️ Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/ReshDeen/perishable-inventory-risk-engine.git

```


2. **Setup Backend:**
```bash
cd backend
npm install
node index.js

```


3. **Setup Frontend:**
```bash
cd frontend
npm install
npm start

```



## 📈 Future Enhancements

* Integration with MongoDB for persistent data storage.
* Automated email alerts for "High Risk" inventory items.
* Barcode scanning integration for rapid stock entry.

---
