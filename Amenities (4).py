#!/usr/bin/env python
# coding: utf-8

# In[1]:


from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import osmnx as ox
get_ipython().run_line_magic('matplotlib', 'inline')


# In[95]:


# adding neighborhoods file
import geopandas as gpd
nhoods = gpd.read_file("Neighborhood Tabulation Areas.geojson")
nhoods.rename(columns = {'ntaname':'Neighborhood'}, inplace = True)
nhoods.crs = {'init': 'epsg:4326'}

# adding boroughs file
import geopandas as gpd
boroughs = gpd.read_file("Borough Boundaries.geojson")
boroughs.rename(columns = {'boro_name':'Borough'}, inplace = True)


# In[3]:


# building the map
import folium

    # defining functions to set the styles
def get_style(feature):
    return {'weight': 2, 'color': 'grey'}
def get_highlighted_style(feature):
    return {'weight': 2, 'color': 'red'}

    # basemap
m = folium.Map(
    location=[40.724174, -73.921368], 
    tiles='CartoDB Positron', 
    zoom_start=10.2)
 
    # adding nhoods geojson
folium.GeoJson(
    nhoods.to_json(), 
    name='Neighborhoods', 
    style_function=get_style, 
    highlight_function=get_highlighted_style, 
    tooltip=folium.GeoJsonTooltip(['Neighborhood'])
).add_to(m)
    
    # adding boroughs geojson
folium.GeoJson(
    boroughs.to_json(), 
    name='Boroughs', 
    style_function=get_style, 
    highlight_function=get_highlighted_style, 
    tooltip=folium.GeoJsonTooltip(['Borough'])
).add_to(m)

    # adding option to toggle layers
folium.LayerControl().add_to(m)

m


# In[4]:


# finding boundary of New York City
NYC = ox.gdf_from_place('New York City, New York, USA')
boundary = NYC.bounds
boundary


# In[5]:


# importing amenities
import pandana as pnda
from pandana.loaders import osm

    # DINING
NYC_restaurants = osm.node_query(40.477399, -74.25909, 40.916179, -73.700181, tags='"amenity"="restaurant"')
NYC_restaurants = NYC_restaurants[['lat','lon','amenity','name']]
NYC_cafes = osm.node_query(40.477399, -74.25909, 40.916179, -73.700181, tags='"amenity"="cafe"')
NYC_cafes = NYC_cafes[['lat','lon','amenity','name']]

NYC_dining = NYC_restaurants.append(NYC_cafes)
NYC_dining


# In[6]:


# NIGHTLIFE
NYC_bar = osm.node_query(40.477399, -74.25909, 40.916179, -73.700181, tags='"amenity"="bar"')
NYC_bar = NYC_bar[['lat','lon','amenity','name']]
NYC_nightclub = osm.node_query(40.477399, -74.25909, 40.916179, -73.700181, tags='"amenity"="nightclub"')
NYC_nightclub = NYC_nightclub[['lat','lon','amenity','name']]

NYC_nightlife = NYC_bar.append(NYC_nightclub)  
NYC_nightlife


# In[7]:


# creating Pandana network
net = osm.pdna_network_from_bbox(40.477399, -74.25909, 40.916179, -73.700181, network_type="walk")


# In[8]:


# creating dining amenities heatmap
from folium.plugins import HeatMap

dining_coordinates = NYC_dining[['lat', 'lon']].values


    # defining functions to set the styles
def get_style2(feature):
    return {'weight': 2, 'color': 'white'}
def get_highlighted_style2(feature):
    return {'weight': 2, 'color': 'black'}

    # basemap
m = folium.Map(
    location=[40.724174, -73.921368],
    tiles='Cartodb dark_matter',
    zoom_start=10.2
)

    # dining amenities heatmap
HeatMap(
    dining_coordinates, 
    name='Dining amenities',
    gradient={0.85: 'orange', 1: 'red'}
).add_to(m)

    # adding nhoods geojson
