import streamlit as st
import utils as utl
from views import dcf, home

st.set_page_config(layout="wide", page_title='Navbar sample')
st.set_option('deprecation.showPyplotGlobalUse', False)
utl.inject_custom_css()
utl.navbar_component()

def navigation():
    route = utl.get_current_route()
    if route == "":
        home.load_view()
    if route == "home":
        home.load_view()
    elif route == "dcf":
        dcf.load_view()
    elif route == None:
        home.load_view()
        
navigation()