import pandas as pd

# File paths
bill_file = "bill test.xlsx"
em_file   = "EM test.csv"
#bill_file = "(12) City_JUNusage_Aug-bill.xlsx"
#em_file = "bill Export.csv"

# Read in the data
df_bill = pd.read_excel(bill_file, dtype={'ACCT#': str})
df_em   = pd.read_csv(em_file, dtype={'Account Number': str})

# Standardize column names (strip whitespace)
df_bill.columns = df_bill.columns.str.strip()
df_em.columns   = df_em.columns.str.strip()

# Mapping of bill columns -> (EM Line Item Type Name, EM column to compare)
utilities = {
    # usage columns
    'H20-CFT':         ('Water-Usage (CF)',      'Line Item Usage'),
    'KWH':             ('Electric-Usage (KWH)',  'Line Item Usage'),
    # cost columns
    'WATER$ 7304':     ('Water-Usage (CF)',      'Line Item Cost'),
    'SEWER$ 7305':     ('Sewer-Usage (CF)',      'Line Item Cost'),
    'TRASH$ 7207':     ('Trash (City Charges)',  'Line Item Cost'),
    'ELECTRIC$ 7303':  ('Electric-Usage (KWH)',  'Line Item Cost'),
    'DEMAND':          ('Demand',                'Line Item Cost'),
}

errors = []   # to collect error messages
results = {}  # to collect per-account pass/fail

# Iterate through each account in the bill (assumed unique)
for idx, bill_row in df_bill.iterrows():
    acct = bill_row['ACCT#']

    # Skip if account number is NaN or "* CPO * ACCT#"
    if pd.isna(acct) or acct.strip() == "* CPO * ACCT#":
        continue

    acct_errors = []

    # Filter EM rows for this account
    em_acct = df_em[df_em['Account Number'] == acct]
    if em_acct.empty:
        acct_errors.append(f"Account {acct}: not found in Energy Manager file.")
        results[acct] = False
        errors.extend(acct_errors)
        continue

    # For each utility mapping, compare values
    for bill_col, (em_type, em_col) in utilities.items():
        # Handle missing bill-cell: assume skip
        bill_val = bill_row.get(bill_col, None)
        if pd.isna(bill_val) or bill_val == ' ' or bill_val == '':
            continue

        # Filter EM rows further by Line Item Type Name
        em_rows = em_acct[em_acct['Line Item Type Name'].str.strip() == em_type]
        if em_rows.empty and bill_val != 0:
            acct_errors.append(
                f"Account {acct}, '{bill_col}': EM missing rows with type '{em_type}'."
            )
            continue

        # Gather all EM values for this utility
        em_vals = []
        for raw in em_rows[em_col]:
            try:
                em_vals.append(float(raw))
            except (TypeError, ValueError):
                em_vals.append(str(raw).strip())

        # Convert the bill value for comparison
        try:
            bill_num = float(bill_val)
            compare_as_number = True
        except (TypeError, ValueError):
            bill_num = str(bill_val).strip()
            compare_as_number = False

        # Check if any EM value matches the bill value exactly
        match_found = False
        for v in em_vals:
            if compare_as_number and isinstance(v, (int, float)) and bill_num == v:
                match_found = True
                break
            if not compare_as_number and bill_num == v:
                match_found = True
                break
        if not match_found and bill_num != 0:
            acct_errors.append(
                f"Account {acct}, '{bill_col}': bill={bill_num} not in EM values {em_vals}"
            )

    # Record result for this account
    if acct_errors:
        results[acct] = False
        errors.extend(acct_errors)
    else:
        results[acct] = True

# Print summary
print("\n=== VALIDATION SUMMARY ===\n")
for acct, ok in results.items():
    status = "OK" if ok else "ERROR"
    print(f"Account {acct}: {status}")
print("\n=== DETAILS ===\n")
if errors:
    for e in errors:
        print(" -", e)
else:
    print("All accounts validated successfully!")
