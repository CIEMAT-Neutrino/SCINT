# ---------------------------------------------------------------------------------------------------------------------- #
#  ========================================= RUN:$ python3 0YVisEvent.py  ============================================== #
# This macro will display an app to display the individual EVENTS of the brwoser file. You can browse a RAW_FILE (.dat)  #
# and an interactive event will be displayed with the main parameters printed. DO NOT change this file (in principle)    #
# $ sshfs USER@pcaeXYZ.ciemat.es:/pnfs/ciemat.es/data/neutrinos/FOLDER ../data  --> making sure empty data folder exists #
# ---------------------------------------------------------------------------------------------------------------------- #

import os, dash
from dash import dcc
from dash import html

jupyter_mode = None
if 'ipykernel' in os.sys.modules:
    from IPython import get_ipython
    if get_ipython() is not None: jupyter_mode = "inline"

app = dash.Dash(__name__)
app.layout = html.Div([
                html.H1("Waveform Visualization"),
                html.Div([ html.Label("Select Waveform File"), dcc.Upload(id='upload-data', children=html.Button('Browse')), 
                        html.Br(), 
                        html.Label("Select the extension of the browsed file"), dcc.Dropdown([".dat",".npx"], ".dat",id='extension'),
                        html.Br(),
                        html.Label("Enter Event Number"), dcc.Input(id='event-number', type='number', value=0),
                        html.Button("Plot Waveform",  id='plot-button'), 
                        html.Br(),
                        html.Br(),
                        html.Button("Previous Event", id='prev-button'),
                        html.Button("Next Event",     id='next-button')]),
                html.Div( id='waveform-info'), dcc.Graph(id='waveform-plot'),
             ])

@app.callback(
    dash.dependencies.Output('waveform-info', 'children'),
    dash.dependencies.Output('waveform-plot', 'figure'),

    dash.dependencies.Input('plot-button', 'n_clicks'),
    dash.dependencies.Input('prev-button', 'n_clicks'),
    dash.dependencies.Input('next-button', 'n_clicks'),
    dash.dependencies.Input('extension',   'value'),

    dash.dependencies.State('upload-data',  'contents'),
    dash.dependencies.State('event-number', 'value'),
)
def update_waveform(plot_clicks, prev_clicks, next_clicks, extension, contents, event_number):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    waveform_info = []
    if triggered_id == 'plot-button' or triggered_id == 'prev-button' or triggered_id == 'next-button':
        if contents is not None:
            content_type, content_string = contents.split(",")
            decoded_content = base64.b64decode(content_string)
            fig = go.Figure()
            if extension == ".dat":
                adc,timestamp = binary2npy_express(io.BytesIO(decoded_content),debug=False)
                df = pd.DataFrame(adc)

            if extension == ".npx":
                adc = np.load(io.BytesIO(decoded_content),allow_pickle=True, mmap_mode="w+")["arr_0"] 
                df = pd.DataFrame(adc)
                print(adc)
                print(df.iloc[0])

            if next_clicks is None: next_clicks = 0
            if prev_clicks is None: prev_clicks = 0
            if triggered_id != "plot-button": event_number = event_number + next_clicks - prev_clicks;

            time2plot = 4e-9*np.arange(len(df.iloc[event_number]))
            waveform  = df.iloc[event_number]
            waveform_info.append(html.Span(f"Waveform Information for Event {event_number}"))
            waveform_info.append(html.Br())
            waveform_info.append(html.Br())
            waveform_info.append(html.Span(f"Max Value: {waveform.max()}"))
            waveform_info.append(html.Br())
            waveform_info.append(html.Span(f"Min Value: {waveform.min()}"))
            waveform_info.append(html.Br())
            waveform_info.append(html.Span(f"Mean Value: {waveform.mean()}"))
            waveform_info.append(html.Br())
            waveform_info.append(html.Span(f"Standard Deviation: {waveform.std()}"))

            fig.add_trace(go.Scatter(x=time2plot, y=waveform))
            custom_plotly_layout(fig, title='Raw Waveform - Event %i'%event_number, xaxis_title='Time [s]', yaxis_title='ADC')
            fig.update_layout(showlegend=False)

            return waveform_info, fig

    return "", {}

if __name__ == '__main__':
    import io, base64
    import pandas               as pd
    import numpy                as np
    import plotly.graph_objs    as go 
    import sys; sys.path.insert(0, '../'); 
    from lib.io_functions  import binary2npy_express;
    from lib.ply_functions import *

    app.run(debug=True)
    # app.run(jupyter_mode=jupyter_mode,debug=True)