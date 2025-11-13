# TezzaWorks Operations Dashboard

A comprehensive business operations dashboard for managing corporate gift orders, production workflows, pricing, and client relationships.

## Features

### 1. Order Management System
- Create, track, and manage corporate gift orders
- Complete order lifecycle from quote to delivery
- Track customization details (logos, personalization)
- Automatic pricing with volume discounts
- Order status tracking: Quote → Confirmed → In Production → Shipped → Delivered

### 2. Production Workflow Tracker
- Visual kanban board for production status
- Real-time order tracking across workflow stages
- Estimated completion dates
- Special instructions and production notes
- Materials and labor tracking

### 3. Dynamic Cost Calculator
- Automatic calculation of:
  - Materials cost
  - Labor hours and costs
  - Overhead allocation
  - Profit margins
- Volume discount tiers:
  - 1-25 units: Base price
  - 26-100 units: 10% discount
  - 101-500 units: 15% discount
  - 500+ units: 25% discount

### 4. Client Relationship Management
- Complete client database
- Contact information management
- Interaction history tracking
- Follow-up reminders
- Order history per client
- Acquisition source tracking

### 5. Analytics Dashboard
- Revenue tracking and trends
- Order statistics by status
- Top-selling products
- Average order value
- Monthly revenue charts
- Client acquisition metrics

### 6. Product Catalog Management
- Product inventory tracking
- Low stock alerts
- Customization options (logo, personalization)
- Category management
- Pricing and cost tracking

### 7. Export Functionality
- Export orders to CSV
- Export client database
- Export product catalog
- Detailed order reports

## Technology Stack

### Backend
- **Framework**: Flask 2.3.3
- **Database**: SQLAlchemy ORM with SQLite (easily switchable to PostgreSQL)
- **API**: RESTful architecture
- **CORS**: Flask-CORS for frontend communication

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **UI Library**: Ant Design 5
- **Routing**: React Router v6
- **Charts**: Chart.js with react-chartjs-2
- **HTTP Client**: Axios

### Database Schema
- **Clients**: Company info, contacts, acquisition tracking
- **Products**: SKU, pricing, inventory, customization options
- **Orders**: Full order lifecycle with items and financial tracking
- **OrderItems**: Line items with customization details
- **ClientInteractions**: CRM interaction history

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd operations_dashboard/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python -c "from database import init_db; init_db()"
```

5. Run the development server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd operations_dashboard/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## Configuration

### Backend Configuration

Create a `.env` file in the backend directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
PORT=5000

# Database Configuration
DATABASE_URL=sqlite:///tezzaworks.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/tezzaworks

# Business Configuration
DEFAULT_TAX_RATE=8.5
DEFAULT_LABOR_RATE=25.00
DEFAULT_OVERHEAD_PERCENTAGE=30.0
```

