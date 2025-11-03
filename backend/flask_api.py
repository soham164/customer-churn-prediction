from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys
import io
import csv
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

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

@app.route('/api/export/customers', methods=['GET'])
def export_customers():
    """Export customer data to CSV"""
    try:
        # Generate sample data
        sample_data = detector.generate_synthetic_data(n_samples=1000)
        
        # Get predictions
        churn_proba, risk_levels = detector.predict_churn_risk(sample_data)
        is_anomaly, anomaly_scores, anomaly_types = detector.detect_anomalies(sample_data)
        
        # Prepare export data
        export_data = []
        for i, row in sample_data.iterrows():
            export_data.append({
                "Customer_ID": row['customer_id'],
                "Tenure_Months": round(row['tenure'], 1),
                "Age": int(row['age']),
                "Monthly_Charges": round(row['monthly_charges'], 2),
                "Total_Charges": round(row['total_charges'], 2),
                "Data_Usage_GB": round(row['data_usage_gb'], 2),
                "Call_Minutes": round(row['call_minutes'], 0),
                "SMS_Count": int(row['sms_count']),
                "Complaints": int(row['complaints']),
                "Service_Calls": int(row['service_calls']),
                "Downtime_Hours": round(row['downtime_hours'], 2),
                "Contract_Type": row['contract_type'],
                "Payment_Method": row['payment_method'],
                "Internet_Service": row['internet_service'],
                "Churn_Probability": round(churn_proba[i], 4),
                "Risk_Level": risk_levels[i],
                "Is_Anomaly": bool(is_anomaly[i]),
                "Anomaly_Score": round(anomaly_scores[i], 4),
                "Anomaly_Type": anomaly_types[i],
                "Actual_Churn": bool(row['churn']),
                "Export_Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
        writer.writeheader()
        writer.writerows(export_data)
        
        # Convert to bytes
        csv_data = output.getvalue()
        output.close()
        
        # Create file-like object
        csv_buffer = io.BytesIO()
        csv_buffer.write(csv_data.encode('utf-8'))
        csv_buffer.seek(0)
        
        filename = f"customer_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return send_file(
            csv_buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate analytics report"""
    try:
        data = request.get_json() or {}
        report_type = data.get('type', 'comprehensive')
        
        # Generate sample data for report
        sample_data = detector.generate_synthetic_data(n_samples=1000)
        churn_proba, risk_levels = detector.predict_churn_risk(sample_data)
        is_anomaly, anomaly_scores, anomaly_types = detector.detect_anomalies(sample_data)
        
        # Create PDF report
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("TelecomGuard Pro Analytics Report", title_style))
        story.append(Spacer(1, 20))
        
        # Report metadata
        report_info = [
            ["Report Type:", report_type.title()],
            ["Generated On:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Total Customers:", str(len(sample_data))],
            ["Analysis Period:", "Current Dataset"]
        ]
        
        info_table = Table(report_info, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        
        high_risk_count = np.sum(np.array(risk_levels) == 'High')
        anomaly_count = np.sum(is_anomaly)
        avg_churn_prob = np.mean(churn_proba)
        
        summary_text = f"""
        This report analyzes {len(sample_data)} customers in our telecom database. 
        Key findings include {high_risk_count} high-risk customers ({high_risk_count/len(sample_data)*100:.1f}%) 
        with an average churn probability of {avg_churn_prob*100:.1f}%. 
        Additionally, {anomaly_count} anomalous usage patterns were detected ({anomaly_count/len(sample_data)*100:.1f}%).
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Risk Distribution Table
        story.append(Paragraph("Risk Level Distribution", styles['Heading2']))
        
        risk_data = [
            ["Risk Level", "Count", "Percentage", "Avg Churn Prob"],
            ["High Risk", str(np.sum(np.array(risk_levels) == 'High')), 
             f"{np.sum(np.array(risk_levels) == 'High')/len(risk_levels)*100:.1f}%",
             f"{np.mean(churn_proba[np.array(risk_levels) == 'High'])*100:.1f}%"],
            ["Medium Risk", str(np.sum(np.array(risk_levels) == 'Medium')), 
             f"{np.sum(np.array(risk_levels) == 'Medium')/len(risk_levels)*100:.1f}%",
             f"{np.mean(churn_proba[np.array(risk_levels) == 'Medium'])*100:.1f}%"],
            ["Low Risk", str(np.sum(np.array(risk_levels) == 'Low')), 
             f"{np.sum(np.array(risk_levels) == 'Low')/len(risk_levels)*100:.1f}%",
             f"{np.mean(churn_proba[np.array(risk_levels) == 'Low'])*100:.1f}%"]
        ]
        
        risk_table = Table(risk_data, colWidths=[1.5*inch, 1*inch, 1.2*inch, 1.3*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 20))
        
        # Anomaly Analysis
        story.append(Paragraph("Anomaly Detection Results", styles['Heading2']))
        
        anomaly_types_unique = list(set(anomaly_types))
        anomaly_data = [["Anomaly Type", "Count", "Percentage"]]
        
        for atype in anomaly_types_unique:
            count = sum(1 for t in anomaly_types if t == atype)
            percentage = count / len(anomaly_types) * 100
            anomaly_data.append([atype, str(count), f"{percentage:.1f}%"])
        
        anomaly_table = Table(anomaly_data, colWidths=[2.5*inch, 1*inch, 1.2*inch])
        anomaly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(anomaly_table)
        story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("Recommendations", styles['Heading2']))
        
        recommendations = [
            f"• Focus retention efforts on {high_risk_count} high-risk customers",
            f"• Investigate {anomaly_count} anomalous usage patterns for potential fraud",
            "• Implement proactive customer outreach for medium-risk segments",
            "• Monitor billing anomalies and usage spikes closely",
            "• Consider loyalty programs for long-tenure, low-risk customers"
        ]
        
        for rec in recommendations:
            story.append(Paragraph(rec, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        filename = f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/schedule', methods=['POST'])
def schedule_report():
    """Schedule a report for future generation"""
    try:
        data = request.get_json()
        
        # For now, we'll just simulate scheduling and return a confirmation
        # In a real implementation, you'd use a task queue like Celery
        
        schedule_data = {
            "id": f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "report_type": data.get('type', 'comprehensive'),
            "frequency": data.get('frequency', 'weekly'),
            "recipients": data.get('recipients', []),
            "next_run": (datetime.now() + timedelta(days=7)).isoformat(),
            "created_at": datetime.now().isoformat(),
            "status": "scheduled"
        }
        
        # In a real app, save this to database
        # For demo, we'll just return the schedule info
        
        return jsonify({
            "message": "Report scheduled successfully",
            "schedule": schedule_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/schedules', methods=['GET'])
def get_scheduled_reports():
    """Get list of scheduled reports"""
    try:
        # Mock data for scheduled reports
        schedules = [
            {
                "id": "schedule_20241205_120000",
                "report_type": "comprehensive",
                "frequency": "weekly",
                "recipients": ["admin@company.com"],
                "next_run": (datetime.now() + timedelta(days=3)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=4)).isoformat(),
                "status": "active"
            },
            {
                "id": "schedule_20241201_090000",
                "report_type": "risk_analysis",
                "frequency": "monthly",
                "recipients": ["manager@company.com", "analyst@company.com"],
                "next_run": (datetime.now() + timedelta(days=25)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=8)).isoformat(),
                "status": "active"
            }
        ]
        
        return jsonify({"schedules": schedules})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get notifications for the user"""
    try:
        # Generate sample notifications
        notifications = []
        
        # Generate some sample notifications based on recent alerts
        sample_data = detector.generate_synthetic_data(n_samples=10)
        churn_proba, risk_levels = detector.predict_churn_risk(sample_data)
        is_anomaly, anomaly_scores, anomaly_types = detector.detect_anomalies(sample_data)
        
        notification_id = 1
        for i, row in sample_data.iterrows():
            if churn_proba[i] > 0.8:
                notifications.append({
                    "id": f"notif_{notification_id}",
                    "title": "High Churn Risk Alert",
                    "message": f"Customer {row['customer_id']} has {churn_proba[i]:.1%} churn probability. Immediate action recommended.",
                    "severity": "critical",
                    "timestamp": (datetime.now() - timedelta(minutes=np.random.randint(5, 120))).isoformat(),
                    "actionRequired": True,
                    "read": np.random.choice([True, False], p=[0.3, 0.7])
                })
                notification_id += 1
            
            if is_anomaly[i] and anomaly_types[i] in ['Billing Anomaly', 'Service Abuse']:
                notifications.append({
                    "id": f"notif_{notification_id}",
                    "title": "Anomaly Detected",
                    "message": f"{anomaly_types[i]} detected for customer {row['customer_id']}. Please investigate.",
                    "severity": "high" if anomaly_types[i] == 'Service Abuse' else "medium",
                    "timestamp": (datetime.now() - timedelta(minutes=np.random.randint(10, 180))).isoformat(),
                    "actionRequired": True,
                    "read": np.random.choice([True, False], p=[0.4, 0.6])
                })
                notification_id += 1
        
        # Add some system notifications
        notifications.extend([
            {
                "id": f"notif_{notification_id}",
                "title": "Daily Report Generated",
                "message": "Your daily analytics report has been generated and is ready for download.",
                "severity": "low",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "actionRequired": False,
                "read": False
            },
            {
                "id": f"notif_{notification_id + 1}",
                "title": "Model Performance Update",
                "message": "Churn prediction model accuracy: 94.2%. Anomaly detection rate: 8.1%.",
                "severity": "low",
                "timestamp": (datetime.now() - timedelta(hours=6)).isoformat(),
                "actionRequired": False,
                "read": True
            }
        ])
        
        # Sort by timestamp (newest first)
        notifications.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            "notifications": notifications[:20],  # Return latest 20
            "summary": {
                "total": len(notifications),
                "unread": sum(1 for n in notifications if not n['read']),
                "actionRequired": sum(1 for n in notifications if n['actionRequired'])
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/<notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        # In a real app, you'd update the database
        return jsonify({
            "message": "Notification marked as read",
            "notification_id": notification_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/mark-all-read', methods=['POST'])
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        # In a real app, you'd update the database
        return jsonify({
            "message": "All notifications marked as read"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts/<alert_id>/investigate', methods=['GET'])
def investigate_alert(alert_id):
    """Get detailed investigation data for a specific alert"""
    try:
        # Generate sample data for investigation
        sample_data = detector.generate_synthetic_data(n_samples=100)
        churn_proba, risk_levels = detector.predict_churn_risk(sample_data)
        is_anomaly, anomaly_scores, anomaly_types = detector.detect_anomalies(sample_data)
        
        # Find the customer related to this alert (simulate)
        customer_idx = np.random.randint(0, len(sample_data))
        customer = sample_data.iloc[customer_idx]
        
        # Generate investigation details
        investigation = {
            "alertId": alert_id,
            "customerId": customer['customer_id'],
            "investigationDate": datetime.now().isoformat(),
            "customerProfile": {
                "id": customer['customer_id'],
                "tenure": round(customer['tenure'], 1),
                "age": int(customer['age']),
                "monthlyCharges": round(customer['monthly_charges'], 2),
                "totalCharges": round(customer['total_charges'], 2),
                "dataUsageGB": round(customer['data_usage_gb'], 2),
                "callMinutes": round(customer['call_minutes'], 0),
                "smsCount": int(customer['sms_count']),
                "complaints": int(customer['complaints']),
                "serviceCalls": int(customer['service_calls']),
                "downtimeHours": round(customer['downtime_hours'], 2),
                "contractType": customer['contract_type'],
                "paymentMethod": customer['payment_method'],
                "internetService": customer['internet_service'],
                "churnProbability": round(churn_proba[customer_idx], 4),
                "riskLevel": risk_levels[customer_idx],
                "isAnomaly": bool(is_anomaly[customer_idx]),
                "anomalyScore": round(anomaly_scores[customer_idx], 4),
                "anomalyType": anomaly_types[customer_idx]
            },
            "historicalData": generate_customer_history(customer['customer_id']),
            "riskFactors": analyze_risk_factors(customer, churn_proba[customer_idx]),
            "recommendations": generate_detailed_recommendations(customer, churn_proba[customer_idx], is_anomaly[customer_idx], anomaly_types[customer_idx]),
            "similarCases": find_similar_cases(customer, sample_data, churn_proba, risk_levels),
            "timeline": generate_alert_timeline(alert_id, customer['customer_id'])
        }
        
        return jsonify(investigation)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts/<alert_id>/actions', methods=['POST'])
def take_alert_action(alert_id):
    """Take action on an alert (resolve, escalate, etc.)"""
    try:
        data = request.get_json()
        action_type = data.get('action', 'resolve')
        notes = data.get('notes', '')
        assigned_to = data.get('assignedTo', '')
        
        # In a real system, you'd update the database
        action_result = {
            "alertId": alert_id,
            "action": action_type,
            "notes": notes,
            "assignedTo": assigned_to,
            "actionDate": datetime.now().isoformat(),
            "actionBy": "current_user",  # In real app, get from auth
            "status": "completed" if action_type == 'resolve' else "in_progress"
        }
        
        return jsonify({
            "message": f"Alert {action_type}d successfully",
            "action": action_result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_customer_history(customer_id):
    """Generate historical data for a customer"""
    history = []
    base_date = datetime.now() - timedelta(days=180)
    
    for i in range(6):  # 6 months of history
        month_date = base_date + timedelta(days=30*i)
        history.append({
            "month": month_date.strftime("%Y-%m"),
            "monthlyCharges": round(np.random.normal(75, 15), 2),
            "dataUsage": round(np.random.normal(25, 8), 2),
            "callMinutes": round(np.random.normal(450, 100), 0),
            "complaints": np.random.poisson(0.3),
            "serviceCalls": np.random.poisson(0.5),
            "downtimeHours": round(np.random.exponential(2), 2),
            "churnProbability": round(np.random.beta(2, 8), 3)
        })
    
    return history

def analyze_risk_factors(customer, churn_prob):
    """Analyze what factors contribute most to churn risk"""
    factors = []
    
    if customer['complaints'] > 2:
        factors.append({
            "factor": "High Complaint Count",
            "value": int(customer['complaints']),
            "impact": "High",
            "description": f"Customer has {customer['complaints']} complaints, above average"
        })
    
    if customer['service_calls'] > 3:
        factors.append({
            "factor": "Frequent Service Calls",
            "value": int(customer['service_calls']),
            "impact": "Medium",
            "description": f"Customer made {customer['service_calls']} service calls recently"
        })
    
    if customer['downtime_hours'] > 10:
        factors.append({
            "factor": "High Downtime",
            "value": round(customer['downtime_hours'], 1),
            "impact": "High",
            "description": f"Customer experienced {customer['downtime_hours']:.1f} hours of downtime"
        })
    
    if customer['tenure'] < 12:
        factors.append({
            "factor": "Low Tenure",
            "value": round(customer['tenure'], 1),
            "impact": "Medium",
            "description": f"Customer tenure of {customer['tenure']:.1f} months is below average"
        })
    
    if customer['contract_type'] == 'Month-to-month':
        factors.append({
            "factor": "Month-to-Month Contract",
            "value": customer['contract_type'],
            "impact": "Medium",
            "description": "Month-to-month contracts have higher churn rates"
        })
    
    return factors

def generate_detailed_recommendations(customer, churn_prob, is_anomaly, anomaly_type):
    """Generate detailed recommendations with priority and timeline"""
    recommendations = []
    
    if churn_prob > 0.7:
        recommendations.append({
            "priority": "Critical",
            "action": "Immediate Retention Call",
            "timeline": "Within 24 hours",
            "description": "Personal call from account manager with retention offer",
            "expectedImpact": "High",
            "cost": "Low"
        })
        
        recommendations.append({
            "priority": "High",
            "action": "Special Discount Offer",
            "timeline": "Within 48 hours",
            "description": "Offer 25-30% discount for 6-month commitment",
            "expectedImpact": "High",
            "cost": "Medium"
        })
    
    if customer['complaints'] > 2:
        recommendations.append({
            "priority": "High",
            "action": "Service Quality Review",
            "timeline": "Within 1 week",
            "description": "Technical team to review and resolve service issues",
            "expectedImpact": "Medium",
            "cost": "Low"
        })
    
    if is_anomaly and anomaly_type == 'Billing Anomaly':
        recommendations.append({
            "priority": "Critical",
            "action": "Billing Investigation",
            "timeline": "Within 24 hours",
            "description": "Review billing accuracy and contact customer immediately",
            "expectedImpact": "High",
            "cost": "Low"
        })
    
    recommendations.append({
        "priority": "Medium",
        "action": "Loyalty Program Enrollment",
        "timeline": "Within 1 week",
        "description": "Enroll customer in loyalty program with benefits",
        "expectedImpact": "Medium",
        "cost": "Low"
    })
    
    return recommendations

def find_similar_cases(customer, sample_data, churn_proba, risk_levels):
    """Find similar customer cases for comparison"""
    similar_cases = []
    
    # Find customers with similar characteristics
    for i, row in sample_data.head(10).iterrows():
        if (abs(row['tenure'] - customer['tenure']) < 6 and 
            abs(row['monthly_charges'] - customer['monthly_charges']) < 20):
            
            similar_cases.append({
                "customerId": row['customer_id'],
                "similarity": round(np.random.uniform(0.7, 0.95), 2),
                "churnProbability": round(churn_proba[i], 3),
                "riskLevel": risk_levels[i],
                "outcome": "Retained" if np.random.random() > 0.3 else "Churned",
                "actionTaken": np.random.choice([
                    "Discount Offer", "Service Upgrade", "Personal Call", 
                    "Loyalty Program", "No Action"
                ])
            })
    
    return similar_cases[:5]  # Return top 5 similar cases

def generate_alert_timeline(alert_id, customer_id):
    """Generate timeline of events for this alert"""
    timeline = []
    base_time = datetime.now() - timedelta(hours=24)
    
    events = [
        "Alert triggered by ML model",
        "Customer risk score updated",
        "Anomaly pattern detected",
        "Alert assigned to analyst",
        "Investigation initiated"
    ]
    
    for i, event in enumerate(events):
        event_time = base_time + timedelta(hours=i*4)
        timeline.append({
            "timestamp": event_time.isoformat(),
            "event": event,
            "details": f"System automatically {event.lower()}",
            "type": "system"
        })
    
    return timeline



def generate_customer_history(customer_id):
    """Generate historical data for a customer"""
    history = []
    base_date = datetime.now() - timedelta(days=180)
    
    for i in range(6):  # 6 months of history
        month_date = base_date + timedelta(days=30*i)
        history.append({
            "month": month_date.strftime("%Y-%m"),
            "monthlyCharges": round(np.random.normal(75, 15), 2),
            "dataUsage": round(np.random.normal(25, 8), 2),
            "callMinutes": round(np.random.normal(450, 100), 0),
            "complaints": np.random.poisson(0.3),
            "serviceCalls": np.random.poisson(0.5),
            "downtimeHours": round(np.random.exponential(2), 2),
            "churnProbability": round(np.random.beta(2, 8), 3)
        })
    
    return history

def analyze_risk_factors(customer, churn_prob):
    """Analyze what factors contribute most to churn risk"""
    factors = []
    
    if customer['complaints'] > 2:
        factors.append({
            "factor": "High Complaint Count",
            "value": int(customer['complaints']),
            "impact": "High",
            "description": f"Customer has {customer['complaints']} complaints, above average"
        })
    
    if customer['service_calls'] > 3:
        factors.append({
            "factor": "Frequent Service Calls",
            "value": int(customer['service_calls']),
            "impact": "Medium",
            "description": f"Customer made {customer['service_calls']} service calls recently"
        })
    
    if customer['total_charges'] > customer['monthly_charges'] * 50:
        factors.append({
            "factor": "High Total Charges",
            "value": customer['total_charges'],
            "impact": "Medium",
            "description": f"Total charges of ${customer['total_charges']:.2f} are unusually high"
        })
    
    if customer['contract_type'] == 'Month-to-month':
        factors.append({
            "factor": "Month-to-month Contract",
            "value": customer['contract_type'],
            "impact": "Medium",
            "description": "Month-to-month contracts have higher churn rates"
        })
    
    if customer['tenure'] < 6:
        factors.append({
            "factor": "Low Tenure",
            "value": customer['tenure'],
            "impact": "High",
            "description": f"Customer tenure of {customer['tenure']:.1f} months is below average"
        })
    
    return factors

def generate_detailed_recommendations(customer, churn_prob, is_anomaly, anomaly_type):
    """Generate detailed recommendations for a customer"""
    recommendations = []
    
    # Churn-based recommendations
    if churn_prob > 0.8:
        recommendations.extend([
            {
                "type": "immediate",
                "action": "Personal Account Manager Assignment",
                "description": "Assign a dedicated account manager for personalized service",
                "priority": "critical",
                "estimated_impact": "high"
            },
            {
                "type": "retention",
                "action": "Special Discount Offer",
                "description": "Offer 25-30% discount for next 6 months",
                "priority": "critical",
                "estimated_impact": "high"
            },
            {
                "type": "engagement",
                "action": "Priority Support Access",
                "description": "Provide VIP support line and faster response times",
                "priority": "high",
                "estimated_impact": "medium"
            }
        ])
    elif churn_prob > 0.5:
        recommendations.extend([
            {
                "type": "retention",
                "action": "Targeted Email Campaign",
                "description": "Send personalized retention emails highlighting service benefits",
                "priority": "medium",
                "estimated_impact": "medium"
            },
            {
                "type": "engagement",
                "action": "Usage Optimization Consultation",
                "description": "Provide consultation to optimize service usage and reduce costs",
                "priority": "medium",
                "estimated_impact": "medium"
            }
        ])
    
    # Anomaly-based recommendations
    if is_anomaly:
        if anomaly_type == 'Sudden Usage Drop':
            recommendations.append({
                "type": "investigation",
                "action": "Usage Pattern Investigation",
                "description": "Contact customer to verify account usage and check for technical issues",
                "priority": "high",
                "estimated_impact": "medium"
            })
        elif anomaly_type == 'Billing Anomaly':
            recommendations.append({
                "type": "billing",
                "action": "Billing Review and Correction",
                "description": "Review billing accuracy and contact customer to resolve discrepancies",
                "priority": "critical",
                "estimated_impact": "high"
            })
        elif anomaly_type == 'Usage Spike':
            recommendations.append({
                "type": "security",
                "action": "Fraud Verification",
                "description": "Verify legitimate usage and check for potential account compromise",
                "priority": "high",
                "estimated_impact": "high"
            })
        elif anomaly_type == 'Service Abuse':
            recommendations.append({
                "type": "policy",
                "action": "Account Review and Limits",
                "description": "Review account for policy violations and implement usage limits",
                "priority": "high",
                "estimated_impact": "medium"
            })
    
    # Contract-based recommendations
    if customer['contract_type'] == 'Month-to-month' and churn_prob > 0.4:
        recommendations.append({
            "type": "contract",
            "action": "Contract Upgrade Incentive",
            "description": "Offer incentives to upgrade to annual contract with discount",
            "priority": "medium",
            "estimated_impact": "high"
        })
    
    return recommendations

def find_similar_cases(customer, sample_data, churn_proba, risk_levels):
    """Find similar customer cases for comparison"""
    similar_cases = []
    
    # Find customers with similar characteristics
    for i, row in sample_data.iterrows():
        if row['customer_id'] == customer['customer_id']:
            continue
            
        # Calculate similarity score based on key features
        similarity_score = 0
        
        # Tenure similarity
        tenure_diff = abs(row['tenure'] - customer['tenure'])
        if tenure_diff < 6:
            similarity_score += 0.3
        
        # Monthly charges similarity
        charges_diff = abs(row['monthly_charges'] - customer['monthly_charges'])
        if charges_diff < 20:
            similarity_score += 0.2
        
        # Contract type match
        if row['contract_type'] == customer['contract_type']:
            similarity_score += 0.2
        
        # Age similarity
        age_diff = abs(row['age'] - customer['age'])
        if age_diff < 10:
            similarity_score += 0.1
        
        # Service usage similarity
        usage_diff = abs(row['data_usage_gb'] - customer['data_usage_gb'])
        if usage_diff < 10:
            similarity_score += 0.2
        
        if similarity_score > 0.6:  # Threshold for similarity
            similar_cases.append({
                "customer_id": row['customer_id'],
                "similarity_score": similarity_score,
                "churn_probability": churn_proba[i],
                "risk_level": risk_levels[i],
                "tenure": row['tenure'],
                "monthly_charges": row['monthly_charges'],
                "contract_type": row['contract_type'],
                "outcome": "churned" if row['churn'] else "retained"
            })
    
    # Sort by similarity score and return top 5
    similar_cases.sort(key=lambda x: x['similarity_score'], reverse=True)
    return similar_cases[:5]

def generate_alert_timeline(alert_id, customer_id):
    """Generate timeline of events for an alert"""
    timeline = []
    
    # Generate sample timeline events
    base_time = datetime.now() - timedelta(days=7)
    
    events = [
        {
            "timestamp": base_time,
            "event": "Customer Profile Created",
            "description": f"Customer {customer_id} account established",
            "type": "info"
        },
        {
            "timestamp": base_time + timedelta(days=2),
            "event": "Usage Pattern Change Detected",
            "description": "Significant change in data usage patterns observed",
            "type": "warning"
        },
        {
            "timestamp": base_time + timedelta(days=4),
            "event": "Churn Risk Increased",
            "description": "Churn probability increased from 45% to 72%",
            "type": "warning"
        },
        {
            "timestamp": base_time + timedelta(days=6),
            "event": "Alert Generated",
            "description": f"High churn risk alert {alert_id} created",
            "type": "alert"
        },
        {
            "timestamp": datetime.now(),
            "event": "Investigation Started",
            "description": "Alert investigation initiated by user",
            "type": "action"
        }
    ]
    
    return events

if __name__ == '__main__':
    print("Starting Flask API server...")
    print("Health check: http://localhost:5000/health")
    print("API endpoints available at: http://localhost:5000/api/")
    app.run(host='0.0.0.0', port=5000, debug=True)