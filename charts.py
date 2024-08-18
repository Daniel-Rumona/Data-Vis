import streamlit as st
import streamlit_highcharts as hg
import pandas as pd
import json
import streamlit.components.v1 as components


def load_cleaned_data(location):
    file_path = 'Cleaned-Refined-Anglodata.xlsx'

    # Dictionary to map location names to their respective sheet names
    location_map = {
        "Rustenburg": "Rusty",
        "Rustenburg-AAZ": "Rusty-AAZ",
        "Polokwane": "Polokwane",
        "Polokwane-AAZ": "Polokwane-AAZ",
        "Amandelbult": "Amanda",
        "Amandelbult-AAZ": "Amanda-AAZ",
        "Mogalakwena": "Mogala",
        "Mogalakwena-AAZ": "Mogala-AAZ",
        "Twickenham": "Twik",
        "Twickenham-AAZ": "Twik-AAZ",
        "Mototolo": "Mototolo",
        "Mototolo-AAZ": "Moto-AAZ",
        "Interview-Data": "Cleaned-Interview-Data.csv"
    }

    if location == "Interview-Data":
        df = pd.read_csv(location_map[location])
    else:
        sheet_name = location_map.get(location)
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            raise ValueError(f"Location '{location}' not found in the location map.")

    return df


st.set_page_config(layout="wide")
selectTarget, selectType, selectOption = st.columns(3)
with selectTarget:
    targetCity = st.selectbox(
        options=['Rustenburg', 'Polokwane', 'Amandelbult', 'Mogalakwena', 'Twickenham', 'Mototolo'],
        label="Select Target")
with selectType:
    targetType = st.selectbox(options=['By Frequency', 'By Number Of Jobs'],
                              label="Select Type")
with selectOption:
    vizOption = st.selectbox(options=['Major Sectors', 'Major and Minor Sectors'],
                             label="Select Type")


def get_filtered_avg(df, keyword):
    # Filter columns based on the keyword
    filtered_columns = [col for col in df.columns if col.startswith(keyword)]
    if not filtered_columns:
        st.error(f"No columns found starting with '{keyword}'")
        return pd.DataFrame()

    # Calculate the average of 'Impact' for each filtered column
    avg_impact = df[filtered_columns].mean(axis=0)

    # Create a new DataFrame with the results
    result_df = pd.DataFrame({
        keyword: filtered_columns,
        'Average Score': avg_impact.values
    })

    return result_df


def create_highcharts_pie_chart(df, loc, keyword, title="Impact Analysis"):
    # Filter data for the selected location
    locdf = df[df['Hub'] == loc]

    # Get the filtered average impact scores
    plotdf = get_filtered_avg(locdf, keyword)

    # Check if the DataFrame is empty after filtering
    if plotdf.empty:
        st.warning(f"No data available for location '{loc}' with keyword '{keyword}'")
        return

    # Remove the prefix from the keyword columns for display
    plotdf[keyword] = plotdf[keyword].apply(lambda x: (x[(x.find(':') + 1):]).strip())

    # Prepare data for the pie chart
    data = list(zip(plotdf[keyword], plotdf['Average Score']))

    # Highcharts configuration
    highcharts_config = {
        "chart": {
            "plotBackgroundColor": None,
            'height': 650,
            "plotBorderWidth": 0,
            "plotShadow": False,
            "type": "pie"
        },
        "title": {
            "text": title,
            "align": "center",
            "verticalAlign": "top",  # Align title at the top
            "y": 15,  # Move the title slightly upwards
            "style": {
                "fontSize": "1.5em",  # Adjust font size for better visibility
                "fontWeight": "bold"  # Make the title bold
            }
        },
        "tooltip": {
            "pointFormat": '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        "accessibility": {
            "point": {
                "valueSuffix": '%'
            }
        },
        "plotOptions": {
            "pie": {
                "allowPointSelect": True,
                "cursor": "pointer",
                "dataLabels": {
                    "enabled": True,
                    "distance": -50,  # Distance of the label from the center
                    "format": '{point.percentage:.1f}%',  # Display percentage
                    "style": {
                        "fontWeight": "bold",
                        "color": "white"
                    }
                },
                "showInLegend": True,
                "startAngle": -90,
                "endAngle": 90,
                "center": ['50%', '65%'],  # Move the pie chart down slightly
                "size": '110%'
            }
        },
        "series": [{
            "type": "pie",
            "name": "Average Score",
            "innerSize": '65%',
            "data": data
        }],
        "legend": {
            'labelFormat': '{name}',
            "align": "center",  # Align the legend horizontally
            "verticalAlign": "middle",  # Align the legend at the bottom
            'y': 200
            # "layout": "horizontal",  # Layout the legend horizontally
            # "itemStyle": {
            #     "fontSize": "12px",  # Adjust the font size for the legend
            #     "fontWeight": "normal"
            # }
        }
    }

    # Display Highcharts with the required module
    components.html(
        f"""
        <div id="container"></div>
        <script src="https://code.highcharts.com/highcharts.js"></script>
        <script>
        Highcharts.chart('container', {json.dumps(highcharts_config)});
        </script>
        """,
        height=600,
    )


