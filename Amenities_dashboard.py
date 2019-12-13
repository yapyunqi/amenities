#!/usr/bin/env python
# coding: utf-8

# In[4]:


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


# In[5]:


# adding neighborhoods file
import pandas as pd
import geopandas as gpd
nhoods = gpd.read_file("https://raw.githubusercontent.com/yapyunqi/amenities/master/Neighborhoods.geojson")
nhoods.rename(columns = {'ntaname':'Neighborhood'}, inplace = True)
nhoods.crs = {'init': 'epsg:4326'}


# In[6]:


# loading csv data (cleaned in another file)
nth_nearest = pd.read_csv('https://raw.githubusercontent.com/yapyunqi/amenities/master/finaldf.csv')
nth_nearest


# In[7]:


# This dictionary contains the formatting for the data in the plots
format_data = [('Cafes', 86, 1000,'0 m', 'Cafes'),
               ('Restaurants', 43, 1000,'0 m', 'Restaurants'),
               ('Bars', 63, 1000,'0 m', 'Bars'),
               ('Nightclubs', 86, 1000,'0 m', 'Nightclubs')]

#Create a DataFrame object from the dictionary 
format_df = pd.DataFrame(format_data, columns = ['field' , 'min_range', 'max_range' , 'format', 'verbage'])
format_df


# In[8]:


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


# In[9]:


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
    layout = row(p, widgets)
    curdoc().clear()
    curdoc().add_root(layout)
    
    # Update the data
    geosource.geojson = new_data 


# In[10]:


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
    
    p = figure(title = 'Distance From Nth Closest ' + verbage + ' by Neighborhood (New York City)',
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

# In[11]:


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
widgets = column(widgetbox(select), widgetbox(slider))
layout = row(p, widgets)
curdoc().add_root(layout)


# In[ ]:




