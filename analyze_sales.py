#!/usr/bin/env python3
"""
Script to analyze sales data grouped by shop and product code.
Groups sales by shop, then by product code, and sums quantities sold.
"""

import csv
import sys
import os
from collections import defaultdict

# List of allowed branches/shops (case-insensitive matching)
ALLOWED_BRANCHES = [
    'AWAISIA',
    'BAHRIA TOWN',
    'IQBAL TOWN',
    'JOHAR TOWN PHARMACY'
]


def parse_quantity(quantity_str):
    """Parse quantity string, handling whitespace and commas."""
    if not quantity_str or quantity_str.strip() == '':
        return 0
    # Remove whitespace and commas, convert to int
    cleaned = quantity_str.strip().replace(',', '')
    try:
        return int(cleaned)
    except ValueError:
        return 0


def is_summary_row(row):
    """Check if a row is a summary/total row that should be skipped."""
    if not row or len(row) < 1:
        return True
    shop = row[0].strip() if row[0] else ''
    # Skip rows that are totals or have empty shop names
    return (shop == '' or 
            'Total' in shop or 
            'Branch Total' in shop or 
            'Grand Total' in shop or
            shop.endswith('Branch Total Sale Value') or
            shop.endswith('Total Branch Sale'))


def is_allowed_branch(shop_name, allowed_branches):
    """
    Check if shop name matches any allowed branch (case-insensitive).
    """
    if not shop_name:
        return False
    shop_lower = shop_name.strip().lower()
    allowed_lower = [branch.lower() for branch in allowed_branches]
    return shop_lower in allowed_lower


def analyze_sales(csv_file_path, allowed_branches):
    """
    Analyze sales data from CSV file.
    Groups by shop and product code, then sums quantities.
    Only processes shops in the allowed_branches list.
    """
    # Dictionary structure: {shop: {product_code: {'name': product_name, 'quantity': total_qty}}}
    sales_data = defaultdict(lambda: defaultdict(lambda: {'name': '', 'quantity': 0}))
    
    # Also track product totals across all branches
    # Structure: {product_code: {'name': product_name, 'quantity': total_qty}}
    product_totals = defaultdict(lambda: {'name': '', 'quantity': 0})
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            _ = next(reader)  # Skip header row
            
            for row in reader:
                # Skip empty rows and summary rows
                if not row or is_summary_row(row):
                    continue
                
                # Extract relevant fields
                if len(row) < 7:
                    continue
                    
                shop = row[0].strip()
                product_code = row[3].strip() if len(row) > 3 else ''
                product_name = row[4].strip() if len(row) > 4 else ''
                quantity_str = row[6].strip() if len(row) > 6 else '0'
                
                # Skip if essential fields are missing
                if not shop or not product_code:
                    continue
                
                # Filter by allowed branches (case-insensitive)
                if not is_allowed_branch(shop, allowed_branches):
                    continue
                
                # Parse quantity
                quantity = parse_quantity(quantity_str)
                
                # Store product name (use first occurrence if multiple)
                if not sales_data[shop][product_code]['name']:
                    sales_data[shop][product_code]['name'] = product_name
                
                # Sum quantities per shop
                sales_data[shop][product_code]['quantity'] += quantity
                
                # Also track product totals across all branches
                if not product_totals[product_code]['name']:
                    product_totals[product_code]['name'] = product_name
                product_totals[product_code]['quantity'] += quantity
    
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found.")
        sys.exit(1)
    except (IOError, csv.Error, UnicodeDecodeError) as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Print results
    print("=" * 80)
    print("SALES ANALYSIS BY SHOP AND PRODUCT CODE")
    print("=" * 80)
    print()
    
    # Sort shops alphabetically
    for shop in sorted(sales_data.keys()):
        print(f"\n{'=' * 80}")
        print(f"SHOP: {shop}")
        print(f"{'=' * 80}")
        print(f"{'Product Code':<20} {'Product Name':<50} {'Total Quantity':>15}")
        print("-" * 80)
        
        shop_total = 0
        # Sort products by product code
        for product_code in sorted(sales_data[shop].keys()):
            product_info = sales_data[shop][product_code]
            product_name = product_info['name']
            total_qty = product_info['quantity']
            shop_total += total_qty
            
            print(f"{product_code:<20} {product_name:<50} {total_qty:>15}")
        
        print("-" * 80)
        print(f"{'SHOP TOTAL':<71} {shop_total:>15}")
        print()
    
    # Print grand summary
    print("\n" + "=" * 80)
    print("GRAND SUMMARY")
    print("=" * 80)
    grand_total = sum(
        sum(product['quantity'] for product in products.values())
        for products in sales_data.values()
    )
    print(f"Total Shops: {len(sales_data)}")
    print(f"Grand Total Quantity Sold: {grand_total:,}")
    print("=" * 80)
    
    return sales_data, product_totals


def write_to_csv(sales_data, product_totals, output_file_path):
    """
    Write the sales analysis results to a CSV file.
    First section: Group by branch with products and quantities.
    Second section: Total sales for each product across all branches.
    """
    try:
        with open(output_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # ===== SECTION 1: SALES BY BRANCH =====
            writer.writerow(['SALES BY BRANCH'])
            writer.writerow(['Shop', 'Product Code', 'Product Name', 'Total Quantity'])
            
            # Write data rows grouped by shop
            for shop in sorted(sales_data.keys()):
                shop_total = 0
                for product_code in sorted(sales_data[shop].keys()):
                    product_info = sales_data[shop][product_code]
                    product_name = product_info['name']
                    total_qty = product_info['quantity']
                    shop_total += total_qty
                    
                    writer.writerow([shop, product_code, product_name, total_qty])
                
                # Write shop total row
                writer.writerow([shop, '', 'SHOP TOTAL', shop_total])
                writer.writerow([])  # Empty row for separation
            
            # ===== SECTION 2: TOTAL SALES BY PRODUCT =====
            writer.writerow([])  # Empty row for separation
            writer.writerow(['TOTAL SALES BY PRODUCT (ACROSS ALL BRANCHES)'])
            writer.writerow(['Product Code', 'Product Name', 'Total Quantity'])
            
            # Write product totals
            for product_code in sorted(product_totals.keys()):
                product_info = product_totals[product_code]
                product_name = product_info['name']
                total_qty = product_info['quantity']
                
                writer.writerow([product_code, product_name, total_qty])
            
            # Write grand total
            grand_total = sum(product['quantity'] for product in product_totals.values())
            writer.writerow(['', 'GRAND TOTAL', grand_total])
        
        print(f"\n✓ Results written to: {output_file_path}")
        
    except (IOError, csv.Error) as e:
        print(f"Error writing CSV file: {e}")
        sys.exit(1)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_sales.py <csv_file_path>")
        print("Example: python analyze_sales.py 'Nutraxin Nov-25.csv'")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    
    # Analyze sales (filter by allowed branches)
    sales_data, product_totals = analyze_sales(csv_file_path, ALLOWED_BRANCHES)
    
    # Generate output filename
    base_name = os.path.splitext(os.path.basename(csv_file_path))[0]
    output_dir = os.path.dirname(csv_file_path) or '.'
    output_file_path = os.path.join(output_dir, f"{base_name}_by_product.csv")
    
    # Write to CSV
    write_to_csv(sales_data, product_totals, output_file_path)


if __name__ == "__main__":
    main()

