from config import config
from flask import Flask, render_template, url_for 
from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output



app = Flask(__name__)
dash_app = Dash(__name__, server=app, url_base_pathname='/', external_stylesheets=[dbc.themes.BOOTSTRAP, '/static/styles.css'])



engine = create_engine(f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}")
sql_query = "SELECT * FROM job_details_view where location = 'US'"
df = pd.read_sql(sql_query, engine)

# Convert salary_in_usd to float
df['salary_in_usd'] = df['salary_in_usd'].astype(float)


dash_app.layout = dbc.Container([
    html.Div([
        html.H1("DataWage Insights - USA (2020-2023)", style={'color': 'white', 'text-align': 'center'}),
    ], style={'background-color': '#8AC8E1', 'padding': '20px'}),  # Cream-blue color for the header
    
    
    html.Div([
       html.Div([
           html.H5("Company Size", style={'color': 'black','text-align': 'center'}),
           dcc.Dropdown(
               id='company-size-dropdown',
               options=[
                {'label': size, 'value': size} for size in df['company_size'].unique()
            ],
            multi=True,
            style={'width': '65%','margin': 'auto'},
            value=df['company_size'].unique(),
            placeholder='Select Company Sizes'
           )
       ], style={'width': '35%','float':'left' ,'display': 'inline-block'}),
       
       html.Div([
           html.H5("Employment Type", style={'color': 'black','text-align': 'center'}),
           dcc.Dropdown(
               id='employment-type-dropdown',
                           options=[
                {'label': employment_type, 'value': employment_type} for employment_type in df['employment_type'].unique()
            ],
            multi=True,
            style={'width': '85%','margin': 'auto'},
            value=df['employment_type'].unique(),
            placeholder='Select Employment Types'
           )
       ], style={'width': '35%', 'float': 'left', 'display': 'inline-block'}),
       
html.Div([
   html.H5("Remote Ratio", style={'color': 'black','text-align': 'center'}),
   dcc.Dropdown(
       id='remote-ratio-dropdown',
       options=[
           {'label': remote_ratio, 'value': remote_ratio} for remote_ratio in df['remote_ratio'].unique()
           ],
       multi=True,
       style={'width': '75%','margin': 'auto'},
       value=df['remote_ratio'].unique(),
       placeholder='Select Work Environment'
   )
], style={'width': '30%', 'float': 'left', 'display': 'inline-block'})
    ]),
    
    
html.Div([

    html.Div([
        html.H5("Work Year", style={'color': 'black','text-align': 'center'}), 
        dcc.Dropdown(
            id='work-year-dropdown',
            options =[{'label': year, 'value': year} for year in df['work_year'].unique()],
            multi=True,
            style={'width': '95%', 'margin': 'auto'},
            value=df['work_year'].unique(),
            placeholder='Select Work Years'
        )
    ], style={'width': '30%', 'float':'left','display': 'inline-block'}),

    html.Div([
    html.H5("Job Title", style={'color': 'black', 'text-align': 'center'}),
    dcc.Dropdown(
       id='job-title-dropdown',
       options=[
           {'label': 'All', 'value': 'All'},  # Add 'All' option
           * [{'label': title, 'value': title} for title in df['job_title'].unique()]
       ],
       multi=True,
       # Set the value as ['All'] initially
       value=['All'],
       style={'width': '65%', 'margin': 'auto'},
       placeholder='Select Job title'
    )
], style={'width': '60%', 'float': 'left', 'display': 'inline-block'}),



    

    html.Div([
        html.H5("Experience Level", style={'color': 'black','text-align': 'center'}),
        dcc.Dropdown(
           id='experience-level-dropdown',
           options =[{'label': level, 'value': level} for level in df['experience_level'].unique()],
           multi=True,
           style={'width': '85%', 'margin': 'auto'},
           value=df['experience_level'].unique(),
           placeholder='Select Experience Levels'
        )
    ], style={'width': '30%', 'float': 'right', 'display': 'inline-block'})
    
]),


        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H5("Total Jobs", style={'color': 'black', 'font-weight': 'bold', 'text-align': 'center'})),
                            dbc.CardBody(
                                html.Div(id="kpi-total-jobs", className="kpi-box"),
                                style={'border': '2px solid #ddd', 'padding': '15px'}
                            ),
                        ]
                    ),
                    style={'width': '50%', 'float': 'left', 'display': 'inline-block', 'padding': '10px'}
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H5("Median Salary", style={'color': 'black', 'font-weight': 'bold','text-align': 'center'})),
                            dbc.CardBody(
                                html.Div(id="kpi-median-salary", className="kpi-box"),
                                style={'border': '2px solid #ddd', 'padding': '15px'}
                            ),
                        ]
                    ),
                    style={'width': '50%', 'float': 'right', 'display': 'inline-block', 'padding': '10px'}
                ),
            ]
        ),
        
        dbc.Row([
        dbc.Col([
            dcc.Graph(id='data-science-jobs-by-year'),
        ], width=6),

        dbc.Col([
            dcc.Graph(id='job-title-distribution'),
        ], width=6)
    ]),
        
    # In the next row, we will add three pie charts - Proportion number for remote ratio, experience level, and employment type
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='remote-ratio-proportion'),
        ], width=4),

        dbc.Col([
            dcc.Graph(id='experience-level-proportion'),
        ], width=4),

        dbc.Col([
            dcc.Graph(id='employment-type-proportion'),
        ], width=4)
    ])
    
])

