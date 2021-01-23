import requests
from bs4 import BeautifulSoup
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# Returns list of show names corresponding IMDb IDs for the search term
def getShows(rawName):
    if rawName != None:
        showName = rawName.replace(' ', '+')
        url = 'http://www.imdb.com/search/title?title=' + showName + '&title_type=tv_series,tv_miniseries'

        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        allShows = soup.find_all(class_='lister-item-header')

        showList = {}

        for show in allShows:
            year = show.find(class_='lister-item-year text-muted unbold').text
            href = str(show.find('a'))
            end = href.find('/', 17)
            imdbID = href[16:end]
            showList[imdbID] = show.find('a').text + " " + year
        return showList

# Uses rating data passed from singleShow() to generate figures
def makeFigure(rt, mode, cleanName):
    demo = []
    rating = []
    votes = []
    markerColor = []

    if mode == 'Gender':
        wanted = ['imdb_users', 'males', 'females']
        markerColor = ['darkslateblue', 'cornflowerblue', 'hotpink']
    elif mode == 'Age':
        wanted = ['imdb_users', 'aged_under_18', 'aged_18_29', 'aged_30_44', 'aged_45_plus']
        markerColor = ['darkslateblue', '#3a4b53', '#57707d', '#7d97a5', '#becbd2']

    # Finds rating and number of voters for listed demographics
    for x in range(0, len(rt) - 5):
        href = str(rt[x].find('a'))
        index = href.find("=", 10) + 1
        index2 = href.find(">", 10) - 1

        if href[index:index2] in wanted:
            title = href[index:index2]
            if mode == 'Gender' and title != 'imdb_users':
                demo.append(title)
                print(title)
                print(title[5:])
            else:
                demo.append(title[5:])
                print(title[5:])

            rating.append(rt[x].find(class_='bigcell').text)
            votes.append(str(rt[x].find('a').text).strip())

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=demo,
        y=rating,
        marker_color=markerColor,
        text=rating,
        textposition='auto'))

    if demo != []:
        fig.update_layout(
            title= mode + ' ratings for ' + cleanName,
            yaxis={'range': [0, 10]},
            margin={'t':40,'l':10,'b':0,'r':10},
            height=400
        )

    else:
        fig.update_layout(
            title='No IMDb Ratings for ' + cleanName)
    return fig

# Collects ratings information for a single show and uses makeFigure() to return figures for Gender and Age
def singleShow(imdbID):

    url2 = 'http://www.imdb.com/title/' + imdbID + '/ratings?ref_=tt_ov_rt'

    page = requests.get(url2)
    soup = BeautifulSoup(page.text, 'html.parser')

    cleanName = soup.find(class_='subpage_title_block__right-column').find('a').text

    rt = soup.find_all(class_='ratingTable')

    figG = makeFigure(rt, 'Gender', cleanName)
    figA = makeFigure(rt, 'Age', cleanName)
    figs = [figG, figA]

    return figs


fig = go.Figure()

# Initiate the app and set theme (other themes at https://bootswatch.com/)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Define the app layout
dropDownList = []
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
GIT_LOGO = "/assets/GitHub-Mark-Light-64px.png"

navbar = dbc.Navbar(
    [
    dbc.Row([
        dbc.Col(
            html.A(
                html.Img(src=PLOTLY_LOGO, height="30px"),
                href = "https://plot.ly"
            ), width=1
        )
        ]),
    dbc.Row([
        dbc.Col(
            dbc.NavbarBrand("IMDb Reviews Visualizer", className="ml-2", style={'font-size': '25px', 'padding-left':'20px'}),
        width=3
        ),
        ] ),
    dbc.Row([
        dbc.Col(
            [
                html.A(
                    html.Img(src=GIT_LOGO, height="30px"),
                    href = "https://github.com/yoyochris924/IMDb_Visualizer"
                )
            ])
        ], justify='between')

    ],
    color="dark",
    dark=True,
)

