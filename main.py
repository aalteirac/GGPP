import streamlit as st
import pandas as pd
from datetime import datetime
from datetime import timedelta
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
custom_html = """
<div class="banner">
    <img src="https://static.wixstatic.com/media/87260b_3ae09b2243664894b60911bf6f830397~mv2.png/v1/fill/w_418,h_150,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/Logo_enedis_header.png" alt="Banner Image">
</div>
<style>
    .banner {
        width: 160%;
        height: 200px;
        overflow: hidden;
    }
    .banner img {
        object-fit: cover;
    }
</style>
"""

st.components.v1.html(custom_html)

gir = pd.read_excel("./data/GIR_01_25.xlsx")  
use = pd.read_excel("./data/USE_01_25.xlsx") 
use=use.rename(columns={'Immatriculation': 'IMMATRICULATION'})

immatriculation_options = use['IMMATRICULATION'].unique()

st.title('Booking, Distance and Battery Level Over Time')

filters = st.toggle("Filter by Car", value=False)

if filters:
    selected_immat = st.selectbox('Select Immatriculation:', immatriculation_options)

# CLEAN AND ADD MISSING DAYS FOR USAGE
if filters:
    use = use[use['IMMATRICULATION'] == selected_immat]

disp1=use.copy()

use['Date'] = pd.to_datetime(use['Date'],format="%d/%m/%Y")
use['Niveau batterie départ'] = use['Niveau batterie départ']*100
use["Début"] = pd.to_datetime(use["Date"].astype(str) + " " + use["Début"], format="%Y-%m-%d %H:%M")
use["Fin"] = pd.to_datetime(use["Date"].astype(str) + " " + use["Fin"], format="%Y-%m-%d %H:%M")


use=use.drop(columns=['IMMATRICULATION'])
use=use.resample('D',on='Date').mean()
# use=use.fillna(0)
use=use.reset_index()

# BUILD BOOKING DF
if filters:
    gir = gir[gir['IMMATRICULATION'] == selected_immat]

disp2=gir.copy()

gir['dumm']=''
gir['Task']=gir['IMMATRICULATION']
gir['Start']=gir['Date départ']
gir['Finish']=gir['Date retour']

# CHARTS
colors = ['#7a0504', (0.2, 0.7, 0.3), 'rgb(210, 60, 180)']
fig = px.timeline(gir, x_start="Start", x_end="Finish", y="dumm")
fig.update_layout(showlegend=False)
# fig.update_layout(yaxis_visible=False)
# fig.update_layout(
#     xaxis=dict(
#         rangeselector=dict(
#             buttons=list([
#                 dict(count=7,
#                      label="Week",
#                      step="day",
#                      stepmode="backward"),
#                 dict(count=1,
#                      label="Month",
#                      step="month",
#                      stepmode="backward"),
#                 dict(count=1,
#                      label="Year",
#                      step="year",
#                      stepmode="backward"),
#                 dict(step="all")
#             ])
#         ),
#         rangeslider=dict(
#             visible=False
#         ),
#         type="date"
#     )
# )
fig.update_yaxes(
    title="",
    tickson="boundaries",
    fixedrange=True,
)
BARHEIGHT = .2
fig.update_layout(
    yaxis={"domain": [max(1 - (BARHEIGHT * len(fig.data)), 0), 1]}, margin={"t": 50, "b": 0}
)


trace1=go.Scatter(x=use['Début'], 
    y=use['Distance'],
    line_color = 'blue',
    mode = 'lines+markers',
    showlegend = False,
)
trace2=go.Scatter(x=use['Début'], 
    y = use['Niveau batterie départ'], 
    line_color = 'orange',
    mode = 'lines+markers',
    showlegend = False)
figcombo = make_subplots(rows=3, cols=1, figure=fig, shared_xaxes=True)
fig.add_trace(trace1, row=2, col=1)
fig.add_trace(trace2, row=3, col=1)
fig.update_layout(xaxis1_showticklabels=False, xaxis2_showticklabels=False, xaxis3_showticklabels=True,yaxis3_range=[0,110])
          
st.plotly_chart(figcombo, use_container_width=True)
with st.expander("Raw Data"):
    st.write("Usage:")
    st.dataframe(disp1,use_container_width=True,hide_index=True)
    st.write("Booking:")
    st.dataframe(disp2,use_container_width=True,hide_index=True)

def setUI():
    hvar='''
        <script>
            var my_style= window.parent.document.createElement('style');
            my_style.innerHTML=`
                footer{
                    display:none;
                }
                .stApp {
                    margin-top: -80px
                }
                .stApp header{
                    background-color: transparent;
                }
                
                .streamlit-expanderHeader p{
                    font-size: x-large;
                }
                .main .block-container{
                    max-width: unset;
                    padding-left:1em;
                    padding-right: 1em;
                    padding-top: 0em;
                    padding-bottom: 1em;
                `;
                window.parent.document.head.appendChild(my_style);       
        </script>
        '''
    components.html(hvar, height=0, width=0)

setUI()