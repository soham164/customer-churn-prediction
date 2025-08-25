import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import GridSearchCV
import joblib
import warnings
warnings.filterwarnings('ignore')

class TelecomChurnAnomalyDetector:
    def __init__(self):
        self.churn_model = None
        self.anomaly_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        
    def generate_synthetic_data(self, n_samples=5000):
        """Generate realistic telecom customer data with churn and anomaly patterns"""
        np.random.seed(42)
        
        # Customer demographics
        customer_ids = [f"CUST_{i:06d}" for i in range(n_samples)]
        tenure = np.random.exponential(24, n_samples)  # Average 24 months tenure
        age = np.random.normal(45, 15, n_samples).astype(int)
        age = np.clip(age, 18, 80)
        
        # Service usage patterns
        monthly_charges = np.random.gamma(2, 30, n_samples)  # Average $60
        total_charges = monthly_charges * tenure + np.random.normal(0, 100, n_samples)
        
        # Usage metrics
        data_usage_gb = np.random.gamma(2, 15, n_samples)  # Average 30GB
        call_minutes = np.random.gamma(1.5, 200, n_samples)  # Average 300 minutes
        sms_count = np.random.poisson(50, n_samples)
        
        # Service issues
        complaints = np.random.poisson(0.5, n_samples)
        service_calls = np.random.poisson(1, n_samples)
        downtime_hours = np.random.gamma(1, 2, n_samples)
        
        # Contract and service details
        contract_type = np.random.choice(['Month-to-month', 'One year', 'Two year'], 
                                       n_samples, p=[0.5, 0.3, 0.2])
        payment_method = np.random.choice(['Electronic check', 'Mailed check', 'Bank transfer', 'Credit card'], 
                                        n_samples, p=[0.4, 0.2, 0.2, 0.2])
        
        # Internet service
        internet_service = np.random.choice(['DSL', 'Fiber optic', 'No'], 
                                          n_samples, p=[0.4, 0.5, 0.1])
        
        # Create DataFrame
        data = pd.DataFrame({
            'customer_id': customer_ids,
            'tenure': tenure,
            'age': age,
            'monthly_charges': monthly_charges,
            'total_charges': total_charges,
            'data_usage_gb': data_usage_gb,
            'call_minutes': call_minutes,
            'sms_count': sms_count,
            'complaints': complaints,
            'service_calls': service_calls,
            'downtime_hours': downtime_hours,
            'contract_type': contract_type,
            'payment_method': payment_method,
            'internet_service': internet_service
        })
        
        # Generate churn based on realistic patterns
        churn_prob = (
            0.1 +  # Base churn rate
            0.3 * (data['tenure'] < 6) +  # New customers more likely to churn
            0.2 * (data['monthly_charges'] > 80) +  # High charges increase churn
            0.15 * (data['complaints'] > 2) +  # Complaints increase churn
            0.1 * (data['contract_type'] == 'Month-to-month') +  # Month-to-month more likely
            0.05 * (data['service_calls'] > 3)  # Service issues
        )
        churn_prob = np.clip(churn_prob, 0, 0.8)
        data['churn'] = np.random.binomial(1, churn_prob)
        
        # Generate anomalies (suspicious patterns)
        anomaly_patterns = np.zeros(n_samples)
        
        # Pattern 1: Sudden usage drop (potential account sharing or fraud)
        sudden_drop_mask = np.random.choice([True, False], n_samples, p=[0.05, 0.95])
        data.loc[sudden_drop_mask, 'data_usage_gb'] *= 0.1
        data.loc[sudden_drop_mask, 'call_minutes'] *= 0.2
        anomaly_patterns[sudden_drop_mask] = 1
        
        # Pattern 2: Billing anomalies (charges don't match usage)
        billing_anomaly_mask = np.random.choice([True, False], n_samples, p=[0.03, 0.97])
        data.loc[billing_anomaly_mask, 'monthly_charges'] *= 2.5  # Unusually high charges
        anomaly_patterns[billing_anomaly_mask] = 1
        
        # Pattern 3: Unusual usage spikes (potential fraud)
        usage_spike_mask = np.random.choice([True, False], n_samples, p=[0.04, 0.96])
        data.loc[usage_spike_mask, 'data_usage_gb'] *= 10
        data.loc[usage_spike_mask, 'call_minutes'] *= 5
        anomaly_patterns[usage_spike_mask] = 1
        
        # Pattern 4: Service abuse (excessive complaints/calls)
        abuse_mask = np.random.choice([True, False], n_samples, p=[0.02, 0.98])
        data.loc[abuse_mask, 'complaints'] += np.random.poisson(10, abuse_mask.sum())
        data.loc[abuse_mask, 'service_calls'] += np.random.poisson(15, abuse_mask.sum())
        anomaly_patterns[abuse_mask] = 1
        
        data['is_anomaly'] = anomaly_patterns
        
        return data
    
    def preprocess_data(self, data, fit=True):
        """Preprocess data for training"""
        df = data.copy()
        
        # Handle categorical variables
        categorical_cols = ['contract_type', 'payment_method', 'internet_service']
        
        for col in categorical_cols:
            if fit:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col])
            else:
                df[col] = self.label_encoders[col].transform(df[col])
        
        # Feature engineering
        df['charges_per_gb'] = df['monthly_charges'] / (df['data_usage_gb'] + 1)
        df['complaints_per_tenure'] = df['complaints'] / (df['tenure'] + 1)
        df['usage_efficiency'] = (df['data_usage_gb'] + df['call_minutes']/60) / df['monthly_charges']
        df['service_issues_ratio'] = df['service_calls'] / (df['tenure'] + 1)
        
        # Select features for modeling
        feature_cols = [
            'tenure', 'age', 'monthly_charges', 'total_charges', 'data_usage_gb',
            'call_minutes', 'sms_count', 'complaints', 'service_calls', 
            'downtime_hours', 'contract_type', 'payment_method', 'internet_service',
            'charges_per_gb', 'complaints_per_tenure', 'usage_efficiency', 'service_issues_ratio'
        ]
        
        X = df[feature_cols]
        
        if fit:
            self.feature_names = feature_cols
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        return X_scaled, df
    
    def train_churn_model(self, data):
        """Train churn prediction model"""
        print("Training churn prediction model...")
        
        X_scaled, df = self.preprocess_data(data, fit=True)
        y_churn = df['churn']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_churn, test_size=0.2, random_state=42, stratify=y_churn
        )
        
        # Use a simpler RandomForestClassifier to avoid version compatibility issues
        self.churn_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        self.churn_model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.churn_model.predict(X_test)
        y_pred_proba = self.churn_model.predict_proba(X_test)[:, 1]
        
        print("Churn Model Performance:")
        print(f"ROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
    def train_anomaly_model(self, data):
        """Train anomaly detection model using a simple statistical approach"""
        print("\nTraining anomaly detection model...")
        
        X_scaled, df = self.preprocess_data(data, fit=False)
        
        # Use a simple statistical approach instead of IsolationForest
        # Calculate percentiles for each feature
        self.anomaly_model = {
            'feature_stats': {},
            'thresholds': {}
        }
        
        # Calculate statistics for each feature
        for i, feature_name in enumerate(self.feature_names):
            feature_values = X_scaled[:, i]
            self.anomaly_model['feature_stats'][feature_name] = {
                'mean': np.mean(feature_values),
                'std': np.std(feature_values),
                'q1': np.percentile(feature_values, 25),
                'q3': np.percentile(feature_values, 75)
            }
        
        # Simple anomaly detection based on statistical outliers
        anomaly_pred = self._detect_statistical_anomalies(X_scaled)
        y_anomaly = df['is_anomaly']
        
        print("Anomaly Detection Performance:")
        print(classification_report(y_anomaly, anomaly_pred))
        
    def predict_churn_risk(self, customer_data):
        """Predict churn probability for customers"""
        X_scaled, _ = self.preprocess_data(customer_data, fit=False)
        
        churn_proba = self.churn_model.predict_proba(X_scaled)[:, 1]
        risk_level = np.where(churn_proba > 0.7, 'High', 
                             np.where(churn_proba > 0.4, 'Medium', 'Low'))
        
        return churn_proba, risk_level
    
    def _detect_statistical_anomalies(self, X_scaled):
        """Simple statistical anomaly detection"""
        anomalies = np.zeros(X_scaled.shape[0], dtype=bool)
        
        for i in range(X_scaled.shape[0]):
            anomaly_score = 0
            for j, feature_name in enumerate(self.feature_names):
                stats = self.anomaly_model['feature_stats'][feature_name]
                value = X_scaled[i, j]
                
                # Check if value is outside 2 standard deviations
                if abs(value - stats['mean']) > 2 * stats['std']:
                    anomaly_score += 1
                
                # Check if value is outside IQR * 1.5
                iqr = stats['q3'] - stats['q1']
                if value < (stats['q1'] - 1.5 * iqr) or value > (stats['q3'] + 1.5 * iqr):
                    anomaly_score += 1
            
            # Consider anomaly if multiple features are outliers
            if anomaly_score >= 3:
                anomalies[i] = True
        
        return anomalies.astype(int)
    
    def detect_anomalies(self, customer_data):
        """Detect anomalous usage patterns"""
        X_scaled, _ = self.preprocess_data(customer_data, fit=False)
        
        is_anomaly = self._detect_statistical_anomalies(X_scaled)
        is_anomaly = is_anomaly.astype(bool)
        
        # Simple anomaly scores (distance from mean)
        anomaly_scores = []
        for i in range(X_scaled.shape[0]):
            score = 0
            for j, feature_name in enumerate(self.feature_names):
                stats = self.anomaly_model['feature_stats'][feature_name]
                value = X_scaled[i, j]
                score += abs(value - stats['mean']) / (stats['std'] + 1e-6)
            anomaly_scores.append(-score / len(self.feature_names))  # Negative for consistency
        
        anomaly_scores = np.array(anomaly_scores)
        
        # Classify anomaly types based on feature patterns
        anomaly_types = []
        for i, row in customer_data.iterrows():
            if is_anomaly[i]:
                if row['data_usage_gb'] < 5 and row['call_minutes'] < 100:
                    anomaly_types.append('Sudden Usage Drop')
                elif row['monthly_charges'] > row['data_usage_gb'] * 10:
                    anomaly_types.append('Billing Anomaly')
                elif row['data_usage_gb'] > 100 or row['call_minutes'] > 2000:
                    anomaly_types.append('Usage Spike')
                elif row['complaints'] > 5 or row['service_calls'] > 8:
                    anomaly_types.append('Service Abuse')
                else:
                    anomaly_types.append('Other Anomaly')
            else:
                anomaly_types.append('Normal')
        
        return is_anomaly, anomaly_scores, anomaly_types
    
    def get_feature_importance(self):
        """Get feature importance for interpretability"""
        if self.churn_model is None:
            return None
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.churn_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def save_models(self, filepath_prefix='telecom_models'):
        """Save trained models"""
        joblib.dump(self.churn_model, f'{filepath_prefix}_churn.joblib')
        joblib.dump(self.anomaly_model, f'{filepath_prefix}_anomaly.joblib')
        joblib.dump(self.scaler, f'{filepath_prefix}_scaler.joblib')
        joblib.dump(self.label_encoders, f'{filepath_prefix}_encoders.joblib')
        joblib.dump(self.feature_names, f'{filepath_prefix}_features.joblib')
        print(f"Models saved with prefix: {filepath_prefix}")
    
    def load_models(self, filepath_prefix='telecom_models'):
        """Load trained models"""
        self.churn_model = joblib.load(f'{filepath_prefix}_churn.joblib')
        self.anomaly_model = joblib.load(f'{filepath_prefix}_anomaly.joblib')
        self.scaler = joblib.load(f'{filepath_prefix}_scaler.joblib')
        self.label_encoders = joblib.load(f'{filepath_prefix}_encoders.joblib')
        self.feature_names = joblib.load(f'{filepath_prefix}_features.joblib')
        print(f"Models loaded from prefix: {filepath_prefix}")

# Training script
if __name__ == "__main__":
    # Initialize detector
    detector = TelecomChurnAnomalyDetector()
    
    # Generate training data
    print("Generating synthetic telecom data...")
    training_data = detector.generate_synthetic_data(n_samples=10000)
    
    # Train models
    detector.train_churn_model(training_data)
    detector.train_anomaly_model(training_data)
    
    # Save models
    detector.save_models()
    
    # Show feature importance
    print("\nTop 10 Most Important Features for Churn Prediction:")
    feature_importance = detector.get_feature_importance()
    print(feature_importance.head(10))
    
    # Test with sample data
    print("\nTesting with sample customers...")
    sample_data = detector.generate_synthetic_data(n_samples=5)
    
    # Predict churn
    churn_proba, risk_levels = detector.predict_churn_risk(sample_data)
    
    # Detect anomalies
    is_anomaly, anomaly_scores, anomaly_types = detector.detect_anomalies(sample_data)
    
    # Display results
    results_df = pd.DataFrame({
        'customer_id': sample_data['customer_id'],
        'churn_probability': churn_proba,
        'risk_level': risk_levels,
        'is_anomaly': is_anomaly,
        'anomaly_type': anomaly_types,
        'anomaly_score': anomaly_scores
    })
    
    print("\nSample Predictions:")
    print(results_df)