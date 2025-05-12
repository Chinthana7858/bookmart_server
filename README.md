# 🛒 Web Tracking & Recommendation E-Commerce App - Book Mart

This is the back-end of the e-commerce web application with web tracking and recommendation features. It allows both registered and guest users to browse products and get recommendations based on user activity.

---
## 📌 ER Diagram
![BookMart](https://github.com/user-attachments/assets/be408ef0-64da-4778-aaaa-21e05c90cb59)

## 📌 Features

  - User Authentication (JWT-based)
  - Product listing with sort/filter by:
  - Price,Date,Stock (asc/desc)
  - Recommendation system based on user interaction logs
  - Web tracking system for both authenticated and anonymous users

---

## 🛠 Tech Stack
- Python 
- FastAPI
- SQLAlchemy ORM
-  MySQL
- Pytest (for testing)
- JWT (auth)


---

## 📋 Getting Started

###  Run locally

```bash
uvicorn app.main:app --reload

