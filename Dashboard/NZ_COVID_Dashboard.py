# Project Name:COVID 19 Dashboard

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
import os
import base64
import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


#############################################################################################
#  IMPORT OUR PROCESSED  DATA
#############################################################################################


NZ_data_df  = pd.read_csv('NZ.csv')
all_data = NZ_data_df

# Save numbers into variables
latest_date = all_data["date"].max()


#########################################################################################################
# Private function
#########################################################################################################
def create_card(title, content, currently, color):
    card = dbc.Card(
        dbc.CardBody(
            [
                html.H6(title, className="card-subtitle"),
                html.H4(content, className="card-subtitle"),
                html.Br(),
                html.P(currently, className="card-subtitle"),
            ],
            className="text-center",
        ),
        style={"color": color},color="#14141e"
    )
    return card


# other key numbers
outbreak_beginning = datetime.date(2019, 12, 31)
days_since_outbreak = (datetime.date.today() - outbreak_beginning).days
Number_total_tests = all_data["total_tests"].max()
Number_total_deaths =  all_data["total_deaths"].max()
Number_total_cases =  all_data["total_cases"].max()
Number_daily_tests_high = all_data["new_tests"].max()
Number_daily_deaths_high = all_data["new_deaths"].max()
Number_daily_cases_high = all_data["new_cases"].max()


# infected countries
infected_countries = 200


#############################################################################################
# Start to make plots
#############################################################################################

# Cards plot
card_days = create_card(
    "Days since outbreak",
     f"{days_since_outbreak:,}",
    f"First Case: 28 Feb 2020",
    "#836af3",  #blue
)
card_cases = create_card(
    "Total Confirmed Cases",
    f"{int(Number_total_cases):,}",
    f"Single day high: {int(Number_daily_cases_high):,}",
    "#e45558", #red
)
card_deaths = create_card(
    "Total Deaths",
    f"{int(Number_total_deaths):,}",
    f"Single day high: {int(Number_daily_deaths_high):,}",
    "gray",
)
card_tests = create_card(
    "Total Tests",
    f"{int(Number_total_tests):,}",
    f"Single day high: {int(Number_daily_tests_high):,}",
    "green",
)
cards = dbc.CardDeck(
    [card_days, card_cases, card_deaths, card_tests], className="mb-2"
)



# Table all_data
table_all_data = (
    all_data[all_data["date"] == latest_date]
    .groupby(["location"])
    .sum()
    .reset_index()
    .rename(
        columns={"location":"Country", "total_cases": "Confirmed", "total_deaths": "Deaths", "new_cases": "New cases"}
    )
    .sort_values(by=["Confirmed"], ascending=False)
    .reset_index(drop=True)
)



# DASH Table

data_table = html.Div(
    [
        dash_table.DataTable(
            id="datatable-interactivity",
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": True}
                for i in table_all_data.columns
                if i == "Confirmed" or i == "Deaths" or i == "New cases" or i=="Country"
            ],
            data=table_all_data.to_dict("records"),
            filter_action="native",
            sort_action="native",
            row_selectable="multi",
            selected_rows=[],
            fixed_rows={"headers": True, "data": 0},
            style_as_list_view=True,
            style_cell={"font_family": "Helvetica Neue",
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white'},
            style_table={
                "maxHeight": "800px",
                "height": "100px",
                "overflowY": "scroll",
            },
       
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                "fontWeight": "bold",
                "padding": "0.4rem",
            },
            virtualization=True,
            page_action="none",
            style_cell_conditional=[
                {"if": {"column_id": "Country"}, "width": "23%"},
                {"if": {"column_id": "Confirmed"}, "width": "23%"},
                {"if": {"column_id": "New cases"}, "width": "23%"},
                {"if": {"column_id": "Deaths"}, "width": "23%"},
                {"if": {"column_id": "Confirmed"}, "color": "#d7191c"},
                {"if": {"column_id": "New cases"}, "color": "#1a9622"},
                {"if": {"column_id": "Deaths"}, "color": "#6c6c6c"},
                {"textAlign": "center"},
            ],
        )
    ],
    className="container mb-2",
)


