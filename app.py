import datetime as dt
import dash
from dash import dcc, html, dash_table, ctx
from dash.dependencies import Input, Output, State
import pandas as pd
import math
import plotly.express as px
import requests as req
import json
import io
from flask_restful import Api, Resource
from flask import request
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

def load_enviro_readings():
    # get latest version of data from gist
    gist_response = req.get(url='https://api.github.com/gists/b961b551f676f0e7511cfccd475912e9',
    headers= dict([('Accept', 'application/vnd.github+json'),
        ('Authorization', 'Bearer ' + cred.github_pat),
        ('X-GitHub-Api-Version', '2022-11-28')])) 
        
    content = gist_response.json()['files']['enviro_readings.csv']['content']
    csv = pd.read_csv(io.StringIO(content))
    return csv

def save_enviro_readings(data):
    payload = {'files': {'enviro_readings.csv':{'content':data.to_csv(index=False)}}}

    req.patch(url = 'https://api.github.com/gists/b961b551f676f0e7511cfccd475912e9',
    headers = dict([('Accept', 'application/vnd.github+json'),
        ('Authorization', 'Bearer ' + cred.github_pat),
        ('X-GitHub-Api-Version', '2022-11-28')]),
        data = json.dumps(payload))
    return True

def round_up_ten(x):
    if x == None or math.isnan(x) or x==0:
        retval = 10
    else:
        retval = int(math.ceil(x / 10)) * 10
    return retval

def plot_readings(type):
    manual = load_manual_readings()
    manual['Method'] = 'Manual'
    manual['Timestamp'] = pd.to_datetime(manual['Timestamp'], utc=True)
    enviro = load_enviro_readings()
    enviro.rename(columns={
        'timestamp': 'Timestamp',
        'temperature': 'Temperature',
        'humidity': 'Humidity',
        'pm1': 'PM1',
        'pm2_5': 'PM2.5',
        'pm10': 'PM10',
        'pressure': 'Pressure',
        'noise': 'Noise'
        },
        inplace=True)
    enviro['Method'] = 'Enviro'
    enviro['Timestamp'] = pd.to_datetime(enviro['Timestamp'], utc=True)
    data = pd.concat([manual, enviro])   
    xrange = [min(data["Timestamp"]) - dt.timedelta(days=1), max(data["Timestamp"]) + dt.timedelta(days=1)]
    if type=="temperature":
        p = px.scatter(
            data,
            x='Timestamp', y='Temperature',
            range_x=xrange,
            range_y=[0,50],
            color='Method',
            color_discrete_map={
                "Manual": "red",
                "Enviro": "orange"},
            symbol='Method',
            symbol_map={
                "Manual": "hexagram",
                "Enviro": "cross"})
    elif type=="humidity":
        p = px.scatter(
            data,
            x='Timestamp', y='Humidity',
            range_x=xrange,
            range_y=[0,100], 
            color='Method',
            color_discrete_map={
                "Manual": "blue",
                "Enviro": "cyan"},
            symbol='Method',
            symbol_map={
                "Manual": "hexagram",
                "Enviro": "cross"})
    elif type=="pressure":
        p = px.scatter(
            data[data['Method']=='Enviro'],
            x='Timestamp', y='Pressure',
            range_x=xrange,
            range_y=[900, 1100],
            color='Method',
            color_discrete_map={
                "Enviro": "green"},
            symbol='Method',
            symbol_map={
                "Manual": "hexagram",
                "Enviro": "cross"})
    elif type=="noise":
        p = px.scatter(
            data[data['Method']=='Enviro'],
            x='Timestamp', y='Noise',
            range_x=xrange,
            range_y=[0, round_up_ten(data.max()['Noise'])],
            color='Method',
            color_discrete_map={
                "Enviro": "brown"},
            symbol='Method',
            symbol_map={
                "Manual": "hexagram",
                "Enviro": "cross"})
    elif type=="aqi":
        p = px.scatter(
            data[data['Method']=='Manual'],
            x='Timestamp', y='AQI',
            range_x=xrange,
            range_y=[0, round_up_ten(data.max()['AQI'])],
            color='Method',
            color_discrete_map={
                "Manual": "orange"},
            symbol='Method',
            symbol_map={
                "Manual": "hexagram",
                "Enviro": "cross"})
    elif type=="pm1":
        p = px.scatter(
            data[data['Method']=='Enviro'],
            x='Timestamp', y='PM1',
            range_x=xrange,
            range_y=[0, round_up_ten(data.max()['PM1'])],
            color='Method',
            color_discrete_map={
                "Enviro": "gray"},
            symbol='Method',
            symbol_map={
                "Manual": "hexagram",
                "Enviro": "cross"})
    elif type=="pm25":
        p = px.scatter(
            data,
            x='Timestamp', y='PM2.5',
            range_x=xrange,
            range_y=[0, round_up_ten(data.max()['PM2.5'])], 
            color='Method',
            color_discrete_map={
                "Manual": "darkgray",
                "Enviro": "gray"},
            symbol='Method',
            symbol_map={
                "Manual": "hexagram",
                "Enviro": "cross"})
    elif type=="pm10":
        p = px.scatter(
            data,
            x='Timestamp', y='PM10',
            range_x=xrange,
            range_y=[0, round_up_ten(data.max()['PM10'])], 
            color='Method',
            color_discrete_map={
                "Manual": "darkslategray",
                "Enviro": "darkgray"},
            symbol='Method',
            symbol_map={
                "Manual": "hexagram",
                "Enviro": "cross"})
    elif type=="tvoc":
        p = px.scatter(
            data[data['Method']=='Manual'],
            x='Timestamp', y='TVOC',
            range_x=xrange,
            range_y=[0, 5],
            color='Method',
            color_discrete_map={
                "Manual": "black"},
            symbol='Method',
            symbol_map={
                "Manual": "hexagram",
                "Enviro": "cross"})
    return p


