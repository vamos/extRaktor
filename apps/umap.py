# Author: libor@labavit.com
# Year: 2021
# Desc.: UMAP application page

from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from apps import graph_settings # custom colors, layout, zoom and hidden modebar
import plotly.express as px
import pandas as pd
from app import app
import umap

layout = html.Div(
    [  # row-umap
        html.Div(
            [
                dcc.Loading(
                    [
                        dcc.Graph(id="graph_umap")
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
                    id='dropdown-umap-init',
                    value='spectral',
                    clearable=False,
                    options=[
                        {'label': 'spectral', 'value': 'spectral'},
                        {'label': 'random', 'value': 'random'}
                    ],
                ),
                html.P("Metric:"),
                dcc.Dropdown(
                    id="dropdown-metric",
                    value='euclidean',
                    clearable=False,
                    placeholder="euclidean",
                    className='round-border tsne-input',
                    options=[
                        {'label': 'euclidean', 'value': 'euclidean'},
                        {'label': 'manhattan', 'value': 'manhattan'},
                        {'label': 'chebyshev', 'value': 'chebyshev'},
                        {'label': 'minkowski', 'value': 'minkowski'},
                    ],
),
                html.P("Min. distance:"),
                dcc.Input(
                    id="input-min-dist",
                    type="number",
                    value=0.1,
                    placeholder="0.0 - 0.99",
                    className='round-border tsne-input'
                ),
                html.P("Nr. of neighbors:"),
                dcc.Input(
                    id="input-neighbors",
                    type="number",
                    value=15,
                    placeholder="2 - 200",
                    className='round-border tsne-input'
                ),
                html.Button(
                    'Reset',
                    id='btn-umap-reset',
                    n_clicks=0,
                    className='round-border btn-gradient'),
            ],
            className='pretty_container_right one column'
        )

    ],
    id='row-umap',
    className='row flex-display'
)


# - - - - - - - - - - CALLBACKS - - - - - - - - - -


@app.callback(
    [
        Output('btn-umap-reset', 'n_clicks'),
        Output('dropdown-umap-init', 'value'),
        Output('dropdown-metric', 'value'),
        Output('input-min-dist', 'value'),
        Output('input-neighbors', 'value'),
    ],
    [
        Input('btn-umap-reset', 'n_clicks'),
    ]
)
def reset_umap(in_n_clicks):  # every callback needs at least one Input, its needed, but not used
    """

    :param in_n_clicks: auxiliary variable
    :return: default values to input elements
    """

    # default UMAP parameter values
    n_clicks = 0
    init = 'spectral'
    min_dist = 0.1
    n_neighbors = 15
    metric = 'euclidean'

    return n_clicks, init, metric, min_dist, n_neighbors


@app.callback(
    [
        Output('graph_umap', 'figure'),  # plot t-SNE
        Output('graph_umap', 'config'),  # default zoom, hide modebar
    ],
    [
        Input('table', 'derived_virtual_data'),  # get data from table
        Input('dropdown-umap-init', 'value'),
        Input('dropdown-metric', 'value'),
        Input('input-min-dist', 'value'),
        Input('input-neighbors', 'value'),
    ]
)
def update_umap(rows, in_init, in_metric, in_dist, in_neighbor):
    """

    :param rows: input data from dash_table.DataTable
    :param in_init: input value
    :param in_metric: input value
    :param in_dist: input value
    :param in_neighbor: input value
    :return: UMAP graph
    """

    print(f'updating umap')
    # take data from cache files
    df = pd.DataFrame(rows)
    filenames = df['file']
    # drop column files in case PDFs were loaded
    # get values only
    df = df.drop('file', axis=1)
    print(f'umap input: {df}')

    umap_2d = umap.UMAP(
        n_components=2,
        init=in_init,
        random_state=1,
        min_dist=in_dist,
        n_neighbors=in_neighbor,
        metric=in_metric
    )
    features = umap_2d.fit_transform(df)
    print(f'umap features: {features}')
    fig_umap = px.scatter(
        features,
        x=0,
        y=1,
        height=700,
        color=filenames,
        color_discrete_sequence = graph_settings.colors,
    )
    fig_umap.update_layout(
        title='Uniform Manifold Approximation and Projection',
        title_x=0.5,                                                # center title
        margin=graph_settings.tight_layout,
        template='plotly_dark',
        showlegend=False,
        xaxis={'visible': False, 'showticklabels': False},
        yaxis={'visible': False, 'showticklabels': False},
    )
    # fig_umap.write_image("umap.pdf")
    return fig_umap, graph_settings.config
