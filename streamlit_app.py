"""import streamlit as st
import pandas as pd
import altair as alt

st.title("Let's analyze some Penguin Data 🐧📊.")

@st.cache  # add caching so we load the data only once
def load_data():
    # Load the penguin data from https://github.com/allisonhorst/palmerpenguins.
    penguins_url = "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/v0.1.0/inst/extdata/penguins.csv"
    return pd.read_csv(penguins_url)

df = load_data()

st.write("Let's look at raw data in the Pandas Data Frame.")

st.write(df)

st.write("Hmm 🤔, is there some correlation between body mass and flipper length? Let's make a scatterplot with [Altair](https://altair-viz.github.io/) to find.")

chart = alt.Chart(df).mark_point().encode(
    x=alt.X("body_mass_g", scale=alt.Scale(zero=False)),
    y=alt.Y("flipper_length_mm", scale=alt.Scale(zero=False)),
    color=alt.Y("species")
).properties(
    width=600, height=400
).interactive()

st.write(chart)"""
import altair as alt
from vega_datasets import data
import pandas as pd
import numpy as np

#Load in the datasets------------------------------------------------------------------------
COUNTY = pd.read_csv("health_ineq_online_table_12.csv")
COVID = pd.read_csv("covidcast-doctor-visits-smoothed_adj_cli-2021-01-26-to-2021-02-26.csv")
#Assign type int to the FIPS County Code we wil join on
COUNTY["cty"] = COUNTY["cty"].astype(int)
COVID["geo_value"] = COVID["geo_value"].astype(int)

#Conduct Inner Join on FIPS County Code
DATA = COUNTY.join(COVID.set_index("geo_value"), how = "inner", on = "cty")

#Aggregate Data by Day, using mean....COVID Doctor Visit Data is daily
DATA = DATA.groupby("cty").mean().reset_index()

print(DATA.columns)

#Feature Engineering/ Data Wrangling-----------------------------------------------------------------------
display(DATA["median_house_value"])
# transform home value to log scale based on observations
DATA.median_house_value = DATA.median_house_value.astype(float) 
#Bin Home value for slider operations
DATA["binned_home_value_ranges"] = pd.cut(np.log(DATA["median_house_value"]), 10)
DATA["binned_home_value"] = pd.cut(np.log(DATA["median_house_value"]), 10, labels = False)

display(DATA["median_house_value"])

True_Home_Values = []


bins_list = DATA["binned_home_value_ranges"].unique().tolist()
for i in range (10):
    left_value = np.exp(bins_list[i].left)
    right_value = np.exp(bins_list[i].right)
    True_Home_Values.append(left_value)
    True_Home_Values.append(right_value)
    
True_Home_Values = (np.sort(np.asarray(True_Home_Values).astype(float)))

#Preparatory Operations to conduct Altair map plot----------------------------------------------------------

#Laod US Counties by FIPS
us_counties = alt.topo_feature(data.us_10m.url, 'counties')

#Ensure binned home values are of type int
DATA['binned_home_value'] = DATA['binned_home_value'].astype(str)

#Ensure value (which is percent Doctor visits that are covid realted) is float
DATA['value'] = DATA['value'].astype(float)

#Pivot the PD Dataframe such that the columns are each bin of home value and rows are indexed by FIPS Code
DATA_BY_HOME_VALUE = DATA.pivot(index='cty', columns='binned_home_value', values='value').reset_index()
columns = DATA_BY_HOME_VALUE.columns[1:10].tolist()

#Altair Map Plot------------------------------------------------------------------------

slider = alt.binding_range(min=0, max=9, step=1)
select_home_value_level = alt.selection_single(name="binned_home_value", fields=['binned_home_value'],
                                   bind=slider, init={'binned_home_value': 0})

alt.Chart(us_counties).mark_geoshape(
    stroke='black',
    strokeWidth=0.2
).project(
    type='albersUsa'
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(DATA_BY_HOME_VALUE, 'cty', columns)
).transform_fold(
    columns, as_=['binned_home_value', 'value']
).transform_calculate(
    binned_home_value='parseInt(datum.binned_home_value)',
    value='isValid(datum.value) ? datum.value : 0'  
).encode(
    tooltip = ['value:Q', 'county_name:N'],
    color = alt.condition(
        'datum.value > 0',
        alt.Color('value:Q', scale=alt.Scale(scheme='reds')),
        alt.value('#FFFFFF')
    )).add_selection(
    select_home_value_level
).properties(
    width=700,
    height=400
).transform_filter(
    select_home_value_level
)

#Displaying Home Values (Bins) for User Transparancey------------------------------------------------------------------
True_Home_Values = np.reshape(True_Home_Values, (10, 2))
HOME_VALUES = pd.DataFrame(True_Home_Values, columns = ['Median Home Value Bin Lower', 'Median Home Value Bin Upper'])
#pd.options.display.float_format = "{:,.2f}".format
HOME_VALUES = HOME_VALUES.round(2)
HOME_VALUES = HOME_VALUES.astype(str)
HOME_VALUES['Median Home Value Bin Lower'] = '$' + HOME_VALUES['Median Home Value Bin Lower']
HOME_VALUES['Median Home Value Bin Upper'] = '$' + HOME_VALUES['Median Home Value Bin Upper']
display(HOME_VALUES)
