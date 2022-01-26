# Author: libor@labavit.com
# Year: 2021
# Desc.: Dendrogram application page

from dash.dependencies import Input, Output
from sklearn.decomposition import PCA
import dash_html_components as html
import dash_core_components as dcc
import plotly.figure_factory as ff              # dendrogram
from apps import graph_settings                 # custom colors, layout, zoom and hidden modebar
import pandas as pd
from app import app

layout = html.Div(
    [  # row-dendrogram
        html.Div(
            [
                dcc.Loading(
                    [
                        dcc.Graph(id="graph_dendrogram")
                    ],
                    color='#00CC96',
                    type='cube',
                    style={
                         'margin-top': '100px',
                    }
                )
            ],
            className="pretty_container twelve columns"
        ),
        html.Div(
            [

            ]
        )
    ],
    id='row-dendrogram',
    className='row flex-display'
)


# - - - - - - - - - - CALLBACKS - - - - - - - - - -


@app.callback(
    [
        Output('graph_dendrogram', 'figure'),  # plot dendrogram
        Output('graph_dendrogram', 'config'),   # default zoom, hide modebar
    ],
    Input('table', 'derived_virtual_data')  # get data from table
)
def update_dendrogram(rows):

    """

    :param rows: input data from dash_table.DataTable
    :return: dendrogram graph
    """

    # miscelaneous figure configuration
    tight_layout = dict(l=20, r=20, t=50, b=20)
    # labels = {str(i): "PC {}".format(i + 1) for i in range(2)}
    config = dict({'scrollZoom': True, 'displayModeBar': False})

    print(f'updating dendrogram')
    df_pca = pd.DataFrame(rows)
    # drop column files in case PDFs were loaded
    filenames = df_pca['file']
    # get values only
    df_pca = df_pca.drop('file', axis=1)
    pca_in = PCA(n_components=2)
    features = pca_in.fit_transform(df_pca)

    # DENDROGRAM
    fig_dendrogram = ff.create_dendrogram(
        features,
        colorscale=graph_settings.colors,
    )

    fig_dendrogram.update_layout(
        title='Hierarchical Clustering Dendrogram',
        title_x=0.5,    # center
        height=700,
        xaxis_title="Data",
        yaxis_title="Divergence",
        margin=tight_layout,
        template='plotly_dark',
    )
    return fig_dendrogram, config