# Employment type proportion
@dash_app.callback(
    Output('employment-type-proportion', 'figure'), 
    [Input('company-size-dropdown', 'value'), 
     Input('experience-level-dropdown', 'value'),  
     Input('remote-ratio-dropdown', 'value'),
     Input('work-year-dropdown', 'value'),
    Input('job-title-dropdown', 'value')]
)

def update_employment_type_pie(company_size,experience_level,remote_ratio,work_year,job_title):
    # Filter data
    if 'All' in job_title:
        job_title = df['job_title'].unique()
    else:
        job_title = [job_title] if isinstance(job_title, str) else job_title
    company_size = [company_size] if isinstance(company_size, str) else company_size 
    experience_level = [experience_level] if isinstance(experience_level, str) else experience_level
    work_year = [work_year] if isinstance(work_year, str) else work_year
    remote_ratio = [remote_ratio] if isinstance(remote_ratio, str) else remote_ratio


    sql_query = f'''
    SELECT employment_type, COUNT(*) as job_count 
    FROM job_details_view 
    WHERE location='US' AND
    company_size IN {tuple(company_size)} AND
    experience_level IN {tuple(experience_level)} AND
    remote_ratio IN {tuple(remote_ratio)} AND
    job_title IN {tuple(job_title)} AND
    work_year IN {tuple(work_year)}
    GROUP BY employment_type
    '''
    employment_type_counts = pd.read_sql(sql_query, engine)
 

    # Create pie chart 
    fig = px.pie(employment_type_counts, 
             values='job_count', 
             names='employment_type',
             color_discrete_sequence=['#a6bddb', '#74a9cf', '#3690c0', '#0570b0'],  
             title='Jobs by Employment Type')

# Pull the slice corresponding to 'FT' to make it stand out
    fig.update_traces(hole=0.4, 
                  textposition='inside', 
                  textinfo='percent+label',
                  pull=[0.1 if employment_type == 'FT' else 0 for employment_type in employment_type_counts['employment_type']])

    fig.update_layout({
    'height': 450,
    'width': 450,
    'title': {'text': 'Jobs by Employment Type', 'x': 0.5},  # Center the title
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'font_color': 'black',
    'margin': dict(t=50, b=50, l=50, r=50),  # Adjust the margin to center the pie chart
})

    return fig


# Experience level proportion
@dash_app.callback(
    Output('experience-level-proportion', 'figure'), 
    [Input('company-size-dropdown', 'value'), 
     Input('employment-type-dropdown', 'value'),  
     Input('remote-ratio-dropdown', 'value'),
     Input('work-year-dropdown', 'value'),
    Input('job-title-dropdown', 'value')]
)

def update_experience_level_pie(company_size,employment_type,remote_ratio,work_year,job_title):
    # Filter data
    if 'All' in job_title:
        job_title = df['job_title'].unique()
    else:
        job_title = [job_title] if isinstance(job_title, str) else job_title
    company_size = [company_size] if isinstance(company_size, str) else company_size 
    employment_type = [employment_type] if isinstance(employment_type, str) else employment_type
    work_year = [work_year] if isinstance(work_year, str) else work_year
    remote_ratio = [remote_ratio] if isinstance(remote_ratio, str) else remote_ratio


    sql_query = f'''
    SELECT experience_level, COUNT(*) as job_count 
    FROM job_details_view 
    WHERE location='US' AND
    company_size IN {tuple(company_size)} AND
    employment_type IN {tuple(employment_type)} AND
    remote_ratio IN {tuple(remote_ratio)} AND
    job_title IN {tuple(job_title)} AND
    work_year IN {tuple(work_year)}
    GROUP BY experience_level
    '''
    experience_counts = pd.read_sql(sql_query, engine)

    # Create pie chart 
    fig = px.pie(experience_counts, 
                 values='job_count', 
                 names='experience_level',
                 color_discrete_sequence=['#a6bddb', '#74a9cf', '#3690c0', '#0570b0'],  
                 title='Jobs by Experience Level')

    fig.update_traces(hole=0.4, 
                  textposition='inside', 
                  textinfo='percent+label')
    
    fig.update_layout({
    'height': 450,
    'width': 450,
    'title': {'text': 'Jobs by Experience Level', 'x': 0.5},  # Center the title
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'font_color': 'black',
    'margin': dict(t=50, b=50, l=50, r=50),  # Adjust the margin to center the pie chart
})

    return fig