folium.GeoJson(
    nhoods.to_json(), 
    name='Neighborhoods', 
    style_function=get_style2, 
    highlight_function=get_highlighted_style2, 
    tooltip=folium.GeoJsonTooltip(['Neighborhood'])
).add_to(m)
    
    # adding boroughs geojson
folium.GeoJson(
    boroughs.to_json(), 
    name='Boroughs', 
    style_function=get_style2, 
    highlight_function=get_highlighted_style2, 
    tooltip=folium.GeoJsonTooltip(['Borough'])
).add_to(m)

    # adding option to toggle layers
folium.LayerControl().add_to(m)

m


# In[9]:


# creating nightlife amenities heatmap
nightlife_coordinates = NYC_nightlife[['lat', 'lon']].values

    # basemap
m = folium.Map(
    location=[40.724174, -73.921368],
    tiles='Cartodb dark_matter',
    zoom_start=10.2
)

    # nightlife amenities heatmap
HeatMap(
    nightlife_coordinates, 
    name='Nightlife amenities',
    gradient={0.5: 'orange', 1: 'red'}
).add_to(m)

    # adding nhoods geojson
folium.GeoJson(
    nhoods.to_json(), 
    name='Neighborhoods', 
    style_function=get_style2, 
    highlight_function=get_highlighted_style2, 
    tooltip=folium.GeoJsonTooltip(['Neighborhood'])
).add_to(m)
    
    # adding boroughs geojson
folium.GeoJson(
    boroughs.to_json(), 
    name='Boroughs', 
    style_function=get_style2, 
    highlight_function=get_highlighted_style2, 
    tooltip=folium.GeoJsonTooltip(['Borough'])
).add_to(m)

    # adding option to toggle layers
folium.LayerControl().add_to(m)

m


# In[10]:


max_distance = 2000  # in meters
num_pois = 10  # only need the 10 nearest POI to each point in the network

# Tell the network where the dining amenities are
amenities = NYC_dining['amenity'].unique()
for amenity in amenities:

    # get the subset of amenities for this type
    pois_subset = NYC_dining[NYC_dining["amenity"] == amenity]

    # set the POI, using the longitude and latitude of POI
    net.set_pois(
        amenity, max_distance, num_pois, pois_subset["lon"], pois_subset["lat"]
    )


# In[11]:


# getting distances from nodes to nearest cafe
amenity = 'cafe'
access = net.nearest_pois(distance=1000, category=amenity, 
                          num_pois=num_pois)

access.head(n=20)


# In[12]:


# merging coordinates of network nodes with distances to nearest cafes

def to_geopandas(df, xcol='x', ycol='y'):
    """
    Utility function to convert from DataFrame to GeoDataFrame
    """
    from shapely.geometry import Point
    
    df['geometry'] = df.apply(lambda row: Point(row[xcol], row[ycol]), axis=1)
    return gpd.GeoDataFrame(df, geometry='geometry', crs={'init':'epsg:4326'})

nodes = pd.merge(net.nodes_df, access, left_index=True, right_index=True)    
nodes = to_geopandas(nodes)

nodes


# In[13]:


# FINDING AVERAGE DISTANCE TO 1st/5th/10th NEAREST CAFE BY NEIGHBORHOOD

    # performing spatial join with nhoods shapefile
nhood_nodes = gpd.sjoin(nodes, nhoods, op='within', how='left')
nhood_nodes = nhood_nodes.dropna(subset=['Neighborhood']) 
nhood_nodes


# In[14]:


from geopandas import GeoDataFrame
cafe_distances = GeoDataFrame(nhood_nodes)
nearest_cafe = cafe_distances.groupby(['Neighborhood'])[1].mean()
nearest_cafe = nearest_cafe.reset_index()

second_nearest_cafe = cafe_distances.groupby(['Neighborhood'])[2].mean()
second_nearest_cafe = second_nearest_cafe.reset_index()

third_nearest_cafe = cafe_distances.groupby(['Neighborhood'])[3].mean()
third_nearest_cafe = third_nearest_cafe.reset_index()

