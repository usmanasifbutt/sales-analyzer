"""
Streamlit web app for sales data analysis.
Upload CSV file, process in memory, and download results.
"""

import streamlit as st
import csv
import io
from collections import defaultdict


def parse_quantity(quantity_str):
    """Parse quantity string, handling whitespace and commas."""
    if not quantity_str or quantity_str.strip() == '':
        return 0
    cleaned = quantity_str.strip().replace(',', '')
    try:
        return int(cleaned)
    except ValueError:
        return 0


def is_summary_row(row):
    """Check if a row is a summary/total row that should be skipped."""
    if not row or len(row) < 1:
        return True
    shop = row[0].strip().lower() if row[0] else ''
    return (shop == '' or 
            'total' in shop or 
            'branch total' in shop or 
            'grand total' in shop or
            shop.endswith('branch total sale value') or
            shop.endswith('total branch sale'))


def is_allowed_branch(shop_name, allowed_branches):
    """Check if shop name matches any allowed branch (case-insensitive)."""
    if not shop_name:
        return False
    shop_lower = shop_name.strip().lower()
    allowed_lower = [branch.lower() for branch in allowed_branches]
    return shop_lower in allowed_lower


def analyze_sales_from_string(csv_content, allowed_branches):
    """
    Analyze sales data from CSV string content.
    Groups by shop and product code, then sums quantities.
    Only processes shops in the allowed_branches list.
    Uses case-insensitive matching but preserves original case.
    """
    sales_data = defaultdict(lambda: defaultdict(lambda: {'name': '', 'quantity': 0}))
    product_totals = defaultdict(lambda: {'name': '', 'quantity': 0})
    # Map lowercase shop names to their canonical (first-seen) case
    shop_case_map = {}

    # Decode bytes if needed
    if isinstance(csv_content, bytes):
        csv_content = csv_content.decode('utf-8')

    # Use StringIO to read from string
    csv_file = io.StringIO(csv_content)
    reader = csv.reader(csv_file)

    try:
        _ = next(reader)  # Skip header row
    except StopIteration:
        return sales_data, product_totals

    for row in reader:
        if not row or is_summary_row(row):
            continue

        if len(row) < 7:
            continue

        shop_original = row[0].strip()
        shop_lower = shop_original.lower()
        product_code = row[3].strip() if len(row) > 3 else ''
        product_name = row[4].strip() if len(row) > 4 else ''
        quantity_str = row[6].strip() if len(row) > 6 else '0'

        if not shop_original or not product_code:
            continue

        # Case-insensitive branch check
        if not is_allowed_branch(shop_original, allowed_branches):
            continue

        # Normalize shop name: use first-seen case as canonical
        if shop_lower not in shop_case_map:
            shop_case_map[shop_lower] = shop_original
        shop_canonical = shop_case_map[shop_lower]

        quantity = parse_quantity(quantity_str)

        if not sales_data[shop_canonical][product_code]['name']:
            sales_data[shop_canonical][product_code]['name'] = product_name

        sales_data[shop_canonical][product_code]['quantity'] += quantity

        if not product_totals[product_code]['name']:
            product_totals[product_code]['name'] = product_name
        product_totals[product_code]['quantity'] += quantity

    return sales_data, product_totals


