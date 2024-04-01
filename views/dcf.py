import streamlit as st
from dcf_utils import get_data
import pandas as pd
import altair as alt

data = {}

def load_view():
    st.title('VALUING CONSISTENT COMPOUNDERS')
    st.markdown("""
        <body>
            <p>Hi there!</p>
            <p>This page will help you calculate intrinsic PE of consistent compounders through growth-RoCE DCF model.</p>
            <p>We then compare this with current PE of the stock to calculate degree of overvaluation.</p>

        </body>

        """, unsafe_allow_html=True)
    
    
    company_name = st.text_input("NSE/BSE symbol")

    #slider

    coc = st.slider('Cost of Capital (CoC): %', 8, 16, 8, 1)
    roce = st.slider('Return on Capital Employed (RoCE): %', 10, 100, 10, 10)
    growth_period = st.slider('Growth during high growth period: $', 8, 20, 8, 2)
    high_growth_period = st.slider('High growth period(years):', 10, 25, 10, 2)
    fade_period = st.slider('Fade period(years):', 5, 20, 5, 5)
    terminal_growth = st.slider('Terminal growth rate: %', 0.0, 7.5, 0.0, 1.0)

    #intrinsic_pe =



    if company_name:
        data = get_data(company_name)
        filtered_links = {key: value for key, value in data['links'].items() if 'BSE' in key or 'NSE' in key}

        for key,links in filtered_links.items():
            if 'BSE' in key:
                st.text(f"{key}")
            elif 'NSE' in key:
                st.text(f"{key}")
                
        if data:
            st.text(f"Current PE: {data['Stock P/E']}")
            st.text(f"FY23 PE: {data['fy23_pe']}")
            st.text(f"5-yr median pre-tax RoCE: {data['roce_median']}%")

            
        else:
            st.warning("Company data not found. Please enter a valid company name")

        st.markdown("### Sales and Profit Growth")
        sales_growth_data = data['tables']['Compounded Sales Growth']
        profit_growth_data = data['tables']['Compounded Profit Growth']
        
        # Extract periods
        periods = list(sales_growth_data.keys())
        combined_table = "<table><tr><th>Period</th>"
        combined_table += f"<th>{(periods[0].rstrip(':'))}</th><th>{(periods[1].rstrip(':'))}</th><th>{(periods[2].rstrip(':'))}</th><th>{(periods[3].rstrip(':'))}</th>"
        combined_table += "</tr>"
        combined_table += "<tr><th>Sales Growth Rate</th>"
        combined_table += f"<td>{sales_growth_data.get(periods[0], '').rstrip('%')}</td><td>{sales_growth_data.get(periods[1], '').rstrip('%')}</td><td>{sales_growth_data.get(periods[2], '').rstrip('%')}</td><td>{sales_growth_data.get(periods[3], '').rstrip('%')}</td>"
        combined_table += "</tr>"
        combined_table += "<tr><th>Profit Growth Rate</th>"
        combined_table += f"<td>{profit_growth_data.get(periods[0], '').rstrip('%')}</td><td>{profit_growth_data.get(periods[1], '').rstrip('%')}</td><td>{profit_growth_data.get(periods[2], '').rstrip('%')}</td><td>{profit_growth_data.get(periods[3], '').rstrip('%')}</td>"
        combined_table += "</tr>"

        combined_table += "</table>"
        st.markdown(combined_table, unsafe_allow_html=True)

        
        sales_growth_data = data['tables']['Compounded Sales Growth']
        sales_periods = list(sales_growth_data.keys())
        sales_growth_rates = [float(sales_growth_data[period].strip('%')) for period in sales_periods]

        sales_df = pd.DataFrame({'Time period': sales_periods, 'Sales Growth (%)': sales_growth_rates})
        sales_df['Time period'] = sales_df['Time period'].apply(lambda x: x[:-1])  # Remove ":" from years
        sales_chart = alt.Chart(sales_df).mark_bar().encode(
            y=alt.Y('Time period:O', title='Time Period'),
            x=alt.X('Sales Growth (%):Q', title='Sales Growth (%)'),
        ).properties(
            width=200,
            height=300
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14,
            labelAngle = 0
        )

        # Profit Growth
        profit_growth_data = data['tables']['Compounded Profit Growth']
        profit_periods = list(profit_growth_data.keys())
        profit_growth_rates = [float(profit_growth_data[period].strip('%')) for period in profit_periods]

        profit_df = pd.DataFrame({'Time period': profit_periods, 'Profit Growth (%)': profit_growth_rates})
        profit_df['Time period'] = profit_df['Time period'].apply(lambda x: x[:-1])  # Remove ":" from years
        profit_chart = alt.Chart(profit_df).mark_bar().encode(
            y=alt.Y('Time period:O', title='Time period'),
            x=alt.X('Profit Growth (%):Q', title='Profit Growth (%)'),
        ).properties(
            width=200,
            height=300
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        )

        # Displaying side by side
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Sales Growth")
            st.altair_chart(sales_chart, use_container_width=True)

        with col2:
            st.markdown("### Profit Growth")
            st.altair_chart(profit_chart, use_container_width=True)

    st.write("Play with inputs to see changes in intrinsic PE and overvaluation:")
    st.write("The calculated intrinsic PE is:", )
    st.write("The degree of overvaluation is:", )

        
    


    
    


    