def create_highcharts_item_chart_unique(df, location, type, title="Main Sector Frequency Distribution", subtitle=""):
    if type.find("Frequency") != -1:
        type = "Frequency"
    else:
        type = "Total Supported"
    # Group by 'Main Sector' and sum the 'Frequency'
    grouped_df = df.groupby('Main Sector')[type].sum().reset_index()

    # Prepare the data
    data = []
    for _, row in grouped_df.iterrows():
        main_sector_name = row['Main Sector']
        # Create shorthand label by taking the first letter of each word in the main sector name
        shorthand_label = ''.join([word[0].upper() for word in main_sector_name.split()])
        data.append([main_sector_name, row[type], None, shorthand_label])

    # Highcharts configuration
    highcharts_config = {
        "chart": {
            "type": "item",
            "height": 620
        },
        "title": {
            "text": title
        },
        "subtitle": {
            "text": subtitle if subtitle else f'{location}. Source: Provided Dataset'
        },
        "legend": {
            "labelFormat": '{name} <span style="opacity: 0.6">{y}</span>',
            'x': 30,
            "layout": "horizontal",  # Arrange legend items vertically
            # "align": "bottom",  # Align the legend to the right of the chart
            "horizontalAlign": "middle",  # Vertically center the legend
            "width": 650,  # Set a fixed width for the legend
            "itemStyle": {
                "width": 300  # Set width for each item in the legend
            }
        },
        "series": [{
            "name": "Frequency",
            "keys": ["name", "y", "color", "label"],
            "data": data,
            "dataLabels": {
                "enabled": True,
                "format": '{point.label}',
                "style": {
                    "textOutline": "3px contrast"
                }
            },
            "center": ["50%", "80%"],
            "size": "125%",
            "startAngle": -100,
            "endAngle": 100
        }],
        "responsive": {
            "rules": [{
                "condition": {
                    "maxWidth": 600
                },
                "chartOptions": {
                    "series": [{
                        "dataLabels": {
                            "distance": -40
                        }
                    }]
                }
            }]
        }
    }

    # Display Highcharts with the required module
    components.html(
        f"""
        <div id="container"></div>
        <script src="https://code.highcharts.com/highcharts.js"></script>
        <script src="https://code.highcharts.com/modules/item-series.js"></script>
        <script>
        Highcharts.chart('container', {json.dumps(highcharts_config)});
        </script>
        """,
        height=700,
    )


col1, col2 = st.columns(2)
with col1:
    df1 = load_cleaned_data(targetCity)
    st.write("Sector Analysis")
    create_highcharts_item_chart_unique(df1, location=f"{targetCity} Data", type="Frequency")
with col2:
    df2 = load_cleaned_data(f"{targetCity}-AAZ")
    st.write("AAZ Analysis")
    create_highcharts_item_chart_unique(df2, location=f"{targetCity} Data", type=targetType)

survey_df = pd.read_csv('Cleaned-Survey-Data.csv')
analysisTargetLocationColumn, analysisTypeColumn = st.columns(2)
# Select the location and keyword
with analysisTargetLocationColumn:
    analysisTargetLocation = st.selectbox(options=[x for x in survey_df['Hub'].unique()], label='Select '
                                                                                                'Location')
with analysisTypeColumn:
    analysisType = st.selectbox(options=list(set(
        x.split(':', 1)[0].strip() for x in survey_df.columns
        if (':' in x) and (not x.startswith('Have:')) and ('Unnamed' not in x)
    )), label='Select Option')
keyword = 'Technology'  # You can choose 'Support' or 'Others' as well
create_highcharts_pie_chart(survey_df, analysisTargetLocation, analysisType,
                            title=f"{analysisType} Impact in {analysisTargetLocation}")