def generate_csv_string(sales_data, product_totals):
    """
    Generate CSV content as string from sales data.
    Properly formatted with comma delimiter for column separation.
    """
    output = io.StringIO()
    writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)

    # ===== SECTION 1: TOTAL SALES BY PRODUCT (ACROSS ALL BRANCHES) =====
    writer.writerow(['TOTAL SALES BY PRODUCT (ACROSS ALL BRANCHES)'])
    writer.writerow(['Product Code', 'Product Name', 'Total Quantity'])

    for product_code in sorted(product_totals.keys()):
        product_info = product_totals[product_code]
        product_name = product_info['name']
        total_qty = product_info['quantity']
        writer.writerow([product_code, product_name, total_qty])

    grand_total = sum(product['quantity'] for product in product_totals.values())
    writer.writerow(['', 'GRAND TOTAL', grand_total])

    # ===== SECTION 2: SALES BY BRANCH =====
    writer.writerow([])
    writer.writerow(['SALES BY BRANCH'])
    writer.writerow(['Shop', 'Product Code', 'Product Name', 'Total Quantity'])

    for shop in sorted(sales_data.keys()):
        shop_total = 0
        for product_code in sorted(sales_data[shop].keys()):
            product_info = sales_data[shop][product_code]
            product_name = product_info['name']
            total_qty = product_info['quantity']
            shop_total += total_qty
            writer.writerow([shop, product_code, product_name, total_qty])

        writer.writerow([shop, '', 'SHOP TOTAL', shop_total])
        writer.writerow([])

    return output.getvalue()


# Streamlit App
st.set_page_config(
    page_title="Sales Data Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Sales Data Analyzer")
st.markdown("Upload a CSV file to analyze sales by branch and product.")

# Branches input field
st.subheader("🔧 Configuration")
branches_input = st.text_input(
    "Branches to Process",
    value="AWAISIA, BAHRIA TOWN, IQBAL TOWN, JOHAR TOWN PHARMACY",
    help="Enter branch names separated by commas (case-insensitive matching)"
)

# Parse branches from input
if branches_input:
    allowed_branches = [branch.strip().lower() for branch in branches_input.split(',') if branch.strip()]
else:
    allowed_branches = []
    st.warning("⚠️ Please enter at least one branch name.")

# File uploader
uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=['csv'],
    help="Upload your sales data CSV file"
)

if uploaded_file is not None:
    if not allowed_branches:
        st.error("❌ Please enter at least one branch name in the configuration above.")
    else:
        try:
            # Read file content
            file_content = uploaded_file.read()

            # Show file info
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            st.info(f"📁 File size: {len(file_content):,} bytes")
            # Display branches with original case from input
            branches_display = [b.strip() for b in branches_input.split(',') if b.strip()]
            st.info(f"🏪 Processing branches: {', '.join(branches_display)}")

            # Process file
            with st.spinner("Processing file..."):
                sales_data, product_totals = analyze_sales_from_string(
                    file_content, 
                    allowed_branches
                )

            # Generate CSV output
            csv_output = generate_csv_string(sales_data, product_totals)

            # Display summary statistics
            st.subheader("📈 Summary Statistics")
            col1, col2, col3 = st.columns(3)

            total_shops = len(sales_data)
            total_products = len(product_totals)
            grand_total = sum(product['quantity'] for product in product_totals.values())

            with col1:
                st.metric("Total Shops", total_shops)
            with col2:
                st.metric("Total Products", total_products)
            with col3:
                st.metric("Grand Total Quantity", f"{grand_total:,}")

            # Show preview of results
            st.subheader("🔍 Preview of Results")

            # Show branch summary
            if sales_data:
                st.markdown("**Sales by Branch:**")
                branch_summary = []
                for shop in sorted(sales_data.keys()):
                    shop_total = sum(
                        product['quantity'] 
                        for product in sales_data[shop].values()
                    )
                    branch_summary.append({
                        'Shop': shop,
                        'Total Quantity': shop_total
                    })

                st.dataframe(branch_summary, use_container_width=True)

            # Download button
            st.subheader("💾 Download Results")
            output_filename = f"{uploaded_file.name.rsplit('.', 1)[0]}_by_product.csv"

            st.download_button(
                label="📥 Download Processed CSV",
                data=csv_output,
                file_name=output_filename,
                mime="text/csv",
                type="primary"
            )

            st.success("✅ Processing complete! Click the button above to download your results.")

        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.exception(e)

else:
    st.info("👆 Please upload a CSV file to get started.")

