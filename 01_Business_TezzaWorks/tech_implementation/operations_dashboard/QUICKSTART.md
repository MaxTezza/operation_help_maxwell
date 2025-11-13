# TezzaWorks Operations Dashboard - Quick Start Guide

Get up and running with the TezzaWorks Operations Dashboard in minutes!

## Prerequisites

Before you begin, ensure you have:
- Python 3.8 or higher installed
- Node.js 16 or higher installed
- Terminal/Command Prompt access

## Step-by-Step Setup

### 1. Backend Setup (5 minutes)

Open a terminal and navigate to the backend directory:

```bash
cd operations_dashboard/backend
```

Create and activate a virtual environment:

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Seed the database with sample data:
```bash
python seed_data.py
```

Start the backend server:
```bash
python app.py
```

You should see:
```
Starting TezzaWorks Operations Dashboard API...
Server running on http://localhost:5000
```

**Keep this terminal open!** The backend server needs to stay running.

### 2. Frontend Setup (5 minutes)

Open a **new terminal** and navigate to the frontend directory:

```bash
cd operations_dashboard/frontend
```

Install dependencies:
```bash
npm install
```

Start the development server:
```bash
npm run dev
```

You should see:
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### 3. Access the Dashboard

Open your web browser and go to:
```
http://localhost:3000
```

You should see the TezzaWorks Operations Dashboard!

## What's Included in Sample Data?

The seed script creates:
- **5 Sample Clients** representing different industries
- **8 Sample Products** across various categories
- **5 Sample Orders** at different stages of the workflow

## Quick Tour of Features

### Dashboard (Home Page)
- View key metrics: Total Revenue, Orders, Clients, Avg Order Value
- See recent orders at a glance
- Check low stock alerts

### Orders
- View all orders with filtering options
- Track order status and financial details
- Click any order to see full details

### Production Board (Kanban)
- Visual workflow tracker
- See orders organized by status:
  - Quote
  - Confirmed
  - In Production
  - Shipped
- Click any card for order details

### Clients
- Browse client database
- Search by company name, contact, or email
- Click "Add Client" to create new clients
- View client details and order history

### Products
- Product catalog with inventory tracking
- See which products are low in stock
- Click "Add Product" to add new items
- Edit pricing and customization options

### Analytics
- Revenue trends over time
- Top-selling products
- Orders by status breakdown
- Filter by date range

## Common Tasks

### Create a New Order

1. Click "Orders" in the sidebar
2. Click "Create Order" button
3. Select a client
4. Add products with quantities
5. Configure customization (logo, personalization)
6. Review pricing and submit

### Add a New Client

1. Click "Clients" in the sidebar
2. Click "Add Client" button
3. Fill in company information
4. Select acquisition source
5. Save

### Check Production Status

1. Click "Production Board" in sidebar
2. View orders by workflow stage
3. Click any card for details
4. Update status as work progresses

### Export Data

1. Navigate to Orders, Clients, or Products
2. Apply any filters you want
3. Click "Export" button
4. Download CSV file

## Troubleshooting

### Backend Won't Start

**Issue**: Port 5000 already in use
**Solution**:
```bash
# Change port in backend/.env file
PORT=5001
```

**Issue**: Module not found errors
**Solution**: Make sure virtual environment is activated
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Frontend Won't Start

**Issue**: Port 3000 already in use
**Solution**: Vite will prompt you to use a different port, just press 'y'

**Issue**: Cannot connect to API
**Solution**: Make sure backend server is running on port 5000

### Database Issues

**Issue**: Database errors or missing tables
**Solution**: Re-run the seed script
```bash
cd backend
python seed_data.py
```

## Next Steps

Now that you're set up, try:

1. **Create a test order** using the sample clients and products
2. **Track it through the workflow** using the Production Board
3. **View analytics** to see how metrics update
4. **Export data** to see reporting capabilities
5. **Add your own products** and clients

## API Testing (Optional)

Test the API directly using curl or Postman:

```bash
# Get all clients
curl http://localhost:5000/api/clients

# Get all products
curl http://localhost:5000/api/products

# Get order analytics
curl http://localhost:5000/api/orders/analytics
```

## Production Deployment

When you're ready to deploy to production:

1. Review the "Production Deployment" section in README.md
2. Configure environment variables for production
3. Switch to PostgreSQL database
4. Deploy backend with Gunicorn
5. Build and deploy frontend

## Need Help?

- Check the full README.md for detailed documentation
- Review API endpoints in README.md
- Check the code comments for implementation details
- Contact TezzaWorks development team

## Tips for Best Experience

1. **Keep both servers running** - Backend and frontend must both be active
2. **Use Chrome or Firefox** - Best browser compatibility
3. **Sample data is editable** - Feel free to modify or delete test data
4. **Try the pricing calculator** - Add products with different quantities to see volume discounts
5. **Explore the kanban board** - Great for visualizing production workflow

---

**Estimated Setup Time**: 10-15 minutes
**Dashboard URL**: http://localhost:3000
**API URL**: http://localhost:5000

Happy operations management!
