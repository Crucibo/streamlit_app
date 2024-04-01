import streamlit as st
from bs4 import BeautifulSoup
import requests
import numpy as np


def scrape_data(company_symbol):
    base_url = "https://www.screener.in/company/"
    regular_url = base_url + company_symbol
    
    try:
        # Fetch data from the regular URL
        response = requests.get(regular_url)
        if response.status_code != 200:
            raise Exception("Failed to fetch data")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract net profit data
        profit_loss_section = soup.find('section', id='profit-loss')
        net_profit_data = extract_net_profit(profit_loss_section)
        
        # Extract Stock P/E
        stock_pe_value = extract_stock_pe(soup)
        
        # Extract all required ratios
        ratios = extract_ratios(soup)
        links=extract_link(soup)
        roce=extract_roce_values(soup)
        tables=ranges_table(soup)
        
        # If certain conditions are met, fetch data from consolidated URL
        if should_use_consolidated_data(soup):
            consolidated_url = base_url + company_symbol + "/consolidated/"
            response = requests.get(consolidated_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Extract net profit data from consolidated URL
                profit_loss_section = soup.find('section', id='profit-loss')
                net_profit_data = extract_net_profit(profit_loss_section)
                # Extract Stock P/E from consolidated URL
                stock_pe_value = extract_stock_pe(soup)

        last_net_profit = net_profit_data.get('Last Net Profit', {}).get(list(net_profit_data.get('Last Net Profit', {}))[0], 0)  # Get the last available net profit, default to 0 if not found
        if last_net_profit:
            fy23_pe = float(ratios.get('Market Cap', 0).replace(',', '')) / float(last_net_profit.replace(',', ''))
        else:
            fy23_pe = None
                
    except Exception as e:
        print(e)
        st.error("Failed to fetch data")
        return None
    
    # Combine all data into a dictionary
    data = {
        'net_profit': net_profit_data,
        'Stock P/E': stock_pe_value,
        **ratios,
        'links':links,
        'fy23_pe':fy23_pe,
        'roce_median':roce,
        'tables':tables
    }
    
    return(data)


def extract_net_profit(profit_loss_section):
    net_profit_data = {}
    if profit_loss_section:
        net_profit_table = profit_loss_section.find('table', {'data-table': ''})
        if net_profit_table:
            rows = net_profit_table.find_all('tr')
            header_cells = rows[0].find_all('th')
            months = [cell.text.strip() for cell in header_cells[1:]]
            for row in rows:
                cells = row.find_all('td', class_='text')
                if cells:
                    label = cells[0].text.strip()
                    if label.startswith('Net Profit'):
                        net_profit_values = [cell.text.strip() for cell in row.find_all('td')[1:]]
                        # Remove TTM value if present
                        if 'TTM' in months:
                            ttm_index = months.index('TTM')
                            del months[ttm_index]
                            del net_profit_values[ttm_index]
                        net_profit_data = {month: profit for month, profit in zip(months, net_profit_values)}
                        # Add last net profit value
                        last_month = months[-1]
                        last_value = net_profit_values[-1]
                        net_profit_data['Last Net Profit'] = {last_month: last_value}
                        break
    return net_profit_data



def extract_stock_pe(soup):
    stock_pe_value = ""
    li_elements = soup.find_all('li')
    for li in li_elements:
        if 'Stock P/E' in li.text:
            stock_pe_value = li.find('span', class_='number').text.strip()
            break
    return stock_pe_value


def extract_ratios(soup):
    ratios = {}
    top_ratios_ul = soup.find('ul', id='top-ratios')
    if top_ratios_ul:
        required_ratios = {
            'Market Cap': 'Market Cap',
            'Current Price': 'Current Price',
            'High / Low': 'High / Low',
            'Book Value': 'Book Value',
            'Dividend Yield': 'Dividend Yield',
            'ROCE': 'ROCE',
            'ROE': 'ROE',
            'Face Value': 'Face Value'
        }
        for key, value in required_ratios.items():
            ratio_li = top_ratios_ul.find(lambda tag: tag.name == 'li' and value in tag.text)
            if ratio_li:
                ratio_value = ratio_li.find('span', class_='number').text.strip()
                ratios[key] = ratio_value
            else:
                print(f"No data found for: {key}")
    return ratios


def should_use_consolidated_data(soup):
    # Your conditions for deciding whether to use consolidated data or not
    return False  # For now, returning False as a placeholder

def extract_roce_values(soup):
    ratios_section = soup.find('section', id='ratios')

    # Find the table containing the ROCE data within the "ratios" section
    roce_table = ratios_section.find('table', class_='data-table')

    # Find all the rows within the table body
    rows = roce_table.find('tbody').find_all('tr')

    # Initialize a dictionary to store the ROCE data
    roce_data = {}

    for row in rows:
        # Extract the text from the row
        row_data = row.find_all('td')
        # Check if the row corresponds to ROCE
        if row_data[0].text.strip() == 'ROCE %':
            # Extract ROCE data for the years 2018 to 2022
            roce_values = [float(cell.text.strip('%')) for cell in row_data[7:12]]

    # Calculate the median
    roce_median = np.median(roce_values)
    return roce_median




def extract_link(soup):
    links = {}
    company_links_div = soup.find('div', class_='company-links show-from-tablet-landscape')
    if company_links_div:
        links_list = company_links_div.find_all('a')
        for link in links_list:
            link_url = link.get('href').strip()
            link_text = link.find('span').text.strip().replace('\n', '').replace(' ','')
            links[link_text] = link_url
    return links

def ranges_table(soup):
    data={}
    tables = soup.find_all('table', class_='ranges-table')
    for table in tables:
            rows = table.find_all('tr')
            header = rows[0].text.strip()
            metrics = {}
            for row in rows[1:]:
                cells = row.find_all('td')
                metric_name = cells[0].text.strip()
                value = cells[1].text.strip()
                metrics[metric_name] = value
            data[header] = metrics
    return data

def get_data(company_name):
    datas=scrape_data(company_name)
    return datas