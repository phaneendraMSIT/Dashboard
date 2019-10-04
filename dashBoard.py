# layout modeling

import sys
import dash
import dash_core_components as dcc
import dash_html_components as html
from urllib.parse import parse_qs
import plotly
import plotly.graph_objs as go
from datetime import datetime as dt, timedelta as td, date

# importing other files
from application import app
import dataParsing
import sqlQuries


# global methods
def loadWeeklyDates():
    endDate = dt.today().date()

    listOfDates = []
    for i in range( 10 ):
        startDate = endDate - td( 6 )
        listOfDates.append( str( startDate ) + " - " + str( endDate ) )
        endDate = startDate - td( 1 )

    return [{'label': date, 'value': date} for date in listOfDates]


# layout design
app.layout = html.Div( [
    dcc.Location( id='url', refresh=True ),
    html.Div( id='user', style={'display': 'none'} ),
    html.Div( [
        html.Div( dcc.Dropdown( id='userLocations', value='location' ),
                  style={'width': '25%', 'float': 'left', 'display': 'inline-block'} )
    ], style={'height': '20%'}, className='container' ),

    html.Div( style={'height': '20px'} ),
    # tabs container
    html.Div( [
        html.Div( dcc.Tabs( id="dataTabs", value='weekly', children=[
            dcc.Tab( label='Weekly', value='weekly' ),
            dcc.Tab( label='Yesterday', value='yesterday' ),
            dcc.Tab( label='Today', value='today' ),
        ], style={'float': 'left'} ), style={'width': '60%', "float": 'left'} ),
        html.Div( style={'width': '20px', "float": 'left'} ),
        html.Div( dcc.Dropdown( id='dateDropdown', options=loadWeeklyDates() ), style={'width': '30%', 'height': '27px',
                                                                                       "float": 'left'} )
    ], className='container', style={"float": 'left'} ),

    # display container
    html.Div( [
        # inward flow container
        html.Div( [
            html.Div( [
                html.Div( [
                    html.H6( "Total Inward Value" ),
                    html.Div( id='inwardValue' )
                ], style={"float": 'left', 'width': '47%'} ),
                html.Div( [
                    html.H6( "Total Inward Volume" ),
                    html.Div( id='inwardVolume' )
                ], style={"float": 'left', 'width': '47%'} )
            ], className='flex-container', style={'margin': '10px'} ),
            html.Div( [
                html.H6( "Top 5 Items" ),
                dcc.Graph( id='itemPieChartInward' )
            ] )
        ], style={"float": 'left', 'width': '45%'} ),
        # outward flow container
        html.Div( [
            html.Div( [
                html.Div( [
                    html.H6( "Total Outward Value" ),
                    html.Div( id='outwardValue' )
                ], style={"float": 'left', 'width': '47%'} ),
                html.Div( [
                    html.H6( "Total Outward Volume" ),
                    html.Div( id='outwardVolume' )
                ], style={"float": 'left', 'width': '47%'} )
            ], className='flex-container', style={'margin': '10px'} ),
            html.Div( [
                html.H6( "Top 5 Items" ),
                dcc.Graph( id='itemPieChartOutward' )
            ] )
        ], style={"float": 'left', 'width': '45%'} )
    ] )

], className='container' )


# loading locations of the user
@app.callback(
    [dash.dependencies.Output( 'user', 'children' ),
     dash.dependencies.Output( 'userLocations', 'options' )],
    [dash.dependencies.Input( 'url', 'search' )]
)
def getuserId(value):
    if value is None:
        raise dash.exceptions.PreventUpdate
    user = parse_qs( value ).get( '?userId' )[0]
    cities = sqlQuries.getCities( user )
    listCity = [{'label': city, 'value': city} for city in cities]
    return user, listCity


# parsing data into html
@app.callback(
    [
        dash.dependencies.Output( 'inwardValue', 'children' ),
        dash.dependencies.Output( 'inwardVolume', 'children' ),
        dash.dependencies.Output( 'itemPieChartInward', 'figure' ),
        dash.dependencies.Output( 'outwardValue', 'children' ),
        dash.dependencies.Output( 'outwardVolume', 'children' ),
        dash.dependencies.Output( 'itemPieChartOutward', 'figure' )
    ],
    [
        dash.dependencies.Input( 'dataTabs', 'value' )
    ],
    [
        dash.dependencies.State( 'user', 'children' ),
        dash.dependencies.State( 'userLocations', 'value' ),
        dash.dependencies.State( 'dateDropdown', 'value' )
    ]
)
def parseDataFromDatabase(tab, userId, location, dateValue):
    try:
        if location is None:
            raise dash.exceptions.PreventUpdate
        startDate = ''
        endDate = ''
        if tab == 'today':
            startDate = str( date.today() )
            endDate = str( date.today() )
        elif tab == 'yesterday':
            startDate = str( date.today() - td( 1 ) )
            endDate = str( date.today() - td( 1 ) )
        elif tab == 'weekly':
            if dateValue is None:
                raise dash.exceptions.PreventUpdate
            startDate = dateValue.split( " - " )[0]
            endDate = dateValue.split( " - " )[1]

        inwardValue, inwardVolume, pieChartInward = sqlQuries.getInwardValue( userId, location, startDate, endDate )
        outwardValue, outwardVolume, pieChartOutward = sqlQuries.getOutwardValue( userId, location, startDate, endDate )

        return inwardValue, inwardVolume, pieChartInward, outwardValue, outwardVolume, pieChartOutward
    except(RuntimeError, TypeError, NameError):
        raise dash.exceptions.PreventUpdate


if __name__ == '__main__':
    app.run_server( debug=True )
