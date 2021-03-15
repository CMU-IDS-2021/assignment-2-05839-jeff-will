# Health, Wealth, and COVID

![A screenshot of your application. Could be a GIF.](screenshot.png)

## Project Goals

In a time where the divide between the rich and poor is growing vastly and health insurance is becoming more and more expensive (and subsequently) unavailable to many people, we were curious if a medical ailment such as COVID is affecting the poor more negatively than the rich. The goal of this project is to analyze the regional variations in COVID data and see if they can be explained through measures of wealth and healthcare inequality. 

## Design

Variables - The first thing we had to decide on was our variables and the corresponding datasets that we would display. These variables included both a COVID metric and at least one wealth metric. For the COVID metric, we decided to go with “percentage of doctor visits that were COVID related”. For the wealth metrics we decided to go with median home value and percentage of the population that is uninsured.

COVID Doctor Visits - The reason we chose this metric is because it is directly related to health  inequality. If a given county has a higher income, they may visit the doctor more for COVID because they have that option as a commodity whereas a lower income county may not due to insurance reasons or other reasons. 
Median Home Value - We chose to utilize this metric to get a representation of the wealth level of each county.
Percent Uninsured - We chose to analyze this variable because it is expensive and unaffordable to some people.

Displays - We first displayed an interactive bar chart overview to let the user explore how COVID Doctor visit rates vary by both state and county. In this plot the user can filter the bar chart by state to see the different rates among various counties. Next, we display an overview of COVID doctor visit rate by states across the country to see if regional trends can explain the variations. After allowing the user to see how neither trends on a county, state, or regional level can explain the variation we apply a case study that examines the interplay of median home value and percent uninsured. We did this by displaying 3 choropleths of the counties of Pennsylvania. One choropleth displays the COVID doctor visit rate, one displays the percentage of uninsured, and one displays the median home value. At this point the user can then see the overlap in these choropleths. The counties with highest median home value and lowest percent uninsured also have the highest percent COVID doctor visit rate. 


## Development

Data Curation - First we needed to identify what datasets we wanted to use for the project. We chose to go with datasets from reputable sources such as the ones provided on the course webpage. Specifically, we chose a dataset from “COVIDCast” containing percentage of doctor visits that were COVID related and a dataset from “US and Social Mobility” containing health and wealth metrics by county such as percent uninsured and median home value. 
Data Wrangling - The next step was to read in these two datasets to pandas and then merge them by county. Both datasets were CSV formatted so we could read them into pandas with read_csv however, the county statistics dataset had a very strange formatting that was resulting in errors. We figured out that it was “latin” encoding which solved this issue. Both datasets had a mutual column that contained a FIPS code. A FIPS code is like a ZIP code and is a universal method of identifying counties. After ensuring the FIPS codes in each data frame would match we did an inner join to merge them. 
Model Exploration - At first we explored the correlation between median home value (by county) and COVID doctor visit rate (by county). One thing we noticed was that the median home value was actually very skewed. In order to improve some of our initial plots we took the log of the home value variable to reduce this skew. Later in the design process as we changed our desired plots this log transformation was not needed.
First Attempt: Map with Slider and Binned Home Value - We spent much of our time designing a first attempt that had a chloropleth map with a slider option. In order to produce this we binned the data by median home value. This resulted in a binned dataset that was where the bins essentially indicated how rich/poor a given county was. Then used these bins as a slider on a chloropleth map. With the resulting map, one can manipulate the slider to see how poorer counties visited the doctor less for COVID while richer counties visited the doctor more. 
Taking a Step Back - After visiting with a TA, we were told that this was not a very good approach to display this data so we took a step back and restarted with a basic bar chart.
Bar Chart Creation - The interactive bar charts were an interesting challenge that revolved around how to get the information we wanted and to link the charts together while also adding a slider to adjust the time accordingly.  The purpose of this chart was to explore how the COVID doctor visits changed over time and to dive deeper into each state and associated counties to see if the trend was similar across the counties or if there was a mix.
State Map Creation - Next we created a chloropleth to show overall regional trend of COVID doctor visit rate.
 Pennsylvania Case Study - Finally we focus in on the state of Pennsylvania to see if we can determine if things like median home value by county and percentage uninsured are related to COVID doctor visits. 

## Success Story

At the end of the process we did ultimately find that wealth inequality did play a role in how often people visited the doctor for COVID. Counties with higher median home value generally visited the doctor more for COVID. Additionally, counties with higher insurance rates also visited the doctor more for COVID.  Another interesting insight we noticed was that there was a significant downward trend in COVID doctor visits as the month of January went on.  

The final and most important success story for this project was the accomplishment of building an interactive website to explore COVID data.  The entire process was interesting and challenging in that we both had to learn and explore Altair and Streamlit to get the app to do what we wanted it to do.
