#!/usr/bin/env python3
"""
Test script to verify the Telecom Churn & Anomaly Detection System
"""

import sys
import os
import requests
import time
import json

def test_imports():
    """Test if all required packages are installed"""
    print("🔍 Testing Python package imports...")
    
    required_packages = [
        'pandas', 'numpy', 'sklearn', 'flask', 'flask_cors', 'joblib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sklearn':
                import sklearn
            elif package == 'flask_cors':
                import flask_cors
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All packages imported successfully!")
    return True

def test_ml_models():
    """Test ML model training"""
    print("\n🤖 Testing ML Models...")
    
    try:
        from ml_models import TelecomChurnAnomalyDetector
        
        # Initialize detector
        detector = TelecomChurnAnomalyDetector()
        print("   ✅ Model class initialized")
        
        # Generate small sample data
        print("   📊 Generating sample data...")
        data = detector.generate_synthetic_data(n_samples=100)
        print(f"   ✅ Generated {len(data)} samples")
        
        # Train models
        print("   🧠 Training churn model...")
        detector.train_churn_model(data)
        print("   ✅ Churn model trained")
        
        print("   🔍 Training anomaly model...")
        detector.train_anomaly_model(data)
        print("   ✅ Anomaly model trained")
        
        # Test prediction
        sample = data.head(1)
        churn_prob, risk_level = detector.predict_churn_risk(sample)
        is_anomaly, anomaly_score, anomaly_type = detector.detect_anomalies(sample)
        
        print(f"   ✅ Sample prediction: {risk_level[0]} risk ({churn_prob[0]:.1%})")
        print(f"   ✅ Anomaly detection: {anomaly_type[0]}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ML Model Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_api():
    """Test Flask API endpoints"""
    print("\n🌐 Testing Flask API...")
    
    # Test if server is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is running")
            print(f"   📊 Health check: {response.json()}")
        else:
            print(f"   ❌ Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to Flask server")
        print("   💡 Make sure to run: python flask_api.py")
        return False
    except Exception as e:
        print(f"   ❌ API Error: {str(e)}")
        return False
    
    # Test API endpoints
    endpoints = [
        "/api/customers",
        "/api/analytics", 
        "/api/alerts"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {endpoint} - OK")
                if 'customers' in data:
                    print(f"      📊 Returned {len(data['customers'])} customers")
                elif 'alerts' in data:
                    print(f"      🚨 {len(data['alerts'])} alerts")
            else:
                print(f"   ❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {str(e)}")
    
    return True

def test_prediction_api():
    """Test single customer prediction"""
    print("\n🎯 Testing Customer Prediction API...")
    
    sample_customer = {
        "id": "TEST_001",
        "tenure": 24.0,
        "age": 35,
        "monthlyCharges": 75.50,
        "totalCharges": 1812.0,
        "dataUsageGB": 25.5,
        "callMinutes": 450,
        "smsCount": 120,
        "complaints": 1,
        "serviceCalls": 2,
        "downtimeHours": 0.5,
        "contractType": "One year",
        "paymentMethod": "Credit card",
        "internetService": "Fiber optic"
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/predict",
            json=sample_customer,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Prediction API working")
            print(f"   📊 Churn Probability: {result['churnProbability']:.1%}")
            print(f"   🎯 Risk Level: {result['riskLevel']}")
            print(f"   🔍 Anomaly: {result['anomalyType']}")
            if result['recommendations']:
                print(f"   💡 Recommendations: {len(result['recommendations'])} items")
            return True
        else:
            print(f"   ❌ Prediction failed - Status: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Prediction Error: {str(e)}")
    
    return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 TELECOM SYSTEM TESTING SUITE")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("ML Models", test_ml_models),
        ("Flask API", test_flask_api),
        ("Prediction API", test_prediction_api)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 RUNNING TEST: {test_name}")
        print('='*60)
        
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print("\n⏹️ Test interrupted by user")
            break
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! System is ready.")
        print("🚀 Next steps:")
        print("   1. Keep Flask server running: python flask_api.py")  
        print("   2. Start React frontend: npm start")
        print("   3. Open http://localhost:3000")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("💡 Troubleshooting tips:")
        print("   - Install missing packages with pip install")
        print("   - Make sure Flask server is running")
        print("   - Check for port conflicts")
    
    print("="*60)

if __name__ == "__main__":
    main()