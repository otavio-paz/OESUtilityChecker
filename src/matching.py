import pandas as pd

def check_utility(file1_bill, file2_EM):
    # Read the files
    bill = pd.read_excel(file1_bill)
    EM = pd.read_csv(file2_EM)

    # Results

    results = []

    # Iterate over the rows of the bill
    for _, row in bill.iterrows():
        
        account_number = row.iloc[0] # Account number in bill

        # Ignore the line if account number is ACCT#, empty, or contains * CPO * ACCT#
        if account_number == 'ACCT#' or pd.isna(account_number) or '* CPO * ACCT#' in account_number:
            continue

        address = row.iloc[1] # Address in bill

        # Ignore line if address contains "SERVICE ADDRESS", "Total NON-CPO Accounts", "Total CPO Accounts", or is empty
        if address == 'SERVICE ADDRESS' or address == 'Total NON-CPO Accounts' or address == 'Total CPO Accounts' or pd.isna(address):
            continue

        # Filter EM for matching account number
        matching_rows = EM[EM.iloc[:,2] == account_number]
        
        if matching_rows.empty:
            results.append(f"{address}: ACCOUNT ({account_number}) NOT FOUND IN FILE 2")
            continue

        # Initialize flags to check each type
        errors = []

        # Check each type
        for data_type, usage_col, cost_col, bill_usage_col, bill_cost_col in [
            ('Water-Usage (CF)', 4, 5, 4, 5),
            ('Sewer-Usage (CF)', None, 5, None, 6),
            ('Trash (City Charges)', None, 5, None, 7),
            ('Electric-Usage (KWH)', 4, 5, 8, 9),
        ]:
            type_rows = matching_rows[matching_rows.iloc[:, 3] == data_type]

            if type_rows.empty:
                errors.append(f"{data_type} data missing")
                continue

            usage = type_rows.iloc[0, usage_col] if usage_col else None
            cost = type_rows.iloc[0, cost_col]

            # Compare usage if applicable
            if bill_usage_col is not None and not pd.isna(row[bill_usage_col]):
                if usage != row[bill_usage_col]:
                    errors.append(f"{data_type} USAGE mismatch (Bill: {row[bill_usage_col]} vs EM: {usage})")

            # Compare cost
            if bill_cost_col is not None and not pd.isna(row[bill_cost_col]):
                if cost != row[bill_cost_col]:
                    errors.append(f"{data_type} COST mismatch (Bill: {row[bill_cost_col]} vs EM: {cost})")

        # Compile results
        if errors:
            results.append(f"{address}: {', '.join(errors)}")
        else:
            results.append(f"{address}: ALL DATA OK")

    # Output results
    for result in results:
        print(result)

# Example usage
check_utility('(12) City_JUNusage_Aug-bill.xlsx', 'bill Export.csv')
