import pandas as pd
import numpy as np
import os

# Task 1: Strip Whitespace Consistently
def strip_all_strings(df):
    """Strip leading and trailing whitespace from all string columns."""
    df_cleaned = df.copy()
    string_cols = df_cleaned.select_dtypes(include=['object']).columns
    
    print("\n--- TASK 1: WHITESPACE STRIPPING ---")
    for col in string_cols:
        before_uniques = df_cleaned[col].nunique()
        df_cleaned[col] = df_cleaned[col].astype(str).str.strip()
        after_uniques = df_cleaned[col].nunique()
        print(f"Column '{col}': {before_uniques} → {after_uniques} unique values")
    
    return df_cleaned

# Task 2: Normalize Casing to Consistent Standard
def normalize_casing(df, columns_to_lower):
    """Normalize casing for specified columns to lowercase."""
    df_cleaned = df.copy()
    print("\n--- TASK 2: CASING NORMALIZATION ---")
    for col in columns_to_lower:
        if col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].str.lower()
            print(f"Normalized '{col}' to lowercase.")
    
    return df_cleaned

# Task 3: Remove Special Characters Using Regex
def remove_special_characters(df, columns):
    """
    Remove non-alphanumeric characters (preserving spaces).
    Regex pattern [^a-zA-Z0-9 ] matches any character that is NOT a letter, number, or space.
    """
    df_cleaned = df.copy()
    print("\n--- TASK 3: SPECIAL CHARACTER REMOVAL ---")
    for col in columns:
        if col in df_cleaned.columns:
            # Replaces non-alphanumeric characters with empty string
            df_cleaned[col] = df_cleaned[col].str.replace(r'[^a-zA-Z0-9 ]', '', regex=True)
            print(f"Removed special characters from '{col}'.")
    
    return df_cleaned

# Task 4: Standardize Categorical Labels Using Mapping Dictionary
def standardize_categories(df, column, mapping_dict):
    """Map spelling variations and abbreviations into canonical forms."""
    df_cleaned = df.copy()
    print(f"\n--- TASK 4: CATEGORICAL MAPPING FOR '{column}' ---")
    print("Value counts before mapping:")
    print(df_cleaned[column].value_counts())
    
    df_cleaned[column] = df_cleaned[column].map(mapping_dict).fillna(df_cleaned[column])
    
    print("\nValue counts after mapping:")
    print(df_cleaned[column].value_counts())
    
    return df_cleaned

# Task 5: Build Reusable String Cleaning Function
def clean_text_column(series, lowercase=True, strip=True, 
                     remove_special=False, mapping=None):
    """Reusable text cleaning function for any string column."""
    result = series.copy()
    
    # Handle nulls safely
    if result.isna().any():
        print(f"Warning: {result.isna().sum()} null values detected in column.")
    
    if strip:
        result = result.astype(str).str.strip()
    
    if lowercase:
        result = result.str.lower()
    
    if remove_special:
        result = result.str.replace(r'[^a-zA-Z0-9 ]', '', regex=True)
    
    if mapping:
        result = result.map(mapping).fillna(result)
    
    return result

if __name__ == "__main__":
    # Load messy raw dataset
    raw_path = 'data/raw/messy_text_data.csv'
    df = pd.read_csv(raw_path)
    
    print("==========================================")
    print("ORIGINAL MESSY DATASET")
    print("==========================================")
    print(df)
    
    # Apply individual task steps
    df_clean = strip_all_strings(df)
    df_clean = normalize_casing(df_clean, ['product_category', 'customer_name'])
    df_clean = remove_special_characters(df_clean, ['city', 'customer_name'])
    
    # Define Segment Mapping Dictionary
    segment_map = {
        'b2b': 'B2B',
        'b 2 b': 'B2B',
        'business-to-business': 'B2B',
        'sme': 'SMB',
        'small medium enterprise': 'SMB',
        'enterprise': 'Enterprise'
    }
    
    df_clean = standardize_categories(df_clean, 'customer_segment', segment_map)
    
    # Demonstrate Reusable Function
    print("\n--- TASK 5: REUSABLE FUNCTION VERIFICATION ---")
    df['product_category_cleaned'] = clean_text_column(
        df['product_category'], 
        lowercase=True, 
        strip=True, 
        remove_special=True
    )
    
    # Edge-Case Testing
    print("\n--- TESTING EDGE CASES ---")
    test_cases = ['  Product A  ', 'PRODUCT B', 'Product_C', None, '']
    test_series = pd.Series(test_cases)
    cleaned_test = clean_text_column(test_series, lowercase=True, strip=True, remove_special=True)
    print("Test Input:", test_cases)
    print("Cleaned Result:")
    print(cleaned_test)
    
    # Export cleaned data
    os.makedirs('data/processed', exist_ok=True)
    df_clean.to_csv('data/processed/cleaned_text_data.csv', index=False)
    print("\n✓ Cleaned dataset saved to 'data/processed/cleaned_text_data.csv'")