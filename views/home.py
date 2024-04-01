import streamlit as st

def load_view():
    home=rf'''
        <body>
            <p>
                This site provides interactive tools to valuate and analyze stocks through Reverse DCF model. Check the navigation bar for more.
            </p>
        </body>

        '''
    st.markdown(home, unsafe_allow_html=True)