# Remote ratio proportion
@dash_app.callback(
    Output('remote-ratio-proportion', 'figure'), 
    [Input('company-size-dropdown', 'value'),
     Input('job-title-dropdown', 'value'), 
     Input('employment-type-dropdown', 'value'),  
     Input('experience-level-dropdown', 'value'),
     Input('work-year-dropdown', 'value')]
)

def update_remote_ratio_pie(company_size, job_title,employment_type,experience_level,work_year):
    # Filter data
    if 'All' in job_title:
        job_title = df['job_title'].unique()
    else:
        job_title = [job_title] if isinstance(job_title, str) else job_title
    # Fetch data based on selected filters
    company_size = [company_size] if isinstance(company_size, str) else company_size 
    employment_type = [employment_type] if isinstance(employment_type, str) else employment_type
    experience_level = [experience_level] if isinstance(experience_level, str) else experience_level
    work_year = [work_year] if isinstance(work_year, str) else work_year


    sql_query = f'''
    SELECT remote_ratio, COUNT(*) as job_count 
    FROM job_details_view 
    WHERE location='US' AND
    company_size IN {tuple(company_size)} AND
    employment_type IN {tuple(employment_type)} AND
    experience_level IN {tuple(experience_level)} AND
    job_title IN {tuple(job_title)} AND
    work_year IN {tuple(work_year)}
    GROUP BY remote_ratio
    '''
    remote_ratio_counts = pd.read_sql(sql_query, engine)
    # remote_ratio_counts = filtered_df.groupby('remote_ratio')['job_id'].count().reset_index(name='count')

    # Create pie chart 
    fig = px.pie(remote_ratio_counts, 
                 values='job_count', 
                 names='remote_ratio',
                 color_discrete_sequence=['#a6bddb', '#74a9cf', '#3690c0'],  
                 title='Jobs by Remote Ratio')

    fig.update_traces(hole=0.4, 
                  textposition='inside', 
                  textinfo='percent+label')
    
    fig.update_layout({
    'height': 450,
    'width': 450,
    'title': {'text': 'Jobs by Remote Ratio', 'x': 0.5},  # Center the title
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'font_color': 'black',
    'margin': dict(t=50, b=50, l=50, r=50),  # Adjust the margin to center the pie chart
})

    return fig


# Callback for median salary
@dash_app.callback(
    Output("kpi-median-salary", "children"),
    [Input('company-size-dropdown', 'value'), 
     Input('remote-ratio-dropdown', 'value'),
     Input('work-year-dropdown', 'value'),
     Input('job-title-dropdown', 'value'),  
     Input('employment-type-dropdown', 'value'),  
     Input('experience-level-dropdown', 'value')]
)
def update_median_salary(company_size, remote_ratio, work_year, job_title, employment_type,experience_level):
    # Wrap all values in lists
    company_size = [company_size] if isinstance(company_size, str) else company_size 
    remote_ratio = [remote_ratio] if isinstance(remote_ratio, str) else remote_ratio
    work_year = [work_year] if isinstance(work_year, str) else work_year
        # Filter data
    if 'All' in job_title:
        job_title = df['job_title'].unique()
    else:
        job_title = [job_title] if isinstance(job_title, str) else job_title
    experience_level = [experience_level] if isinstance(experience_level, str) else experience_level
    employment_type = [employment_type] if isinstance(employment_type, str) else employment_type


    filtered_df = df[(df['company_size'].isin(company_size)) &
                     (df['remote_ratio'].isin(remote_ratio)) &
                     (df['work_year'].isin(work_year)) &
                     (df['job_title'].isin(job_title)) &
                     (df['employment_type'].isin(employment_type)) &
                     (df['experience_level'].isin(experience_level))]
    
    print(f"Filtered DataFrame: {filtered_df}")

    if not filtered_df.empty:
        median_salary = round(filtered_df['salary_in_usd'].median(), 2) 
        return f"{median_salary}"
    else:
        return "No data available"


