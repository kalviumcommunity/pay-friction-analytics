import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

def detect_exact_duplicates(df):
    """Find rows where all values are identical."""
    exact_dups = df.duplicated().sum()
    dup_rows = df[df.duplicated(keep=False)].sort_values(by=df.columns.tolist())
    
    print("\nEXACT DUPLICATE DETECTION")
    print("="*60)
    print(f"Exact duplicates found: {exact_dups}")
    print(f"Total duplicate rows (including originals): {len(dup_rows)}")
    
    if len(dup_rows) > 0:
        print(f"\nSample duplicate rows:")
        print(dup_rows.head(10).to_string())
    
    return exact_dups, dup_rows

def detect_near_duplicates(df, key_columns):
    """Find rows with same key values but different other fields."""
    duplicate_keys = df[df.duplicated(subset=key_columns, keep=False)]
    
    print("\nNEAR-DUPLICATE DETECTION")
    print("="*60)
    print(f"Records with duplicate keys: {len(duplicate_keys)}")
    
    if len(duplicate_keys) > 0:
        grouped = duplicate_keys.groupby(key_columns)
        print(f"Unique key combinations with duplicates: {len(grouped)}")
        print(f"\nSample groups with duplicate keys:")
        for keys, group in list(grouped)[:3]:
            print(f"\n  Key: {keys}")
            print(f"  Records in group: {len(group)}")
            print(group.to_string())
    
    return duplicate_keys

def remove_exact_duplicates(df, keep='first'):
    """Remove exact duplicates, choosing which record to keep."""
    rows_before = len(df)
    df_dedup = df.drop_duplicates(keep=keep)
    
    rows_after = len(df_dedup)
    rows_removed = rows_before - rows_after
    removal_pct = (rows_removed / rows_before) * 100 if rows_before > 0 else 0
    
    print("\nEXACT DUPLICATE REMOVAL")
    print("="*60)
    print(f"Keep strategy: {keep}")
    print(f"Rows before: {rows_before:,}")
    print(f"Rows after:  {rows_after:,}")
    print(f"Rows removed: {rows_removed:,} ({removal_pct:.2f}%)")
    
    return df_dedup

def remove_near_duplicates(df, key_columns, keep_strategy='most_complete'):
    """Remove near-duplicates by choosing the best record."""
    rows_before = len(df)
    
    if keep_strategy == 'most_complete':
        def keep_most_complete(group):
            null_counts = group.isnull().sum(axis=1)
            best_idx = null_counts.idxmin()
            return group.loc[[best_idx]]
        
        df_dedup = df.groupby(key_columns, group_keys=False).apply(keep_most_complete).reset_index(drop=True)
    elif keep_strategy == 'last':
        df_dedup = df.drop_duplicates(subset=key_columns, keep='last')
    else:
        df_dedup = df.drop_duplicates(subset=key_columns, keep='first')
    
    rows_after = len(df_dedup)
    rows_removed = rows_before - rows_after
    removal_pct = (rows_removed / rows_before) * 100 if rows_before > 0 else 0
    
    print("\nNEAR-DUPLICATE REMOVAL")
    print("="*60)
    print(f"Keep strategy: {keep_strategy}")
    print(f"Key columns: {key_columns}")
    print(f"Rows before: {rows_before:,}")
    print(f"Rows after:  {rows_after:,}")
    print(f"Rows removed: {rows_removed:,} ({removal_pct:.2f}%)")
    
    return df_dedup

def log_removed_duplicates(df_original, df_dedup):
    """Save all removed duplicate rows to audit file for compliance."""
    os.makedirs('output', exist_ok=True)
    
    # Identify removed rows by comparing full row values or indices
    removed_records = df_original[~df_original.index.isin(df_dedup.index)]
    
    print("\nAUDIT LOGGING")
    print("="*60)
    print(f"Total records removed: {len(removed_records)}")
    
    removed_records.to_csv('output/removed_duplicates_audit.csv', index=False)
    print(f"✓ Removed records saved to output/removed_duplicates_audit.csv")
    
    audit_summary = {
        'removal_timestamp': datetime.now().isoformat(),
        'total_removed': int(len(removed_records)),
        'reason': 'Duplicate detection and deduplication',
        'audit_file': 'output/removed_duplicates_audit.csv',
        'audit_note': 'All removed records logged for compliance and recovery if needed'
    }
    
    with open('output/dedup_audit_summary.json', 'w') as f:
        json.dump(audit_summary, f, indent=2, default=str)
    
    print(f"✓ Audit summary saved to output/dedup_audit_summary.json")
    print("="*60)
    
    return removed_records, audit_summary

def compare_before_after(df_original, df_dedup):
    """Log before/after metrics confirming deduplication worked."""
    os.makedirs('output', exist_ok=True)
    rows_before = len(df_original)
    rows_after = len(df_dedup)
    rows_removed = rows_before - rows_after
    removal_pct = round((rows_removed / rows_before) * 100, 2) if rows_before > 0 else 0.0
    
    comparison = {
        'rows_before': rows_before,
        'rows_after': rows_after,
        'rows_removed': rows_removed,
        'removal_percentage': removal_pct,
        'columns': len(df_original.columns),
        'nulls_before': int(df_original.isnull().sum().sum()),
        'nulls_after': int(df_dedup.isnull().sum().sum()),
        'timestamp': datetime.now().isoformat()
    }
    
    print("\n" + "="*70)
    print("DEDUPLICATION FINAL SUMMARY")
    print("="*70)
    print(f"Rows before: {comparison['rows_before']:,}")
    print(f"Rows after:  {comparison['rows_after']:,}")
    print(f"Removed:     {comparison['rows_removed']:,} ({comparison['removal_percentage']}%)")
    print(f"\nNulls before: {comparison['nulls_before']:,}")
    print(f"Nulls after:  {comparison['nulls_after']:,}")
    print(f"Null change:  {comparison['nulls_before'] - comparison['nulls_after']:,}")
    print("="*70)
    
    with open('output/dedup_summary.json', 'w') as f:
        json.dump(comparison, f, indent=2)
    
    return comparison

if __name__ == "__main__":
    raw_path = 'data/raw/data_with_dupes.csv'
    df_original = pd.read_csv(raw_path)
    df = df_original.copy()
    
    print("\n" + "="*70)
    print("STARTING DEDUPLICATION WORKFLOW")
    print("="*70)
    print(f"Initial record count: {len(df):,}")
    
    # Step 1: Detect exact duplicates
    print("\n[Step 1/4] Detecting exact duplicates...")
    exact_count, exact_rows = detect_exact_duplicates(df)
    
    # Step 2: Detect near-duplicates
    print("\n[Step 2/4] Detecting near-duplicates by key...")
    near_dups = detect_near_duplicates(df, key_columns=['customer_id', 'transaction_date'])
    
    # Step 3: Remove exact duplicates
    print("\n[Step 3/4] Removing exact duplicates (keeping first)...")
    df = remove_exact_duplicates(df, keep='first')
    
    # Step 4: Remove near-duplicates
    print("\n[Step 4/4] Removing near-duplicates (keeping most complete)...")
    df = remove_near_duplicates(
        df,
        key_columns=['customer_id', 'transaction_date'],
        keep_strategy='most_complete'
    )
    
    # Log removals comparing un-deduplicated original vs final
    print("\n[Audit] Logging removed records for compliance...")
    log_removed_duplicates(df_original, df)
    
    # Compare metrics
    compare_before_after(df_original, df)
    
    # Save deduplicated data
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv('data/processed/deduplicated_data.csv', index=False)
    print("\n✓ Deduplicated data saved to data/processed/deduplicated_data.csv")