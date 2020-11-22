import requests
from bs4 import BeautifulSoup
import plotly.offline as pyo
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

#### Returns list of show names correspnding IMDb IDs for the search term
def getShows(rawName):
    if rawName != None:
        showName = rawName.replace(' ', '+')
        url = 'http://www.imdb.com/search/title?title=' + showName + '&title_type=tv_series'

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

#### Collects IMDb rating information for a given show and returns a figure
def singleShow(imdbID):

    url2 = 'http://www.imdb.com/title/' + imdbID + '/ratings?ref_=tt_ov_rt'

    page = requests.get(url2)
    soup = BeautifulSoup(page.text, 'html.parser')

    cleanName = soup.find(class_='subpage_title_block__right-column').find('a').text

    rt = soup.find_all(class_='ratingTable')

    demo = []
    rating = []
    votes = []
    wanted = ['imdb_users', 'males', 'females']

    #####Finds rating and number of voters for listed demographics
    for x in range(0, len(rt)-5):
        href = str(rt[x].find('a'))
        index = href.find("=", 10) + 1
        index2 = href.find(">", 10) - 1

        if href[index:index2] in wanted:
            demo.append(href[index:index2])
            rating.append(rt[x].find(class_='bigcell').text)
            votes.append(str(rt[x].find('a').text).strip())


    fig = go.Figure()
    fig.add_trace(go.Bar(
        x= demo,
        y = rating,
        marker_color = ['darkslateblue', 'cornflowerblue', 'hotpink'],
        text = rating,
        textposition = 'auto'))

    if demo != []:
        fig.update_layout(
            title='IMDb Ratings for ' + cleanName)
    else:
        fig.update_layout(
            title='No IMDb Ratings for ' + cleanName)
    return fig


fig = go.Figure()

#### Initiate the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

#### Set up the layout

dropDownList = []
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
GIT_LOGO = "/assets/GitHub-Mark-Light-64px.png"
navbar = dbc.Navbar(
    [
    dbc.Row([
        dbc.Col([
            html.A(
                html.Img(src=PLOTLY_LOGO, height="30px"),
                href = "https://plot.ly"
            ),
            dbc.NavbarBrand("IMDb Visualizer", className="ml-2", style={'font-size': '25px', 'padding-left':'20px'}),
        ]),
        dbc.Col(
            html.A(
                html.Img(src=GIT_LOGO, height="30px"),
                href = "https://plot.ly"
            )
        )
        ])
    ],
    color="dark",
    dark=True,
)
app.layout = html.Div(children=[
    navbar,
    html.Br(),
    dcc.Input(id="input1", type="text", placeholder="Type name of show", debounce=True),
    html.Button('Search', id='submit-val'),
    html.Div(id="output1"),
    html.Div(id="dropText"),
    dcc.Dropdown(
        id='dropdown',
        options=dropDownList,
        value='',
        style={'display': 'none'}
    ),
    dcc.Graph(
        id='IMDb',
        figure=fig),
]
)


#### Update figure and text upon search
@app.callback(
    [Output('IMDb', 'figure'),
    Output('output1', 'children'),
    Output('dropdown', 'options'),
    Output('dropdown', 'style'),
    Output('dropText', 'children')],
    [Input('submit-val', 'n_clicks'),
    Input('dropdown', 'value')],
    [State('input1', 'value')]
)

#### Confused how to make decide when to take show value from text box vs dropdown
def update_from_search(clicks, dropValue, input_value):
    global dropDownList
    trigger = dash.callback_context.triggered[0]['prop_id']
    print(trigger)
    if trigger == 'submit-val.n_clicks':
        if input_value != None:

            showList = getShows(input_value)

            if showList != {}:
                firstShowID = next(iter(showList.keys()))
                updatedFig = singleShow(firstShowID)
                dropDownList = [{'label': showList[i], 'value': i} for i in iter(showList.keys())]
                return(updatedFig,
                       '',
                       dropDownList,
                       {'display': 'block'},
                       'Wrong show? Check here for other results:'
                       )
            else:
                return(go.Figure(),
                       'No show found with name: {}'.format(input_value),
                      [],
                      {'display': 'none'},
                      ''
                       )

    elif trigger == 'dropdown.value':
        if dropValue != '':
            print("dropValue trying to update")
            print(dropValue)
            updatedFig = singleShow(dropValue)
            return(updatedFig,
                   '',
                   dropDownList,
                   {'display': 'block'},
                   'Wrong show? Check here for other results:'
                   )

    return(go.Figure(),
           '',
           [],
           {'display': 'none'},
           ''
           )

if __name__ == '__main__':
    app.run_server()