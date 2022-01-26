# Author: libor@labavit.com
# Year: 2021
# Desc.: PCA application page

from dash.dependencies import Input, Output
from sklearn.decomposition import PCA
import dash_core_components as dcc
import dash_html_components as html
from sklearn.cluster import KMeans
import plotly.graph_objects as go
from apps import graph_settings
import pandas as pd
import plotly.express as px
from app import app
import numpy as np
import dash

layout = html.Div(
    [  # row-pca
        html.Div(
            [  # PCA graph
                dcc.Loading(
                    [
                        dcc.Graph(id="graph_pca")
                    ],
                    color='#00CC96',
                    type='cube',
                    style={
                        'margin-top': '400px',
                    }
                )
            ],
            className="pretty_container_left eight columns"
        ),
        html.Div(
            [  # graph for first four principal components
                dcc.Loading(
                    [
                        dcc.Graph(id='graph_pcomps'),
                    ],
                    color='#00CC96',
                    type='cube'
                ),
                html.Div(
                    [
                        dcc.Slider(
                            id='slider-pca',
                            min=1,
                            max=4,
                            value=2,
                            marks={
                                1: '',
                                2: '',
                                3: '',
                                4: '',
                            },
                        ),
                        html.P("Drag to select components.",
                               style={
                                   'fontSize': 16,
                                   'color': '#CACACA',
                                   'margin-left': '15px'
                               }
                        ),
                    ],
                    style={
                        'margin-left': '20px',
                        'margin-right': '10px'
                    }
                ),
                html.Div(
                    [
                        dcc.Loading(
                            [
                                dcc.Graph(id="graph_clusters")
                            ],
                            color='#00CC96',
                            type='cube'
                        )
                    ]
                )
            ],
            className='pretty_container_right three columns'
        )
    ],
    id='row-pca',
    className='row flex-display'
)


# - - - - - - - - - - CALLBACKS - - - - - - - - - -