fourth_nearest_cafe = cafe_distances.groupby(['Neighborhood'])[4].mean()
fourth_nearest_cafe = fourth_nearest_cafe.reset_index()

fifth_nearest_cafe = cafe_distances.groupby(['Neighborhood'])[5].mean()
fifth_nearest_cafe = fifth_nearest_cafe.reset_index()

sixth_nearest_cafe = cafe_distances.groupby(['Neighborhood'])[6].mean()
sixth_nearest_cafe = sixth_nearest_cafe.reset_index()

seventh_nearest_cafe = cafe_distances.groupby(['Neighborhood'])[7].mean()
seventh_nearest_cafe = seventh_nearest_cafe.reset_index()

eighth_nearest_cafe = cafe_distances.groupby(['Neighborhood'])[8].mean()
eighth_nearest_cafe = eighth_nearest_cafe.reset_index()

ninth_nearest_cafe = cafe_distances.groupby(['Neighborhood'])[9].mean()
ninth_nearest_cafe = ninth_nearest_cafe.reset_index()

tenth_nearest_cafe = cafe_distances.groupby(['Neighborhood'])[10].mean()
tenth_nearest_cafe = tenth_nearest_cafe.reset_index()


# In[15]:


# merging them all
dfs = [nearest_cafe, second_nearest_cafe, third_nearest_cafe, fourth_nearest_cafe, fifth_nearest_cafe, sixth_nearest_cafe, seventh_nearest_cafe, eighth_nearest_cafe, ninth_nearest_cafe, tenth_nearest_cafe]
nth_nearest_cafe = pd.concat(dfs, join='outer', axis=1)
nth_nearest_cafe = nth_nearest_cafe.loc[:,~nth_nearest_cafe.columns.duplicated()]

nth_nearest_cafe


# In[16]:


# rinse and repeat for restaurants
    
    # getting distances from nodes to nearest restaurant
amenity = 'restaurant'
access = net.nearest_pois(distance=1000, category=amenity, 
                          num_pois=num_pois)
    
    # merging coordinates of network nodes with distances to nearest restaurants
nodes = pd.merge(net.nodes_df, access, left_index=True, right_index=True)    
nodes = to_geopandas(nodes)

    # performing spatial join with nhoods shapefile
nhood_nodes = gpd.sjoin(nodes, nhoods, op='within', how='left')
nhood_nodes = nhood_nodes.dropna(subset=['Neighborhood']) 

    # finding average distance to nth nearest restaurant
from geopandas import GeoDataFrame
res_distances = GeoDataFrame(nhood_nodes)
nearest_res = res_distances.groupby(['Neighborhood'])[1].mean()
nearest_res = nearest_res.reset_index()

second_nearest_res = res_distances.groupby(['Neighborhood'])[2].mean()
second_nearest_res = second_nearest_res.reset_index()

third_nearest_res = res_distances.groupby(['Neighborhood'])[3].mean()
third_nearest_res = third_nearest_res.reset_index()

fourth_nearest_res = res_distances.groupby(['Neighborhood'])[4].mean()
fourth_nearest_res = fourth_nearest_res.reset_index()

fifth_nearest_res = res_distances.groupby(['Neighborhood'])[5].mean()
fifth_nearest_res = fifth_nearest_res.reset_index()

sixth_nearest_res = res_distances.groupby(['Neighborhood'])[6].mean()
sixth_nearest_res = sixth_nearest_res.reset_index()

seventh_nearest_res = res_distances.groupby(['Neighborhood'])[7].mean()
seventh_nearest_res = seventh_nearest_res.reset_index()

eighth_nearest_res = res_distances.groupby(['Neighborhood'])[8].mean()
eighth_nearest_res = eighth_nearest_res.reset_index()

ninth_nearest_res = res_distances.groupby(['Neighborhood'])[9].mean()
ninth_nearest_res = ninth_nearest_res.reset_index()

tenth_nearest_res = res_distances.groupby(['Neighborhood'])[10].mean()
tenth_nearest_res = tenth_nearest_res.reset_index()

    # merging them all
