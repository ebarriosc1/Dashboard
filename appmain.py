import dash
from dash import Dash, dcc, html, dash_table, callback_context, clientside_callback,ClientsideFunction
from dash.dependencies import Input, Output,MATCH, State
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash import dcc
import plotly.express as px

# from arusdUtils import directory
# from arusdUtils.creds import retrieve_credentials
# from arusdUtils import check_file
# from arusdUtils import directory

# from data.retrieveQSSdata import retrieveData
from data.data import tradeData

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.stats import norm
import ssl
import os
try:
   import truststore
   truststore.inject_into_ssl()
except ModuleNotFoundError:
   print("Truststore not installed - please add it if possible. Truststore should help with self-signed certificates issues.\
               If it's working without that's fine, but I recommend using it if you can.")
   pass




#Raeding IN Data
filepath = os.path.join("data", "employee_data_50.csv")
df_temp = pd.read_csv(filepath)
df = pd.read_csv(filepath, dtype={col: str for col in df_temp.columns})

df_expiredUsers = pd.read_csv("data/ExpiredUser.csv")
df_expiredDays = df_expiredUsers['DaysBeforeExpiration'].apply( lambda x: x * (-1))
df_expiredDays = df_expiredDays[df_expiredDays <= 1000]
data_x = df_expiredDays.to_list()
negative_range = -1 * max(data_x)
data_x = np.linspace(-400, 600, 1000)
std_dev  = df_expiredDays.std()
mean = df_expiredDays.mean()
# func_x = lambda x: -1*(1/(std_dev*np.sqrt(2*np.pi)))**(-((x-mean)**2/(2*std_dev**2))) #Normal DIstribution Function


pdf = norm.pdf(data_x, mean, std_dev)
fig = px.line(x=data_x,y=pdf)
for key in df.keys():
   if 'date' in key:
       df[key]= pd.to_datetime(df[key])
   else:
       pass


#ADD active/inactive column to classify the employees
for i, row in df.iterrows():
   if pd.isna(row['term_date']):
       df.at[i,'active'] = True


   elif (row['rehire_date'] > row['term_date']) and not pd.isna(row['rehire_date']) and not pd.isna(row['term_date']):
       df.at[i, 'active'] = True


   else:
       df.at[i, 'active'] = False



error_keys = ['first_name','last_name','extref_no','inet_email_home']

potential_errors = df[df[error_keys].apply(lambda x: x.str.strip() == '').any(axis=1)]

potential_errors=potential_errors[potential_errors['active']==True]
potential_errors = potential_errors[error_keys] 
num_potential_errors = len(potential_errors)


#Return DataFrame where 'active' = True
df = df[df['active']==True]
columnsInterested = ['first_name', 'last_name', 'extref_no','hire_date', 'term_date', 'rehire_date', 'orig_hire_date']


hired_last_7_days = df[df['hire_date'] >= (pd.Timestamp.now() - pd.Timedelta(days=7))]
hired_last_7_days = hired_last_7_days[columnsInterested]
terminated_next_7_days = df[(df['term_date'] <= (pd.Timestamp.now() + pd.Timedelta(days=7))) & (df['term_date'] >= pd.Timestamp.now())]
terminated_next_7_days = terminated_next_7_days[columnsInterested]


zip_code_counts = df['zip_code'].value_counts()
zip_codes_to_include = zip_code_counts[zip_code_counts>=25].index
df_filtered = df[df['zip_code'].isin(zip_codes_to_include)]




zip_code_counts = zip_code_counts[zip_code_counts>30]
zip_code_data = zip_code_counts.to_list()
zip_codes = zip_code_counts.index.to_list()


zip_code_counts_dict = zip_code_counts.reset_index().to_dict()
zip_code_counts_dict = [{x:y} for x,y in zip(list(zip_code_counts_dict['zip_code'].values()) , list(zip_code_counts_dict['count'].values()))]
zip_code_columns = zip_code_counts.index.to_list()

Gender_counts = df['sex'].value_counts()
Gender_counts_data= Gender_counts.to_list()

df = df[columnsInterested]
# fig = px.pie(zip_code_counts,values='count',names=zip_code_counts.index,color=zip_code_counts.index)

with open('file.json', 'w') as f:   
   df_filtered.to_json('file.json',orient='records',lines=False)   


