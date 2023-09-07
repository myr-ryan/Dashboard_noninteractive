import streamlit as st
import pandas as pd
import leafmap.foliumap as leafmap
import folium

from Plot_Data import *
# from Pie_chart import *
from Pie_chart_st import *
from Heatmap_st import *
from Bar_chart_st import *
from utils import apply_cat_filters, get_location
from streamlit_option_menu import option_menu

# st.set_page_config(
#     page_title='Dashboard',
#     layout='wide',
# )

# st.title("Dashboard")

f = 'datasheet/datasheet.xlsx'
datasheet = pd.read_excel(f, sheet_name='Sheet1', engine='openpyxl')

empty_data = {'x':[],'y':[]}
plot_data = Plot_Data(empty_data)
plot_data.preprocessing(df=datasheet)

# with tab1: 
def neural_networks():
    st.markdown("### Filters")
    cancer_type_cb = st.checkbox("cancer types", False)
    if cancer_type_cb:
        global plot_data
        ct = st.sidebar.multiselect('cancer types', plot_data.subspec_list, [])
        plot_data = apply_cat_filters(ct, plot_data, 'subspec')
    
    # selected_filters = [f for f_name, f in filters.items() if st.sidebar.checkbox(f_name, True)]
    # df = pd.DataFrame(plot_data.source.data).copy()
    pie_generator = PieChart_st(plot_data=plot_data)
    # pie_chart_columns = ['neural_network_type', 'explainability', 'augmentation_techniques', 'task']
    pie_1 = pie_generator.generate_plot(column_name='neural_network_type')
    pie_2 = pie_generator.generate_plot(column_name='explainability')
    pie_3 = pie_generator.generate_plot(column_name='augmentation_techniques')
    pie_4 = pie_generator.generate_plot(column_name='task')

    # st.bokeh_chart(pie_2, use_container_width=False)

    col_1, col_2 = st.columns(2)
    with col_1:
        with st.container():
            st.bokeh_chart(pie_1, use_container_width=False)
            st.bokeh_chart(pie_2, use_container_width=False)
    with col_2:
        with st.container():
            st.bokeh_chart(pie_3, use_container_width=False)
            st.bokeh_chart(pie_4, use_container_width=False)

def neural_network_performance():
    heatmap_generator = Heatmap_st(plot_data=plot_data)

    heat_1 = heatmap_generator.generate_plot(column_name='neural_network_type', exclude_seg=True)
    heat_2 = heatmap_generator.generate_plot(column_name='subspec', exclude_prefix=True)
    heat_3 = heatmap_generator.generate_plot(column_name='task', exclude_prefix=True)
    heat_4 = heatmap_generator.generate_plot(column_name='DataSize_all', exclude_seg=True)
    

    # st.bokeh_chart(heat_1, use_container_width=False)

    col_1, col_2 = st.columns(2)
    with col_1:
        with st.container():
            st.bokeh_chart(heat_1, use_container_width=False)
            st.bokeh_chart(heat_2, use_container_width=False)
    with col_2:
        with st.container():
            st.bokeh_chart(heat_3, use_container_width=False)
            # heat_4_column = st.selectbox("Data size", ('DataSize_all', 'DataSize_training', 'DataSize_testing', 'DataSize_validation'))
            st.bokeh_chart(heat_4, use_container_width=False)
            

def key_statistics():
    barchart_generator = BarChart_st(plot_data=plot_data)

    bar_1 = barchart_generator.generate_plot(column_name='year')

    st.bokeh_chart(bar_1, use_container_width=True)
    # ROADMAP, TERRAIN, SATELLITE, HYBRID
    m = leafmap.Map(locate_control=True, google_map="TERRAIN")
    location = get_location(plot_data, "affil_first_country")
    # print(location)
    # m.add_circle_markers_from_xy(location, popup=['country', 'count'], radius=5)
    # m.add_markers_from_xy(location, popup=['countries', 'count'])
    # m.add_data(location, 'countries')
    for index, row in location.iterrows():
        radius = row['radius']
        lat = row['latitude']
        lon = row['longitude']
        country = row['country']
        count = str(row['count'])

        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.6,
            popup= folium.Popup("Country: "+country+"\nCount: "+count)
        ).add_to(m)
    
    m.to_streamlit(height=700)

page_names_to_funcs = {
    "Key statistics": key_statistics,
    "Neural network Performances": neural_network_performance,
    "Neural networks": neural_networks
}


# chart_name = st.sidebar.selectbox("Choose a chart", page_names_to_funcs.keys())
# page_names_to_funcs[chart_name]()




#################################################################################
# One option for the navigation bar
selected = option_menu(
    menu_title=None,
    options=["Key statistics", "Neural network Performances", "Neural networks"],
    # icons=["house", "book"],
    # menu_icon="cast",
    default_index=2,
    orientation="horizontal",
)


if selected == "Key statistics":
    key_statistics()
elif selected == "Neural network Performances":
    neural_network_performance()
elif selected == "Neural networks":
    neural_networks()
#################################################################################
