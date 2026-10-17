import streamlit as st

pg = st.navigation([st.Page('Home.py'),
                    st.Page('Risk.py'),
                    st.Page('Map.py')])

pg.run()
