"""
Clean and standardize offense codes in CDCR commitment data.

Strips PC/VC/HS prefixes and parenthetical suffixes from offense codes
to enable matching with selection_criteria.xlsx severity tables.

Usage:
    python update_penal_codes.py                    # Use local files
    python update_penal_codes.py --source github    # Use GitHub URLs
"""

import pandas as pd
import argparse
from pathlib import Path


def clean_offense_code(code):
    """
    Strip PC/VC prefixes and (a)(1) suffixes from offense codes.
    
    Examples:
        "PC187(A)" → "187"
        "VC10851" → "10851"
        "HS11378(B)(1)" → "11378"
    """
    if pd.isna(code):
        return code

    code = str(code).strip().upper()

    # Remove prefixes
    prefixes = ['PC', 'VC', 'HS', 'BP', 'WI', 'CC']
    for prefix in prefixes:
        if code.startswith(prefix):
            code = code[len(prefix):]
            break

    # Remove suffixes (parentheses)
    if '(' in code:
        code = code.split('(')[0]

    return code.strip()


def main():
    parser = argparse.ArgumentParser(description='Clean CDCR offense codes')
    parser.add_argument(
        '--source',
        choices=['local', 'github'],
        default='local',
        help='Data source: local files or GitHub URLs (default: local)'
    )
    parser.add_argument(
        '--data-dir',
        default='../data',
        help='Directory containing local data files (default: ../data)'
    )
    parser.add_argument(
        '--output-dir',
        default='../data',
        help='Directory to save cleaned files (default: ../data)'
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("OFFENSE CODE CLEANING")
    print("="*70)
    
    # Load data
    if args.source == 'github':
        print("\nLoading data from GitHub...")
        current_url = "https://raw.githubusercontent.com/redoio/resentencing_data_initiative/main/data/current_commitments.csv"
        prior_url = "https://raw.githubusercontent.com/redoio/resentencing_data_initiative/main/data/prior_commitments.csv"
        
        current = pd.read_csv(current_url)
        prior = pd.read_csv(prior_url)
        print(f"✓ Loaded {len(current):,} current commitments")
        print(f"✓ Loaded {len(prior):,} prior commitments")
    else:
        print("\nLoading data from local files...")
        data_path = Path(args.data_dir)
        current = pd.read_csv(data_path / "current_commitments.csv")
        prior = pd.read_csv(data_path / "prior_commitments.csv")
        print(f"✓ Loaded {len(current):,} current commitments")
        print(f"✓ Loaded {len(prior):,} prior commitments")
    
    # Clean offense codes
    print("\nCleaning offense codes...")
    current['offense_clean'] = current['offense'].apply(clean_offense_code)
    prior['offense_clean'] = prior['offense'].apply(clean_offense_code)
    
    # Show examples
    print("\nExample transformations:")
    print("-"*60)
    sample = current[['offense', 'offense_clean']].dropna().head(10)
    for idx, row in sample.iterrows():
        if row['offense'] != row['offense_clean']:
            print(f"  {row['offense']:20s} → {row['offense_clean']}")
    
    # Statistics
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Current commitments:")
    print(f"  Original unique codes: {current['offense'].nunique():,}")
    print(f"  Cleaned unique codes:  {current['offense_clean'].nunique():,}")
    
    print(f"\nPrior commitments:")
    print(f"  Original unique codes: {prior['offense'].nunique():,}")
    print(f"  Cleaned unique codes:  {prior['offense_clean'].nunique():,}")
    
    # Save
    print("\nSaving cleaned data...")
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    current.to_csv(output_path / "current_commitments_clean.csv", index=False)
    prior.to_csv(output_path / "prior_commitments_clean.csv", index=False)
    
    print(f"✓ Saved: {output_path / 'current_commitments_clean.csv'}")
    print(f"✓ Saved: {output_path / 'prior_commitments_clean.csv'}")
    print("\n" + "="*70)
    print("✓ COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
