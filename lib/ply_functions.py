import numpy                as np
import pandas               as pd
import plotly.express       as px
import plotly.graph_objs    as go 
import plotly.offline       as pyoff
import matplotlib.pyplot    as plt
import ipywidgets           as widgets
from rich                   import print as print

from .io_functions import binary2npy_express


def custom_legend_name(fig_px,new_names):
    for i, new_name in enumerate(new_names): fig_px.data[i].name = new_name
    return fig_px


def custom_plotly_layout(fig_px, xaxis_title="", yaxis_title="", title="",barmode="stack",bargap=0):
    fig_px.update_layout( updatemenus=[ dict( buttons=list([ dict(args=[{"xaxis.type": "linear", "yaxis.type": "linear"}], label="LinearXY", method="relayout"),
                                                             dict(args=[{"xaxis.type": "log", "yaxis.type": "log"}],       label="LogXY",    method="relayout"),
                                                             dict(args=[{"xaxis.type": "linear", "yaxis.type": "log"}],    label="LogY",     method="relayout"),
                                                             dict( args=[{"xaxis.type": "log", "yaxis.type": "linear"}],   label="LogX",     method="relayout") ]),
                          direction="down", pad={"r": 10, "t": 10}, showactive=True, x=-0.1, xanchor="left", y=1.5, yanchor="top" ) ] )
    fig_px.update_layout(   template="presentation", title=title, xaxis_title=xaxis_title, yaxis_title=yaxis_title, barmode=barmode,bargap=bargap,
                            font=dict(family="serif"), legend_title_text='', legend = dict(yanchor="top", xanchor="right", x = 0.99), showlegend=True)
    fig_px.update_xaxes(showline=True,mirror=True,zeroline=False)
    fig_px.update_yaxes(showline=True,mirror=True,zeroline=False)
    return fig_px


def show_html(fig_px):
    return pyoff.plot(fig_px, include_mathjax='cdn')


def save_plot(fig_px,name):
    if ".hmtl" in name: return fig_px.write_html(name, include_mathjax = 'cdn')
    if ".json" in name: return fig_px.write_json(name)


def vis_event(in_file):
    adc,timestamp = binary2npy_express(in_file,debug=False)
    df = pd.DataFrame(adc,timestamp)
    col_names  = (list(range(1,len(df.columns)+1))); df.columns = col_names
    
    def update_plot(column):
        fig = go.Figure()
        if column in df.columns.to_list(): 
            fig.add_trace(go.Scatter(x=df.index.to_list(), y=df[column].to_list()))
            fig.update_layout(title='Raw Waveform - Event %i'%column, xaxis_title='Time [s]', yaxis_title='ADC')
            return fig
            
    column_input = widgets.IntText(value=0, description='#Event:')
    widgets.interact(update_plot, column=column_input)

    return None