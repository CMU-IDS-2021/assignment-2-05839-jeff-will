import altair as alt
from vega_datasets import data
import pandas as pd
import numpy as np
import streamlit as st


def load_data():
    COVID = pd.read_csv("covidcast-doctor-visits-smoothed_adj_cli-2021-01-01-to-2021-01-31.csv")
    COUNTY = pd.read_csv("health_ineq_online_table_12.csv", encoding = "latin-1")
    COUNTY["cty"] = COUNTY["cty"].astype(int)
    COVID["geo_value"] = COVID["geo_value"].astype(int)
    DATA = COUNTY.join(COVID.set_index("geo_value"), how = "inner", on = "cty")
    DATA['Date'] = pd.to_datetime(DATA.time_value)
    DATA['Date'] = DATA.Date.dt.strftime('%d').astype(int)
    return DATA[["Date", "cty", "statename", "state_id", "county_name", "value", "median_house_value", "puninsured2010"]]

DATA = load_data()

st.title("% of Doctor Visits by State and County")
st.write("In this section, we explore the percentage of doctor visits for COVID by State and County.  We begin by hilighting Pennsylvania and as we can see, there are some interesting observatins for <> county.  As you probably noticed, there looks to be a correlation between ")

alt.data_transformers.disable_max_rows()

slider = alt.binding_range(min=1, max=31, step=1)
select_date = alt.selection_single(name="January", fields=['Date'], bind=slider, init={'Date':1})

state_selector = alt.selection_multi(fields=['statename'], init=[{'statename':'Pennsylvania'}])

States = alt.Chart(DATA).mark_bar().encode(
    x=alt.X('value:Q', title="% of Visits to Doctor about COVID", aggregate="mean", scale=alt.Scale(domain=[0, 35])),
    y=alt.Y('statename:N', title="State"),
    color=alt.condition(state_selector, alt.value("#f76f5c"), alt.value("#451076")),
    tooltip=[alt.Tooltip("statename:N", title='State'), alt.Tooltip("value:Q", aggregate="mean", title="% of COVID Doctor Visits", format='.2f')]
    ).add_selection(
        state_selector
    ).add_selection(
        select_date
    ).transform_filter(
        select_date).interactive()

Counties = alt.Chart(DATA).mark_bar(color='#451076').encode(
    x=alt.X('value:Q', title="% of Visits to Doctor about COVID", scale=alt.Scale(domain=[0,35])),
    y=alt.Y('county_name:N', title = "County"),
    tooltip=[alt.Tooltip("statename:N", title='State'), alt.Tooltip("county_name:N", title='County'),alt.Tooltip("value:Q", aggregate="mean", title="% of COVID Doctor Visits", format='.2f'), alt.Tooltip("puninsured2010:Q", aggregate="mean", title="% Uninsured (as of 2010)", format='.2f')]
    ).transform_filter(
        state_selector & select_date).interactive()
joint_chart = States | Counties
st.write(joint_chart)


st.header("Geographical Representation")

st.write("Now that we've had a chance to explore how COVID Docotor visits vary by state and county, let's look at a geographical representaion to see if we can spot any regional trends that weren't present earlier.")



alt.data_transformers.disable_max_rows()


DATA["COVID_Doctor_Visits"] = DATA["value"].astype(float).round(2)
DATA["State_Name"] = DATA["statename"]
DATA["County_Name"] = DATA["county_name"]
DATA["Percent_Uninsured"] = DATA["puninsured2010"].astype(float).round(2)

DATA["state_id"] = DATA["state_id"].astype(int)

states = alt.topo_feature(data.us_10m.url, 'states')

DATA_STATE = DATA.groupby("State_Name").mean()

DATA_STATE = DATA_STATE.reset_index()

DATA_STATE["state_id"] = DATA_STATE["state_id"].astype(int)
DATA_STATE["state_id"] = DATA_STATE["state_id"].astype(str)

#Create the chart
state_chart = alt.Chart(states).mark_geoshape(
    stroke='black',
    strokeWidth=0.2
).project(
    type='albersUsa'
).properties(
        width=700,
        height=400
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(DATA_STATE, 'state_id', ["COVID_Doctor_Visits", "State_Name", "Percent_Uninsured"])
).encode(
    tooltip = ["State_Name:N", 'COVID_Doctor_Visits:Q', "Percent_Uninsured:Q", alt.Tooltip("COVID_Doctor_Visits:Q", format=".2%")],
    color = alt.condition(
        'datum.COVID_Doctor_Visits > 0',
        alt.Color('COVID_Doctor_Visits:Q', scale=alt.Scale(scheme="magma", domain=[0, 20])),
        alt.value('#FFFFFF')
    )
)




counties = alt.topo_feature(data.us_10m.url, 'counties')

DATA_ALABAMA = DATA[DATA["statename"] == "Pennsylvania"]
DATA_CTY = DATA_ALABAMA.groupby("County_Name").mean()

DATA_CTY = DATA_CTY.reset_index()

DATA_CTY["cty"] = DATA_CTY["cty"].astype(int)
DATA_CTY["cty"] = DATA_CTY["cty"].astype(str)


#Create the chart
county_chart_LA_doctor = alt.Chart(counties).mark_geoshape(
    stroke='black',
    strokeWidth=0.2
).project(
    type='albersUsa'
).properties(
        width=700,
        height=400
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(DATA_CTY, 'cty', ["COVID_Doctor_Visits", "County_Name", "Percent_Uninsured"])
).encode(
    tooltip = ["County_Name:N", 'COVID_Doctor_Visits:Q', "Percent_Uninsured:Q"],
    color = alt.condition(
        'datum.COVID_Doctor_Visits > 0',
        alt.Color('COVID_Doctor_Visits:Q', scale=alt.Scale(scheme="magma", domain=[0, 20])),
        alt.value('#FFFFFF')
    )
)

#Create the chart
county_chart_LA_puninsured = alt.Chart(counties).mark_geoshape(
    stroke='black',
    strokeWidth=0.2
).project(
    type='albersUsa'
).properties(
        width=700,
        height=400
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(DATA_CTY, 'cty', ["COVID_Doctor_Visits", "County_Name", "Percent_Uninsured"])
).encode(
    tooltip = ["County_Name:N", 'COVID_Doctor_Visits:Q', "Percent_Uninsured:Q"],
    color = alt.condition(
        'datum.Percent_Uninsured > 0',
        alt.Color('Percent_Uninsured:Q', scale=alt.Scale(scheme="magma", domain=[0, 40])),
        alt.value('#FFFFFF')
    )
)

#Create the chart
county_chart_LA_home_value = alt.Chart(counties).mark_geoshape(
    stroke='black',
    strokeWidth=0.2
).project(
    type='albersUsa'
).properties(
        width=700,
        height=400
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(DATA_CTY, 'cty', ["COVID_Doctor_Visits", "County_Name", "Percent_Uninsured", "median_house_value"])
).encode(
    tooltip = ["County_Name:N", 'COVID_Doctor_Visits:Q', "Percent_Uninsured:Q", "median_house_value:Q"],
    color = alt.condition(
        'datum.median_house_value > 0',
        alt.Color('median_house_value:Q', scale=alt.Scale(scheme="magma")),
        alt.value('#FFFFFF')
    )
)
st.header("COVID Doctor Visits By State")
st.write(state_chart)
st.write("In the chart above we can see that even outside of counties and states there are some bigger regional trends going on. The southeastern states tend have higher percentage of doctor visits that are COVID related related while the northwestern states have a lower percentage. SOme other anomalies stand out and that is California and New/New Jersey. These states likely have a higher percentage of COVID related Doctor vists due to the dense urban citiies within them.")

st.header("Pennsylvania Case Study")
st.write("In order to get a more focused understanding of COVID Doctor Visits vary by location, we can take all the counties in Pennsylvania as a case study.")
st.write(county_chart_LA_doctor)
st.write("In the chart above we can see that COVID Doctor visits vary a lot by county. As you hover over the various counties below you can see how differnt metics by county change such as median home value and percent uninsured.")

st.write(county_chart_LA_puninsured)
st.write("If we display the percentage of residents that are uninsured we can actually see that it has some overlap to the map above (COVID Doctor Vists). Counties with higher percent uninsured tend to have lower COVID related Doctor visits. As medical insurance costs money, it is likely that there is a welath-class interplay going on here.")

st.write(county_chart_LA_home_value)
st.write("If we dislay median home value we can narrow down the analysis even more. Consider two drastically differnt counties, Bucks in the southeast and Warren in the northwest. Buck is a relatively wealthy county and we can see by hovering that is has ~13 percent COVID Doctor visit rate with only ~9 percent uninsured. Warren on the other hand, with a much lower median home value, has a ~8 percent COVID Doctor visit rate and ~12 percent uninsured. We can liekly conclude here that COVID is affecting these poorer counties more negatively than the richer counties.")
