# Author: libor@labavit.com
# Year: 2021
# Desc.: t-SNE application page

from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from sklearn.manifold import TSNE
from apps import graph_settings                 # custom colors, layout, zoom and hiddne modebar
import plotly.express as px
import pandas as pd
from app import app


layout = html.Div(
    [  # row-tsne
        html.Div(
            [
                dcc.Loading(
                    [
                        dcc.Graph(id="graph_tsne")
                    ],
                    color='#00CC96',
                    type='cube'
                )
            ],
            className="pretty_container_left eleven columns"
        ),
        html.Div(
            [
                html.P("Initialization:"),
                dcc.Dropdown(
                    id='dropdown-init',
                    value='random',
                    clearable=False,
                    options=[
                        {'label': 'random', 'value': 'random'},
                        {'label': 'pca', 'value': 'pca'}
                    ],
                ),
                html.P("Nr. of Iterations:"),
                dcc.Input(
                    id="input-iterations",
                    type="number",
                    value=1000,
                    placeholder="1000",
                    className='round-border tsne-input'
                ),
                html.P("Learning Rate:"),
                dcc.Input(
                    id="input-learning-rate",
                    type="number",
                    value=50,
                    placeholder="50",
                    className='round-border tsne-input'
                ),
                html.P("Perplexity:"),
                dcc.Input(
                    id="input-perplexity",
                    type="number",
                    value=30,
                    placeholder="30",
                    className='round-border tsne-input'
                ),
                html.Button(
                    'Reset',
                    id='btn-tsne-reset',
                    n_clicks=0,
                    className='round-border btn-gradient'),
            ],
            className='pretty_container_right one column'
        )
    ],
    id='row-tsne',
    className='row flex-display'
)


# - - - - - - - - - - CALLBACKS - - - - - - - - - -


@app.callback(
    [
        Output('btn-tsne-reset', 'n_clicks'),
        Output('dropdown-init', 'value'),
        Output('input-iterations', 'value'),
        Output('input-learning-rate', 'value'),
        Output('input-perplexity', 'value'),
    ],
    [
        Input('btn-tsne-reset', 'n_clicks'),        # reset parameter values
    ]
)
def reset_tsne(in_n_clicks):
    """

    :param in_n_clicks: auxiliary variable
    :return: default values to input elements
    """

    # definition of default t-SNE parameters
    n_clicks = 0
    init = 'random'
    iterations = 1000
    learning_rate = 50
    perplexity = 30

    return n_clicks, init, iterations, learning_rate, perplexity


@app.callback(
    [
        Output('graph_tsne', 'figure'),  # plot t-SNE
        Output('graph_tsne', 'config'),  # default zoom, hide modebar
    ],
    [
        Input('table', 'derived_virtual_data'),  # get data from table
        Input('input-iterations', 'value'),
        Input('input-learning-rate', 'value'),
        Input('input-perplexity', 'value'),
        Input('dropdown-init', 'value'),
    ]
)
def update_tsne(rows,in_iterations,in_learning_rate,in_perplexity,in_init):
    """

    :param rows: input data from dash_table.DataTable
    :param in_iterations: input value
    :param in_learning_rate: input value
    :param in_perplexity: input value
    :param in_init: input value
    :return: t-SNE graph
    """

    print(f'updating tsne')
    print(f'iterations: {in_iterations}')

    # take data from cache files
    df = pd.DataFrame(rows)
    filenames = df['file']
    # drop column files in case PDFs were loaded
    # get values only
    df = df.drop('file', axis=1)
    print(f't-SNE input: {df}')

    # configure TSNE
    tsne = TSNE(
        n_components=2,
        n_iter=in_iterations,
        init=in_init,
        random_state=1,
        perplexity=in_perplexity,      # expected density
        learning_rate=in_learning_rate,
    )
    features = tsne.fit_transform(df)
    print(f't-SNE features: {features}')
    fig_tsne = px.scatter(
        features,
        x=0,
        y=1,
        height=700,
        color=filenames,
        color_discrete_sequence=graph_settings.colors,
    )

    fig_tsne.update_layout(
        title='t-distributed Stochastic Neighbor Embedding',
        title_x=0.5,                                                # center title
        margin=graph_settings.tight_layout,
        template='plotly_dark',
        showlegend=False,
        xaxis={'visible': False, 'showticklabels': False},
        yaxis={'visible': False, 'showticklabels': False},
    )
    # fig_tsne.write_image("tsne.png")

    return fig_tsne, graph_settings.config