# cases over time figure
time_series_grouped_country =(all_data
    .groupby(["location","date"])
    .sum()
    .reset_index()
    .rename(
        columns={"location":"Country", "total_cases": "Confirmed", "total_deaths": "Deaths", "new_cases": "New cases"}
    )
)

time_series_grouped = (all_data
    .groupby(["date"])
    .sum()
    .reset_index()
    .rename(
        columns={"location":"Country", "total_cases": "Confirmed", "total_deaths": "Deaths", "new_cases": "New cases"}
    )
)

time_series_controls = html.Div(
    [
    
        dbc.RadioItems(
            id="yaxis-type",
            options=[{"label": i, "value": i} for i in ["Linear", "Log"]],
            value="Linear",
            inline=True,
            
        )
    ],
    style={"width": "100%", "height": "30px", "display": "inline-block",  'backgroundColor': "#111144"},
)



#



##################################################################################################
# Start dash app
##################################################################################################


# Navigation Bar with INFO BUTTON
modal = html.Div(
    [
        dbc.Button("Info", id="open", className="btn-info mt-1 mb-1"),
        dbc.Modal(
            [
                dbc.ModalHeader("Welcome to the project: Coronavirus Dashboard"),
                dbc.ModalBody(
                    [
                        html.P(
                            f"On Dec 31, 2019, the World Health Organization (WHO) was informed of \
                    an outbreak of “pneumonia of unknown cause” detected in Wuhan City, Hubei Province, China – the \
                    seventh-largest city in China with 11 million residents. The novel respiratory infection disease we \
                         are collectively battling emerged last year inChina, and has since triggered a COVID-19 outbreak \
                         on a global scale. According tofindings, this disease is the product of natural evolution.\
                    This dash board is developed to visualise and track the recent reported \
                    cases in Zew Zealand."
                        ),
                       
                        html.P(
                            " "
                        ),
                        
                        html.B(html.P("Data sources: ")),
                        html.P(
                            ["1)Time series Covid-19 data of New Zealand extracted from World covid data available at ourworldindata.org ", html.Br(),
                            " 2) Mobility Data of New Zealand from COVID-19 Community Mobility Reports provided by google."]
                            ),
                        html.P(
                                [" Note: Dashboard is made for COVID data Upto 28 March 2021"
                                ]
                        ),
                   
                     
                        html.H6(
                            [   "Developers:  Pranay Junare  &  Mihir Kulkarni ", html.Br(),
                                "Mentor: Baraa Said" , html.Br(),
                                "Built using ",
                                html.A("Dash", href="https://dash.plotly.com/"),
                            ]
                        ),
                    ]
                ),
                dbc.ModalFooter(dbc.Button("Close", id="close", className="ml-auto")),
            ],
            id="modal",
        ),
    ]
)

#Navigation Bar 
navbar = dbc.NavbarSimple(
    children=[dbc.NavItem([modal])],
    brand="Coronavirus (COVID-19) NEW-ZEALAND Dashboard",
    brand_href="#",
    color="dark",
    dark=True,
    fluid=True,
    className="mb-2",
)


#Footer 
footer = html.Div(
    id="my-footer",
    style={
        "marginLeft": "1.5%",
        "marginRight": "1.5%",
        "marginBottom": "1%",
        "marginTop": ".5%",
        'backgroundColor': "#111111"
    },
    children=[
        html.Hr(style={"marginBottom": ".5%"},),
        html.P(
            style={"textAlign": "center", "margin": "auto"},
            children=[
                " | ",
                html.A(
                    "Developed by Pranay Junare & Mihir Kulkarni",
                    href="https://www.linkedin.com/in/pranay-junare/",
                ),
                " | ",
                html.A(
                    "About this dashboard",
                    href="https://github.com/",
                    target="_blank",
                ),
                " | ",
                #   html.A('Report a bug', href='', target='_blank')
            ],
        ),
        html.P(
            style={"textAlign": "center", "margin": "auto", "marginTop": ".5%","color":'white'},
            children=["Stay home stay safe"],
        ),
        html.P(
            style={"textAlign": "center", "margin": "auto", "marginTop": ".5%"},
            children=[],
        ),
    ],
)



