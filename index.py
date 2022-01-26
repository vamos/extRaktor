# Author: libor@labavit.com
# Year: 2021
# Desc.: Index page

# DASH
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
from app import app
import dash_table
import dash

# internal packages
from apps import pca, dendrogram, tsne, umap, control_chart      # sub-pages
import pandas as pd

# MISCELLANEOUS
import parser                                   # pdf parser file
import base64                                   # decoding/encoding
import os                                       # path

# necessary global variables
DIRECTORY = "uploaded_files"
extraktor_logo = 'assets/extRaktor_logo.png'
plotly_logo = 'assets/footer_plotly.png'
encoded_image = base64.b64encode(open(extraktor_logo, 'rb').read())
plotly_encoded_image = base64.b64encode(open(plotly_logo, 'rb').read())

app.layout = html.Div(
    [
        html.Div(
            [  # first row - navbar
                html.A(
                    [  # extRactor logo
                        html.Img(
                            id='fp-logo',
                            src='data:image/png;base64,{}'.format(encoded_image.decode()),
                            style={
                                'width': '210px',
                            },
                        ),
                    ],
                    id='extRactor-logo',
                    className='six columns',
                    style={
                        'position': 'relative',
                        'top': '9px',
                        'textAlign': 'center',
                    },
                    href='http://extraktor.herokuapp.com',

                ),
                html.Div(
                    [  # buttons
                        html.Div(
                            [
                                dcc.Link('new_input', href='/', target='_blank'),
                                dcc.Link('pca', href='/apps/pca'),
                                dcc.Link('dendrogram', href='/apps/dendrogram'),
                                dcc.Link('t-sne', href='/apps/tsne'),
                                dcc.Link('umap', href='/apps/umap'),
                            ],
                            className="nav-links",
                            style={
                                'position': 'absolute',
                                'top': '14px'
                            }
                        ),
                        dcc.Location(id='url', refresh=False),
                    ],
                    className='six columns',
                    id='main-menu',
                )
            ], className='row flex-display navbar'
        ),
        html.Div(
            [   # right under navbar is empty div for future page content accessed via navbar links
                html.Div(id='page-content', children=[])
            ]
        ),
        # hidden div / storing filenames between callbacks
        html.Div(id='div-storing-filenames', style={'display': 'none'}),
        html.Div(
            [  # third row - upload
                html.Div(
                    [  # load sample datasets
                        html.Button(
                            'Load sample data',
                            id='btn-load-sample',
                            n_clicks=0,
                            className='round-border btn-gradient'
                        ),
                        html.Button(
                            'Load iris',
                            id='btn-iris-sample',
                            n_clicks=0,
                            className='round-border btn-gradient'
                        )
                    ],
                    id='input-div',
                    className='row flex-display',
                ),
                html.Div(
                    [   # upload
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                'Drag and Drop or Click to ',
                                html.A('Select multiple PDFs or a CSV file'),
                                html.Br(),
                                'PDF can be only Shimadzu Analysis Reports (4 files minimum)',
                                html.Br(),
                                'CSV file must contain only numeric data (1 file maximum)'

                            ]),
                            style={
                                'position': 'fixed',
                                'width': '97.5%',
                                'height': '70%',
                                'lineHeight': '60px',
                                'borderWidth': '3px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'top': '160px',
                                'margin': '10px',
                                'float': 'center',
                                'display': 'inline',
                                'color': '#CECECE'
                            },
                            style_active={
                                'background': '#232323',
                            },
                            multiple=True,
                            className='twelve columns'
                        ),
                    ],  # div Upload nad Image
                ),
            ],
            id='upload-div',
            className='row flex-display',
            style={
                'display': 'inline',
                'position': 'relative'
            }
        ),  # third row end
        html.Div(
            [  # fourth row - table
                html.Div(
                    [
                        html.Div(
                            [  # extract column / sheet
                                html.P("Extract: ")
                            ],
                            style={
                                'width': 120,
                                'padding-top': 7,
                                'margin-left': 8
                            }
                        ),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id='dropdown-extract',
                                    value=[1],
                                    clearable=False,
                                    options=[
                                        {'label': 'tmp', 'value': 'tmp'}
                                    ],
                                ),
                            ],
                            style={
                                'width': 150,
                            }
                        )
                    ],
                    id="div-extract",
                    style={
                        'display': 'flex',
                        'margin-top': 20,
                        'margin-bottom': 20,
                    }
                ),
                dcc.Loading(
                    [
                        html.Div(
                            [

                            ],
                            id='div-table',
                            className='pretty_container twelve columns',
                        ),

                    ],
                    color='#00CC96',
                    type='cube'
                )
            ],
            id='row-table',
            className='row flex-display',
            style={
                'display': 'none',
                'background-color':  '#444444',
                   }
        ),
        # footer
        html.Div(
            [
                html.Div(
                    [
                        html.Label(
                            [
                                'Poured into the web from a mixture of '
                            ],
                            style={
                                'verticalAlign': 'middle'
                            }
                        ),
                        html.Img(
                            id='plotly-logo',
                            src='data:image/png;base64,{}'.format(plotly_encoded_image.decode()),
                            style={
                                'verticalAlign': 'middle',
                                'width': '10%'
                            },

                        ),
                        html.Label(
                            [
                                ' and some '
                            ],
                        ),
                        dcc.Link('VUT', href='http://fit.vut.cz', target='_blank'),
                        html.Label(
                            [
                                ' knowledge. | '
                            ],
                            className='footer-label'
                        ),
                        dcc.Link('Libor Dvoracek', href='mailto:libor@lavabit.com', target='_blank'),
                    ],
                    className='footer'
                )
            ],
            className='row flex-display',
            id='footer-div',
            style={
                'display': 'none'
            }
        )
    ],
    id='mainContainer',
    style={
        "display": "flex",
        "flex-direction": "column"
    },
)


