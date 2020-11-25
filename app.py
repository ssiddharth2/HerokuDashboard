import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                  encoding='cp1252', na_values=['IAP', 'IAP,DK,NA,uncodeable', 'NOT SURE',
                                                'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk']
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss': 'weight',
                              'educ': 'education',
                              'coninc': 'income',
                              'prestg10': 'job_prestige',
                              'mapres10': 'mother_job_prestige',
                              'papres10': 'father_job_prestige',
                              'sei10': 'socioeconomic_index',
                              'fechld': 'relationship',
                              'fefam': 'male_breadwinner',
                              'fehire': 'hire_women',
                              'fejobaff': 'preference_hire_women',
                              'fepol': 'men_bettersuited',
                              'fepresch': 'child_suffer',
                              'meovrwrk': 'men_overwork'}, axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older': '89'})
gss_clean.age = gss_clean.age.astype('float')


text = """
    The Gender wage gap has been an issue that has agreed to be a problem by many although there are some who simply
    refuse to acknowlege that this an issue. This has been a problem that has been talked for a long, but has come to more
    prominence in the past 2-3 years. Research such as the one conducted by payscale, show that women do get paid less than
    their male counterparts, in particular the statistic from Payscale for 2020 shows that a women makes $0.81 of a dollar that a man makes.\n
    \n \n
    GSS is a survey that examines the attitudes of American through a series of questions and statements.This data contains attributes 
    like the sex and income of the respondent, it asks the respondent how would they evaluate their occupational prestige
    along with how much they agree to various statements like \"A preschool child is likely to suffer if his or her mother works\". 
    According to Wikipedia, it uses an \"area probability design\" for random sampling so that they can gather data  on American
    people from all kinds of backgrounds(urban, rural, suburban,etc).

    Sources consulted: https://www.payscale.com/data/gender-pay-gap , http://www.gss.norc.org/About-The-GSS , https://en.wikipedia.org/wiki/General_Social_Survey 
    
    

"""
gss_clean.groupby('sex').agg({'income': 'mean'})

gss_display = gss_clean.groupby('sex').agg(
    {'income': 'mean', 'job_prestige': 'mean', 'socioeconomic_index': 'mean', 'education': 'mean'})
gss_display = gss_display[['income', 'job_prestige',
                           'socioeconomic_index', 'education']]
gss_display = gss_display.rename({'sex': 'Sex',
                                  'income': 'Income',
                                  'job_prestige': 'Job Prestige',
                                  'socioeconomic_index': 'Socioeconomic Index',
                                  'education': 'Education'}, axis=1)
gss_display = round(gss_display, 2)
gss_display = gss_display.reset_index().rename({'sex': 'Sex'}, axis=1)
gss_display

table = ff.create_table(gss_display)

breadwinner = pd.crosstab(gss_clean.male_breadwinner,
                          gss_clean.sex).reset_index()
breadwinner = pd.melt(breadwinner, id_vars='male_breadwinner',
                      value_vars=['male', 'female'])
breadwinner = breadwinner.rename({'value': 'count'}, axis=1)

fig1 = px.bar(breadwinner, x='male_breadwinner', y='count', color='sex',
              labels={'male_breadwinner': 'Level of Agreement',
                      'count': 'Number of People'},
              hover_data=['male_breadwinner'],
              text='count',
              barmode='group')
fig1.update_layout(showlegend=True)
fig1.update(layout=dict(title=dict(x=0.5)))

gss_clean2 = gss_clean.dropna(subset=['sex'])
fig2 = px.scatter(gss_clean, x='job_prestige', y='income', color='sex',
                  trendline='ols',
                  height=600, width=600,
                  labels={'job_prestige': 'Job Prestige',
                          'income': 'Income'},
                  hover_data=['job_prestige', 'income', 'education', 'socioeconomic_index'])
fig2.update(layout=dict(title=dict(x=0.5)))

