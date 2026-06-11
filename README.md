# P.I.R.E. – Perishable Inventory Risk Engine

**Predict. Prevent. Preserve.**

P.I.R.E. is a production-style MERN + Python + XGBoost platform for perishable inventory risk analysis. It predicts expiry risk, surfaces operational alerts, provides analytics, and exports inventory intelligence for demonstration and reporting.

## Architecture

- **Frontend:** React, Vite, Tailwind CSS, React Router, Axios, Recharts, Lucide React
- **Backend:** Node.js, Express, MongoDB, JWT authentication
- **Machine Learning:** Python, scikit-learn, XGBoost, joblib
- **Integration:** Node `spawn` executes Python prediction script and returns JSON to the frontend

## Project Structure

- `smart-grocery-frontend/` - React dashboard UI
- `smart-grocery-backend/` - Express API, authentication, analytics, alerts, export, and prediction services
- `smart-grocery-backend/ml/` - dataset generation, training, and prediction pipeline

## Features

- JWT authentication with register/login/profile flow
- Inventory CRUD with search and risk filtering
- XGBoost-driven expiry risk prediction
- KPI dashboard and charts
- Alert engine for expiry, high-risk, and overstock conditions
- CSV and PDF export
- Responsive green-themed dashboard UI

## Screenshots

Add your screenshots here before submission:

- Landing page
- Login page
- Dashboard
- Inventory list
- Prediction result
- Analytics page
- Alerts page

## Setup Instructions

### 1. Install dependencies

Frontend:

```bash
cd smart-grocery-frontend
npm install
```

Backend:

```bash
cd smart-grocery-backend
npm install
```

### 2. Configure environment files

Copy the example files:

- `smart-grocery-backend/.env.example` to `smart-grocery-backend/.env`
- `smart-grocery-frontend/.env.example` to `smart-grocery-frontend/.env`

Update values if needed:

- MongoDB connection string
- JWT secret
- Frontend URL

### 3. Prepare Python ML assets

From the backend folder:

```bash
cd smart-grocery-backend/ml
python generate_dataset.py
python train_model.py
```

This creates:

- `ml/data/synthetic_inventory_data.csv`
- `ml/model/risk_model.pkl`
- `ml/model/label_encoder.pkl`

### 4. Run the backend

```bash
cd smart-grocery-backend
npm run dev
```

Backend default URL:

- `http://localhost:5000`

### 5. Run the frontend

```bash
cd smart-grocery-frontend
npm run dev
```

Frontend default URL:

- `http://localhost:5173`

### 6. Optional npm start support

The frontend also supports:

```bash
npm start
```

because the `start` script points to Vite.

## API Documentation

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Inventory

- `GET /api/inventory`
- `POST /api/inventory`
- `GET /api/inventory/:id`
- `PUT /api/inventory/:id`
- `DELETE /api/inventory/:id`

### Prediction

- `POST /api/predict`

### Analytics

- `GET /api/analytics/summary`
- `GET /api/analytics/risk-distribution`
- `GET /api/analytics/monthly-trends`

### Alerts

- `GET /api/alerts`

### Export

- `GET /api/export/inventory/csv`
- `GET /api/export/analytics/pdf`

## Prediction Output Format

```json
{
  "riskPrediction": "High Risk",
  "confidenceScore": 0.94,
  "recommendedAction": "Apply Discount Immediately"
}
```

## Deployment Notes

- Configure `MONGO_URI` in production with a hosted MongoDB instance
- Set a strong `JWT_SECRET`
- Set `FRONTEND_URL` to the deployed frontend origin
- Set `VITE_API_URL` to the deployed backend API base URL
- Ensure the Python runtime is available on the backend host

## Final Demo Flow

1. Register or login
2. Add inventory items
3. Open the dashboard to inspect risk KPIs
4. Run prediction on selected items
5. Review alerts and analytics
6. Export CSV or PDF reports