app = dash.Dash(__name__)
server = app.server

app.title = 'EMBS Urban Nature Garden'
app.config.suppress_callback_exceptions = False

api = Api(app.server)

class receive_data(Resource):
    def post(self):
        response_code = 400
        reqjson = json.loads(request.data.decode('utf-8'))
        # make sure single readings are in a list
        if type(reqjson) == dict:
            allreadings = []
            allreadings.append(reqjson)
        else:
            allreadings = reqjson
        # append new readings to existing ones
        data = load_enviro_readings()
        for line in allreadings:
            if line['nickname'] == 'embsgarden':
                new_row = pd.DataFrame({
                    'timestamp': [line['timestamp']],
                    'temperature': [line['readings']['temperature']],
                    'humidity': [line['readings']['humidity']],
                    'pressure': [line['readings']['pressure']],
                    'noise': [line['readings']['noise']],
                    'pm1': [line['readings']['pm1']],
                    'pm2_5': [line['readings']['pm2_5']],
                    'pm10': [line['readings']['pm10']]
                    })
                data = pd.concat([data, new_row])
            else:
                # ignore post
                msg = 'invalid source'
        if save_enviro_readings(data):
            response_code = 200

        return response_code

api.add_resource(receive_data, '/envirodata')

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
                html.Button(
                    'TEST ENVIRO POST',
                    id='save-enviro',
                    className='submit__button',
                ),
                html.Span(id='test-output')
            ],
            hidden=True
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
                                        dcc.Graph(id='plot-pressure',
                                        figure=plot_readings("pressure"))
                                    ],
                                    className='graph_container',
                                ),
                                html.Div(
                                    [
                                        dcc.Graph(id='plot-noise',
                                        figure=plot_readings("noise"))
                                    ],
                                    className='graph_container',
                                ),
                                html.Div(
                                    [
                                        dcc.Graph(id='plot-aqi',
                                        figure=plot_readings("aqi"))
                                    ],
                                    className='graph_container',
                                ),
                                html.Div(
                                    [
                                        dcc.Graph(id='plot-pm1',
                                        figure=plot_readings("pm1"))
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
                                html.Div(
                                    [
                                        dcc.Graph(id='plot-tvoc',
                                        figure=plot_readings("tvoc"))
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
                                            html.P('Temperature (C):'),
                                            dcc.Input(
                                                id='input-temperature',
                                                type='number',
                                                min=0,
                                                max=50,
                                                step=1,
                                                ),
                                            html.P('Humidity (%):'),
                                            dcc.Input(
                                                id='input-humidity',
                                                type='number',
                                                min=0,
                                                max=90,
                                                step=1,
                                            ),
                                            html.P('AQI:'),
                                            dcc.Input(
                                                id='input-aqi',
                                                type='number',
                                                min=0,
                                                max=999,
                                                step=1,
                                                ),
                                            html.P('PM2.5 (ug/m3):'),
                                            dcc.Input(
                                                id='input-pm25',
                                                type='number',
                                                min=0,
                                                max=999,
                                                step=0.1,
                                            ),
                                            html.P('PM10 (ug/m3):'),
                                            dcc.Input(
                                                id='input-pm10',
                                                type='number',
                                                min=0,
                                                max=999,
                                                step=0.1,
                                            ),
                                            html.P('TVOC (mg/m3):'),
                                            dcc.Input(
                                                id='input-tvoc',
                                                type='number',
                                                min=0,
                                                max=5,
                                                step=0.01,
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
                                html.Div(
                                    [
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
                                        )
                                    ],
                                    className='container__1',
                                )
                            ],
                        ),
                        dcc.Tab(
                            label='INSTRUCTIONS',
                            value='instructions',
                            children=[
                                html.Div(
                                    [
                                        dcc.Markdown('''

                                        This website has been created for Science Together: Oxford Researchers and Communities 2022/23.
                                        The code is openly available at <https://github.com/phuongquan/embs> and <https://github.com/phuongquan/enviro>


                                        ### Enviro Urban Raspberry Pi Pico kit

                                        This kit has been set up to take environmental readings automatically every 15 minutes, 
                                        and to send them to this website when the POKE button is pressed. It requires a wifi 
                                        or a mobile phone hotspot connection in order to upload the readings.

                                        The kit has a limited amount of storage space so readings should be uploaded whenever possible.
                                        It also needs to be checked regularly for failures (see Troubleshooting below).
                                        

                                        #### How to send readings to the website

                                        The Enviro kit should already be set up to send readings using a particular mobile hotspot.
                                        
                                        1. Turn on the mobile hotspot
                                        1. Press the POKE button on the Enviro kit
                                        1. Wait for the LED to finish pulsing with a white light
                                        1. Check the new readings are showing in the Graphs tab

                                        If the LED blinks red, an error has occurred. Check the hotspot is live by seeing if it can be found by a different device.
                                        Try again by pressing the RESET button, wait for the LED to stop pulsing, then press the POKE button again.

                                        #### How to connect to a different mobile hotspot

                                        As well as a smartphone that will act as the hotspot, you need to have a second device (smartphone, tablet or laptop) 
                                        which will be used to update the connection settings on the Enviro kit.

                                        NOTE: The name and the password of the hotspot must *not* contain any special characters such as dashes (-) or apostrophes ('),
                                        though underscores (_) are ok. If the name or password contains any special characters, these need to be removed first.
                                        On an iPhone, the name of the hotspot may be based on the name of the device, so to change this you may need to update the name of the device in Settings.

                                        1. Turn on the mobile hotspot 
                                        1. On the Enviro kit, while holding down the POKE button, press and release the RESET button, and continue holding down the POKE button until the LED blinks fast.
                                        This means the kit has entered "Provisioning mode", and its settings can be updated.
                                        1. On the second device, view the available Wifi networks.
                                        1. Connect to the "Enviro Urban Setup" network
                                        1. An introduction screen should pop up automatically. Follow the instructions to get to the Networking screen. 
                                        Do not change the nickname of the board or any of the other settings otherwise it might stop working!
                                        1. On the Networking screen, select the name of the hotspot and enter the password.
                                        If the hotspot is not in the list of available networks, check it is live by seeing if it can be found by a different device, then click "Try scanning again".
                                        1. Click through the rest of the screens
                                        1. On the final screen there is a "Reset the board" button. When you click on this, the LED on the Enviro kit should pulse for a few seconds then turn off.
                                        If the LED flashes red, try to follow these instructions again from the beginning.
                                        If it still flases red, try to connect to a different mobile hotspot
                                        If that still doesn't work, open an issue at <https://github.com/phuongquan/embs/issues>
                                        1. If all seems well, press the POKE button to send the latest readings to the website
                                        
                                        #### Troubleshooting

                                        If all is working correctly, the LED will ordinarily be off. 
                                        A few times an hour, when the kit wakes itself up to take a reading, the LED will turn white, pulse for a few seconds, then turn off again.

                                        ##### What to do if the LED is showing white all the time

                                        Sometimes the Enviro kit crashes, which leaves the LED constantly on white. Press the RESET button to restart it.
                                        The LED should turn on, pulse, then turn off again.

                                        ##### What to do if the LED is blinking red

                                        If there has been an error, the LED will blink red. 
                                        Make sure the mobile hotspot is active, then press the RESET button on the Enviro kit to restart it.
                                        Hopefully, the LED should turn on, pulse, then turn off again. 
                                        If it starts blinking red again then open an issue at <https://github.com/phuongquan/embs/issues>

                                        ##### What to do if the LED doesn't light up

                                        If you have pressed the POKE or RESET button on the Enviro kit, and the LED doesn't light up, it may be that the batteries have run out.
                                        Check the switch on the battery pack is set to On. If the RESET button still doesn't light up the LED, try changing the batteries.

                                        ''')
                                    ],
                                    className='container__1'
                                )
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
        State('input-aqi', 'value'),
        State('input-pm25', 'value'),
        State('input-pm10', 'value'),
        State('input-tvoc', 'value'),
        State('edit-table', 'data')
    ],
    prevent_initial_call=True
)
def save_changes(submit_reading_clicks, save_table_clicks, input_date, input_time, input_temperature, input_humidity, input_aqi, input_pm25, input_pm10, input_tvoc, table_data):
    triggered_id = ctx.triggered_id
    if triggered_id == 'save-reading':
        new_row = pd.DataFrame({
                'Timestamp': [dt.datetime.combine(dt.date.fromisoformat(input_date),
                dt.time.fromisoformat(input_time))],
                'Temperature': [input_temperature],
                'Humidity': [input_humidity],
                'AQI': [input_aqi],
                'PM2.5': [input_pm25],
                'PM10': [input_pm10],
                'TVOC': [input_tvoc]
                }
            )
        save_manual_readings(pd.concat([load_manual_readings(), new_row]))
    elif triggered_id == 'save-table':
        save_manual_readings(pd.DataFrame(table_data))
    return '/'


@app.callback(
    Output('test-output', 'children'),
    Input('save-enviro', 'n_clicks'),
    prevent_initial_call=True
)
def test_enviro(save_enviro_clicks):
    auth = None
    target = 'http://127.0.0.1:5000/envirodata'
#    target = 'https://embsgarden.pythonanywhere.com/envirodata'

#    reading = json.load(open(f"2023-01-08T17_32_33Z.json", "r"))
#    result = req.post(url=target, auth=auth, json=reading)

    allreadings = []
    with open(f"2023-01-24.txt", "rt") as f:
        # get column headings
        headings = f.readline().rstrip('\n').split(',')
        # and assume first is timestamp
        headings.pop(0)
        for line in f:
            data = line.rstrip('\n').split(',')
            readings = {
                "nickname": "embsgarden",
                "timestamp": data.pop(0),
                "readings": dict(zip(headings, data)),
                "model": "urban",
                "uid": "e6614103e75c6322"
            }
            allreadings.append(readings)
    result = req.post(url=target, auth=auth, json=allreadings)

    result.close()  
    return result.status_code


if __name__ == '__main__':
    app.run_server(debug=True)