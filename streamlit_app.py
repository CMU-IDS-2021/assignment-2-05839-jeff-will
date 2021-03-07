import altair as alt
from vega_datasets import data
import pandas as pd
import numpy as np
import streamlit as st
#Load in the datasets------------------------------------------------------------------------
st.title("Does COVID Affect the Rich Differently than the Poor?")

st.write("In order to figure this out, we'll look out two measures of wealth and two measures\
    of COVID effects.")

st.header("Median Home Value vs Percentage of COVID Related Doctor Visits (By County")

st.write("In the graph below, all counties are shown. The higher the color density of the county the higher percentage of doctor\
    visits that were COVID related (01/26 to 02/26. Additionally, median household income is binned and can be toggled with the slider below.\
        Play around with the slider to see if you notice any change in color density from high to low home value counties.")

#Load initial data
COVID = pd.read_csv("covidcast-doctor-visits-smoothed_adj_cli-2021-01-01-to-2021-01-31.csv")
COUNTY = pd.read_csv("health_ineq_online_table_12.csv", encoding = "latin-1")
COUNTY["cty"] = COUNTY["cty"].astype(int)
COVID["geo_value"] = COVID["geo_value"].astype(int)
#Conduct Inner Join on FIPS County Code
DATA = COUNTY.join(COVID.set_index("geo_value"), how = "inner", on = "cty")
#Aggregate Data by Day, using mean....COVID Doctor Visit Data is daily
DATA = DATA.groupby("cty").mean().reset_index()

def bin_and_log_scale(DATA, column):
    #Feature Engineering/ Data Wrangling
    # transform home value to log scale based on observations
    DATA[column] = DATA[column].astype(float)
    #Bin Home value for slider operations
    ranges = column + "_ranges"
    binned = "binned_col"
    DATA[ranges] = pd.qcut(np.log(DATA[column]), 5)
    DATA[binned] = pd.qcut(np.log(DATA[column]), 5, labels = False).astype(str)
    True_Values = []
    DATA_BINNED_GROUPBY = DATA.groupby(by = ["binned_col"]).mean()
    value_list = ((DATA_BINNED_GROUPBY["value"]).tolist())
    DATA_BINNED_GROUPBY["mean_value"] = DATA_BINNED_GROUPBY["value"]
    DATA_BINNED_GROUPBY = DATA_BINNED_GROUPBY["mean_value"]
    bins_list = DATA[ranges].unique().tolist()
    for i in range (5):
        left_value = np.exp(bins_list[i].left)
        right_value = np.exp(bins_list[i].right)
        True_Values.append(left_value)
        True_Values.append(right_value)
    True_Values = (np.sort(np.asarray(True_Values).astype(float)))
    True_Values_Return = []
    for i in range (15):
        if (i%3 == 0):
            True_Values_Return.append(True_Values[int((i*2)/3)])
        elif (i%3 == 1):
            True_Values_Return.append(True_Values[int((i*2)/3) + 1])
        else:
            True_Values_Return.append(value_list[int(i/3)])     
    DATA_BINNED_GROUPBY = DATA_BINNED_GROUPBY.reset_index()
    DATA_BINNED_GROUPBY["binned_col"] = DATA_BINNED_GROUPBY["binned_col"].astype(str)
    DATA_BINNED_GROUPBY = DATA_BINNED_GROUPBY.set_index("binned_col")
    DATA = DATA.join(DATA_BINNED_GROUPBY, how = "inner", on = "binned_col")                     
    return DATA, True_Values_Return

DATA, True_Home_Values = bin_and_log_scale(DATA, "median_house_value")

