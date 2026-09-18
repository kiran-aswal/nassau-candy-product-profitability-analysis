import streamlit as st
import pandas as pd



# PAGE CONFIGURATION

st.set_page_config(
    page_title="Nassau Candy Profitability Dashboard",
    page_icon="🍫",
    layout="wide"
)


# TITLE
st.title("🍫 Nassau Candy - Product Profitability & Margin Analysis")


#DATASET
df = pd.read_csv("nassau_candy_cleaned.csv")

df.columns = df.columns.str.strip()

df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    errors="coerce"
)



st.sidebar.header("🔎 Filters")


# Date Range
date_range = st.sidebar.date_input(
    "📅 Order Date",
    value=(
        df["Order Date"].min().date(),
        df["Order Date"].max().date()
    )
)



# Division Filter
division = st.sidebar.selectbox(
    "🏢 Division",
    ["All"] + sorted(df["Division"].dropna().unique().tolist())
)




# Margin Threshold
margin_threshold = st.sidebar.slider(
    "📊 Minimum Gross Margin (%)",
    min_value=0,
    max_value=100,
    value=50
)


# Product Search
product_search = st.sidebar.text_input(
    "🔍 Search Product"
)

filtered_df = df.copy()


# Date filter
if len(date_range) == 2:

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    filtered_df = filtered_df[
        (filtered_df["Order Date"] >= start_date) &
        (filtered_df["Order Date"] <= end_date)
    ]



# Division filter
if division != "All":

    filtered_df = filtered_df[
        filtered_df["Division"] == division
    ]


# Product search
if product_search:

    filtered_df = filtered_df[
        filtered_df["Product Name"].str.contains(
            product_search,
            case=False,
            na=False
        )
    ]


#Product Profitability
st.header("📊 1. Product Profitability")


product_analysis = filtered_df.groupby(
    ["Product ID", "Product Name"]
).agg({
    "Sales": "sum",
    "Units": "sum",
    "Gross Profit": "sum",
    "Cost": "sum"
}).reset_index()


# Gross Margin
product_analysis["Gross Margin %"] = (
    product_analysis["Gross Profit"] /
    product_analysis["Sales"]
) * 100


# Profit per Unit
product_analysis["Profit per Unit"] = (
    product_analysis["Gross Profit"] /
    product_analysis["Units"]
)


# Apply margin threshold
product_analysis = product_analysis[
    product_analysis["Gross Margin %"] >= margin_threshold
]


# Sort by profit
product_analysis = product_analysis.sort_values(
    "Gross Profit",
    ascending=False
)


st.dataframe(
    product_analysis,
    use_container_width=True
)

st.bar_chart(
    product_analysis.set_index("Product Name")["Gross Profit"]
)


#Division Performance
st.header("🏢 2. Division Performance")


division_analysis = filtered_df.groupby(
    "Division"
).agg({
    "Sales": "sum",
    "Units": "sum",
    "Gross Profit": "sum",
    "Cost": "sum"
}).reset_index()


# Gross Margin
division_analysis["Gross Margin %"] = (
    division_analysis["Gross Profit"] /
    division_analysis["Sales"]
) * 100


# Revenue Contribution
division_analysis["Revenue Contribution %"] = (
    division_analysis["Sales"] /
    division_analysis["Sales"].sum()
) * 100


# Profit Contribution
division_analysis["Profit Contribution %"] = (
    division_analysis["Gross Profit"] /
    division_analysis["Gross Profit"].sum()
) * 100


division_analysis = division_analysis.sort_values(
    "Gross Profit",
    ascending=False
)


st.dataframe(
    division_analysis,
    use_container_width=True
)

st.subheader("Gross Profit by Division")

st.bar_chart(
    division_analysis.set_index("Division")["Gross Profit"]
)


#Cost vs Margin Diagnostics
st.header("💰 3. Cost vs Margin Diagnostics")


cost_margin = product_analysis.copy()


# Cost as percentage of sales
cost_margin["Cost % of Sales"] = (
    cost_margin["Cost"] /
    cost_margin["Sales"]
) * 100


cost_margin = cost_margin.sort_values(
    "Cost % of Sales",
    ascending=False
)


st.dataframe(
    cost_margin[
        [
            "Product Name",
            "Sales",
            "Cost",
            "Gross Profit",
            "Gross Margin %",
            "Cost % of Sales"
        ]
    ],
    use_container_width=True
)

st.subheader("Cost % of Sales by Product")

st.bar_chart(
    cost_margin.set_index("Product Name")["Cost % of Sales"]
)



#Profit Concentration / Pareto Analysis
st.header("📈 4. Profit Concentration / Pareto Analysis")

# Create Pareto data from filtered data
pareto_data = filtered_df.groupby(
    ["Product ID", "Product Name"]
).agg({
    "Gross Profit": "sum"
}).reset_index()

# Sort by profit
profit_pareto = pareto_data.sort_values(
    "Gross Profit",
    ascending=False
).copy()

# Cumulative profit
profit_pareto["Cumulative Profit"] = (
    profit_pareto["Gross Profit"].cumsum()
)

# Cumulative profit percentage
total_profit = profit_pareto["Gross Profit"].sum()

if total_profit != 0:

    profit_pareto["Cumulative Profit %"] = (
        profit_pareto["Cumulative Profit"] /
        total_profit
    ) * 100

else:

    profit_pareto["Cumulative Profit %"] = 0


st.dataframe(
    profit_pareto[
        [
            "Product Name",
            "Gross Profit",
            "Cumulative Profit %"
        ]
    ],
    use_container_width=True
)

# Pareto chart
st.subheader("Cumulative Profit Contribution")

st.line_chart(
    profit_pareto.set_index("Product Name")[
        "Cumulative Profit %"
    ]
)
