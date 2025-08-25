from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys

# Import our ML models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ml_models import TelecomChurnAnomalyDetector

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])  # Allow React dev server

# Global model instance
detector = TelecomChurnAnomalyDetector()

# Load models on startup
try:
    detector.load_models()
    print("Models loaded successfully!")
except:
    print("No pre-trained models found. Training new models...")
    # Generate and train on synthetic data
    training_data = detector.generate_synthetic_data(n_samples=10000)
    detector.train_churn_model(training_data)
    detector.train_anomaly_model(training_data)
    detector.save_models()
    print("New models trained and saved!")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": detector.churn_model is not None
    })

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Get sample customer data with predictions"""
    try:
        # Generate sample data
        sample_data = detector.generate_synthetic_data(n_samples=50)
        
        # Get predictions
        churn_proba, risk_levels = detector.predict_churn_risk(sample_data)
        is_anomaly, anomaly_scores, anomaly_types = detector.detect_anomalies(sample_data)
        
        # Prepare response data
        customers = []
        for i, row in sample_data.iterrows():
            customer = {
                "id": row['customer_id'],
                "tenure": round(row['tenure'], 1),
                "age": int(row['age']),
                "monthlyCharges": round(row['monthly_charges'], 2),
                "totalCharges": round(row['total_charges'], 2),
                "dataUsageGB": round(row['data_usage_gb'], 2),
                "callMinutes": round(row['call_minutes'], 0),
                "smsCount": int(row['sms_count']),
                "complaints": int(row['complaints']),
                "serviceCalls": int(row['service_calls']),
                "downtimeHours": round(row['downtime_hours'], 2),
                "contractType": row['contract_type'],
                "paymentMethod": row['payment_method'],
                "internetService": row['internet_service'],
                "churnProbability": round(churn_proba[i], 4),
                "riskLevel": risk_levels[i],
                "isAnomaly": bool(is_anomaly[i]),
                "anomalyScore": round(anomaly_scores[i], 4),
                "anomalyType": anomaly_types[i],
                "actualChurn": bool(row['churn']),
                "lastActivity": (datetime.now() - timedelta(days=np.random.randint(0, 30))).isoformat()
            }
            customers.append(customer)
        
        return jsonify({
            "customers": customers,
            "summary": {
                "total": len(customers),
                "highRisk": sum(1 for c in customers if c['riskLevel'] == 'High'),
                "mediumRisk": sum(1 for c in customers if c['riskLevel'] == 'Medium'),
                "lowRisk": sum(1 for c in customers if c['riskLevel'] == 'Low'),
                "anomalies": sum(1 for c in customers if c['isAnomaly']),
                "averageChurnProb": round(np.mean([c['churnProbability'] for c in customers]), 4)
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict_customer():
    """Predict churn and anomalies for a single customer"""
    try:
        data = request.get_json()
        
        # Convert to DataFrame
        customer_df = pd.DataFrame([{
            'customer_id': data.get('id', 'UNKNOWN'),
            'tenure': float(data.get('tenure', 0)),
            'age': int(data.get('age', 0)),
            'monthly_charges': float(data.get('monthlyCharges', 0)),
            'total_charges': float(data.get('totalCharges', 0)),
            'data_usage_gb': float(data.get('dataUsageGB', 0)),
            'call_minutes': float(data.get('callMinutes', 0)),
            'sms_count': int(data.get('smsCount', 0)),
            'complaints': int(data.get('complaints', 0)),
            'service_calls': int(data.get('serviceCalls', 0)),
            'downtime_hours': float(data.get('downtimeHours', 0)),
            'contract_type': data.get('contractType', 'Month-to-month'),
            'payment_method': data.get('paymentMethod', 'Electronic check'),
            'internet_service': data.get('internetService', 'DSL')
        }])
        
        # Get predictions
        churn_proba, risk_levels = detector.predict_churn_risk(customer_df)
        is_anomaly, anomaly_scores, anomaly_types = detector.detect_anomalies(customer_df)
        
        # Prepare response
        result = {
            "customerId": data.get('id', 'UNKNOWN'),
            "churnProbability": round(churn_proba[0], 4),
            "riskLevel": risk_levels[0],
            "isAnomaly": bool(is_anomaly[0]),
            "anomalyScore": round(anomaly_scores[0], 4),
            "anomalyType": anomaly_types[0],
            "recommendations": generate_recommendations(churn_proba[0], risk_levels[0], is_anomaly[0], anomaly_types[0])
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data for dashboard"""
    try:
        # Generate larger sample for analytics
        sample_data = detector.generate_synthetic_data(n_samples=1000)
        
        # Get predictions
        churn_proba, risk_levels = detector.predict_churn_risk(sample_data)
        is_anomaly, anomaly_scores, anomaly_types = detector.detect_anomalies(sample_data)
        
        # Calculate analytics
        analytics = {
            "churnDistribution": {
                "high": int(np.sum(np.array(risk_levels) == 'High')),
                "medium": int(np.sum(np.array(risk_levels) == 'Medium')),
                "low": int(np.sum(np.array(risk_levels) == 'Low'))
            },
            "anomalyDistribution": {
                "normal": int(np.sum(~is_anomaly)),
                "sudden_usage_drop": int(np.sum([t == 'Sudden Usage Drop' for t in anomaly_types])),
                "billing_anomaly": int(np.sum([t == 'Billing Anomaly' for t in anomaly_types])),
                "usage_spike": int(np.sum([t == 'Usage Spike' for t in anomaly_types])),
                "service_abuse": int(np.sum([t == 'Service Abuse' for t in anomaly_types])),
                "other": int(np.sum([t == 'Other Anomaly' for t in anomaly_types]))
            },
            "monthlyTrends": generate_monthly_trends(),
            "topFeatures": detector.get_feature_importance().head(10).to_dict('records'),
            "riskMetrics": {
                "totalCustomers": len(sample_data),
                "averageChurnProb": round(np.mean(churn_proba), 4),
                "anomalyRate": round(np.sum(is_anomaly) / len(is_anomaly), 4),
                "highRiskRevenue": round(sample_data[np.array(risk_levels) == 'High']['monthly_charges'].sum(), 2)
            }
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get current alerts and notifications"""
    try:
        # Generate sample data for alerts
        sample_data = detector.generate_synthetic_data(n_samples=20)
        churn_proba, risk_levels = detector.predict_churn_risk(sample_data)
        is_anomaly, anomaly_scores, anomaly_types = detector.detect_anomalies(sample_data)
        
        alerts = []
        
        for i, row in sample_data.iterrows():
            if churn_proba[i] > 0.8:
                alerts.append({
                    "id": f"alert_{len(alerts)+1}",
                    "type": "high_churn_risk",
                    "severity": "critical",
                    "customerId": row['customer_id'],
                    "message": f"Customer {row['customer_id']} has {churn_proba[i]:.1%} churn probability",
                    "timestamp": datetime.now().isoformat(),
                    "actionRequired": True
                })
            
            if is_anomaly[i]:
                severity = "high" if anomaly_scores[i] < -0.5 else "medium"
                alerts.append({
                    "id": f"alert_{len(alerts)+1}",
                    "type": "anomaly_detected",
                    "severity": severity,
                    "customerId": row['customer_id'],
                    "message": f"Anomaly detected: {anomaly_types[i]} for customer {row['customer_id']}",
                    "timestamp": datetime.now().isoformat(),
                    "actionRequired": anomaly_types[i] in ['Billing Anomaly', 'Service Abuse']
                })
        
        # Sort by severity and timestamp
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        alerts.sort(key=lambda x: (severity_order.get(x['severity'], 999), x['timestamp']), reverse=True)
        
        return jsonify({
            "alerts": alerts[:10],  # Return top 10 alerts
            "summary": {
                "total": len(alerts),
                "critical": sum(1 for a in alerts if a['severity'] == 'critical'),
                "high": sum(1 for a in alerts if a['severity'] == 'high'),
                "medium": sum(1 for a in alerts if a['severity'] == 'medium'),
                "actionRequired": sum(1 for a in alerts if a['actionRequired'])
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_recommendations(churn_prob, risk_level, is_anomaly, anomaly_type):
    """Generate actionable recommendations"""
    recommendations = []
    
    if risk_level == 'High':
        recommendations.extend([
            "Immediate retention campaign",
            "Personal account manager assignment",
            "Special discount offer (20-30%)",
            "Priority customer support"
        ])
    elif risk_level == 'Medium':
        recommendations.extend([
            "Targeted retention email campaign",
            "Usage optimization consultation",
            "Loyalty program enrollment"
        ])
    
    if is_anomaly:
        if anomaly_type == 'Sudden Usage Drop':
            recommendations.append("Investigate potential account sharing or technical issues")
        elif anomaly_type == 'Billing Anomaly':
            recommendations.append("Review billing accuracy and contact customer")
        elif anomaly_type == 'Usage Spike':
            recommendations.append("Verify legitimate usage and check for fraud")
        elif anomaly_type == 'Service Abuse':
            recommendations.append("Review account for potential abuse and set limits")
    
    return recommendations

def generate_monthly_trends():
    """Generate sample monthly trends data"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    base_churn = 0.15
    base_anomaly = 0.08
    
    trends = []
    for i, month in enumerate(months):
        # Add some seasonality
        seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * i / 12)
        churn_rate = base_churn * seasonal_factor + np.random.normal(0, 0.02)
        anomaly_rate = base_anomaly * seasonal_factor + np.random.normal(0, 0.01)
        
        trends.append({
            "month": month,
            "churnRate": max(0, round(churn_rate, 3)),
            "anomalyRate": max(0, round(anomaly_rate, 3)),
            "totalCustomers": np.random.randint(8000, 12000)
        })
    
    return trends

if __name__ == '__main__':
    print("Starting Flask API server...")
    print("Health check: http://localhost:5000/health")
    print("API endpoints available at: http://localhost:5000/api/")
    app.run(host='0.0.0.0', port=5000, debug=True)