def create_map(DATA_MAP, FIPS_NAME, binned_col, value_col, SCHEME, low_scale, high_scale):
    DATA_MAP[value_col] = DATA_MAP[value_col].astype(float)
    #Laod US Counties by FIPS
    us_counties = alt.topo_feature(data.us_10m.url, 'counties')
    #Pivot the PD Dataframe such that the columns are each bin of home value and rows are indexed by FIPS Code
    DATA_MAP = DATA_MAP.pivot(index=FIPS_NAME, columns=binned_col, values=value_col).reset_index()
    columns = DATA_MAP.columns[1:6].tolist()
    #Create the slider
    slider = alt.binding_range(min=0, max=4, step=1)
    select_home_value_level = alt.selection_single(name=binned_col, fields=[binned_col],
                                       bind=slider, init={binned_col: 0})
    #Create the chart
    chart = alt.Chart(us_counties).mark_geoshape(
        stroke='black',
        strokeWidth=0.2
    ).project(
        type='albersUsa'
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(DATA_MAP, FIPS_NAME, columns)
    ).transform_fold(
        columns, as_=[binned_col, 'value']
    ).transform_calculate(
        binned_col='parseInt(datum.binned_col)',
        value='isValid(datum.value) ? datum.value : 0'  
    ).encode(
        tooltip = ['value:Q', 'county_name:N'],
        color = alt.condition(
            'datum.value > 0',
            alt.Color('value:Q', scale=alt.Scale(scheme=SCHEME, domain=[low_scale, high_scale])),
            alt.value('#FFFFFF')
        )).add_selection(
        select_home_value_level
    ).properties(
        width=700,
        height=400
    ).transform_filter(
        select_home_value_level
    ) 
    return chart


chart = create_map(DATA, "cty", "binned_col", "mean_value", "greens", 7.5, 9.5)
st.write(chart)

st.write("At first it may seem like there is no noticeable effect. There is one interesting \
    observation that the home values in the middle of the range seem to have very low COVID doctor visits\
        while the richest and the poorest have the highest COVID Doctor visits. This may be the result of 2 phenomenon. The\
            rich have time to visit the docor more for COVID while the poor are still more likely to be affected by it.")


True_Home_Values = np.reshape(True_Home_Values, (5, 3))
TRUE_HOME_VALUES = pd.DataFrame(True_Home_Values, columns = ['Median Home Value Bin Lower', 'Median Home Value Bin Upper', 'Percent of Doctor Visits COVID Related'])
#pd.options.display.float_format = "{:,.2f}".format
TRUE_HOME_VALUES = TRUE_HOME_VALUES.round(2)
TRUE_HOME_VALUES = TRUE_HOME_VALUES.astype(str)
TRUE_HOME_VALUES['Median Home Value Bin Lower'] = '$' + TRUE_HOME_VALUES['Median Home Value Bin Lower']
TRUE_HOME_VALUES['Median Home Value Bin Upper'] = '$' + TRUE_HOME_VALUES['Median Home Value Bin Upper']
st.write(TRUE_HOME_VALUES)


st.write("Let's consider another measure of wealth, median income, and see if we notice the same phenomenon.")

st.header("Median Income vs Percentage of COVID Related Doctor Visits (By County)")

COUNTY2 = pd.read_csv("cty_covariates.csv", encoding = "latin1")
#This data set does not come with FIPS so we have to create it by appending state and county FIPS
COUNTY2["FIPS"] = (COUNTY2["state"]*1000 + COUNTY2["county"]).astype(int)
#Conduct Inner Join on FIPS County Code
DATA = COUNTY2.join(COVID.set_index("geo_value"), how = "inner", on = "FIPS")
#Aggregate Data by Day, using mean....COVID Doctor Visit Data is daily
DATA = DATA.groupby("FIPS").mean().reset_index()

DATA, True_Inc_Values = bin_and_log_scale(DATA, "hhinc_mean2000")

chart = create_map(DATA, "FIPS", "binned_col", "mean_value", "greens", 7.5, 10)
st.write(chart)

st.write("Again, it seems like the counties with the highest percentage of COVID Doctor visits are both the poorest and richest counties.")

True_Inc_Values = np.reshape(True_Inc_Values, (5, 3))
INC_VALUES = pd.DataFrame(True_Inc_Values, columns = ['Median Income Bin Lower', 'Median Income Bin Upper', 'Percent of Doctor Visits COVID Related'])
#pd.options.display.float_format = "{:,.2f}".format
INC_VALUES = INC_VALUES.round(2)
INC_VALUES = INC_VALUES.astype(str)
INC_VALUES['Median Income Bin Lower'] = '$' + INC_VALUES['Median Income Bin Lower']
INC_VALUES['Median Income Bin Upper'] = '$' + INC_VALUES['Median Income Bin Upper']
st.write(INC_VALUES)