# Few charts with dropdown


# left column with information, tables and newsfeed
left_column = dbc.Col(
    html.Div(
        [ html.Div([data_table]),
          html.Div([
            dcc.Dropdown(
                id="ticker",
                options=[{"label": x, "value": x} 
                        for x in all_data.columns[1:]],
                value=all_data.columns[1],
                clearable=False,
                multi=True,
                style={'backgroundColor': '#1E1E1E'},
             ),
            dcc.Graph(id="time-series-chart"),
                ])
        ]
    ),
        lg=4,
    width={"order": 2},

)

# right column with visuals
right_column = dbc.Col(
    html.Div(
        [
           
            html.Div(
                [time_series_controls, html.Div(id="time-series-cases")],
                className="border bg-white",
            ),
        ]
    ),
    lg=8,
    width={"order": 2},
    
)


body_row = html.Div([dbc.Row([left_column, right_column])])

#########################################################################################
#  DEFAULT LAYOUT 
########################################################################################
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server
app.title = "Covid-19 tracker"


def serve_layout():
    return dbc.Container(
        [html.Div(navbar),html.Div([cards, body_row]),footer],
        fluid=True,
        className="bg-light",
    )

app.layout = serve_layout




#########################################################################################
# WRAPPERS TO ADD INP OUTPUT TO THE COMPONENTS
#########################################################################################
# Modal control
@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("time-series-cases", "children"),
    [
        Input("yaxis-type", "value"),
        Input("datatable-interactivity", "derived_virtual_data"),
        Input("datatable-interactivity", "derived_virtual_selected_rows"),
    ],
)
def time_series_control(radio_items_value, rows, derived_virtual_selected_rows):
    # Which radiobutton has been chosen
    if radio_items_value == "Linear":
        log_y = False
    elif radio_items_value == "Log":
        log_y = True

    if derived_virtual_selected_rows is not None:
        table_rows = [rows[i] for i in derived_virtual_selected_rows]
        country_rows = [item.get("Country") for item in table_rows]
        print(table_rows)
        print(country_rows)
    else:
        country_rows = ""

    def time_series(data_frame, y, label_name, log_y, title, color_discrete):
        time_series_figure = px.line(
            data_frame,
            x="date",
            y=y,
            labels={"date": "Date", y: label_name},
            log_y=log_y,
            title=title,
            color_discrete_sequence=[color_discrete],
            template='plotly_dark'

        )
        time_series_figure.update_layout(
            # margin={"r": 0, "t": 40, "l": 0, "b": 0},
            # xaxis_title="",
            # yaxis_title="",
            # hovermode="x",
        )

        return time_series_figure

    if len(country_rows) != 0:                   # Plots when Selected 
        times_series_cases = px.line(
            time_series_grouped_country[time_series_grouped_country["Country"].isin(country_rows)],
            x="date",
            y="New cases",
            labels={"date": "Date"},
            log_y=log_y,
            title="New Cases Timeline",
            color="Country",
            template='plotly_dark'
        )
        times_series_cases.update_layout(
            # margin={"r": 0, "t": 40, "l": 0, "b": 0},
            # xaxis_title="",
            # yaxis_title="",
            # hovermode="x",
        )
    else:                                         # Plots in default State
        times_series_cases = time_series(
            time_series_grouped,
            "new_tests",
            "New Tests",
            log_y,
            "New Tests Timeline",
            "red",
        )
    times_series_cases.update_traces(mode="lines")   #"lines+markers" if we want both

    return dcc.Graph(figure=times_series_cases)


#Few time charts (Left ones)
@app.callback(
    Output("time-series-chart", "figure"), 
    [Input("ticker", "value")])
def display_time_series(ticker):
    fig = px.line(all_data, x='date', y=ticker,
                    template='plotly_dark')
                                    
                                    
    return fig

#########################################################################################
# START THE APP
#########################################################################################

if __name__ == '__main__':
    app.run_server(debug=True)    #runs local server