# - - - - - - - - - - HELPER FUNCTIONS - - - - - - - - - -
def save_files(name, content):
    # store uploaded file(s)
    if os.path.isfile(DIRECTORY + '/' + name):
        print(f'File {name} exists, skipping upload.')
    else:
        print(f'Uploading file: {name}')
        data = content.encode("utf8").split(b";base64,")[1]
        # TODO create before?
        with open(os.path.join(DIRECTORY, name), "wb") as fp:
            fp.write(base64.decodebytes(data))


def get_optional_extracts(filenames):
    """
    get list of optional data for extraction

    extract column names in case of PDFs
    extract sheet names in case of xlsx file
    extract filename in case of csv file
    :return: list of table columns or sheets, first column/sheet
    """
    file_ext = os.path.splitext(filenames[0])[1]
    options = []
    if file_ext == '.xlsx':
        # get list of sheets
        print(f'extracting all sheets from xlsx')
        sheets = pd.ExcelFile(filenames[0])
        options = sheets.sheet_names
    elif file_ext.lower() == '.pdf':
        # get list of columns
        print(f'extracting all columns from pdf')
        options = parser.get_shimadzu_columns(filenames[0])
        # TODO
    elif file_ext.lower() == '.csv':
        options = ['csv']
    else:
        pass
    first_option = options[0]
    options = [{"label": f"{v}", "value": v} for v in options]
    return options, first_option


def parse_contents(filenames, optional_extract):
    """


    :param filenames:
    :param optional_extract:
    :return: parsed: pd.Dataframe
    """
    print(f'extracting column: {optional_extract}')
    file_ext = os.path.splitext(filenames[0])[1]
    print(f'extracting: {file_ext}')
    parsed = []
    if file_ext == '.xlsx':
        parsed = pd.read_excel(filenames[0], sheet_name=optional_extract)
        parsed['file'] = filenames[0]
    elif file_ext == '.csv':
        parsed = pd.read_csv(filenames[0])
        parsed['file'] = filenames[0]
    elif file_ext == '.pdf':
        try:
            parsed = parser.extract_shimadzu(filenames, optional_extract)
            # cut file path
            parsed['file'] = parsed['file'].str.split('/').str[1]
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])

    return parsed


# - - - - - - - - - - CALLBACKS - - - - - - - - - -


@app.callback(
    [  # fill data_table with data and render it
        Output('div-table', 'children'),
        Output('row-table', 'style'),
        Output('footer-div', 'style'),
        Output('upload-data', 'style'),
        Output('input-div', 'style'),
        Output('dropdown-extract', 'value'),
        Output('dropdown-extract', 'options'),
        Output('div-storing-filenames', 'children')
    ],
    [   # triggers callback when
        Input('upload-data', 'contents'),                       # user select files
        Input('btn-load-sample', 'n_clicks'),                   # button is pressed
        Input('btn-iris-sample', 'n_clicks'),                   # button is pressed
        Input('dropdown-extract', 'value')                      # another column for extraction is selected
    ],
    [   # does not trigger callback
        State('upload-data', 'filename'),                       # filenames from upload element
        State('div-storing-filenames', 'children')              # aux. state: filenames shared betweem callbacks
                                                                # needed for additional column extraction
    ])