external_stylesheets = [
   {"href" : "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined",
   "rel":"stylesheet"},
]

external_scripts = [
   {'src':'https://cdn.jsdelivr.net/npm/apexcharts'}
]

app = dash.Dash(__name__ ,
               external_stylesheets=external_stylesheets,
               assets_folder="assets/",
               external_scripts=external_scripts,
               )


page = [ inst_page for inst_page in dash.page_registry.values()]

def modal_content(dataframe: pd.DataFrame, idName: str):
    modal_content = dbc.Modal([
    dbc.ModalHeader("Table Popup"),
    dbc.ModalBody([
        # Ag-Grid table container
        html.Div([
            dag.AgGrid(
                id=idName+'-modal-user-table',style={'height':'400px','width':'100%'},rowData=dataframe.to_dict('records'), columnDefs=[{"field": i} for i in dataframe.columns],
                defaultColDef={'filter':True},columnSize="sizeToFit", className="ag-theme-quartz-dark",
                dashGridOptions={"animateRows":False})
        ])
    ]),
    dbc.ModalFooter(
        dbc.Button("Close", id=idName+"-close-modal", className="ml-auto")
    ),
], id=idName+"-modal")
    return modal_content

modal_ids =['error','active','hired', 'term','expiringUser']

app.layout = html.Div([ 
   html.Div([
   dcc.Store(id='chartsSampleData',data=zip_code_data),
   dcc.Store(id='zipCodeColumns',data=zip_code_columns),
   dcc.Store(id='doughnutChart',data=Gender_counts_data ),
   dcc.Store(id='doughnutChartColumns',data=['Female','Male'] ),
   dcc.Store(id='norm_x_data',data=data_x.tolist()),
   dcc.Store(id='PDF', data=pdf.tolist()),
   html.Script('''
       (function(a, s, y, n, c, h, i, d, e) {
         s.className += ' ' + y;
         h.start = 1 * new Date;
         h.end = i = function() {
           s.className = s.className.replace(RegExp(' ?' + y), '')
         };
         (a[n] = a[n] || []).hide = h;
         setTimeout(function() {
           i();
           h.end = null
         }, c);
         h.timeout = c;
       })(window, document.documentElement, 'async-hide', 'dataLayer', 4000, {
         'GTM-K9BGS8K': true
       });
   '''),
   html.Script('''
       (function(i, s, o, g, r, a, m) {
         i['GoogleAnalyticsObject'] = r;
         i[r] = i[r] || function() {
           (i[r].q = i[r].q || []).push(arguments)
         }, i[r].l = 1 * new Date();
         a = s.createElement(o),
           m = s.getElementsByTagName(o)[0];
         a.async = 1;
         a.src = g;
         m.parentNode.insertBefore(a, m)
       })(window, document, 'script', 'https://www.google-analytics.com/analytics.js', 'ga');
       ga('create', 'UA-46172202-22', 'auto', {
         allowLinker: true
       });
       ga('set', 'anonymizeIp', true);
       ga('require', 'GTM-K9BGS8K');
       ga('require', 'displayfeatures');
       ga('require', 'linker');
       ga('linker:autoLink', ["2checkout.com", "avangate.com"]);
   '''),
   html.Script('''
       (function(w, d, s, l, i) {
         w[l] = w[l] || [];
         w[l].push({
           'gtm.start': new Date().getTime(),
           event: 'gtm.js'
         });
         var f = d.getElementsByTagName(s)[0],
           j = d.createElement(s),
           dl = l != 'dataLayer' ? '&l=' + l : '';
         j.async = true;
         j.src =
           'https://www.googletagmanager.com/gtm.js?id=' + i + dl;
         f.parentNode.insertBefore(j, f);
       })(window, document, 'script', 'dataLayer', 'GTM-NKDMSK6');
   '''),
   html.Script(defer=True, **{'data-site': 'demos.creative-tim.com'}, src='../../js/nepcha-analytics.js'),
   html.Noscript(html.Iframe(height='0', width='0', src='https://www.googletagmanager.com/ns.html?id=GTM-NKDMSK6', style={'display': 'none', 'visibility': 'hidden'})),


   html.Div(className="sidenav navbar navbar-vertical navbar-expand-xs border-0 border-radius-xl my-3 fixed-start ms-3 bg-gradient-dark", id="sidenav-main",
                   children=[
                       html.A(className="fas fa-times p-3 cursor-pointer text-white opacity-5 position-absolute end-0 top-0 d-none d-xl-none", id="iconSidenav"),
                       html.A([
                           html.Img(src="../assets/img/ARUSD_Logo.png", className="navbar-brand-img h-100"),
                           html.Span("Qss Dashboard", className="ms-1 font-weight-bold text-white")
                       ], className="navbar-brand m-0", href="dashboard-1.html", target="_blank"),
                       html.Hr(className="horizontal light mt-0 mb-2"),
                       html.Div([
                           html.Ul([
                               html.Li([
                                   html.A([
                                       html.Div([
                                           html.I("dashboard", className="material-symbols-outlined opacity-10")
                                       ], className="text-white text-center me-2 d-flex align-items-center justify-content-center"),
                                       html.Span("Dashboard", className="nav-link-text ms-1")
                                   ], className="nav-link text-white active bg-gradient-primary", href="dashboard.html")
                               ], className="nav-item"),
                               # More list items here...
                           ], className="navbar-nav"),
                       ], className="collapse navbar-collapse w-auto", id="sidenav-collapse-main"),
                       html.Div([
                           html.H6("Provided by ARUSD IT Depart.", className="ps-4 ms-2 text-uppercase text-xs text-white font-weight-bolder opacity-8", style={"margin-top": "1rem"}),
                       ], className="nav-item mt-3"),
                       # More content here...
                       html.Div([], className="mx-3")]), #NAVBAR MAIN
   html.Div(className='main-content position-relative max-height-vh-100 h-100 border-radius-lg ps ps--active-y',
            children=[
               html.Nav(className="navbar navbar-main navbar-expand-lg px-0 mx-4 shadow-none border-radius-xl", id="navbarBlur", **{'data-scroll': "true"},
                       children=[
                           html.Div([
                               html.Ol([
                                   html.Li([
                                       html.A("Pages", className="opacity-5 text-dark")
                                   ], className="breadcrumb-item text-sm"),
                                   html.Li("Dashboard", className="breadcrumb-item text-sm text-dark active")
                               ], className="breadcrumb bg-transparent mb-0 pb-0 pt-1 px-0 me-sm-6 me-5"),
                               html.H6("Dashboard", className="font-weight-bolder mb-0")
                           ], className="container-fluid py-1 px-3"),
               ]),#NAVBAR
               html.Div(className="container-fluid py-4" ,style={'height':'100vh','overflow-y':'auto'},
                       children=[
                           html.Div(className='row',
                                   children=[
                                       html.Div(className="col-xl-3 col-sm-6 mb-xl-0 mb-4",
                                               children=[
                                                    html.A(className='card', href='#', id='open-error-modal-button', children=[
                                                            html.Div(className="card-header p-3 pt-2", children=[
                                                                html.Div(className="icon icon-lg icon-shape bg-gradient-dark shadow-dark text-center border-radius-xl mt-n4 position-absolute", children=[
                                                                    html.I("weekend", className="material-symbols-outlined opacity-10")
                                                                ]),
                                                                html.Div(className='text-end pt-1', children=[
                                                                    html.P("Potential User Sync Error", className='text-sm mb-0 text-capitalize'),
                                                                    html.H4(str(num_potential_errors), className='mb-0')
                                                                ])
                                                            ])
                                                        ]),
                                                        modal_content(potential_errors,modal_ids[0])
                                                       ]),
                                       html.Div(className="col-xl-3 col-sm-6 mb-xl-0 mb-4",
                                               children=[
                                                    html.A(className='card',href='#',id='open-active-modal-button',
                                                               children=[
                                                                   html.Div( className="card-header p-3 pt-2",
                                                                       children=[
                                                                           html.Div(className="icon icon-lg icon-shape bg-gradient-primary shadow-dark text-center border-radius-xl mt-n4 position-absolute",
                                                                                   children=[
                                                                                           html.I("groups", className="material-symbols-outlined opacity-10")
                                                                                       ]),
                                                                           html.Div(className='text-end pt-1',
                                                                                   children=[
                                                                                       html.P("Total Active Users",className='text-sm mb-0 text-capitalize'),
                                                                                       html.H4(str(len(df)), className='mb-0')
                                                                                       ])
                                                                           ])
                                                            ]),
                                                    modal_content(df, modal_ids[1])
                                                       ]),
                                                      
                                       html.Div(className="col-xl-3 col-sm-6 mb-xl-0 mb-4",
                                               children=[
                                                   html.A(id='open-hired-modal-button',className='card',href="#",
                                                               children=[
                                                                   html.Div( className="card-header p-3 pt-2",
                                                                       children=[
                                                                           html.Div(className="icon icon-lg icon-shape bg-gradient-success shadow-dark text-center border-radius-xl mt-n4 position-absolute",
                                                                                   children=[
                                                                                           html.I("weekend", className="material-symbols-outlined opacity-10")
                                                                                       ]),
                                                                           html.Div(className='text-end pt-1',
                                                                                   children=[
                                                                                       html.P("User Hired Last 7 Days",className='text-sm mb-0 text-capitalize'),
                                                                                       html.H4(str(len(hired_last_7_days)), className='mb-0')
                                                                                       ])
                                                                           ])
                                                               ]),
                                                modal_content(hired_last_7_days,modal_ids[2])
                                                       ]),
                                                      
                                       html.Div(className="col-xl-3 col-sm-6 mb-xl-0 mb-4",
                                               children=[
                                                   html.A(id='open-term-modal-button',className='card',href='#',
                                                               children=[
                                                                   html.Div( className="card-header p-3 pt-2",
                                                                       children=[
                                                                           html.Div(className="icon icon-lg icon-shape bg-gradient-info shadow-dark text-center border-radius-xl mt-n4 position-absolute",
                                                                                   children=[
                                                                                           html.I("weekend", className="material-symbols-outlined opacity-10")
                                                                                       ]),
                                                                           html.Div(className='text-end pt-1',
                                                                                   children=[
                                                                                       html.P("Terminated Next 7 Days",className='text-sm mb-0 text-capitalize'),
                                                                                       html.H4(str(len(terminated_next_7_days)), className='mb-0')
                                                                                       ])
                                                                           ])
                                                               ]),
                                                    modal_content(terminated_next_7_days,modal_ids[3])
                                                       ]),
                                                      
                                                      
                                       ]),
                           html.Div(className='row mt-4', children=[
                               html.Div(className="col-lg-4 col-md-6 mt-4 mb-4", children=[
                                   html.Div( className='card z-index-2', children=[
                                       html.Div(className='card-header p-0 position-relative mt-n4 mx-3 z-index-2 bg-transparent',children=[
                                           html.Div(className='bg-gradient-primary shadow-primary border-radius-lg py-3 pe-1',children=[
                                               html.Div(className='chart', children=[
                                                   html.Div(id='apex-bars',style={'display':'block','box-sizing':'border-box','height':170,'width':'100%'}),
                                                  # html.Canvas(id='chart-bars', className='chart-canvas', height=170, width=488,style={'display':'block','box-sizing':'border-box','height':170,'width':488.7})
                                               ])
                                           ] )
                                       ]),
                                       html.Div(className='card-body', children=[
                                           html.H6('Employee Distribution',className="mb-0"),
                                           # html.P("Last Campaign Performance", className='text-sm'),
                                           html.Hr(className="dark horizontal")
                                       ])
                                   ])
                               ]),
                               html.Div(className="col-lg-4 col-md-6 mt-4 mb-4", children=[
                                   html.Div( className='card z-index-2', children=[
                                       html.Div(className='card-header p-0 position-relative mt-n4 mx-3 z-index-2 bg-transparent',children=[
                                           html.Div(className='bg-gradient-dark shadow-primary border-radius-lg py-3 pe-1',children=[
                                               html.Div(className='chart', children=[
                                                   # html.Div(style={'display':'block','box-sizing':'border-box','height':170,'width':488.7},children=[dcc.Graph(figure=fig)])
                                                   html.Div(id='apex-bars2',style={'display':'block','box-sizing':'border-box','height':170,'width':'100%'}),
                                                  # html.Canvas(id='chart-bars', className='chart-canvas', height=170, width=488,style={'display':'block','box-sizing':'border-box','height':170,'width':488.7})
                                               ])
                                           ] )
                                       ]),
                                       html.Div(className='card-body', children=[
                                           html.H6('Gender Distribution',className="mb-0"),
                                           # html.P("Last Campaign Performance", className='text-sm'),
                                           html.Hr(className="dark horizontal")
                                       ])
                                   ])
                               ]),
                                html.Div(className="col-lg-4 mt-4 mb-3", children=[
                                   html.Div( className='card z-index-2', children=[
                                       html.Div(className='card-header p-0 position-relative mt-n4 mx-3 z-index-2 bg-transparent',children=[
                                           html.Div(className='bg-gradient-dark shadow-primary border-radius-lg py-3 pe-1',children=[
                                               html.Div(className='chart', children=[
                                                   # html.Div(style={'display':'block','box-sizing':'border-box','height':170,'width':488.7},children=[dcc.Graph(figure=fig)])
                                                   html.Div(id='apex-bars3',style={'display':'block','box-sizing':'border-box','height':170,'width':'100%'}),
                                                  # html.Canvas(id='chart-bars', className='chart-canvas', height=170, width=488,style={'display':'block','box-sizing':'border-box','height':170,'width':488.7})
                                               ])
                                           ] )
                                       ]),
                                       html.Div(className='card-body', children=[
                                           html.A([html.H6('Employees with Expired Passwords',className="mb-0")],id='open-expiringUser-modal-button',href='#'),
                                           # html.P("Last Campaign Performance", className='text-sm'),
                                           html.Hr(className="dark horizontal"),
                                           modal_content(df_expiredUsers,modal_ids[4])
                                       ])
                                   ])
                               ]),
                           ]),
                           
                          
                           html.Div(className='row mb-4', children=[
                               html.Div(className="col-lg-8 col-md-6 mb-md-0 mb-4", style={'width':'100%'},children=[
                                   html.Div(className='card',style={'height':500},children=[
                                       html.Div(className='card-header pb-0', children=[
                                           html.Div(className='row',children=[
                                               html.Div(className='col-lg-6 col-7', children=[
                                                   html.H6("Find Users in QSS")
                                               ]),
                                               ])
                                           ]),

                                       html.Div(className='card-body px-0 pb-2',style={'height':300}, children=[
                                           html.Div(className='table-responsive',style={'height':'100%'},children=[
                                               dag.AgGrid(
                                                   id='user-table',style={'height':'400px','width':'100%'},rowData=df.to_dict('records'), columnDefs=[{"field": i} for i in terminated_next_7_days.columns],
                                                   defaultColDef={'filter':True},columnSize="sizeToFit", className="ag-theme-quartz-dark",
                                                   dashGridOptions={"animateRows":False})
                                           ])
                                       ])
                                   ]),
                               ])
                           ]),


                           ]),#container_fluid_py-4


]),#This is for Main-content
dash.page_container],)
],)#Initialized DIV


