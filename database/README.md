# Iqraa Bookstore Database System

## Overview
This is a comprehensive PostgreSQL database system designed for the Iqraa Bookstore application. The system manages book inventory, user transactions (both purchases and borrows), and delivery tracking in a Docker containerized environment.

## 🚀 Key Features

### 1. Transaction Management
- **Dual Transaction Types**
  - Book purchases
  - Book borrowing system
- **Complete Transaction Lifecycle**
  - Status tracking from pending to completion
  - Support for both purchase and borrow workflows
  - Transaction history and audit trails

### 2. Inventory Management
- **Book Catalog**
  - ISBN tracking
  - Stock quantity management
  - Borrow availability status
  - Price management
- **Real-time Inventory Views**
  - Current stock levels
  - Active borrows
  - Pending sales

### 3. Delivery System
- **Multiple Delivery Methods**
  - Standard shipping
  - Express shipping
  - Local pickup
  - Local delivery
- **Delivery Tracking**
  - Estimated delivery times
  - Actual delivery tracking
  - Status updates
  - Location tracking

### 4. User Management
- User authentication
- Profile management
- Address and contact information
- Transaction history

## 🛠 Technical Setup

### Prerequisites
- Docker (version 20.10.0 or higher)
- Docker Compose (version 2.0.0 or higher)
- Minimum 2GB RAM available for Docker
- 10GB free disk space

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd [repository-directory]
   ```

2. **Start the Database**
   ```bash
   docker-compose up -d
   ```
   This command will:
   - Pull the PostgreSQL 15 image
   - Create a new container named `iqraa_db`
   - Initialize the database with the schema
   - Set up the network and volumes

3. **Verify Installation**
   ```bash
   docker ps
   ```
   You should see the `iqraa_db` container running.

### Database Connection

#### Connection Details
- **Host**: localhost
- **Port**: 5432
- **Database**: iqraa_db
- **Username**: iqraa_user
- **Password**: iqraa_password

#### Connection String
For your backend application at `A:\in\Gradution\code\backend\latest\iqraa`:
```
postgresql://iqraa_user:iqraa_password@localhost:5432/iqraa_db
```

## 📊 Database Schema

### Core Tables

1. **users**
   - User authentication and profile information
   - Contact details and address management
   - Account creation and update timestamps

2. **books**
   - Book metadata (title, author, ISBN)
   - Inventory management (stock, price)
   - Borrow availability status
   - Publication details

3. **transactions**
   - Transaction records (purchases/borrows)
   - Status tracking
   - Delivery information
   - Financial details

4. **transaction_items**
   - Individual items in transactions
   - Quantity and pricing
   - Borrow duration for borrowed items
   - Return tracking

5. **delivery_tracking**
   - Delivery status updates
   - Location tracking
   - Tracking numbers
   - Delivery notes

### Custom Types
- `transaction_type`: 'borrow' | 'buy'
- `transaction_status`: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'returned' | 'cancelled'
- `delivery_method`: 'standard_shipping' | 'express_shipping' | 'pickup' | 'local_delivery'

### Views
1. **active_transactions**
   - Real-time view of ongoing transactions
   - Includes user and delivery information
   - Tracks transaction status and items

2. **book_inventory_status**
   - Current inventory levels
   - Active borrows count
   - Pending sales
   - Available for borrow status

## 🔧 Maintenance

### Regular Operations

1. **Start the Database**
   ```bash
   docker-compose up -d
   ```

2. **Stop the Database**
   ```bash
   docker-compose down
   ```

3. **View Logs**
   ```bash
   docker-compose logs -f
   ```

### Data Management

1. **Backup Database**
   ```bash
   docker exec iqraa_db pg_dump -U iqraa_user iqraa_db > backup_$(date +%Y%m%d).sql
   ```

2. **Restore Database**
   ```bash
   docker exec -i iqraa_db psql -U iqraa_user iqraa_db < backup.sql
   ```

3. **Reset Database**
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

## 🔍 Monitoring

### Health Checks
The database includes automatic health checks:
- Runs every 10 seconds
- Verifies database connectivity
- Retries 5 times before marking unhealthy

### Performance
- Indexed fields for optimal query performance
- Automatic timestamp updates
- Efficient transaction tracking

## 🚨 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Verify Docker is running
   - Check if port 5432 is available
   - Ensure container is running (`docker ps`)

2. **Database Initialization Failed**
   - Check Docker logs: `docker-compose logs`
   - Verify init.sql syntax
   - Ensure sufficient disk space

3. **Performance Issues**
   - Monitor container resources: `docker stats`
   - Check database logs
   - Verify index usage

## 📝 Notes
- Always backup before major operations
- Monitor disk space for the postgres_data volume
- Regular maintenance recommended
- Keep Docker and Docker Compose updated

## 🔐 Security Notes
- Change default password in production
- Regularly update PostgreSQL image
- Monitor database access logs
- Implement proper backup strategy 