def files2table(contents, sample_clicks, iris_clicks, extract_column, filenames, stored_filenames):  # , date):
    """

    :param contents: content of the extracted files
    :param sample_clicks:
    :param iris_clicks:
    :param extract_column: column to be actracted
    :param filenames:
    :param stored_filenames:
    :return: dash_table.DataTable
    """
    hide = {'display': 'none'}
    show = {'display': 'inline'}
    show_footer = {'display': 'flex'}

    print(f'stored_filenames: {stored_filenames}')

    # use new filenames from upload, or actual working filenames
    if filenames is not None:
        working_filenames = filenames
    else:
        working_filenames = stored_filenames

    # determine which input triggered this callback
    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if trigger == 'upload-data':
        # new files are saved into uploaded_directory
        for file, content in zip(working_filenames, contents):
            save_files(file, content)
    elif trigger == 'btn-load-sample':
        # use data from sample file
        working_filenames = ['samples3.xlsx']
    elif trigger == 'btn-iris-sample':
        # use data from sample file
        working_filenames = ['iris2.xlsx']

    print(f'FILES2TABLE CALLBACK')
    print(f'triggered by: {trigger}')
    print(f'filenames: {working_filenames}')

    file_path = [DIRECTORY + '/' + filename for filename in working_filenames]  # TODO move in from of save

    # get dict of optional columns for extraction + string with name of first column
    options, first_option = get_optional_extracts(file_path)
    # take first column from PDF / first sheet from xlsx if not selected from extract dropdown
    if trigger != 'dropdown-extract':
        extract_column = first_option

    # print(f'extract_column: {extract_column}')
    df = parse_contents(file_path, extract_column)
    # fetching the number of rows and columns
    #rows = df.shape[0]
    #cols = df.shape[1]

    #print(f'df size: {df.size}')
    #print(f'df memory usage: {df.info(memory_usage="deep")}')
    #print(f'rows: {rows}')
    #print(f'cols: {cols}')
    #print(f'cells: {rows*cols}')

    #print(f'df: {df}')
    #print(f'options: {options}')
    print(f'{df}')

    # returns whole datatable into parent div
    return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        page_size=20,
        # editable=True,
        filter_action='native',
        fixed_columns={  # fixed first column when scrolling horizontaly
            'headers': True,
            'data': 1
        },
        style_table={
            'minWidth': '100%',
        },
        style_cell={
            'overflow': 'hidden',
            'width': '100px', 'minWidth': '100px', 'maxWidth': '180px',
            'textOverflow': 'elipsis',
            'font-family': 'sans-serif',
            'fontSize': '15px',
            'backgroundColor': '#111111',
            'color': '#CECECE',
            'border': '2px solid #2A3441',
        },
        style_header={
            'backgroundColor': '#111111',
            'color': '#CECECE',
            'border': '2px solid #2A3441',
        }
    ), show, show_footer, hide, hide, extract_column, options, working_filenames


@app.callback(
    [  # show sub-pages
        Output('page-content', 'children'),  # show sub-page
        Output('upload-div', 'style')        # hide upload
    ],
    Input('url', 'pathname'),               # click in link in navbar triggers this callback
    prevent_initial_call=True
)
def goto_page(pathname):
    """

    :param pathname: path to sub page
    :return: web page acording to navbar link
    """

    # auxiliary variables updating element visibility
    hide = {'display': 'none'}
    disp_inline = {'display': 'inline'}

    if pathname == '/apps/pca':
        return pca.layout, hide
    elif pathname == '/apps/dendrogram':
        return dendrogram.layout, hide
    elif pathname == '/apps/tsne':
        return tsne.layout, hide
    elif pathname == '/apps/umap':
        return umap.layout, hide
    elif pathname == '/apps/cc':
        return control_chart.layout, hide
    elif pathname == '/':
        return 'http://extraktor.herokuapp.com/', disp_inline


if __name__ == '__main__':
    app.run_server(debug=False)