st.write("Perhaps percentage of COVID Doctor Visits is a bit obfuscated. Let's look at a more grim measure, COVID related Deaths.")

st.header("Median Home Value vs Percentage of COVID Deaths (By County")

COVID = pd.read_csv("covidcast-indicator-combination-confirmed_incidence_prop-2021-01-26-to-2021-01-26.csv")
#COVID = pd.read_csv("covidcast-doctor-visits-smoothed_adj_cli-2021-01-01-to-2021-01-31.csv")
COUNTY = pd.read_csv("health_ineq_online_table_12.csv", encoding = "latin-1")
COUNTY["cty"] = COUNTY["cty"].astype(int)
COVID["geo_value"] = COVID["geo_value"].astype(int)
#Conduct Inner Join on FIPS County Code
DATA = COUNTY.join(COVID.set_index("geo_value"), how = "inner", on = "cty")
#Aggregate Data by Day, using mean....COVID Doctor Visit Data is daily
DATA = DATA.groupby("cty").mean().reset_index()
DATA = DATA[(DATA["median_house_value"] != 0)]

DATA, True_Home_Values = bin_and_log_scale(DATA, "median_house_value")

chart = create_map(DATA, "cty", "binned_col", "mean_value", "reds", 30, 90)
st.write(chart)

True_Home_Values = np.reshape(True_Home_Values, (5, 3))
TRUE_HOME_VALUES = pd.DataFrame(True_Home_Values, columns = ['Median Home Value Bin Lower', 'Median Home Value Bin Upper', 'COVID Deaths per 100,000 People'])
#pd.options.display.float_format = "{:,.2f}".format
TRUE_HOME_VALUES = TRUE_HOME_VALUES.round(2)
TRUE_HOME_VALUES = TRUE_HOME_VALUES.astype(str)
TRUE_HOME_VALUES['Median Home Value Bin Lower'] = '$' + TRUE_HOME_VALUES['Median Home Value Bin Lower']
TRUE_HOME_VALUES['Median Home Value Bin Upper'] = '$' + TRUE_HOME_VALUES['Median Home Value Bin Upper']
st.write(TRUE_HOME_VALUES)

st.write("Wow! This one is even more even out throughout the ranks of society. Let's look at how COVID realted deaths realte to median income.")
st.header("Median Income vs Percentage of COVID Deaths (By County)")

#This data set does not come with FIPS so we have to create it by appending state and county FIPS
COUNTY2["FIPS"] = (COUNTY2["state"]*1000 + COUNTY2["county"]).astype(int)
#Conduct Inner Join on FIPS County Code
DATA = COUNTY2.join(COVID.set_index("geo_value"), how = "inner", on = "FIPS")
#Aggregate Data by Day, using mean....COVID Doctor Visit Data is daily
DATA = DATA.groupby("FIPS").mean().reset_index()
DATA = DATA.dropna(subset = ["hhinc_mean2000"])
DATA = DATA[(DATA["hhinc_mean2000"] != 0)]

#Aggregate Data by Day, using mean....COVID Doctor Visit Data is daily
DATA, True_Inc_Values = bin_and_log_scale(DATA, "hhinc_mean2000")


chart = create_map(DATA, "FIPS", "binned_col", "mean_value", "reds", 30, 90)
st.write(chart)


True_Inc_Values = np.reshape(True_Inc_Values, (5, 3))
INC_VALUES = pd.DataFrame(True_Inc_Values, columns = ['Median Income Bin Lower', 'Median Income Bin Upper', 'COVID Deaths per 100,000 People'])
#pd.options.display.float_format = "{:,.2f}".format
INC_VALUES = INC_VALUES.round(2)
INC_VALUES = INC_VALUES.astype(str)
INC_VALUES['Median Income Bin Lower'] = '$' + INC_VALUES['Median Income Bin Lower']
INC_VALUES['Median Income Bin Upper'] = '$' + INC_VALUES['Median Income Bin Upper']
st.write(INC_VALUES)
