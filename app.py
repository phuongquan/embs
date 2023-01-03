import datetime as dt
import dash
from dash import dcc, html, dash_table, ctx
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import requests as req
import json
import io
# store credentials in a file called cred.py in root folder
import cred

def load_manual_readings():
    # get latest version of data from gist
    gist_response = req.get(url='https://api.github.com/gists/e7c8598e3ba54bf86f0586c745026918',
    headers= dict([('Accept', 'application/vnd.github+json'),
        ('Authorization', 'Bearer ' + cred.github_pat),
        ('X-GitHub-Api-Version', '2022-11-28')])) 
        
    content = gist_response.json()['files']['manual_readings.csv']['content']
    csv = pd.read_csv(io.StringIO(content))
    return csv

def save_manual_readings(data):
    payload = {'files': {'manual_readings.csv':{'content':data.to_csv(index=False)}}}

    req.patch(url = 'https://api.github.com/gists/e7c8598e3ba54bf86f0586c745026918',
    headers = dict([('Accept', 'application/vnd.github+json'),
        ('Authorization', 'Bearer ' + cred.github_pat),
        ('X-GitHub-Api-Version', '2022-11-28')]),
        data = json.dumps(payload))
    return True

def plot_readings(type):
    data = load_manual_readings()
    if type=="temperature":
        p = px.line(data,
        x='Timestamp', y='Temperature',
        range_y=[-5,40], 
        markers=True,
        color_discrete_sequence=['red'])
    elif type=="humidity":
        p = px.line(data,
        x='Timestamp', y='Humidity',
        range_y=[0,100], 
        markers=True,
        color_discrete_sequence=['blue'])
    elif type=="pm25":
        p = px.line(data,
        x='Timestamp', y='PM2.5',
        range_y=[0,30], 
        markers=True,
        color_discrete_sequence=['darkgray'])
    elif type=="pm10":
        p = px.line(data,
        x='Timestamp', y='PM10',
        range_y=[0,30], 
        markers=True,
        color_discrete_sequence=['darkslategray'])
    return p


app = dash.Dash(__name__)
server = app.server

app.title = 'EMBS Urban Nature Garden'
app.config.suppress_callback_exceptions = False