clientside_callback(
   ClientsideFunction(
       namespace='apexCharts',
       function_name='apexBar'
   ),
   Output('apex-bars','children'),
   Input('chartsSampleData','data'),
   Input('zipCodeColumns','data'),
)
clientside_callback(
   ClientsideFunction(
       namespace='apexCharts',
       function_name='apexBar2'
   ),
   Output('apex-bars2','children'),
   Input('doughnutChart','data'),
   Input('doughnutChartColumns','data'),
)
clientside_callback(
   ClientsideFunction(
       namespace='apexCharts',
       function_name='apexBar3'
   ),
   Output('apex-bars3','children'),
   Input('norm_x_data','data'),
   Input('PDF','data'),
)

#Creating a @app.callback() function generator
def callback_generator(modal_id):
    @app.callback(
        Output(f"{modal_id}-modal", "is_open"),
        [Input(f"open-{modal_id}-modal-button", "n_clicks"), Input(f"{modal_id}-close-modal", "n_clicks")],
        [State(f"{modal_id}-modal", "is_open")],
        prevent_initial_call=True
        )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

callback_generator(modal_ids[0])
callback_generator(modal_ids[1])
callback_generator(modal_ids[2])
callback_generator(modal_ids[3])
callback_generator(modal_ids[4])

if __name__ == '__main__':
    app.run_server(debug=True)
#    app.run_server(host='0.0.0.0', port='8050')
application = app.server