dfs = [nearest_res, second_nearest_res, third_nearest_res, fourth_nearest_res, fifth_nearest_res, sixth_nearest_res, seventh_nearest_res, eighth_nearest_res, ninth_nearest_res, tenth_nearest_res]
nth_nearest_res = pd.concat(dfs, join='outer', axis=1)
nth_nearest_res = nth_nearest_res.loc[:,~nth_nearest_res.columns.duplicated()]

nth_nearest_res


# In[17]:


# rinse and repeat for bars

# Tell the network where the dining amenities are
amenities = NYC_nightlife['amenity'].unique()
for amenity in amenities:

    # get the subset of amenities for this type
    pois_subset = NYC_nightlife[NYC_nightlife["amenity"] == amenity]

    # set the POI, using the longitude and latitude of POI
    net.set_pois(
        amenity, max_distance, num_pois, pois_subset["lon"], pois_subset["lat"]
    )

    # getting distances from nodes to nearest bar
amenity = 'bar'
access = net.nearest_pois(distance=1000, category=amenity, 
                          num_pois=num_pois)
    
    # merging coordinates of network nodes with distances to nearest bars
nodes = pd.merge(net.nodes_df, access, left_index=True, right_index=True)    
nodes = to_geopandas(nodes)

    # performing spatial join with nhoods shapefile
nhood_nodes = gpd.sjoin(nodes, nhoods, op='within', how='left')
nhood_nodes = nhood_nodes.dropna(subset=['Neighborhood']) 

    # finding average distance to nth nearest bar
from geopandas import GeoDataFrame
bar_distances = GeoDataFrame(nhood_nodes)
nearest_bar = bar_distances.groupby(['Neighborhood'])[1].mean()
nearest_bar = nearest_bar.reset_index()

second_nearest_bar = bar_distances.groupby(['Neighborhood'])[2].mean()
second_nearest_bar = second_nearest_bar.reset_index()

third_nearest_bar = bar_distances.groupby(['Neighborhood'])[3].mean()
third_nearest_bar = third_nearest_bar.reset_index()

fourth_nearest_bar = bar_distances.groupby(['Neighborhood'])[4].mean()
fourth_nearest_bar = fourth_nearest_bar.reset_index()

fifth_nearest_bar = bar_distances.groupby(['Neighborhood'])[5].mean()
fifth_nearest_bar = fifth_nearest_bar.reset_index()

sixth_nearest_bar = bar_distances.groupby(['Neighborhood'])[6].mean()
sixth_nearest_bar = sixth_nearest_bar.reset_index()

seventh_nearest_bar = bar_distances.groupby(['Neighborhood'])[7].mean()
seventh_nearest_bar = seventh_nearest_bar.reset_index()

eighth_nearest_bar = bar_distances.groupby(['Neighborhood'])[8].mean()
eighth_nearest_bar = eighth_nearest_bar.reset_index()

ninth_nearest_bar = bar_distances.groupby(['Neighborhood'])[9].mean()
ninth_nearest_bar = ninth_nearest_bar.reset_index()

tenth_nearest_bar = bar_distances.groupby(['Neighborhood'])[10].mean()
tenth_nearest_bar = tenth_nearest_bar.reset_index()

    # merging them all
dfs = [nearest_bar, second_nearest_bar, third_nearest_bar, fourth_nearest_bar, fifth_nearest_bar, sixth_nearest_bar, seventh_nearest_bar, eighth_nearest_bar, ninth_nearest_bar, tenth_nearest_bar]
nth_nearest_bar = pd.concat(dfs, join='outer', axis=1)
nth_nearest_bar = nth_nearest_bar.loc[:,~nth_nearest_bar.columns.duplicated()]

nth_nearest_bar


# In[18]:


# rinse and repeat for nightclubs
    
    # getting distances from nodes to nearest nightclub
amenity = 'nightclub'
access = net.nearest_pois(distance=1000, category=amenity, 
                          num_pois=num_pois)
    
    # merging coordinates of network nodes with distances to nearest nightclubs