def serve_layout():
    return html.Div(
    [
        dcc.Location(id='url'),
        html.Div(
            [
                html.Span(children=[
                    html.Img(src='assets/embs-logo.png', 
                    style={'padding': 10, 'height': '80px'}),
                    html.Img(src='assets/ox_brand1_pos.gif', 
                    style={'padding': 10, 'height': '80px'})
                ]
                ),
                html.H2('EMBS Urban Nature Garden',
                style={'padding': 10}),
                html.Span(children=[
                    html.Img(src='assets/science-together-logo.png', 
                    style={'padding': 10, 'height': '80px'}),
                ]
                ),
            ],
            className='app__header'
        ),
        html.Div(
            [
                dcc.Tabs(
                    id='tabs',
                    value='view-graphs',
                    children=[
                        dcc.Tab(
                            label='GRAPHS',
                            value='view-graphs',
                            children=[
                                html.Div(
                                    [
                                        dcc.Graph(id='plot-temperature',
                                        figure=plot_readings("temperature"))
                                    ],
                                    className='graph_container',
                                ),
                                html.Div(
                                    [
                                        dcc.Graph(id='plot-humidity',
                                        figure=plot_readings("humidity"))
                                    ],
                                    className='graph_container',
                                ),
                                html.Div(
                                    [
                                        dcc.Graph(id='plot-pm25',
                                        figure=plot_readings("pm25"))
                                    ],
                                    className='graph_container',
                                ),
                                html.Div(
                                    [
                                        dcc.Graph(id='plot-pm10',
                                        figure=plot_readings("pm10"))
                                    ],
                                    className='graph_container',
                                ),
                            ],
                        ),
                        dcc.Tab(
                            label='SUBMIT NEW READING',
                            value='new-reading',
                            children=[
                                html.Div(
                                    [
                                        html.Div(children=[
                                            html.P(
                                                'Date (DD/MM/YYYY)',
                                            ),
                                            dcc.DatePickerSingle(
                                                id='input-date',
                                                initial_visible_month=dt.datetime.today(),
                                                date=dt.date.today(),
                                                display_format='DD/MM/YYYY'
                                            ),
                                            html.P(
                                                'Time (HH:MM)',
                                            ),
                                            dcc.Input(
                                                id='input-time',
                                                value=dt.datetime.today().strftime('%H:%M'), 
                                                style={'width':'130px'},
                                            )],
                                            className='input__container'                                        
                                        ),
                                        html.Div(children=[
                                            html.P('Temperature (C): '),
                                            dcc.Input(
                                                id='input-temperature',
                                                type='number',
                                                step=1,
                                                ),
                                            html.P(
                                                'Humidity (%):',
                                            ),
                                            dcc.Input(
                                                id='input-humidity',
                                                type='number',
                                                step=1,
                                            ),
                                            html.P(
                                                'PM2.5 (ug/m3):',
                                            ),
                                            dcc.Input(
                                                id='input-pm25',
                                                type='number',
                                                step=0.1,
                                            ),
                                            html.P(
                                                'PM10 (ug/m3):',
                                            ),
                                            dcc.Input(
                                                id='input-pm10',
                                                type='number',
                                                step=0.1,
                                            )],
                                            className='input__container',
                                        ),
                                        html.Div(
                                            [
                                                html.Button(
                                                    'SUBMIT',
                                                    id='save-reading',
                                                    className='submit__button',
                                                )
                                            ]
                                        ),
                                    ],
                                    className='container__1',
                                )
                            ],
                        ),
                        dcc.Tab(
                            label='EDIT DATA',
                            value='manual-readings-table',
                            children=[
                                html.Div([
                                    dash_table.DataTable(
                                        id='edit-table',
                                        data=load_manual_readings().to_dict('records'),
                                        columns=[{'name': i, 'id': i} for i in load_manual_readings().columns],
                                        editable=True,
                                        row_deletable=True
                                    )
                                ]),
                                html.Div(id='edit-table-dummy', hidden=True),
                                html.Div(
                                    [
                                        html.Button(
                                            'SAVE CHANGES',
                                            id='save-table',
                                            className='submit__button',
                                        )
                                    ]
                                ),
                            ],
                        )
                    ],
                )
            ],
            className='tabs__container',
        ),
    ],
    className='app__container',
)

app.layout = serve_layout


@app.callback(
    Output('url', 'href'),
    Input('save-reading', 'n_clicks'),
    Input('save-table', 'n_clicks'),
    [
        State('input-date', 'date'),
        State('input-time', 'value'),
        State('input-temperature', 'value'),
        State('input-humidity', 'value'),
        State('input-pm25', 'value'),
        State('input-pm10', 'value'),
        State('edit-table', 'data')
    ],
    prevent_initial_call=True
)
def save_changes(submit_reading_clicks, save_table_clicks, input_date, input_time, input_temperature, input_humidity, input_pm25, input_pm10, table_data):
    triggered_id = ctx.triggered_id
    if triggered_id == 'save-reading':
        new_row = pd.DataFrame({
                'Timestamp': [dt.datetime.combine(dt.date.fromisoformat(input_date),
                dt.time.fromisoformat(input_time))],
                'Temperature': [input_temperature],
                'Humidity': [input_humidity],
                'PM2.5': [input_pm25],
                'PM10': [input_pm10]
                }
            )
        save_manual_readings(pd.concat([load_manual_readings(), new_row]))
    elif triggered_id == 'save-table':
        save_manual_readings(pd.DataFrame(table_data))
    return '/'


if __name__ == '__main__':
    app.run_server(debug=True)