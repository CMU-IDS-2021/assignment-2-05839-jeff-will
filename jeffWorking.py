#!/usr/bin/env python
# coding: utf-8

# In[15]:


import altair as alt
from vega_datasets import data
import pandas as pd
import numpy as np
import streamlit as st

# Import Data

COVID = pd.read_csv("covidcast-doctor-visits-smoothed_adj_cli-2021-01-01-to-2021-01-31.csv")
COUNTY = pd.read_csv("health_ineq_online_table_12.csv", encoding = "latin-1")
COUNTY["cty"] = COUNTY["cty"].astype(int)
COVID["geo_value"] = COVID["geo_value"].astype(int)
# pd.options.display.max_columns
# pd.set_option('display.max_columns', None)
# print(COVID.head());
# print(COUNTY.head());

# print("COVID Column List")
# for col in COVID.columns:
#    print(col)
#
# print("COUNTY Column List")
# for col in COUNTY.columns:
#    print(col)

DATA = COUNTY.join(COVID.set_index("geo_value"), how = "inner", on = "cty")
DATA['Date'] = pd.to_datetime(DATA.time_value)
DATA['Date'] = DATA.Date.dt.strftime('%d').astype(int)

def createMap(workingData):

    us_counties = alt.topo_feature(data.us_10m.url, 'counties')
    columns = workingData.columns[1:6].tolist()
    chart = alt.Chart(us_counties).mark_geoshape(
        stroke='black',
        strokeWidth=0.2
    ).project(
        type='albersUsa'
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(workingData, workingData.cty, columns)).properties(
        width=700,
        height=400)
    return chart

#chart = createMap(DATA)
# chart.show()

def createTable(workingData):
    #slider = alt.binding_range(min=1, max=31, step=1)
    #select_date = alt.selection_single(name="January", fields=workingData.Date, bind=slider)


    return table


# In[ ]:


bin_labels_9 = ['Under 15,000', '15,000 to 24,999', '25,000 to 34,999', 
                '35,000 to 49,999', '50,000 to 74,999', '75,000 to 99,999', 
                '100,000 to 149,999', '150,000 to 199,999', '200,000 and over']
newDATA['Income Range'] = 
for i in range(DATA):
    if DATA.


# In[62]:


alt.data_transformers.disable_max_rows()


slider = alt.binding_range(min=1, max=31, step=1)
select_date = alt.selection_single(name="January", fields=['Date'], bind=slider, init={'Date':1})

state_selector = alt.selection_multi(fields=['statename'], init=[{'statename':'Alabama'}])

table = alt.Chart(DATA).mark_bar().encode(
    x=alt.X('value:Q', title="% of Visits to Doctor about COVID", aggregate="mean", scale=alt.Scale(domain=[0, 25])),
    y=alt.Y('statename:N', title="State")
    ).add_selection(
        state_selector
    ).add_selection(
        select_date
    ).transform_filter(
        select_date)

secondTable = alt.Chart(DATA).mark_bar().encode(
    x=alt.X('value:Q', title="% of Visits to Doctor about COVID", aggregate="mean", scale=alt.Scale(domain=[0,25])),
    y=alt.Y('county_name:N', title = "County"),
    color = alt.Color('punisured2010:Q')
    ).transform_filter(
        state_selector & select_date)

table | secondTable


# In[ ]:


display(DATA[DATA.Date == 10])


# In[46]:


source = pd.DataFrame({
    'a': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
    'b': [28, 55, 43, 91, 81, 53, 19, 87, 52]
})

alt.Chart(source).mark_bar().encode(
    y='a',
    x='b'
)


# In[ ]:




