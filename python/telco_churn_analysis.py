
from pathlib import Path
import pandas as pd

base_dir = Path(__file__).resolve().parents[1]

input_file = base_dir / "data" / "Cleaned" / "Telco_Customer_Churn_Cleaned.xlsx"
output_file = base_dir / "reports" / "Telco_Churn_Analysis_Results.xlsx"

df = pd.read_excel(input_file, sheet_name="Cleaned_Data")

df["Churn"] = df["Churn"].astype(str).str.strip()

total_customers = len(df)
churned_customers = (df["Churn"] == "Yes").sum()
retained_customers = (df["Churn"] == "No").sum()

kpi_summary = pd.DataFrame({
    "Metric": [
        "Total Customers",
        "Churned Customers",
        "Retained Customers",
        "Churn Rate (%)",
        "Retention Rate (%)",
        "Average Tenure (Months)",
        "Average Monthly Charges",
        "Average Total Charges"
    ],
    "Value": [
        total_customers,
        churned_customers,
        retained_customers,
        round(churned_customers / total_customers * 100, 2),
        round(retained_customers / total_customers * 100, 2),
        round(df["tenure"].mean(), 2),
        round(df["MonthlyCharges"].mean(), 2),
        round(df["TotalCharges"].mean(), 2)
    ]
})

def analyze_segment(column):
    result = df.groupby(column, dropna=False).agg(
        Total_Customers=("customerID", "count"),
        Churned_Customers=("Churn", lambda x: (x == "Yes").sum()),
        Retained_Customers=("Churn", lambda x: (x == "No").sum()),
        Average_Tenure=("tenure", "mean"),
        Average_Monthly_Charges=("MonthlyCharges", "mean")
    ).reset_index()

    result["Churn_Rate_Percent"] = (
        result["Churned_Customers"] / result["Total_Customers"] * 100
    ).round(2)

    result["Retention_Rate_Percent"] = (
        result["Retained_Customers"] / result["Total_Customers"] * 100
    ).round(2)

    return result.round(2)

contract_analysis = analyze_segment("Contract")
internet_analysis = analyze_segment("InternetService")
payment_analysis = analyze_segment("PaymentMethod")
senior_analysis = analyze_segment("SeniorCitizen")
gender_analysis = analyze_segment("gender")
dependents_analysis = analyze_segment("Dependents")
security_analysis = analyze_segment("OnlineSecurity")
support_analysis = analyze_segment("TechSupport")

df["Tenure_Group"] = pd.cut(
    df["tenure"],
    bins=[-1, 12, 24, 48, 72],
    labels=["0-12 Months", "13-24 Months", "25-48 Months", "49-72 Months"]
)

tenure_analysis = analyze_segment("Tenure_Group")

monthly_charges_analysis = pd.cut(
    df["MonthlyCharges"],
    bins=[0, 35, 70, 100, float("inf")],
    labels=["0-35", "35-70", "70-100", "100+"],
    include_lowest=True
)

df["Monthly_Charges_Group"] = monthly_charges_analysis
charges_analysis = analyze_segment("Monthly_Charges_Group")

output_file.parent.mkdir(parents=True, exist_ok=True)

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    kpi_summary.to_excel(writer, sheet_name="KPI_Summary", index=False)
    contract_analysis.to_excel(writer, sheet_name="Contract_Analysis", index=False)
    internet_analysis.to_excel(writer, sheet_name="Internet_Analysis", index=False)
    payment_analysis.to_excel(writer, sheet_name="Payment_Analysis", index=False)
    senior_analysis.to_excel(writer, sheet_name="Senior_Citizens", index=False)
    gender_analysis.to_excel(writer, sheet_name="Gender_Analysis", index=False)
    dependents_analysis.to_excel(writer, sheet_name="Dependents_Analysis", index=False)
    security_analysis.to_excel(writer, sheet_name="Online_Security", index=False)
    support_analysis.to_excel(writer, sheet_name="Tech_Support", index=False)
    tenure_analysis.to_excel(writer, sheet_name="Tenure_Analysis", index=False)
    charges_analysis.to_excel(writer, sheet_name="Monthly_Charges", index=False)

analysis_results = {
    "KPI_Summary": kpi_summary,
    "Contract_Analysis": contract_analysis,
    "Internet_Analysis": internet_analysis,
    "Payment_Analysis": payment_analysis,
    "Senior_Citizens": senior_analysis,
    "Gender_Analysis": gender_analysis,
    "Dependents_Analysis": dependents_analysis,
    "Online_Security": security_analysis,
    "Tech_Support": support_analysis,
    "Tenure_Analysis": tenure_analysis,
    "Monthly_Charges": charges_analysis
}

print("\nTelco churn analysis results:")
for sheet_name, result in analysis_results.items():
    print(f"\n--- {sheet_name} ---")
    print(result.to_string(index=False))

print("Customer churn analysis completed.")
print(f"Total customers: {total_customers}")
print(f"Churned customers: {churned_customers}")
print(f"Retained customers: {retained_customers}")
print(f"Churn rate: {churned_customers / total_customers * 100:.2f}%")
print(f"Retention rate: {retained_customers / total_customers * 100:.2f}%")
print(f"Results saved to: {output_file}")
