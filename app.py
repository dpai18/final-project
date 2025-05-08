'''
Name: Dhruvi Pai
CS230: Section 2
Data: Top2000CompaniesGlobally
Description:
This interactive Streamlit web app visualizes data from the Top 2000 Companies Globally dataset.
Users can filter companies by name, maximum sales, and maximum profits using sidebar widgets, and then explore multiple dynamic visualizations.
This project demonstrates data cleaning, filtering, aggregation, custom chart styling, and use of advanced features like tooltips, legends, and calculated fields.
'''
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk

default_sales = 500
default_profits = 100

#read in data
#error checking with try/except
def read_data():
    try:
        return pd.read_csv("Top2000CompaniesGlobally.csv").set_index("Global Rank")
    except FileNotFoundError:
        st.error("Data file not found.")
        return pd.DataFrame()

#filter the data
def filter_data(selected_companies, max_sales=500, max_profits=100):
    df = read_data()
    #clean data
    df = df.dropna(subset=['Company', 'Sales ($billion)', 'Profits ($billion)', 'Latitude', 'Longitude'])

    df = df.loc[df['Company'].isin(selected_companies)]
    df = df.loc[df['Sales ($billion)'] < max_sales]
    df = df.loc[df['Profits ($billion)'] < max_profits]
    return df

#function returns more than one value
def get_min_max(df):
    return df['Sales ($billion)'].min(), df['Sales ($billion)'].max()

#list comprehension
def all_companies():
    df = read_data()
    lst = []
    for ind, row in df.iterrows():
        if row['Company'] not in lst:
            lst.append(row['Company'])
    return lst

#sum values
def count_sales(companies, df):
    return [df.loc[df['Company'] == Company, 'Sales ($billion)'].sum() for Company in companies]
def count_profits(companies, df):
    return [df.loc[df['Company'] == Company, 'Profits ($billion)'].sum() for Company in companies]

#lists for charts
def company_sales(df):
    sales = [row['Sales ($billion)'] for ind, row in df.iterrows()]
    companies = [row['Company'] for ind, row in df.iterrows()]
    dict = {}
    for company in companies:
        dict[company] = []
    for i in range(len(sales)):
        dict[companies[i]].append(sales[i])
    return dict

def company_profits(df):
    profits = [row['Profits ($billion)'] for ind, row in df.iterrows()]
    companies = [row['Company'] for ind, row in df.iterrows()]
    dict = {}
    for company in companies:
        dict[company] = []
    for i in range(len(profits)):
        dict[companies[i]].append(profits[i])
    return dict

#dictionary keys/values access
def company_averages(dict_sales):
    dict = {}
    for key in dict_sales.keys():
        dict[key] = float(np.mean(dict_sales[key]))
    return dict

#pie chart
def generate_pie_chart(counts, selected_companies, label="Sales"):
    plt.figure(figsize=(6, 6))
    plt.pie(counts, labels=selected_companies, autopct="%.2f%%", explode=[0.05]*len(counts),
            textprops={'fontsize': 10}, colors=plt.cm.Paired.colors)
    plt.title(f"{label} Distribution of Selected Companies", fontsize=14, fontweight='bold')
    return plt

#bar chart
def generate_bar_chart(dict_averages, label="Sales"):
    plt.figure(figsize=(8, 5))
    x = dict_averages.keys()
    y = dict_averages.values()
    bars = plt.bar(x, y, color='skyblue', edgecolor='black')
    plt.bar(x, y)
    plt.xticks(rotation=45, fontsize=9)
    plt.yticks(fontsize=9)
    plt.ylabel(f'{label} ($billion)', fontsize=11, fontweight='bold')
    plt.xlabel('Company', fontsize=11, fontweight='bold')
    plt.title(f"Average {label} for Selected Companies: {', '.join(dict_averages.keys())}", fontsize=14, fontweight='bold')
    plt.grid(axis='y', linestyle='--', linewidth=0.5)
    plt.legend([bars[0]], [f'{label} Avg'], loc='upper right', fontsize=9)
    return plt

#map
def generate_map(df):
    map_df = df.filter(['Company', 'Latitude', 'Longitude'])
    view_state = pdk.ViewState(latitude=map_df["Latitude"].mean(),
                               longitude=map_df["Longitude"].mean(),
                               zoom=1.5)
    layer = pdk.Layer('ScatterplotLayer',
                      data=map_df,
                      get_position='[Longitude, Latitude]',
                      get_radius=150000,
                      get_color = [20, 175, 250],
                      pickable=True)

    tool_tip = {'html': 'Company:<br/> <b>{Company}</b>', 'Style': {'BackgroundColor': 'SteelBlue', 'Color': 'White'}}
    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers=[layer],
                   tooltip=tool_tip)
    st.pydeck_chart(map)

def main():
    st.title("Top 2000 Global Companies")
    st.write("Use the sidebar to filter companies by sales and profits, then view maps and visualizations!")

    st.sidebar.header("Filter Options")
    companies = st.sidebar.multiselect("Select Companies:", all_companies())
    max_sales = st.sidebar.slider("Max Sales ($billion):", 0, 500, default_sales)
    max_profits = st.sidebar.slider("Max Profits ($billion):", 0, 200, default_profits)

    #call filtered data with or without default values
    data = filter_data(companies)  #default used
    data = filter_data(companies, max_sales, max_profits)  #override default

    #sort data by sales descending
    data = data.sort_values(by='Sales ($billion)', ascending=False)

    #calculated column
    data['Profit Margin'] = data['Profits ($billion)'] / data['Sales ($billion)']

    #download button for filtered data
    csv = data.to_csv().encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name='filtered_companies.csv',
        mime='text/csv'
    )


    if len(companies) > 0 and not data.empty:
        sales_series = count_sales(companies, data)
        profits_series = count_profits(companies, data)

        st.subheader('🌎Company Headquarters Map:')
        st.write('This map below shows the geographic locations of the selected companies.')
        generate_map(data)

        st.subheader('📈Sales Visualizations')
        st.write('The pie chart below shows the percentage of total sales by each selected company.')
        st.pyplot(generate_pie_chart(sales_series, companies, label="Sales"))

        st.write('The bar chart below shows the average sales amount for each selected company.')
        st.pyplot(generate_bar_chart(company_averages(company_sales(data)), label="Sales"))

        st.subheader('💰Profit Visualizations')
        st.write('The pie chart shows how much each selected company contributes to total profit.')
        st.pyplot(generate_pie_chart(profits_series, companies, label="Profits"))

        st.write('This bar chart displays the average profits of each selected company.')
        st.pyplot(generate_bar_chart(company_averages(company_profits(data)), label="Profits"))

        #top 5 companies by profit
        st.subheader("💸Top 5 Companies by Profit")
        top_profits = data.nlargest(5, 'Profits ($billion)')
        st.dataframe(top_profits[['Company', 'Profits ($billion)']])

        #summary
        st.subheader("📋Summary Statistics")
        st.write("Summary table of the filtered data for sales and profits.")
        st.dataframe(data[['Company', 'Sales ($billion)', 'Profits ($billion)']].describe())

        #pivot table
        pivot = data.pivot_table(values='Sales ($billion)', index='Company', aggfunc='mean')
        st.subheader("📊Sales Pivot Table (Company vs. Average Sales)")
        st.dataframe(pivot)


    elif len(companies) == 0:
        st.warning("Please select at least one company from the sidebar.")
    else:
        st.warning("No data available for the selected filters.")
main()

