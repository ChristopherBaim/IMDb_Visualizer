import requests
from bs4 import BeautifulSoup
import plotly.offline as pyo
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#### Gets IMDb ID from show name


def singleShow(rawName):
    #rawName = input("Show name:")
    showName = rawName.replace(' ', '+')
    url = 'http://www.imdb.com/search/title?title=' + showName + '&title_type=tv_series'

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    show = soup.find(class_='lister-item-header')

    href = str(show.find('a'))
    # print(href)

    #### Confirm correct show name
    print(show.find('a').text)
    imdbID = href[16:25]
    print(imdbID)

    url2 = 'http://www.imdb.com/title/' + imdbID + '/ratings?ref_=tt_ov_rt'

    page = requests.get(url2)
    soup = BeautifulSoup(page.text, 'html.parser')

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


    fig.update_layout(
        title='IMDb Ratings by Demographic')
    return fig
#pyo.plot(fig, filename='IMDb.html')
####delete if not separate method
fig = go.Figure()
#fig.show()

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title="Breakdown of IMDb Ratings by Demographic"

########### Set up the layout
app.layout = html.Div(children=[
    html.H1("Breakdown of IMDb Ratings by Demographic"),
    html.Br(),
    dcc.Input(id="input1", type="text", placeholder="Type name of show", debounce=True),
    html.Div(id="output"),
    html.Div(id="output2"),
    dcc.Graph(
        id='IMDb',
        figure=fig),
    ]
)

@app.callback(
    Output('IMDb', 'figure'),
    [Input("input1", "value")]
)
def update_output_fig(input_value):
    return singleShow(input_value)

@app.callback(
    Output("output2", "children"),
    [Input("input1", "value")]
)
def update_output_div(input_value):
    return 'Output: {}'.format(input_value)

if __name__ == '__main__':
    app.run_server()