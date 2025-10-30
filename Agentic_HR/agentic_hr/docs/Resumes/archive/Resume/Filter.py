import pandas as pd

# Load your Excel file
df = pd.read_csv("Resume.csv")

# Randomly select 50 rows (without replacement)
df_sample = df.sample(n=50, random_state=42)

# Save to a new Excel or CSV file (optional)
df_sample.to_csv("random_50_rows.csv", index=False)
# or df_sample.to_csv("random_50_rows.csv", index=False)

print(df_sample.head())
