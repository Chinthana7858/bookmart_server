from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


ORDER_COMPAT_COLUMNS = {
    "status": "VARCHAR(30) NOT NULL DEFAULT 'pending'",
    "payment_status": "VARCHAR(30) NOT NULL DEFAULT 'unpaid'",
    "total_amount": "NUMERIC(10, 2) NOT NULL DEFAULT 0",
}

PRODUCT_COMPAT_COLUMNS = {
    "publisher": "VARCHAR(150)",
    "author": "VARCHAR(150)",
    "language": "VARCHAR(80)",
}

USER_COMPAT_COLUMNS = {
    "phone_country_code": "VARCHAR(10)",
    "phone_number": "VARCHAR(30)",
    "birthday": "DATE",
    "gender": "VARCHAR(30)",
}


def run_compat_migrations(engine: Engine):
    """Small compatibility migrations for local databases created before Alembic.

    Production deployments should use Alembic migrations. This keeps existing
    local/dev databases usable when columns are added during the project.
    """
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    with engine.begin() as connection:
        if "orders" in table_names:
            existing_columns = {column["name"] for column in inspector.get_columns("orders")}
            missing_columns = [
                (name, definition)
                for name, definition in ORDER_COMPAT_COLUMNS.items()
                if name not in existing_columns
            ]
            for name, definition in missing_columns:
                connection.execute(text(f"ALTER TABLE orders ADD COLUMN {name} {definition}"))

        if "products" in table_names:
            existing_columns = {column["name"] for column in inspector.get_columns("products")}
            missing_columns = [
                (name, definition)
                for name, definition in PRODUCT_COMPAT_COLUMNS.items()
                if name not in existing_columns
            ]
            for name, definition in missing_columns:
                connection.execute(text(f"ALTER TABLE products ADD COLUMN {name} {definition}"))

        if "products" in table_names and "categories" in table_names and "product_categories" not in table_names:
            connection.execute(text(
                "CREATE TABLE product_categories ("
                "product_id INTEGER NOT NULL, "
                "category_id INTEGER NOT NULL, "
                "PRIMARY KEY (product_id, category_id), "
                "FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE, "
                "FOREIGN KEY(category_id) REFERENCES categories (id) ON DELETE CASCADE"
                ")"
            ))
            connection.execute(text(
                "INSERT OR IGNORE INTO product_categories (product_id, category_id) "
                "SELECT id, category_id FROM products WHERE category_id IS NOT NULL"
            ))

        if "users" in table_names:
            existing_columns = {column["name"] for column in inspector.get_columns("users")}
            missing_columns = [
                (name, definition)
                for name, definition in USER_COMPAT_COLUMNS.items()
                if name not in existing_columns
            ]
            for name, definition in missing_columns:
                connection.execute(text(f"ALTER TABLE users ADD COLUMN {name} {definition}"))

        if "users" in table_names and "user_addresses" not in table_names:
            connection.execute(text(
                "CREATE TABLE user_addresses ("
                "id INTEGER NOT NULL PRIMARY KEY, "
                "user_id INTEGER NOT NULL, "
                "label VARCHAR(40) NOT NULL DEFAULT 'Home', "
                "recipient_name VARCHAR(100), "
                "phone_country_code VARCHAR(10), "
                "phone_number VARCHAR(30), "
                "line1 VARCHAR(150) NOT NULL, "
                "line2 VARCHAR(150), "
                "city VARCHAR(80) NOT NULL, "
                "state VARCHAR(80), "
                "postal_code VARCHAR(30), "
                "country VARCHAR(80) NOT NULL, "
                "is_default BOOLEAN NOT NULL DEFAULT 0, "
                "created_at DATETIME, "
                "updated_at DATETIME, "
                "FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE"
                ")"
            ))
            connection.execute(text("CREATE INDEX ix_user_addresses_user_id ON user_addresses (user_id)"))
