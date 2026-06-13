# BookMart Backend

FastAPI backend for BookMart, an e-commerce bookstore with customer accounts, admin catalogue management, carts, orders, Stripe payments, activity tracking, and recommendations.
<img width="1391" height="1693" alt="database" src="https://github.com/user-attachments/assets/a0b936f9-8918-4baa-bdf1-767cb29dd47e" />

## Web Tracking And Recommendations

The backend stores product activity events for authenticated users and guest sessions. These events support popular-book displays, recommendation generation, and co-engagement statistics.

Tracked actions:

- `view`
- `add_to_cart`
- `buy`

Important endpoints:

- `POST /activities/` - store a product activity event.
- `GET /activities/top-viewed-details` - return popular products for the frontend.
- `GET /activities/user/{user_id}` - inspect activity by user.
- `GET /activities/session/{session_id}` - inspect activity by guest session.
- `POST /generate` - regenerate recommendations.
- `GET /recommendations` - list generated recommendations.
- `GET /recommendations/{base_product_id}` - get recommendations for a product.

Activity records are stored with `session_id`, `product_id`, `action`, and `timestamp`. Co-engagement statistics are stored separately and used by the recommendation flow.

## Features

- Cookie-based JWT authentication.
- Customer signup/signin with profile details and address book.
- Role-based access for customers and admins.
- Admin APIs for users, inventory, categories, orders, and dashboard metrics.
- Product catalogue with image upload, publisher, author, language, stock, pricing, and multiple categories.
- Cart and checkout flow.
- Order lifecycle and payment status management.
- Stripe checkout integration with webhook support.
- Activity tracking for product views, cart actions, and purchases.
- Product recommendations and co-engagement statistics.
- SQLite support for local testing and MySQL support for real deployment.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- Alembic
- MySQL / SQLite
- Pytest
- Cloudinary
- Stripe

## Project Structure

```text
bookmart_server/
  app/
    auth/          # JWT, password hashing, auth dependencies
    models/        # SQLAlchemy models
    routers/       # FastAPI route modules
    schemas/       # Pydantic request/response schemas
    services/      # Business logic
  postman/         # Postman collection
  tests/           # Backend test suite
  alembic/         # Database migrations
```

## Environment Variables

Create `.env` from `.env.example`.

```env
DATABASE_URL=mysql+pymysql://root:rootpass@localhost:3306/bookmart
JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=600
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://mybookmarket.netlify.app
FRONTEND_BASE_URL=http://localhost:5173
PAYMENT_PROVIDER=stripe
PAYMENT_CURRENCY=USD
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
ALLOW_PUBLIC_ADMIN_REGISTRATION=false
```

For quick local SQLite testing:

```env
DATABASE_URL=sqlite:///./test.db
JWT_SECRET_KEY=test-secret
```

## Setup

```bash
cd bookmart_server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run the server:

```bash
uvicorn app.main:app --reload
```

The API will run at:

```text
http://localhost:8000
```

Swagger docs:

```text
http://localhost:8000/docs
```

## Database

For MySQL, create a database first:

```sql
CREATE DATABASE bookmart CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Then set:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/bookmart
```

Production schema changes should use Alembic:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

The app also runs small startup compatibility migrations for older local databases, but Alembic should be used for production changes.

## Seed Users

Seed basic local accounts:

```bash
python seed_users.py
```

Default seeded accounts:

```text
Admin: admin@bookmart.local / admin123
User:  user@bookmart.local / user123
```

## Important Endpoints

Auth:

- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/authenticate`

Users:

- `GET /users/paginated?role=user`
- `GET /users/me/profile`
- `PUT /users/me/profile`
- `GET /users/me/addresses`
- `POST /users/me/addresses`
- `PUT /users/me/addresses/{address_id}`
- `DELETE /users/me/addresses/{address_id}`

Admin:

- `GET /admin/dashboard/summary`
- `POST /admin/users/`
- `POST /admin/users/public-admin`

Products and categories:

- `GET /products/paginated`
- `GET /products/getproductbyid/{product_id}`
- `POST /products/`
- `PUT /products/{product_id}`
- `DELETE /products/{product_id}`
- `GET /categories/paginated`
- `POST /categories/`
- `PUT /categories/{category_id}`
- `DELETE /categories/{category_id}`

Orders and payments:

- `POST /orders/checkout`
- `GET /orders/me`
- `GET /orders/paginated`
- `PATCH /orders/{order_id}/status`
- `POST /payments/checkout-session`
- `POST /payments/orders/{order_id}/confirm`
- `POST /payments/stripe/webhook`

## Payments

Stripe requires:

```env
PAYMENT_PROVIDER=stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

For local webhook testing, use the Stripe CLI:

```bash
stripe listen --forward-to localhost:8000/payments/stripe/webhook
```

Copy the printed `whsec_...` value into `STRIPE_WEBHOOK_SECRET`.

## Postman

The collection is available at:

```text
postman/bookmart_api.postman_collection.json
```

It includes auth, users, profile/address book, inventory, categories, cart, orders, payments, recommendations, activity tracking, and admin dashboard requests.

## Tests

Run:

```bash
$env:DATABASE_URL='sqlite:///./test.db'
$env:JWT_SECRET_KEY='test-secret'
python -m pytest
```

Expected current result:

```text
51 passed
```

## Production Notes

Before deploying:

- Set a strong `JWT_SECRET_KEY`.
- Set `COOKIE_SECURE=true` when the frontend uses HTTPS.
- Set `FRONTEND_BASE_URL` to the deployed frontend URL.
- Restrict `CORS_ORIGINS` to trusted frontend domains only.
- Keep `ALLOW_PUBLIC_ADMIN_REGISTRATION=false`.
- Configure Cloudinary credentials before using product image upload.
- Configure Stripe credentials before enabling real payments.
- Run Alembic migrations before starting the app in production.
- Do not commit `.env`, local databases, or generated cache files.

Recommended checks:

```bash
python -m pytest
pip check
```
