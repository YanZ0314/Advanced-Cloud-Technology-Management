# Cloud Strategy Simulation – Streamlit Web App

A Streamlit web application for simulating company revenue growth rates, cash flow projections, sensitivity analysis, and AI investment trends.

## Features

- **Revenue Growth Simulation**: 5-year projection based on Porter's Five Forces (competition, new entrants, supplier/buyer power, substitutes) and product-market fit, differentiator
- **Linear & Radar Charts**: Growth rate trends and variable comparison
- **Sensitivity Analysis**: Best (120%), baseline (100%), worst (80%) scenarios
- **Cash Flow Table**: Capital, Revenue, Expense, Net Profit, Cumulative Cash
- **Leadership Variables**: Adaptive learning, deep learning, process management
- **AI Investments vs US Business Apps**: Historical data (2015-2023), predictions (2024-2025), gap analysis
- **Multi-Tenant Auth**: User registration/login, admin user management

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd "d:\cs\CSCI E-176 Advanced cloud strategy"
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

### 3. Access the App

Open `http://localhost:8501` in your browser.

### 4. First-Time Admin Login

- **Email**: `admin@cloudstrategy.local`
- **Password**: `admin123` (change after first login in production)

### 5. Create a User Account

1. Click **Sign Up** in the sidebar  
2. Enter email and password  
3. Log in to use the app with your own account  

## Project Structure

```
├── app.py              # Main Streamlit application
├── growth_model.py     # Revenue growth calculation logic
├── auth_utils.py       # Authentication and user management
├── data/               # User data (created at runtime)
│   └── users.json
├── requirements.txt
└── README.md
```

## Azure Deployment

For multi-tenant deployment on Azure:

1. **Web App**: Deploy using Azure App Service
2. **Authentication**: Replace `auth_utils.py` with Azure AD B2C or Microsoft Entra ID
3. **Data**: Use Azure SQL Database or Cosmos DB for user storage

Example deployment:

```bash
# Create Azure Web App
az webapp create --resource-group <rg> --plan <plan> --name <app-name> --runtime "PYTHON:3.11"
```

Configure the app to run `streamlit run app.py --server.port=8000`.