nodes = pd.merge(net.nodes_df, access, left_index=True, right_index=True)    
nodes = to_geopandas(nodes)

    # performing spatial join with nhoods shapefile
nhood_nodes = gpd.sjoin(nodes, nhoods, op='within', how='left')
nhood_nodes = nhood_nodes.dropna(subset=['Neighborhood']) 

    # finding average distance to nth nearest nightclub
from geopandas import GeoDataFrame
nc_distances = GeoDataFrame(nhood_nodes)
nearest_nc = nc_distances.groupby(['Neighborhood'])[1].mean()
nearest_nc = nearest_nc.reset_index()

second_nearest_nc = nc_distances.groupby(['Neighborhood'])[2].mean()
second_nearest_nc = second_nearest_nc.reset_index()

third_nearest_nc = nc_distances.groupby(['Neighborhood'])[3].mean()
third_nearest_nc = third_nearest_nc.reset_index()

fourth_nearest_nc = nc_distances.groupby(['Neighborhood'])[4].mean()
fourth_nearest_nc = fourth_nearest_nc.reset_index()

fifth_nearest_nc = nc_distances.groupby(['Neighborhood'])[5].mean()
fifth_nearest_nc = fifth_nearest_nc.reset_index()

sixth_nearest_nc = nc_distances.groupby(['Neighborhood'])[6].mean()
sixth_nearest_nc = sixth_nearest_nc.reset_index()

seventh_nearest_nc = nc_distances.groupby(['Neighborhood'])[7].mean()
seventh_nearest_nc = seventh_nearest_nc.reset_index()

eighth_nearest_nc = nc_distances.groupby(['Neighborhood'])[8].mean()
eighth_nearest_nc = eighth_nearest_nc.reset_index()

ninth_nearest_nc = nc_distances.groupby(['Neighborhood'])[9].mean()
ninth_nearest_nc = ninth_nearest_nc.reset_index()

tenth_nearest_nc = nc_distances.groupby(['Neighborhood'])[10].mean()
tenth_nearest_nc = tenth_nearest_nc.reset_index()

    # merging them all
dfs = [nearest_nc, second_nearest_nc, third_nearest_nc, fourth_nearest_nc, fifth_nearest_nc, sixth_nearest_nc, seventh_nearest_nc, eighth_nearest_nc, ninth_nearest_nc, tenth_nearest_nc]
nth_nearest_nc = pd.concat(dfs, join='outer', axis=1)
nth_nearest_nc = nth_nearest_nc.loc[:,~nth_nearest_nc.columns.duplicated()]

nth_nearest_nc


# In[101]:


# changing all from wide to long format
long_cafe = pd.melt(nth_nearest_cafe,id_vars=['Neighborhood'],var_name='N', value_name='Cafes')
long_res = pd.melt(nth_nearest_res,id_vars=['Neighborhood'],var_name='N', value_name='Restaurants')
long_bar = pd.melt(nth_nearest_bar,id_vars=['Neighborhood'],var_name='N', value_name='Bars')
long_nc = pd.melt(nth_nearest_cafe,id_vars=['Neighborhood'],var_name='N', value_name='Nightclubs')

# merging them all together
dfs = [long_cafe, long_res, long_bar, long_nc]
nth_nearest = pd.concat(dfs, join='outer', axis=1)
nth_nearest = nth_nearest.loc[:,~nth_nearest.columns.duplicated()]

nth_nearest.head()


# In[102]:


# THE PLOT 
import math
import matplotlib.pyplot as plt
import json
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter
from bokeh.palettes import brewer
from bokeh.io.doc import curdoc
from bokeh.models import Slider, HoverTool, Select
from bokeh.layouts import widgetbox, row, column


# In[103]:


# This dictionary contains the formatting for the data in the plots
format_data = [('Cafes', 86, 1000,'0 m', 'Cafes'),
               ('Restaurants', 43, 1000,'0 m', 'Restaurants'),
               ('Bars', 63, 1000,'0 m', 'Bars'),
               ('Nightclubs', 86, 1000,'0 m', 'Nightclubs')]

