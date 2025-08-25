# Telecom Customer Churn & Anomaly Detection Dashboard

A comprehensive enterprise-level analytics platform that helps telecom companies predict customer churn and detect anomalous usage patterns using machine learning.

## 🚀 Features

- **Real-time Churn Prediction**: ML-powered customer churn probability scoring
- **Anomaly Detection**: Identifies unusual usage patterns and potential fraud
- **Interactive Dashboard**: Modern React-based UI with real-time updates
- **Risk Classification**: Categorizes customers as High/Medium/Low risk
- **Alert System**: Automated notifications for critical situations
- **Analytics & Insights**: Comprehensive reporting and trend analysis

## 🏗️ Architecture

```
📁 customer_churn/
├── 📁 backend/                    # Python Flask API
│   ├── flask_api.py              # REST API endpoints
│   ├── ml_models.py              # Machine Learning models
│   └── data_loader.py            # Data processing utilities
└── 📁 telecom-dashboard/         # React Frontend (Vite)
    ├── src/
    │   ├── App.jsx               # Main React application
    │   ├── Telecom.jsx           # Dashboard component
    │   └── index.css             # Styling
    └── .env                      # Environment variables
```

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **scikit-learn** - Machine learning
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **Flask-CORS** - Cross-origin requests

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. Install Python dependencies:
```bash
pip install flask flask-cors pandas numpy scikit-learn joblib
```

5. Start the Flask server:
```bash
python flask_api.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd telecom-dashboard
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `telecom-dashboard` directory:

```env
VITE_BASE_URL="http://localhost:5000/api"
```

## 📊 API Endpoints

### Health Check
- `GET /health` - Server health status

### Customer Data
- `GET /api/customers` - Get customer data with predictions
- `POST /api/predict` - Predict churn for a single customer

### Analytics
- `GET /api/analytics` - Get dashboard analytics data
- `GET /api/alerts` - Get current alerts and notifications

## 🤖 Machine Learning Models

### Churn Prediction Model
- **Algorithm**: Random Forest Classifier
- **Features**: Customer demographics, usage patterns, service history
- **Output**: Churn probability (0-1) and risk level (High/Medium/Low)

### Anomaly Detection Model
- **Algorithm**: Statistical outlier detection
- **Features**: Usage patterns, billing data, service metrics
- **Output**: Anomaly classification and type identification

### Anomaly Types Detected
- **Sudden Usage Drop**: Potential account sharing or technical issues
- **Billing Anomaly**: Charges don't match usage patterns
- **Usage Spike**: Potential fraud or unusual activity
- **Service Abuse**: Excessive complaints or service calls

## 📈 Dashboard Features

### Overview Tab
- Key performance indicators (KPIs)
- Churn risk distribution
- Anomaly detection overview
- Monthly trends visualization

### Customer Risk Monitor
- Real-time customer list with risk scores
- Advanced filtering and search
- Churn probability visualization
- Customer action buttons

### Active Alerts
- Critical, high, and medium priority alerts
- Action-required notifications
- Alert categorization and timestamps

### Advanced Analytics
- Feature importance analysis
- Trend analysis and forecasting
- Risk metrics and revenue impact

## 🔄 Data Flow

1. **Synthetic Data Generation**: Creates realistic telecom customer data
2. **Feature Engineering**: Processes raw data into ML-ready features
3. **Model Prediction**: Runs churn and anomaly detection models
4. **API Response**: Serves predictions via REST endpoints
5. **Dashboard Update**: Frontend displays real-time insights

## 🚦 Usage

1. Start the backend Flask server
2. Start the frontend Vite development server
3. Open your browser to `http://localhost:5173`
4. Explore the dashboard tabs:
   - **Overview**: High-level metrics and trends
   - **Customer Risk Monitor**: Individual customer analysis
   - **Active Alerts**: Critical notifications
   - **Advanced Analytics**: Detailed insights

## 🔒 Security Considerations

- CORS configured for development environments
- Input validation on API endpoints
- No real customer data used (synthetic data only)
- Environment variables for configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern web technologies
- Inspired by real-world telecom analytics needs
- Designed for scalability and maintainability

## 📞 Support

For support, email your-email@example.com or create an issue in this repository.

---

**Note**: This project uses synthetic data for demonstration purposes. In a production environment, you would integrate with real customer databases and implement proper data security measures.