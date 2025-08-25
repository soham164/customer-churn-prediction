import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

class DatasetLoader:
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.column_mapping = {}
        
    def analyze_dataset(self, filepath):
        """Analyze the structure of your dataset"""
        print("🔍 ANALYZING YOUR DATASET")
        print("=" * 50)
        
        try:
            # Try different file formats
            if filepath.endswith('.csv'):
                df = pd.read_csv("C:/Users/soham/customer_churn/backend/churn.csv")
            elif filepath.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            elif filepath.endswith('.json'):
                df = pd.read_json(filepath)
            else:
                # Try CSV as default
                df = pd.read_csv(filepath)
            
            print(f"✅ Dataset loaded successfully!")
            print(f"📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns")
            
            print(f"\n📋 Column Names:")
            for i, col in enumerate(df.columns, 1):
                print(f"   {i:2d}. {col}")
            
            print(f"\n📈 Data Types:")
            print(df.dtypes.to_string())
            
            print(f"\n📊 Sample Data (first 5 rows):")
            print(df.head().to_string())
            
            print(f"\n🔍 Missing Values:")
            missing = df.isnull().sum()
            missing_percent = (missing / len(df)) * 100
            missing_info = pd.DataFrame({
                'Missing Count': missing,
                'Percentage': missing_percent.round(2)
            })
            print(missing_info[missing_info['Missing Count'] > 0].to_string())
            
            print(f"\n📊 Numerical Columns Summary:")
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            if len(numerical_cols) > 0:
                print(df[numerical_cols].describe().to_string())
            
            print(f"\n📋 Categorical Columns:")
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                unique_values = df[col].nunique()
                print(f"   {col}: {unique_values} unique values")
                if unique_values <= 10:
                    print(f"      Values: {list(df[col].unique())}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading dataset: {str(e)}")
            print("💡 Supported formats: CSV, Excel (.xlsx, .xls), JSON")
            return None
    
    def suggest_column_mapping(self, df):
        """Suggest how to map your columns to our model features"""
        print(f"\n🎯 COLUMN MAPPING SUGGESTIONS")
        print("=" * 50)
        print("Please map your columns to our standard features:")
        print("(Enter the column name or number, or 'skip' if not available)")
        
        # Define required features and their descriptions
        required_features = {
            'customer_id': 'Customer ID or identifier',
            'tenure': 'How long customer has been with company (months)',
            'age': 'Customer age',
            'monthly_charges': 'Monthly bill amount',
            'total_charges': 'Total amount charged to customer',
            'churn': 'Target variable: Did customer churn? (1/0, Yes/No, True/False)',
        }
        
        optional_features = {
            'data_usage_gb': 'Monthly data usage in GB',
            'call_minutes': 'Monthly call minutes',
            'sms_count': 'Monthly SMS count',
            'complaints': 'Number of complaints',
            'service_calls': 'Number of service calls',
            'downtime_hours': 'Hours of service downtime',
            'contract_type': 'Contract type (monthly, yearly, etc.)',
            'payment_method': 'Payment method',
            'internet_service': 'Internet service type'
        }
        
        column_mapping = {}
        
        print(f"\n📊 Your columns:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        print(f"\n🎯 REQUIRED FEATURES:")
        for feature, description in required_features.items():
            while True:
                user_input = input(f"\n{feature} ({description}): ").strip()
                
                if user_input.lower() == 'skip':
                    print(f"   ⚠️  Skipping {feature}")
                    break
                elif user_input.isdigit():
                    col_idx = int(user_input) - 1
                    if 0 <= col_idx < len(df.columns):
                        column_mapping[feature] = df.columns[col_idx]
                        print(f"   ✅ Mapped to: {df.columns[col_idx]}")
                        break
                    else:
                        print(f"   ❌ Invalid number. Use 1-{len(df.columns)}")
                elif user_input in df.columns:
                    column_mapping[feature] = user_input
                    print(f"   ✅ Mapped to: {user_input}")
                    break
                else:
                    print(f"   ❌ Column '{user_input}' not found")
        
        print(f"\n🔧 OPTIONAL FEATURES (press Enter to skip):")
        for feature, description in optional_features.items():
            while True:
                user_input = input(f"\n{feature} ({description}): ").strip()
                
                if user_input == '' or user_input.lower() == 'skip':
                    break
                elif user_input.isdigit():
                    col_idx = int(user_input) - 1
                    if 0 <= col_idx < len(df.columns):
                        column_mapping[feature] = df.columns[col_idx]
                        print(f"   ✅ Mapped to: {df.columns[col_idx]}")
                        break
                    else:
                        print(f"   ❌ Invalid number. Use 1-{len(df.columns)}")
                elif user_input in df.columns:
                    column_mapping[feature] = user_input
                    print(f"   ✅ Mapped to: {user_input}")
                    break
                else:
                    print(f"   ❌ Column '{user_input}' not found")
        
        return column_mapping
    
    def auto_detect_columns(self, df):
        """Automatically detect column mappings based on common patterns"""
        print(f"\n🤖 AUTO-DETECTING COLUMN MAPPINGS")
        print("=" * 50)
        
        auto_mapping = {}
        df_columns_lower = [col.lower() for col in df.columns]
        
        # Common patterns for different features
        patterns = {
            'customer_id': ['customer_id', 'customerid', 'cust_id', 'id', 'customer'],
            'tenure': ['tenure', 'months', 'subscription_length', 'contract_length'],
            'age': ['age', 'customer_age'],
            'monthly_charges': ['monthly_charges', 'monthlycharges', 'monthly_fee', 'monthly_bill', 'charges'],
            'total_charges': ['total_charges', 'totalcharges', 'total_amount', 'total_bill'],
            'churn': ['churn', 'churned', 'left', 'cancelled', 'attrition'],
            'data_usage_gb': ['data_usage', 'data_gb', 'usage_gb', 'monthly_gb'],
            'call_minutes': ['call_minutes', 'minutes', 'voice_minutes', 'calls'],
            'sms_count': ['sms', 'messages', 'text_messages', 'sms_count'],
            'complaints': ['complaints', 'complaint', 'issues'],
            'service_calls': ['service_calls', 'support_calls', 'calls_to_support'],
            'contract_type': ['contract', 'contract_type', 'plan', 'subscription_type'],
            'payment_method': ['payment_method', 'payment', 'pay_method'],
            'internet_service': ['internet_service', 'internet', 'service_type']
        }
        
        for feature, possible_names in patterns.items():
            for pattern in possible_names:
                if pattern in df_columns_lower:
                    actual_col = df.columns[df_columns_lower.index(pattern)]
                    auto_mapping[feature] = actual_col
                    print(f"   ✅ {feature} -> {actual_col}")
                    break
        
        if not auto_mapping:
            print("   ⚠️  No automatic mappings detected")
            print("   💡 You may need to map columns manually")
        
        return auto_mapping
    
    def transform_dataset(self, df, column_mapping):
        """Transform your dataset to match our model format"""
        print(f"\n🔄 TRANSFORMING DATASET")
        print("=" * 50)
        
        try:
            transformed_df = pd.DataFrame()
            
            # Map columns
            for our_feature, your_column in column_mapping.items():
                if your_column in df.columns:
                    transformed_df[our_feature] = df[your_column].copy()
                    print(f"   ✅ Mapped {your_column} -> {our_feature}")
            
            # Handle missing required columns by filling with defaults
            required_columns = ['customer_id', 'tenure', 'monthly_charges', 'churn']
            for col in required_columns:
                if col not in transformed_df.columns:
                    if col == 'customer_id':
                        transformed_df[col] = [f"CUST_{i:06d}" for i in range(len(df))]
                    elif col == 'tenure':
                        transformed_df[col] = 12  # Default 12 months
                    elif col == 'monthly_charges':
                        transformed_df[col] = 50.0  # Default $50
                    elif col == 'churn':
                        print(f"   ⚠️  WARNING: No churn column found! Creating dummy values.")
                        transformed_df[col] = 0
                    print(f"   🔧 Added default values for {col}")
            
            # Fill missing optional columns with defaults
            default_values = {
                'age': 35,
                'total_charges': lambda x: x['monthly_charges'] * x['tenure'] if 'monthly_charges' in x and 'tenure' in x else 600,
                'data_usage_gb': 25.0,
                'call_minutes': 300,
                'sms_count': 50,
                'complaints': 0,
                'service_calls': 1,
                'downtime_hours': 0.5,
                'contract_type': 'Month-to-month',
                'payment_method': 'Electronic check',
                'internet_service': 'DSL'
            }
            
            for col, default_val in default_values.items():
                if col not in transformed_df.columns:
                    if callable(default_val):
                        transformed_df[col] = default_val(transformed_df)
                    else:
                        transformed_df[col] = default_val
            
            # Clean and validate data
            print(f"\n🧹 CLEANING DATA")
            
            # Handle missing values
            numeric_columns = transformed_df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if transformed_df[col].isnull().any():
                    median_val = transformed_df[col].median()
                    transformed_df[col].fillna(median_val, inplace=True)
                    print(f"   🔧 Filled missing {col} with median: {median_val}")
            
            # Handle categorical columns
            categorical_columns = transformed_df.select_dtypes(include=['object']).columns
            for col in categorical_columns:
                if col != 'customer_id' and transformed_df[col].isnull().any():
                    mode_val = transformed_df[col].mode()[0] if len(transformed_df[col].mode()) > 0 else 'Unknown'
                    transformed_df[col].fillna(mode_val, inplace=True)
                    print(f"   🔧 Filled missing {col} with mode: {mode_val}")
            
            # Convert churn to binary if needed
            if 'churn' in transformed_df.columns:
                unique_churn_values = transformed_df['churn'].unique()
                print(f"   🎯 Churn values found: {unique_churn_values}")
                
                if transformed_df['churn'].dtype == 'object':
                    # Convert text values to binary
                    churn_mapping = {
                        'yes': 1, 'no': 0,
                        'true': 1, 'false': 0,
                        '1': 1, '0': 0,
                        1: 1, 0: 0
                    }
                    
                    transformed_df['churn'] = transformed_df['churn'].str.lower().map(
                        lambda x: churn_mapping.get(x, x)
                    )
                
                # Ensure binary values
                transformed_df['churn'] = pd.to_numeric(transformed_df['churn'], errors='coerce')
                transformed_df['churn'].fillna(0, inplace=True)
                transformed_df['churn'] = transformed_df['churn'].astype(int)
            
            print(f"\n✅ Dataset transformation completed!")
            print(f"📊 Final shape: {transformed_df.shape}")
            print(f"🎯 Churn rate: {transformed_df['churn'].mean():.2%}")
            
            return transformed_df
            
        except Exception as e:
            print(f"❌ Error transforming dataset: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_mapping_config(self, column_mapping, filepath="column_mapping.json"):
        """Save column mapping for future use"""
        import json
        try:
            with open(filepath, 'w') as f:
                json.dump(column_mapping, f, indent=2)
            print(f"💾 Column mapping saved to {filepath}")
        except Exception as e:
            print(f"❌ Error saving mapping: {str(e)}")
    
    def load_mapping_config(self, filepath="column_mapping.json"):
        """Load saved column mapping"""
        import json
        try:
            with open(filepath, 'r') as f:
                column_mapping = json.load(f)
            print(f"📂 Column mapping loaded from {filepath}")
            return column_mapping
        except Exception as e:
            print(f"⚠️  Could not load mapping file: {str(e)}")
            return {}

def main():
    """Interactive dataset integration"""
    print("=" * 60)
    print("📊 DATASET INTEGRATION TOOL")
    print("=" * 60)
    
    loader = DatasetLoader()
    
    # Get dataset path
    dataset_path = input("📂 Enter path to your dataset file: ").strip()
    
    if not dataset_path:
        print("❌ No dataset path provided")
        return
    
    # Analyze dataset
    df = loader.analyze_dataset(dataset_path)
    
    if df is None:
        return
    
    # Ask user for mapping preference
    print(f"\n🔧 COLUMN MAPPING OPTIONS:")
    print("1. Auto-detect columns (recommended)")
    print("2. Manual mapping")
    print("3. Load saved mapping")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "3":
        column_mapping = loader.load_mapping_config()
        if not column_mapping:
            print("Falling back to auto-detection...")
            column_mapping = loader.auto_detect_columns(df)
    elif choice == "2":
        column_mapping = loader.suggest_column_mapping(df)
    else:
        column_mapping = loader.auto_detect_columns(df)
    
    if column_mapping:
        # Transform dataset
        transformed_df = loader.transform_dataset(df, column_mapping)
        
        if transformed_df is not None:
            # Save transformed dataset
            output_path = "transformed_dataset.csv"
            transformed_df.to_csv(output_path, index=False)
            print(f"💾 Transformed dataset saved to: {output_path}")
            
            # Save mapping config
            loader.save_mapping_config(column_mapping)
            
            print(f"\n🎉 SUCCESS! Your dataset is ready for the ML models.")
            print(f"📊 Next steps:")
            print(f"   1. Use transformed_dataset.csv with the ML models")
            print(f"   2. Run: python ml_models.py --dataset transformed_dataset.csv")
    else:
        print("❌ No column mapping created. Cannot proceed.")

if __name__ == "__main__":
    main()