
# Author: libor@labavit.com
# Year: 2021
# Desc.: Main application file
import dash

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