fig3 = px.box(gss_clean, x='income', y='sex', color='sex',
              labels={'income': 'Income', 'sex': ''})
fig3.update_layout(showlegend=False)
fig3.update(layout=dict(title=dict(x=0.5)))

fig4 = px.box(gss_clean, x='job_prestige', y='sex', color='sex',
              labels={'job_prestige': 'Job Presitge', 'sex': ''})
fig4.update_layout(showlegend=False)
fig4.update(layout=dict(title=dict(x=0.5)))

gss_sub = gss_clean[['income', 'sex', 'job_prestige']]
gss_sub['prestige_category'] = pd.cut(gss_sub['job_prestige'], bins=6, labels=[
                                      '1', '2', '3', '4', '5', '6'])
gss_sub = gss_sub.dropna()

fig5 = px.box(gss_sub, x='income', y='sex', color='sex',
              facet_col='prestige_category', facet_col_wrap=2,
              hover_data=['income', 'sex'],
              labels={'income': 'Income', 'sex': 'Sex'},
              color_discrete_map={'male': 'blue', 'female': 'red'},
              category_orders={"prestige_category": [
                  '1', '2', '3', '4', '5', '6']},
              width=1000, height=600)
fig5.update(layout=dict(title=dict(x=0.5)))
fig5.update_layout(showlegend=True)
fig5.for_each_annotation(lambda a: a.update(text=a.text.replace("vote=", "")))

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server

app.layout = html.Div(
    [
        html.H1("Exploring the GSS Survey Data"),

        dcc.Markdown(children=text),

        html.H5("Comparing Male and Females by Average Income, Average Occupational Prestige, Average Socioeconomic Index, and Average Years of Education"),

        dcc.Graph(figure=table),

        html.H5(
            "Assessing Level of Agreement between Males and Females on the following Poll Statement"),

        dcc.Markdown(children="Statement: It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family."),
        dcc.Graph(figure=fig1),

        html.H5("Plotting Income Against Occupational Prestige By Sex"),

        dcc.Graph(figure=fig2),

        html.Div([

            html.H5("Distribution of Income By Sex"),

            dcc.Graph(figure=fig3)

        ], style={'width': '48%', 'float': 'left'}),

        html.Div([

            html.H5("Distribution of Job Prestige By Sex"),

            dcc.Graph(figure=fig4)

        ], style={'width': '48%', 'float': 'right'}),

        html.H5(
            "Assessing Distribution of Income By Sex For Each of the Job Prestige Cateogories"),

        dcc.Graph(figure=fig5),


        html.H5("Extra Credit Portion Part 2: User Input Barplot"),

        html.Div([

            html.H3("x-axis feature"),

            dcc.Dropdown(id='x-axis',
                         options=[{'label': i, 'value': i} for i in ['satjob', 'relationship',
                                                                     'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork']],
                         value='satjob'),



            html.H3("group"),

            dcc.Dropdown(id='group',
                         options=[{'label': i, 'value': i}
                                  for i in ['sex', 'region', 'education']],
                         value='sex')

        ], style={'width': '25%', 'float': 'left','color':'pink'}),
        html.Div([

            dcc.Graph(id="graph")

        ], style={'width': '70%', 'float': 'right','color':'blue'})
    ]

)


@app.callback(Output(component_id="graph", component_property="figure"),
              [Input(component_id='x-axis', component_property="value"),
               Input(component_id='group', component_property="value")])
def make_bar(x, group):
    gss_trial = pd.crosstab(gss_clean[x], gss_clean[group]).reset_index()
    gss_trial = pd.melt(gss_trial, id_vars=x, value_vars=gss_trial.columns[1:])
    gss_trial = gss_trial.rename({'value': 'count'}, axis=1)
    return px.bar(gss_trial, x=x, y='count', color=group,
                  labels={'count': 'Number of People'},
                  hover_data=[x],
                  text='count',
                  barmode='group')


if __name__ == '__main__':
    app.run_server(debug=True)