# Callback for total jobs
@dash_app.callback(
    Output("kpi-total-jobs", "children"),
    [Input('company-size-dropdown', 'value'), 
     Input('remote-ratio-dropdown', 'value'),
     Input('work-year-dropdown', 'value'),
     Input('job-title-dropdown', 'value'),  
     Input('employment-type-dropdown', 'value'),
     Input('experience-level-dropdown', 'value')]
)
def update_total_jobs(company_size, remote_ratio, work_year, job_title, employment_type,experience_level):
    
        # Wrap all values in lists
    company_size = [company_size] if isinstance(company_size, str) else company_size 
    remote_ratio = [remote_ratio] if isinstance(remote_ratio, str) else remote_ratio
    work_year = [work_year] if isinstance(work_year, str) else work_year
        # Filter data
    if 'All' in job_title:
        job_title = df['job_title'].unique()
    else:
        job_title = [job_title] if isinstance(job_title, str) else job_title
    experience_level = [experience_level] if isinstance(experience_level, str) else experience_level
    employment_type = [employment_type] if isinstance(employment_type, str) else employment_type
    filtered_df = df[(df['company_size'].isin(company_size)) &
                     (df['remote_ratio'].isin(remote_ratio)) &
                     (df['work_year'].isin(work_year)) &
                     (df['job_title'].isin(job_title)) &
                     (df['employment_type'].isin(employment_type)) &
                     (df['experience_level'].isin(experience_level))]
    
    total_jobs = len(filtered_df)
    return f"{total_jobs}"



# Callback for first graph
@dash_app.callback(
     Output('data-science-jobs-by-year', 'figure'),
    [Input('company-size-dropdown', 'value'), 
     Input('remote-ratio-dropdown', 'value'), 
     Input('employment-type-dropdown', 'value'),
     Input('experience-level-dropdown', 'value'),
     Input('work-year-dropdown', 'value'),  
     Input('job-title-dropdown', 'value')]
)
def update_data_science_jobs_by_year(company_size, remote_ratio, employment_type, experience_level,work_year, job_title):
    # Fetch data based on selected filters
    company_size = [company_size] if isinstance(company_size, str) else company_size 
    remote_ratio = [remote_ratio] if isinstance(remote_ratio, str) else remote_ratio
    experience_level = [experience_level] if isinstance(experience_level, str) else experience_level
    employment_type = [employment_type] if isinstance(employment_type, str) else employment_type
    work_year = [work_year] if isinstance(work_year, str) else work_year
        # Filter data
    if 'All' in job_title:
        job_title = df['job_title'].unique()
    else:
        job_title = [job_title] if isinstance(job_title, str) else job_title

    sql_query = f'''
    SELECT work_year, COUNT(*) as job_count 
    FROM job_details_view 
    WHERE location='US' AND
    company_size IN {tuple(company_size)} AND
    remote_ratio IN {tuple(remote_ratio)} AND
    experience_level IN {tuple(experience_level)} AND
    employment_type IN {tuple(employment_type)} AND
    job_title IN {tuple(job_title)} AND
    work_year IN {tuple(work_year)} 
    GROUP BY work_year 
    ORDER BY work_year;
    '''
    data = pd.read_sql(sql_query, engine)
    


  # Create a line chart with a trend line
    fig = px.line(data, x='work_year', y='job_count', title='Data Science Jobs by Year', labels={'work_year':'Year','job_count': 'Number of Jobs'}, markers=True, line_shape='linear')

    # Set tick values to show only whole numbers on the x-axis
    fig.update_xaxes(tickmode='array', tickvals=data['work_year'].unique(), ticktext=data['work_year'].unique())
    
    return fig


# Callback to update (Job title distribution)
@dash_app.callback(
    Output('job-title-distribution', 'figure'),
    [Input('company-size-dropdown', 'value'), 
     Input('remote-ratio-dropdown', 'value'), 
     Input('employment-type-dropdown', 'value'),
     Input('experience-level-dropdown', 'value'),
     Input('work-year-dropdown', 'value')]
)
def update_job_title_distribution(company_size, remote_ratio,employment_type, experience_level,work_year):
    # Fetch data based on selected filters
    company_size = [company_size] if isinstance(company_size, str) else company_size 
    remote_ratio = [remote_ratio] if isinstance(remote_ratio, str) else remote_ratio
    employment_type = [employment_type] if isinstance(employment_type, str) else employment_type
    experience_level = [experience_level] if isinstance(experience_level, str) else experience_level
    work_year = [work_year] if isinstance(work_year, str) else work_year


    sql_query = f'''
    SELECT job_title, COUNT(*) as job_count 
    FROM job_details_view 
    WHERE location='US' AND
    company_size IN {tuple(company_size)} AND
    remote_ratio IN {tuple(remote_ratio)} AND
    experience_level IN {tuple(experience_level)} AND
    employment_type IN {tuple(employment_type)} AND
    work_year IN {tuple(work_year)}
    GROUP BY job_title
    ORDER BY job_count DESC
    LIMIT 10;
    '''
    data = pd.read_sql(sql_query, engine)
    
    fig = px.bar(data, x='job_count', y='job_title', title='Roles Distribution (Top 10)', labels={'job_count': 'Number of Jobs', 'job_title': 'Roles'}, orientation='h')

    return fig
    


@app.route('/')
def app2():
    return render_template('dash_index.html')

if __name__ == '__main__':
    app.run(port=5001)
    app.run(debug=True)
