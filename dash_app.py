from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import dash_dataframe_table
from helper_functions import ebookData

ebooks = ebookData()

app = Dash(__name__,
           external_stylesheets=[dbc.themes.YETI],
           url_base_pathname='/ebook_search/')

app.layout = dbc.Container([
    html.H2("Standard eBooks AZW3 search"),
    html.Div([
        "Input: ",
        dbc.Input(id='my-input',
                  placeholder='Search title or author...',
                  value='',
                  type='text',
                  debounce=500)
    ]),
    html.Br(),
    dcc.Markdown(
        "Title links should directly download Kindle compatible .azw3 file, ideal for loading from the Kindle broswer directly."
    ),
    html.Div(id='my-output'),
])


@app.callback(Output(component_id='my-output', component_property='children'),
              Input(component_id='my-input', component_property='value'))
def update_output_div(input_value):
    return dbc.Table.from_enhanced_dataframe(ebooks.search(input_value))


if __name__ == '__main__':
    app.run_server(debug=True)