tab1 = dbc.Card(
    dbc.CardBody(
        [
            html.H3("What is the IMDb Reviews Visualizer?"),
            html.P(children=[
                "When looking for a new show to watch, we often "
                "check the ratings first on a site like IMDb. When deciding between shows like ",
                html.Em('Amish Mafia'),
                " (3.1) or ",
                html.Em('Chernobyl'),
                " (9.4), the choice is clear. But when the stakes are high",
                " and the ratings are close, a single value rating just doesn't cut it.",
                " In these cases, we can take a closer look at the ratings broken down by demographics",
                " such as age or gender.",
                html.Br(),html.Br(),
                "Some shows skew heavily towards one demographic, like ",
                html.Em('Sex & the City'),
                " with a whopping 2.1 point difference between men and women. Or ",
                html.Em('Beavis & Butt-Head'),
                " with a 1 point difference in the other direction. And it seems like the older you get,",
                " the more you love shows like ",
                html.Em('Downton Abbey'),
                " while the teens just can't get enough of their ",
                html.Em('Gossip Girl.'),
                html.Br(),html.Br(),
                "Check out the ratings yourself by clicking the ",
                html.Strong("Try it!"),
                " tab."
            ])
        ]
    )
)

tab2 = dbc.Card(
    dbc.CardBody(
        [
            html.P(children=[
                    "Now, take these ratings with a grain of salt. Just because a show is poorly rated by people"
                    " of your age or gender, that doesn't mean you wont like it. ",
                    html.Em('The Mindy Project'),
                    " is an objectively great show even though men rated it 1.6 points lower than women! "
            ]),
            html.P("Search for a specific show or leave it blank and click Search for the current top shows:"),
            dcc.Input(id="input1", type="text", placeholder="Type name of show",value='', debounce=True),
            dbc.Button('Search', id='submit-val', color='primary'),
            html.Div(id="output1"),
            html.Div(id="dropText"),
            dcc.Dropdown(
                id='dropdown',
                options=dropDownList,
                value='',
                style={'display': 'none',}
            ),
        ]
    )
)

tabs = dbc.Tabs(
    [
        dbc.Tab(tab1, label="About"),
        dbc.Tab(tab2, label="Try it!"),
    ]
)

app.layout = html.Div(children=[
    navbar,
    html.Br(),
    dbc.Row([
        dbc.Col(tabs),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card(id='GCard', children=[
                dbc.CardBody(
                    dcc.Graph(
                    id='Gender',
                    figure=fig),

                )], style={'display': 'none'}
            )
        ),
        dbc.Col(
            dbc.Card(id='ACard', children=[
                dbc.CardBody(
                    dcc.Graph(
                        id='Age',
                        figure=fig),

                )], style={'display': 'none'}
                     )
        ),
    ])
])

# Update figure and text upon search
@app.callback(
    [Output('Gender', 'figure'),
    Output('Age', 'figure'),
    Output('output1', 'children'),
    Output('dropdown', 'options'),
    Output('dropdown', 'style'),
    Output('dropText', 'children'),
    Output('GCard', 'style'),
    Output('ACard', 'style'),],
    [Input('submit-val', 'n_clicks'),
    Input('dropdown', 'value'),],
    [State('input1', 'value')]
)

# Called whenever an Input value changes, but not when a State value changes
def update_from_search(clicks, dropValue, input_value):
    global dropDownList
    global showList

    trigger = dash.callback_context.triggered[0]['prop_id']

    if trigger == 'submit-val.n_clicks':
        if input_value != None:

            showList = getShows(input_value)

            if showList != {}:
                firstShowID = next(iter(showList.keys()))
                updatedFigs = singleShow(firstShowID)
                dropDownList = [{'label': showList[i], 'value': i} for i in iter(showList.keys())]
                return(updatedFigs[0],
                       updatedFigs[1],
                       '',
                       dropDownList,
                       {'display': 'block'},
                       'Wrong show? Check here for other results:',
                       {'display': 'block'},
                       {'display': 'block'}
                       )
            else:
                return(fig,
                        fig,
                        'No show found with name: {}'.format(input_value),
                        [],
                        {'display': 'none'},
                        '',
                        {'display': 'block'},
                        {'display': 'block'}
                       )

    elif trigger == 'dropdown.value':
        if dropValue != '':
            updatedFigs = singleShow(dropValue)
            return(updatedFigs[0],
                   updatedFigs[1],
                   '',
                   dropDownList,
                   {'display': 'block'},
                   'Wrong show? Check here for other results:',
                   {'display': 'block'},
                   {'display': 'block'}
                   )

    return(fig,
           fig,
           '',
           [],
           {'display': 'none'},
           '',
           {'display': 'none'},
           {'display': 'none'}
           )

# Start server
if __name__ == '__main__':
    app.run_server()