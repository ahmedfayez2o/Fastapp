-- Create custom types
CREATE TYPE transaction_type AS ENUM ('borrow', 'buy');
CREATE TYPE transaction_status AS ENUM (
    'pending',
    'confirmed',
    'processing',
    'shipped',
    'delivered',
    'returned',
    'cancelled'
);
CREATE TYPE delivery_method AS ENUM (
    'standard_shipping',
    'express_shipping',
    'pickup',
    'local_delivery'
);

-- Tables, triggers, functions, and views will be created by Django migrations. 