@app.callback(
    [
        Output('graph_pca', 'figure'),          # plot PCA
        Output('graph_pca', 'config'),          # default zoom, hide modebar
        Output('graph_pcomps', 'figure'),       # plot first four principal components
        Output('graph_pcomps', 'config'),
        Output('graph_clusters', 'figure'),     # print k-means inertia graph
        Output('graph_clusters', 'config'),
    ],
    [
        Input('table', 'derived_virtual_data'),  # get data from table
        Input('slider-pca', 'value'),            # get data from slider
        Input('graph_clusters', 'clickData'),    # get data from clusters graph
    ]
)
def update_pca(rows, input_components, clusters_selected):
    """

    :param rows: iinput data from table
    :param input_components: number of principal components
    :param clusters_selected: selected number of clusters
    :return: pca graph, pc graph, k-means graph
    """

    # determine which input triggered callback
    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

    print(f'updating pca | triggered by: {trigger}')
    print(f'number of clusters selected: {clusters_selected}')

    df_pca = pd.DataFrame(rows)
    print(f'pca input: {df_pca}')
    # drop column files in case PDFs were loaded
    filenames = df_pca['file']
    # get values only
    df_pca = df_pca.drop('file', axis=1)
    pca_in = PCA(n_components=input_components)
    features = pca_in.fit_transform(df_pca)

    # PCA side menu barchart
    if trigger == 'slider-pca':
        print(f'not updating EVR')
        fig_evr = dash.no_update
        graph_settings.config_nozoom = dash.no_update
    else:
        pca_in4 = PCA(n_components=4)
        pca_in4.fit_transform(df_pca)
        ev_ratio = np.round(pca_in4.explained_variance_ratio_ * 100, decimals=1)
        print(f'EVR: {ev_ratio}')
        print(f'features: {features}')
        fig_evr = go.Figure()
        fig_evr.add_trace(
            go.Scatter(
                x=['PC1', 'PC2', 'PC3', 'PC4'],
                y=ev_ratio,
                line=dict(color='#7BFBC5', width=4, shape='hvh'),
            )
        )
        fig_evr.update_layout(
            title='Explained variance [%]',
            title_x=0.5,
            height=300,
            margin=graph_settings.tight_layout,
            template='plotly_dark',
            showlegend=False,
        )
    if clusters_selected is not None:
        nr_clusters = clusters_selected['points'][0]['x']
        features_reduced = pd.DataFrame(features, index=df_pca.index)
        kmeans = KMeans(n_clusters=nr_clusters)
        kmeans.fit(features_reduced)
        kmeans_model = kmeans.predict(features_reduced)

        if input_components == 2:
            pca_kmeans = go.Scatter(
                x=features_reduced[0],
                y=features_reduced[1],
                text=df_pca.index,
                name='',
                mode='markers',
                marker=dict(
                    color=kmeans_model,
                    colorscale=graph_settings.colors
                ),
                showlegend=False,
                hovertext=filenames,
                hoverinfo="text",
            )
        if input_components == 3:
            pca_kmeans = go.Scatter3d(
                x=features_reduced[0],
                y=features_reduced[1],
                z=features_reduced[2],
                text=df_pca.index,
                name='',
                mode='markers',
                marker=dict(
                    color=kmeans_model,
                    colorscale=graph_settings.colors
                ),
                showlegend=False,
                hovertext=filenames,
                hoverinfo="text",
            )

        layout_pk = go.Layout(
            hovermode='closest',
            xaxis=go.layout.XAxis(
                showgrid=False, zeroline=False, showticklabels=False),
            yaxis=go.layout.YAxis(
                showgrid=False, zeroline=False, showticklabels=False),
        )
        layout_pk['title'] = f'PCA + k-means: {nr_clusters} clusters)'
        fig_pca = go.Figure(data=pca_kmeans, layout=layout_pk)

    else:
        if input_components == 2:
            labels = {str(i): "PC {}".format(i + 1) for i in range(2)}
            fig_pca = px.scatter(
                features,
                x=0,
                y=1,
                labels=labels,
                color=filenames, # TODO comment for xlsx files
                color_discrete_sequence=graph_settings.colors,
            )
            fig_pca.update_layout(
                xaxis={'visible': True, 'showticklabels': False},
                yaxis={'visible': True, 'showticklabels': False},
            )
        elif input_components == 3:  # TODO nefunguje pro tri soubory
            # 3D PCA
            labels = {str(i): "PC {}".format(i + 1) for i in range(3)}
            fig_pca = px.scatter_3d(
                features,
                x=0,
                y=1,
                z=2,
                labels=labels,
                color=filenames,
                color_discrete_sequence=graph_settings.colors,
            )
        else:
            labels = {str(i): "PC {}".format(i + 1) for i in range(4)}
            fig_pca = px.scatter_matrix(
                features,
                dimensions=range(4),
                labels=labels,
                color=filenames,
                color_discrete_sequence=graph_settings.colors,
            )
            fig_pca.update_traces(diagonal_visible=False)

    fig_pca.update_layout(
        # responsive to parent without explicit size
        title='Principal Component Analysis',
        title_x=0.5,
        margin=graph_settings.tight_layout,
        template='plotly_dark',
        showlegend=False,
    )

    #  k-means support graph
    max_clusters = len(features)
    # reduce number of computed clusters in case of larger datasets
    if max_clusters > 20:
        max_clusters = 20

    # apply k-means checkbox
    inertias = np.zeros(max_clusters)
    for i in range(1, max_clusters):
        kmeans = KMeans(n_clusters=i)
        kmeans.fit(features)
        inertias[i] = kmeans.inertia_
    rangeprint = range(1, max_clusters)
    print(f'cluster range: {rangeprint}')
    kmeans_data = go.Scatter(
        x=list(range(1, max_clusters)),
        y=inertias[1:],
        line=dict(color='#7BFBC5', width=4),
    )
    layout_kmeans = go.Layout(
        title='Select Number of Clusters',
        xaxis=go.layout.XAxis(title='Number of clusters', range=[0, max_clusters]),
        yaxis=go.layout.YAxis(title='Inertia')
    )
    fig_clusters = go.Figure(data=kmeans_data, layout=layout_kmeans)
    fig_clusters.update_layout(
        # responsive to parent without explicit size
        title_x=0.5,
        margin=graph_settings.tight_layout,
        template='plotly_dark',
        showlegend=False,
        height=300,
        hovermode='x',
    )

    return \
        fig_pca, graph_settings.config,\
        fig_evr, graph_settings.config_nozoom,\
        fig_clusters, graph_settings.config_nozoom