#Create a DataFrame object from the dictionary 
format_df = pd.DataFrame(format_data, columns = ['field' , 'min_range', 'max_range' , 'format', 'verbage'])
format_df


# In[104]:


# Create a function the returns json_data for the year selected by the user
def json_data(selectedN):
    N = selectedN
    
    # Pull selected year from neighborhood summary data
    df_N = nth_nearest[nth_nearest['N'] == N]
    
    # Merge with nhood file
    merged = pd.merge(nhoods, df_N, on='Neighborhood', how='left')
    
    # Bokeh uses geojson formatting, representing geographical features, with json
    # Convert to json
    merged_json = json.loads(merged.to_json())
    
    # Convert to json preferred string-like object 
    json_data = json.dumps(merged_json)
    return json_data


# In[105]:


# Define the callback function: update_plot
def update_plot(attr, old, new):
    
    # The input N is selected from the slider
    N = slider.value
    new_data = json_data(N)
    
    # The input cr is the criteria selected from the select box
    cr = select.value
    input_field = format_df.loc[format_df['verbage'] == cr, 'field'].iloc[0]
    
    # Update the plot based on the changed inputs
    p = make_plot(input_field)
    
    # Update the layout, clear the old document and display the new document
    layout = column(p, widgetbox(select), widgetbox(slider))
    curdoc().clear()
    curdoc().add_root(layout)
    
    # Update the data
    geosource.geojson = new_data 


# In[106]:


# Create a plotting function
def make_plot(field_name):    
    # Set the format of the colorbar
    min_range = format_df.loc[format_df['field'] == field_name, 'min_range'].iloc[0]
    max_range = format_df.loc[format_df['field'] == field_name, 'max_range'].iloc[0]
    field_format = format_df.loc[format_df['field'] == field_name, 'format'].iloc[0]
    
    # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(palette = palette, low = min_range, high = max_range)
    
    # Create color bar.
    format_tick = NumeralTickFormatter(format=field_format)
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=18, formatter=format_tick,
                         border_line_color=None, location = (0, 0))
    
    # Create figure object.
    verbage = format_df.loc[format_df['field'] == field_name, 'verbage'].iloc[0]
    
    p = figure(title = 'Nth Closest ' + verbage + ' by Neighborhoods in New York City', 
             plot_height = 800, plot_width = 800,
             toolbar_location = None)
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.axis.visible = False
    
    # Add patch renderer to figure. 
    p.patches('xs','ys', source = geosource, fill_color = {'field' : field_name, 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
    
    # Specify color bar layout.
    p.add_layout(color_bar, 'right')
    
    # Add the hover tool to the graph
    p.add_tools(hover)
    return p


# 

# In[110]:


# Input geojson source that contains features for plotting for:
# initial N=1 and initial criteria Cafes
geosource = GeoJSONDataSource(geojson = json_data(1))
input_field = 'Cafes'

# Define a sequential multi-hue color palette.
palette = brewer['Blues'][8]
# Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]

# Add hover tool
hover = HoverTool(tooltips = [ ('Neighborhood','@Neighborhood'),
                               ('Mean Distance to Nth Nearest Cafe','@Cafes m'),
                               ('Mean Distance to Nth Nearest Restaurant','@Restaurants m'),
                               ('Mean Distance to Nth Nearest Bar','@Bars m'),
                               ('Mean Distance to Nth Nearest Nightclub','@Nightclubs m') ] )

# Call the plotting function
p = make_plot(input_field)

# Make a slider object: slider 
slider = Slider(title = 'N',start = 1, end = 10, step = 1, value = 1)
slider.on_change('value', update_plot)

# Make a selection object: select
select = Select(title='Select Amenity:', value='Cafes', options=['Cafes', 'Restaurants', 'Bars', 'Nightclubs'])
select.on_change('value', update_plot)

# Make a column layout of widgetbox(slider) and plot, and add it to the current document
layout = column(p, widgetbox(select), widgetbox(slider))
curdoc().add_root(layout)

# Display the current document
#output_notebook()
#show(p)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