### Frontend Configuration

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:5000/api
```

## API Endpoints

### Clients
- `GET /api/clients` - Get all clients
- `GET /api/clients/:id` - Get client by ID
- `POST /api/clients` - Create new client
- `PUT /api/clients/:id` - Update client
- `DELETE /api/clients/:id` - Delete client
- `GET /api/clients/:id/interactions` - Get client interactions
- `POST /api/clients/:id/interactions` - Create interaction
- `GET /api/clients/:id/stats` - Get client statistics

### Products
- `GET /api/products` - Get all products
- `GET /api/products/:id` - Get product by ID
- `POST /api/products` - Create new product
- `PUT /api/products/:id` - Update product
- `DELETE /api/products/:id` - Delete product
- `POST /api/products/:id/pricing` - Calculate pricing
- `GET /api/products/low-stock` - Get low stock products
- `GET /api/products/categories` - Get product categories

### Orders
- `GET /api/orders` - Get all orders
- `GET /api/orders/:id` - Get order by ID
- `POST /api/orders` - Create new order
- `PUT /api/orders/:id` - Update order
- `DELETE /api/orders/:id` - Delete order
- `PUT /api/orders/:id/status` - Update order status
- `GET /api/orders/kanban` - Get kanban board data
- `GET /api/orders/analytics` - Get analytics data
- `POST /api/orders/quote` - Generate quote

### Export
- `GET /api/export/orders` - Export orders to CSV
- `GET /api/export/clients` - Export clients to CSV
- `GET /api/export/products` - Export products to CSV
- `GET /api/export/order-details/:id` - Export order details

## Database Models

### Client Model
```python
- id (Primary Key)
- company_name
- contact_person
- email (Unique)
- phone
- address, city, state, zip_code, country
- industry
- acquisition_source (Enum)
- preferences, notes
- created_at, updated_at
- last_contact_date, next_follow_up
```

### Product Model
```python
- id (Primary Key)
- sku (Unique)
- name, description
- category (Enum)
- base_cost, labor_hours, overhead_percentage
- stock_quantity, reorder_level
- allows_logo, allows_personalization
- customization_cost
- is_active
- created_at, updated_at
```

### Order Model
```python
- id (Primary Key)
- order_number (Unique)
- client_id (Foreign Key)
- status (Enum)
- order_date, confirmed_date, production_start_date
- estimated_completion_date, ship_date, delivery_date
- shipping information
- financial fields (subtotal, tax, total, discounts)
- cost tracking (materials, labor, overhead, profit_margin)
- notes, internal_notes, special_instructions
- created_at, updated_at
```

### OrderItem Model
```python
- id (Primary Key)
- order_id (Foreign Key)
- product_id (Foreign Key)
- quantity, unit_price, line_total
- customization details (logo, personalization)
- cost tracking fields
- production_notes
```

## Pricing Calculator

The pricing calculator implements sophisticated business rules:

### Volume Discount Tiers
- 1-25 units: 0% discount (base price)
- 26-100 units: 10% discount
- 101-500 units: 15% discount
- 500+ units: 25% discount

### Price Calculation Formula
```
Base Price = Material Cost × (1 + Overhead %)
Discounted Price = Base Price × (1 - Volume Discount)
Final Price = Discounted Price + Customization Cost
```

### Profit Margin Calculation
```
Total Cost = Materials + Labor + Overhead
Profit Margin % = ((Selling Price - Total Cost) / Selling Price) × 100
```

## Usage Examples

### Creating an Order

1. Navigate to Orders page
2. Click "Create Order"
3. Select client
4. Add products with quantities
5. Configure customization options
6. Review pricing and margins
7. Submit order

### Tracking Production

1. Navigate to Production Board (Kanban)
2. View orders by status column
3. Click order card for details
4. Update status by editing order
5. Track estimated completion dates

### Generating Reports

1. Navigate to desired section (Orders, Clients, Products)
2. Apply filters as needed
3. Click Export button
4. Download CSV file

### Viewing Analytics

1. Navigate to Analytics Dashboard
2. Select date range
3. View revenue trends
4. Analyze top products
5. Review order statistics

## Production Deployment

### Backend Deployment

1. Set production environment variables
2. Use PostgreSQL for production database
3. Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

4. Set up reverse proxy (Nginx recommended)
5. Enable HTTPS with SSL certificate

### Frontend Deployment

1. Build production bundle:
```bash
npm run build
```

2. Deploy the `dist` folder to:
   - Static hosting (Vercel, Netlify)
   - CDN (CloudFront, CloudFlare)
   - Web server (Nginx, Apache)

### Docker Deployment (Optional)

Backend Dockerfile:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Frontend Dockerfile:
```dockerfile
FROM node:16 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Security Considerations

1. **Change default SECRET_KEY** in production
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** in production
4. **Implement authentication** (OAuth, JWT)
5. **Add rate limiting** to API endpoints
6. **Validate all inputs** server-side
7. **Use parameterized queries** (SQLAlchemy handles this)
8. **Regular security updates** for dependencies

## Maintenance

### Database Backups
```bash
# SQLite backup
cp tezzaworks.db tezzaworks_backup_$(date +%Y%m%d).db

# PostgreSQL backup
pg_dump -U username tezzaworks > backup_$(date +%Y%m%d).sql
```

### Updating Dependencies
```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
npm update
```

## Support & Troubleshooting

### Common Issues

**Issue**: Database not found
**Solution**: Run `python -c "from database import init_db; init_db()"`

**Issue**: CORS errors
**Solution**: Check that CORS is enabled in app.py and frontend API URL is correct

**Issue**: Port already in use
**Solution**: Change PORT in .env file or kill process using the port

**Issue**: Module not found
**Solution**: Ensure virtual environment is activated and dependencies are installed

## Future Enhancements

- User authentication and role-based access control
- Email notifications for order updates
- PDF invoice generation
- Mobile responsive design improvements
- Real-time WebSocket updates
- Integration with accounting software (QuickBooks, Xero)
- Vendor management system
- Purchase order tracking
- Advanced reporting and business intelligence
- Mobile app (React Native)

## License

Proprietary - TezzaWorks Internal Use Only

## Contact

For questions or support, contact the TezzaWorks development team.

---

**Version**: 1.0.0
**Last Updated**: 2025-11-11
**Developed for**: TezzaWorks Business Operations
