  # To Do:

  #  - deal with missing dT, dTL, transmit_trigger
  #  - event_plot(): make height depend on number of columns
  #  - cohort_event_plot(): deal with participant that have empty columns
  #  - Do something with ts_inspection_plotly2() 
  #  - add id_participant to plots
  #  - add data source to plot (log_file / influxdb)
  #  - parse question flow file with Cozie() for retrieval of ws_questions and order of responses.
  #  - Add PDF report
  #  - Clean up all docstrings
  #  - ts_inspection: Clean up variable names (column_name, modality, df, df_participant)
  #  - Fix warning: "The behavior of DatetimeProperties.to_pydatetime is deprecated"
  # Issues
  #  - Kaleido is not working properly with plotly.
  #    - Different Kaleido version are available and/or working on Windows and Linux.
  #    - Note that Colab is running on Linux.
  #    - In Colab, Kaleido 0.4.1 causes an error when calling fig.show(): TypeError: argument of type 'NoneType' is not iterable
  #    - In Colab, Kaleido 0.1.0 works with plotly
  #    - On Windows 11, Kaleido 0.1.0.post1 appears to be working. 0.1.0.post1 is not available in Colab
  #    - It is a known issue, e.g., https://stackoverflow.com/questions/69016568/unable-to-export-plotly-images-to-png-with-kaleido
  #    - Fix: Use conditional requirements.txt (https://stackoverflow.com/questions/29222269/is-there-a-way-to-have-a-conditional-requirements-txt-file-for-my-python-applica)


import pandas as pd
import numpy as np
import pytz
from pytz import timezone
import datetime
import math
from textwrap import wrap
import json
import requests

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FormatStrFormatter
import matplotlib.ticker as ticker
import seaborn as sns

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import shapely.geometry
import utm
import geopandas as gpd

pd.options.mode.chained_assignment = None # Mitigates SettingWithCopyWarning: 
                                          #A value is trying to be set on a copy of a slice from a DataFrame.
                                          #Try using .loc[row_indexer,col_indexer] = value instead
#print("Cozie Plot Module start")

class CoziePlot:  
  """
  Class to plot Cozie-Apple data
  """

  def __init__(self, df, participant_list=None, ws_questions=None, id_participant=None, valid_votes=False, timezone=None, ws_file=None, ws_url=None):   
    """
    Constructor initializes class attributes and prints test string
    
    Arguments
    ----------
      - df, Pandas dataframe, Dataframe with Cozie data
      - participant_list, list of str, List with Participant IDs
      - valid_votes, boolean, indicates whether to use only valid votes (default) or all votes
      - timezone (str): ? 
      - ws_file (str): Path to local watch survey json file 
      - ws_url (str): URL to watch survey json file
    Returns
    -------
      -
    """
    self.df = df.copy()
    self.watch_survey = None
    self.ws_questions={}
    self.valid_votes = valid_votes
    if participant_list == None:
      self.participant_list = df["id_participant"].unique()
      self.participant_list = np.sort(self.participant_list)
    else:
      self.participant_list = participant_list

    if id_participant == None:
        self.id_participant = self.participant_list[0]
    else:
        self.id_participant = id_participant
    
    if ws_questions != None:
      self.ws_questions = ws_questions
    elif ws_file != None:
      self.watch_survey = json.load(open(ws_file))
    elif ws_url != None:
      response = requests.get(ws_url)
      self.watch_survey = response.json()
    else:
      try:
        ws_url = df[df['api_watch_survey_url'].notna()]['api_watch_survey_url'].values[-1]
        response = requests.get(ws_url)
        self.watch_survey = response.json()
      except:
        print('Failed to fetch watch survey from df["api_watch_survey_url"]')
        # Collect questions from prefix dataframe columns into ws_questions
        for col in df.columns:
          if "q_" in col[:2]:
            self.ws_questions[col]=col

    # Collect questions from watch_survey into ws_questions
    if self.ws_questions == {} and self.watch_survey != None:
      for i, item in enumerate(self.watch_survey['survey']):
        self.ws_questions[item['question_id']] = item['question']

    # Add empty columns for question IDs that are not in the dataframe
    for question_id in self.ws_questions:
      if question_id not in self.df.columns:
        self.df[question_id] = None

    if timezone == None:
      self.timezone = str(df.index[0].tz)
    else:
      self.timezone = timezone
    
    return
  
  def test(self):  
    """
    Function that plots some string for debugging
    
    Arguments
    ----------
      - 
      
    Returns
    -------
      - 
    """
    print("CoziePlot Test")
    return
  

  def ts_inspection(self, column_name, id_participant=None):  
    """
    Function to plot time-series data in detail for one participant
    Arguments
    ----------
      - column_name, str, Name of column with time-series data that should be 
      plotted
      - id_participant, str, Participant ID of which the time-series data should 
      be plotted

    Returns
      - fig, plotly figure object, figure with subplots
    """


    if id_participant == None:
      id_participant = self.id_participant

    df_participant = self.df[self.df['id_participant']==id_participant]
    
    # Check columns
    if column_name not in df_participant.columns:
      print("Column name does not exist in dataframe.")
      return None
    
    # Check rows
    df_participant = df_participant[df_participant[column_name].notna()]
    num_rows = len(df_participant.index)
    if (num_rows<2):
      print("Dataframe has less than two rows that are not NaN. No plots could be drawn")
      return None

    # Data processing
    modality = column_name
    date_start = df_participant.index[0]
    date_end = df_participant.index[-1]
    df2 = df_participant[df_participant[column_name].notna()]

    # Compute difference between index timestamps in minutes
    df2['dT'] = df2.index.to_series().diff().dt.total_seconds()/60

    # Compute difference between timestamps (index-lambda)
    if "timestamp_lambda" in df2.columns:
      if column_name+'_lambda' in df2.columns:
        # Check if there actually values available
        if len(df2[df2[column_name+'_lambda'].notna()][column_name+'_lambda'])>0:
          timestamp_lambda = pd.to_datetime(df2[column_name+'_lambda'], format="%Y-%m-%dT%H:%M:%S.%f%z", errors='coerce')
          timestamp_lambda_str = column_name +'_lambda'
          transmit_trigger_str = column_name+'_trigger'
        else:
          timestamp_lambda = df2["timestamp_lambda"]
          timestamp_lambda_str = "timestamp_lambda"
          transmit_trigger_str = 'transmit_trigger'
      else:
        timestamp_lambda = df2["timestamp_lambda"]
        timestamp_lambda_str = "timestamp_lambda"
        transmit_trigger_str = 'transmit_trigger'
      
      df2['dTL'] = (timestamp_lambda-df2.index).dt.total_seconds()/60 # Compute time difference between timestamps in minutes
    else:
      df2['dTL'] = None
      timestamp_lambda_str = column_name +'_lambda'
      transmit_trigger_str = column_name+'_trigger'
      transmit_trigger_str = column_name+'_trigger'
      df_participant[transmit_trigger_str] = 'transmit_trigger not available'
      df_participant[timestamp_lambda_str] = None
      df2[transmit_trigger_str] = 'transmit_trigger not available'
      df2[timestamp_lambda_str] = None

    # Prepare stats:
    stats = dict(
    id_participant_text = ["id_participant:",  df2.id_participant.values[0]],
    dt_median =           ["Median time between data points:", str(round(df2["dT"].median(),1)) + " minutes"], # Median time between two responses if the difference is more than 0 seconds.
    dt_mean =             ["Average time between data points:", str(round(df2["dT"].mean(),1)) + " minutes"],  # Median time between two responses if the difference is more than 0 seconds.
    num_entries =         ["Number of data points:", str(df2[column_name].count())],
    timestamp_first =     ["First timestamp:", str(df2.index[1].strftime('%H:%M:%S%Z, %d.%m.%Y'))],
    timestamp_last =      ["Last timestamp:", str(df2.index[-1].strftime('%H:%M:%S%Z, %d.%m.%Y'))],
    timestamp_lambda=     ["Timestamp column name:", timestamp_lambda_str])

    # Create histograms
    counts_dT, bins_dT = np.histogram(df2['dT'][2:], bins=100, density=False)
    dTL_series = df2[df2['dTL'].notna()]['dTL']

    if len(dTL_series)>0:
      counts_dTL, bins_dTL = np.histogram(dTL_series, bins=100, density=False)
      #bins_all = 0.5 * (bins_participant[:-1] + bins_participant[1:])
    else:
      counts_dTL=[0]
      bins_dTL = [0]

    # Assign marker color
    color_map = {'background_task': 'rgb(0,0,255)',
                  'watch_survey': 'rgb(255,0,0)',
                  'application_appear': 'rgb(255,165,0)',
                  'app_change_settings': 'rgb(0,255,0)',
                  'push_notification_action_button': 'rgb(165,42,42)',
                  'push_notification_foreground': 'rgb(128,0,128)',
                  'sync_button_data_tab': 'rgb(0,0,0)',
                  'sync_button_settings_tab': 'rgb(202,202,202)',
                  'sync_button_backend_tab': 'rgb(202,202,202)',
                  'location_change': 'rgb(255,255,0)',
                  'transmit_trigger': 'rgb(000, 0, 0)',
                  'transmit_trigger not available': 'rgb(000, 0, 0)'}

    # Plotting
    fig = make_subplots(rows=3, cols=2,
                        subplot_titles=("Time Series", "Stats", "Duration between Timestamps", "Duration between Timestamps (Histogram)", "Duration between timestamp_lambda and index", "Duration between timestamp_lambda and index (Histogram)"),
                        vertical_spacing = 0.1,
                        horizontal_spacing = 0.1)

    # Plot 1 - Time-Series
    # Plot line
    fig.add_trace(go.Scatter(x=df_participant.index, y=df_participant[modality],
                            mode="lines",
                            name=f'{id_participant}',
                            line=dict(width=1, color='rgb(27,105,159)'),
                            showlegend=False),
                  row=1, col=1)
    # Plot markers
    for trigger in color_map:
      df3 = df_participant[df_participant[transmit_trigger_str]==trigger]
      fig.add_trace(go.Scatter(x=df3.index, y=df3[modality],
                              mode="markers",
                              name=trigger,
                              marker=dict(color=color_map[trigger]), showlegend=False, legendgroup=trigger),
                    row=1, col=1)
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text=modality, row=1, col=1)

    # Plot 2 - Stats
    for i, key in enumerate(stats):
      fig.add_annotation(text=stats[key][0],
                        x=0, y=6-i, xanchor='left', yanchor='bottom', 
                        showarrow=False, xshift=0, row=1, col=2)
      fig.add_annotation(text=stats[key][1],
                        x=1.2, y=6-i, xanchor='left', yanchor='bottom', 
                        showarrow=False, xshift=0, row=1, col=2)
    
    fig.update_xaxes(showticklabels=False, row=1, col=2)
    fig.update_yaxes(showticklabels=False, row=1, col=2)
    fig.update_layout(xaxis2 = dict(range=[0, 2]))
    fig.update_layout(yaxis2 = dict(range=[0, 7]))

    # Plot 3 - dTimestamp_lambda
    # Plot line
    fig.add_trace(go.Scatter(x=df2.index, y=df2['dT'],
                             mode="lines",
                             name=f'{id_participant}',
                             line=dict(width=1, color='rgb(27,105,159)'), 
                             showlegend=False),
                  row=2, col=1)
    # Plot markers
    for trigger in color_map:
      df3 = df2[df2[transmit_trigger_str]==trigger]
      fig.add_trace(go.Scatter(x=df3.index, y=df3['dT'],
                              mode="markers",
                              name=f'trigger',
                              marker=dict(color=color_map[trigger]), 
                              showlegend=False, legendgroup=trigger),
                    row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text=modality, row=2, col=1)

    # Plot 4 - dTimestamp_lambda (histogram)
    fig.add_trace(go.Bar(x=bins_dT, y=counts_dT, showlegend=False, marker=dict(color='rgb(27,105,159)')),
                  row=2, col=2)
    fig.update_xaxes(title_text="dT, Duration [min]", row=2, col=2)
    fig.update_yaxes(title_text="Counts [n]", row=2, col=2)

    # Plot 5 - dTimestamp_lambda-dIndex
    # Plot line
    fig.add_trace(go.Scatter(x=df2.index, y=df2['dTL'],
                             mode="lines",
                             name=f'{id_participant}',
                             line=dict(width=1, color='rgb(27,105,159)'), 
                             showlegend=False),
                  row=3, col=1)
    # Plot markers
    for trigger in color_map:
      df3 = df2[df2[transmit_trigger_str]==trigger]
      fig.add_trace(go.Scatter(x=df3.index, y=df3['dTL'],
                              mode="markers",
                              name=trigger,
                              marker=dict(color=color_map[trigger]), 
                              showlegend=True, legendgroup=trigger),
                    row=3, col=1)
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text=modality, row=3, col=1)

    # Plot 6 - dTimestamp_lambda-dIndex (histogram)
    fig.add_trace(go.Bar(x=bins_dTL, y=counts_dTL, showlegend=False, marker=dict(color='rgb(27,105,159)')),
                  row=3, col=2)
    fig.update_xaxes(title_text="dTL, Duration [min]", row=3, col=2)
    fig.update_yaxes(title_text="Counts [n]", row=3, col=2)

    # Share x-axes
    fig.update_xaxes(matches='x', row=1, col=1)
    fig.update_xaxes(matches='x', row=2, col=1)
    fig.update_xaxes(matches='x', row=3, col=1)

    # Change some more figure settings
    fig.update_layout(height=1000, width=1200, 
                      title_text=f'{id_participant}: {modality}',
                      title_x = 0.5,
                      legend_title_text='Trigger')
    return fig


  def ts_inspection_plotly2(self, column_name, id_participant=None):  
    """
    Function to plot time-series data in detail for one participant
    Arguments
    ----------
      - column_name, str, Name of column with time-series data that should be
      plotted
      - id_participant, str, Participant ID of which the time-series data should 
      be plotted
    Returns
    -------
      - fig, plotly figure object, figure with subplots
    """

    # Input processing
    df = self.df.copy()
    modality = column_name

    if id_participant == None:
      id_participant = self.id_participant

    df_participant = self.df[self.df['id_participant']==id_participant]

    # Data processing
    # Filter data
    df_all = df[(df[modality].notna())]# create the bins
    modality_min = df_all[modality].min()
    modality_max = df_all[modality].max()

    # Create histograms
    counts_all, bins_all = np.histogram(df_all[modality], bins=range(int(modality_min), int(modality_max), 5), density=True)
    bins_all = 0.5 * (bins_all[:-1] + bins_all[1:])

    counts_participant, bins_participant = np.histogram(df_participant[modality], bins=range(int(modality_min), int(modality_max), 5), density=True)
    bins_all = 0.5 * (bins_participant[:-1] + bins_participant[1:])

    # Create data for heatmap
    df_heatmap = df_participant.copy()
    df_heatmap = df_heatmap[df_heatmap[modality].notna()]
    df_heatmap = df_heatmap[modality].resample('h').mean().to_frame()
    df_heatmap['hour'] = df_heatmap.index.hour
    df_heatmap['date'] = df_heatmap.index.date

    # Plotting
    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=("Time Series", "Histogram (normalized)", "Heatmap", "Stats"),
                        vertical_spacing = 0.1,)

    # Plot 1 - Time-Series
    fig.add_trace(go.Scatter(x=df_all.index, y=df_all[modality],
                             mode="markers",
                             marker=dict(color="lightgrey"),
                             name='All Participants'),
                  row=1, col=1)

    fig.add_trace(go.Scatter(x=df_participant.index, y=df_participant[modality],
                             mode="markers",
                             name=f'{id_participant}'),
                  row=1, col=1)
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text=modality, row=1, col=1)


    # Plot 2 - Histogram
    fig.add_trace(go.Bar(x=bins_all, y=counts_all, 
                         marker_color="lightgrey", 
                         name='All Participants'),
                  row=1, col=2)

    fig.add_trace(go.Bar(x=bins_participant, 
                         y=counts_participant, 
                         name=f'{id_participant}'),
                  row=1, col=2)

    fig.update_xaxes(title_text=modality, row=1, col=2)
    fig.update_yaxes(title_text="Probability Density [-]", row=1, col=2)


    # Plot 3 - Heat Map
    fig.add_trace(go.Heatmap(x=df_heatmap.date,
                            y=df_heatmap.hour,
                            z=df_heatmap[modality],
                            colorscale='YlOrRd',
                            colorbar_lenmode='fraction',
                            colorbar_len=0.5,
                            colorbar_yanchor='top',
                            colorbar_title=modality),
                  row=2, col=1)
    fig.update_xaxes(title_text='Date', tickangle=-45, row=2, col=1)
    fig.update_yaxes(title_text='Time of Day', row=2, col=1)
    fig.update_yaxes(range=[0, 24], row=2, col=1)

    # Plot 4 - Stats
    x_bar = ["Min", "Median", "Mean", "Max"]
    y_bar = [df_participant[modality].min(),
            df_participant[modality].median(),
            df_participant[modality].mean(),
            df_participant[modality].max()]
    
    y_bar_all = [df_all[modality].min(),
                 df_all[modality].median(),
                 df_all[modality].mean(),
                 df_all[modality].max()]
    
    fig.add_trace(go.Bar(x = x_bar, y=y_bar, name=f"{id_participant}"),
                  row=2, col=2)
    fig.add_trace(go.Bar(x = x_bar, y=y_bar_all, name=f'All Participants'),
                  row=2, col=2)
    fig.update_yaxes(title_text=modality, row=2, col=2)

    fig.update_layout(height=1200, width=1200, 
                      title_text=f'{id_participant}: {modality}',
                      title_x = 0.5)

    return fig


  def cohort_survey_count_bar(self):
    """
    Function to plot bar chart of ws_survey_count for all participants
    
    Arguments
    ----------
      - None

    Returns
    -------
      - fig, plotly figure object, figure with subplots
    """
    
    df = self.df.copy()

    # Filter for participant_list
    df = df[df.id_participant.isin(self.participant_list)]

    # Filter for valid votes
    valid_votes_title = "(all votes)"
    if "valid_vote" in df.columns:
      if self.valid_votes == True: 
        df = df[df["valid_vote"]==True]
        valid_votes_title = "(only valid votes)"

    # Cumulate data
    df2 =(df[df["ws_survey_count"].notna()]
    .groupby("id_participant")
    .resample('D')["ws_survey_count"]
    .count()
    .unstack()
    .T)
    
    # Add missing participants as empty columns
    for id_participant in self.participant_list:
      if id_participant not in df2.columns:
        df2[id_participant] = pd.Series(dtype='float64')

    # Plot data
    fig = px.bar(df2, x=df2.index, y=df2.columns, 
                barmode='group',
                title=f'ws_survey_count counts daily, individual {valid_votes_title}',
                width = 800,
                height = 400)
    fig.update_layout(yaxis_title = "ws_survey_count [#]",
                      title_x=0.5,
                      xaxis_title = 'Date',
                      legend_title = 'Participants')
    #fig.show()
    return fig


  def cohort_all_survey_count_bar(self):
    """
    Function to plot bar chart of the sum of ws_survey_count for 
    all participants
    
    Arguments
    ----------
      - None
    
    Returns
    -------
      - fig, ?, plotly figure object
    """

    df = self.df.copy()
    
    # Filter for valid votes
    valid_votes_title = "(all votes)"
    if "valid_vote" in df.columns:
      if self.valid_votes == True: 
        df = df[df["valid_vote"]==True]
        valid_votes_title = "(only valid votes)"

    # Process data    
    df2 = (df[df["ws_survey_count"].notna()]
    .resample('D')["ws_survey_count"]
    .count()
    )

    # Plot data
    fig = px.bar(df2, x=df2.index, y=df2.values, 
                title=f'ws_survey_count counts daily, all participants {valid_votes_title}',
                width = 800,
                height = 400)
    fig.update_layout(yaxis_title = "ws_survey_count [#]",
                      title_x=0.5,
                      xaxis_title = 'Date',
                      legend_title = 'Participants')

    return fig

  
  def cohort_individual_survey_count_bar(self):
    """
    Function to plot bar chart of ws_survey_count for individual participants
    
    Arguments
    ----------
      - None
    
    Returns
    -------
      - fig, ?, plotly figure object
    """
    
    df = self.df.copy()

    # Filter for valid votes
    valid_votes_title = "(all votes)"
    if "valid_vote" in df.columns:
      if self.valid_votes == True: 
        df = df[df["valid_vote"]==True]
        valid_votes_title = "(only valid votes)"

    # Process data
    df2 = (df[df["ws_survey_count"].notna()]
    .groupby("id_participant")["ws_survey_count"]
    .count()
    )
    
    # Plot data
    fig = px.bar(df2, x=df2.index, y=df2.values, 
                title=f'ws_survey_count counts overall, individual {valid_votes_title}',
                width = 800,
                height = 400)
    fig.update_layout(yaxis_title = "ws_survey_count [#]",
                      title_x=0.5,
                      xaxis_title = 'Participant ID')

    return fig


  def cohort_survey_count_line(self, threshold=None):
    """
    Function to plot bar chart of the sum of ws_survey_count for all 
    participants using Plotly
    
    Arguments
    ----------
      - threshold, int, Number of responses required for the completion of the 
      participation in experiment
    
    Returns
    -------
      - fig, ?, plotly figure object
    """

    df = self.df.copy()

    # Filter for valid votes
    valid_votes_title = "(all votes)"
    if "valid_vote" in df.columns:
      if self.valid_votes == True: 
        df = df[df["valid_vote"]==True]
        valid_votes_title = "(only valid votes)"
    
    # Process data
    df = df[df.ws_survey_count.notna()]
    df['ws_survey_count_count'] = (df
    .groupby('id_participant')["ws_survey_count"]
    .cumcount()
    )

    # Plot data
    fig = go.Figure()
    first = True
    for id_participant in self.participant_list:
      df2 = df[df["id_participant"]==id_participant]
      fig.add_trace(go.Scatter(x=df2.index, y=df2["ws_survey_count_count"], 
                               name=id_participant, mode='lines',
                               legendgroup='participants',
                               showlegend=True,
                               legendgrouptitle_text="Participants"))

    # Plot threshold line
    if threshold != None:
      fig.add_trace(go.Scatter(x=[0, 1], 
                               y=[threshold, threshold], 
                               name=f"Threshold: <br>{int(threshold)} responses",
                               mode="lines",
                               xaxis='x2',
                               showlegend=True,
                               line=dict(width=1),
                               legendgroup = 'threshold',
                               legendgrouptitle_text="Threshold"))
      fig.update_layout(
        xaxis2=dict(
            overlaying='x',
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0,1]),)

    fig.update_layout(title = f'Cohort cumulative ws_survey_count, individual {valid_votes_title}',
                      yaxis_title = 'Cumulative ws_survey_count [#]',
                      title_x=0.5,
                      xaxis_title = 'Date',
                      legend_tracegroupgap = 10,
                      width = 800, height = 400,)

    return fig


  def cohort_all_survey_count_line(self):
    """
    Function to plot line chart of the cumsum of ws_survey_count for all 
    participants using Plotly
    
    Arguments
    ----------
      - None
    
    Returns
    -------
      - fig, ?, plotly figure object
    """

    df = self.df.copy()

    # Process data
    df["ws_survey_count_count"] = df["ws_survey_count"].notnull().astype('int').cumsum()
    
    # Filter for valid votes
    valid_votes_title = "(all votes)"
    if "valid_vote" in df.columns:
      if self.valid_votes == True: 
        df = df[df["valid_vote"]==True]
        valid_votes_title = "(only valid votes)"

    # Plot data
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["ws_survey_count_count"], name="All Participants", mode='lines'))
    fig.update_layout(title = f'Cohort cumulative ws_survey_count, all participants {valid_votes_title}',
                      yaxis_title = 'Cumulative ws_survey_count [#]',
                      title_x=0.5,
                      xaxis_title = 'Date',
                      legend_title = 'Participants',
                      showlegend=True)
    return fig
  

  def cohort_all_survey_count_line2(self):
    """
    Function to plot line chart of the cumsum of ws_survey_count for entire cohort and individual participants using Plotly
    
    Arguments
    ----------

    Returns
    -------
      - fig, ?, Plotly figure object
    """
    df = self.df.copy()

    # Filter for valid votes
    valid_votes_title = "(all votes)"
    if "valid_vote" in df.columns:
      if self.valid_votes == True: 
        df = df[df["valid_vote"]==True]
        valid_votes_title = "(only valid votes)"

    # Process data for individual participants
    df = df[df.ws_survey_count.notna()]
    df = df.sort_index()
    df['ws_survey_count_count'] = (df.groupby('id_participant')["ws_survey_count"]
                                .cumcount())

    # Process data for all
    df["ws_survey_count_count_all"] = df["ws_survey_count"].notnull().astype('int').cumsum()

    # Plot data for all
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["ws_survey_count_count_all"], name="All Participants", mode='lines'))
    fig.update_layout(title = f'Cohort cumulative ws_survey_count, all participants {valid_votes_title}',
                      yaxis_title = 'Cumulative ws_survey_count [#]',
                      title_x=0.5,
                      xaxis_title = 'Date',
                      legend_title = 'Participants',
                      showlegend=True)
    
    # Plot data for individual participants
    for id_participant in self.participant_list:
      df2 = df[df["id_participant"]==id_participant]
      fig.add_trace(go.Scatter(x=df2.index, y=df2["ws_survey_count_count"], name=id_participant, mode='lines'))

    return fig
  
  
  def cohort_dt_swarm(self, threshold=None):
    """
    Function to plot swarm chart of the time between two ws_survey_count 
    timestamps for individual participants with Plotly
    
    Arguments
    ----------
      - threshold, int, Minimal allowed duration between two watch_survey 
      responses in minutes
    
    Returns
    -------
      - fig, ?, plotly figure object
    """

    df = self.df.copy()
    
    # Filter for valid votes
    valid_votes_title = "(all votes)"
    if "valid_vote" in df.columns:
      if self.valid_votes == True: 
        df = df[df["valid_vote"]==True]
        valid_votes_title = "(only valid votes)"

    df = df[df.ws_survey_count.notna()]
    df['dT'] = df['dT']/60

    fig = px.strip(df, x="id_participant", y="dT")
    fig.update_layout(title = f'Cohort cumulative ws_survey_count, all participants {valid_votes_title}',
                      title_x=0.5,
                      yaxis_title = 'Duration between two micro-survey responses [h]',
                      xaxis_title = 'Participants',
                      showlegend=True,
                      yaxis_range=[0,20])
  
    # Plot threshold line
    if threshold != None:
      #fig.add_vline(x=threshold, line_width=1, line_dash="solid", line_color="red")
      fig.add_trace(go.Scatter(x=[0, 1], 
                               y=[threshold/60, threshold/60], 
                               name=f"Threshold ({int(threshold)} min)",
                               mode="lines",
                               xaxis='x2',
                               showlegend=True,
                               line=dict(width=1)))
      fig.update_layout(
        xaxis2=dict(
            overlaying='x',
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0,1]),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01))

    return fig


  def cohort_dt_hist(self, mode='plotly', threshold=None):
    """
    Function to swarm chart chart of the time between two ws_survey_count 
    timestamps for individual participants with Plotly
    
    Arguments
    ----------
      - threshold, int, Minimal allowed duration between two watch_survey
      responses in minutes
    
    Returns
    -------
      - fig, ?, plotly figure object
    """

    df = self.df.copy()

    # Filter for valid votes
    valid_votes_title = "(all votes)"
    if "valid_vote" in df.columns:
      if self.valid_votes == True: 
        df = df[df["valid_vote"]==True]
        valid_votes_title = "(only valid votes)"

    # Process data
    df["dT"] = df["dT"]/60

    fig = go.Figure()
    fig.add_trace(go.Histogram(histfunc="count", 
                               x=df["dT"].values, 
                               xbins=dict(
                                  start=0,
                                  end=12,
                                  size=1/12),
                                showlegend=False))
    
    fig.update_layout(title = f'Histogram - Duration between two watch survey responses {valid_votes_title}',
                      title_x=0.5,
                      yaxis_title = 'Counts [#]',
                      xaxis_title = 'Duration [h]',
                      xaxis_range=[0,12],
                      width = 800,
                      height = 400)
    
    # Plot threshold line
    if threshold != None:
      threshold = threshold/60
      #fig.add_vline(x=threshold, line_width=1, line_dash="solid", line_color="red")
      fig.add_trace(go.Scatter(x=[threshold, threshold], 
                               y=[0, 1], 
                               name=f"Threshold ({int(threshold*60)} min)",
                               mode="lines",
                               yaxis='y2',
                               showlegend=True))
      fig.update_layout(
        yaxis2=dict(
            overlaying='y',
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0,1]),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99))

    return fig
  

  def cohort_duration_since_last_entry(self, modality='ws_survey_count', threshold=1):
    """
    Function to plot bar chart of duration since last the watch survey response 
    was submitted with plotly
    
    Arguments
    ----------
      - None
    
    Returns
    -------
      - fig, ?, plotly figure object
    """
    
    df = self.df.copy()

    # Filter for valid votes
    valid_votes_title = "all votes"
    if "valid_vote" in df.columns:
      if self.valid_votes == True: 
        df = df[df["valid_vote"]==True]
        valid_votes_title = "only valid votes"

    # Compute duration
    timestamp_now = datetime.datetime.now(pytz.timezone("UTC"))
    df2 = df[df[modality].notna()]
    df2['timestamp'] = df2.index
    my_series = df2.groupby("id_participant")["timestamp"].last()
    df3 = (timestamp_now-my_series).dt.total_seconds().div(3600).to_frame()
    df3['above_threshold'] = df3[df3>=threshold]['timestamp']
    df3['below_threshold'] = df3[df3<threshold]['timestamp']

    # Plot
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df3.index, y=df3['below_threshold'], name='Below threshold'))
    fig.add_trace(go.Bar(x=df3.index, y=df3['above_threshold'], name='Above threshold'))
    fig.update_layout(barmode = 'stack',
                      yaxis_title = f"Duration since last {modality} entry [h]",
                      xaxis_title = 'Participant ID',
                      legend_title = 'Threshold',
                      title_text = f"Duration since last {modality} entry (threshold={threshold}h, {valid_votes_title})",
                      title_x=0.75)
    
    return fig


  def cohort_threshold_undercut(self, threshold=None, mode='plotly'):
    """
    Wrapper function to plot bar chart of cumulative threshold exceedances
    per participant
    
    Arguments
    ----------
      - mode, str, flat that indicates whether to use matplotlib or plotly as 
      chart engine
    
    Returns
    -------
      - fig, ?, matplotlib figure object
      - fig, ?, plotly figure object
    """
    
    if mode=='matplotlib':
      return self.cohort_threshold_undercut_matplotlib(threshold=threshold)
    if mode=='plotly':
      return self.cohort_threshold_undercut_plotly(threshold=threshold)

  def cohort_threshold_undercut_matplotlib(self, threshold):
    """
    Function to plot bar chart of cumulative threshold exceedances per 
    participant
    
    Arguments
    ----------
      - threshold, int, Minimal allowed duration between two watch_survey 
      responses in minutes

    Returns
    -------
      - fig, ?, matplotlib figure object
    """
    df = self.df.copy()

    # Filter for valid votes
    valid_votes_title = "(all votes)"
    if "valid_vote" in df.columns:
      if self.valid_votes == True: 
        df = df[df["valid_vote"]==True]
        valid_votes_title = "(only valid votes)"

    # Plot data
    fig, ax = plt.subplots(1,1, figsize =(20, 10))
    ax = (df[df['dT']<threshold].groupby(['id_participant'])["ws_survey_count"]
                    .count()
                    .plot(kind='bar', 
                          title=f'Instances where the duration between two watch survey responses that are less than {threshold} min {valid_votes_title}', 
                          ylabel='Counts [x]', 
                          xlabel='Participants', 
                          figsize=(25, 7))
    )
    ax.tick_params(axis='x', labelrotation=0)

    return fig
  
  def cohort_threshold_undercut_plotly(self, threshold):
    """
    Function to plot bar chart of cumulative threshold s per participant
    
    Arguments
    ----------
      - threshold, int, Minimal allowed duration between two watch_survey 
      responses in minutes

    Returns
    -------
      - fig, ?, Plotly figure object
    """
    df = self.df.copy()

    # Filter for valid votes
    valid_votes_title = "(all votes)"
    if "valid_vote" in df.columns:
      if self.valid_votes == True: 
        df = df[df["valid_vote"]==True]
        valid_votes_title = "(only valid votes)"

    # Process data
    df2 = df[df['dT']<threshold].groupby(['id_participant'])["ws_survey_count"].count()

    # Plot data
    fig = px.bar(df2, x=df2.index, y=df2.values, 
                barmode='group',
                title=f'Instances where the duration between two watch survey responses that are less than {threshold} min {valid_votes_title}',
                width = 800,
                height = 400)
    fig.update_layout(yaxis_title = "Counts [#]",
                      title_x=0.5,
                      xaxis_title = 'Participants')

    return fig
  

  def cohort_threshold_report(self, threshold):
    """
    Function to print some stats about the threshold of duration between two 
    vote_counts
    
    Arguments
    ----------
      - threshold, int, Minimal allowed duration between two watch_survey 
      responses in minutes

    Returns
    -------
      - n1, int, Number of watch survey responses that with less then 
      'threshold' minutes in between
      - n2, int, Number of watch survey responses with equal or more than 
      'threshold' minutes in between
    """
    df = self.df.copy()

    # Filter for valid votes
    valid_votes_title = "(all votes)"
    if "valid_vote" in df.columns:
      if self.valid_votes == True: 
        df = df[df["valid_vote"]==True]
        valid_votes_title = "(only valid votes)"
    
    n1 = df[df['dT']<threshold].ws_survey_count.count()
    n2 = df[df['dT']>=threshold].ws_survey_count.count()

    print(f"Total votes less than {threshold}min apart:", n1)
    print(f"Total votes more or equal than {threshold}min apart:", n2)

    return n1, n2


  def cohort_ws_inspection(self, num_cols=2, mode='plotly'):
    """
    Function to plot bar chart with the responses to the watch survey 
    for the entire cohort
    
    Arguments
    ----------
      - num_cols, int, number of columns for the plot
      - mode, str, flat that indicates whether to use matplotlib or plotly as 
      chart engine
    
    Returns
    -------
      - fig, ?, matplotlib figure object
      - fig, ?, plotly figure object
    """
    
    if mode=='matplotlib':
      return self.cohort_ws_inspection_matplotlib()
    if mode=='plotly':
      return self.cohort_ws_inspection_plotly(num_cols=num_cols)

  def cohort_ws_inspection_matplotlib(self):
    """
    Function to plot bar chart with the responses to the watch surveys for the 
    entire cohort with Matplotlib
    
    Arguments
    ----------

    Returns
    -------
      - fig, ?, matplotlib figure object
    """
    df = self.df.copy()

    # Filter for valid votes
    valid_votes_title = "(all votes)"
    if "valid_vote" in df.columns:
      if self.valid_votes == True: 
        df = df[df["valid_vote"]==True]
        valid_votes_title = "(only valid votes)"

    number_of_questions = len(self.ws_questions)
    number_of_columns = 2
    number_of_rows = math.ceil(number_of_questions/number_of_columns)+1

    # Add column for questions for which no responses were logged for current question
    for question in self.ws_questions:
      if question not in df.columns:
        df[question] = None

    fig, axs = plt.subplots(number_of_rows, number_of_columns, figsize =(18, 25))
    fig.tight_layout(pad=7.5)
    gs = fig.add_gridspec(number_of_rows,number_of_columns)
    axs2 = fig.add_subplot(gs[number_of_rows-1, :])

    current_row = 0
    current_column = 0
    my_dict = {}      

    # Bar charts of responses to individual questions
    for index, (question_id, question_value) in enumerate(self.ws_questions.items()):
      df[question_id].count()
      current_row = math.ceil((index+1)/number_of_columns)-1
      current_column = index % number_of_columns
      # Skip subplot if no responses were logged for current question
      if df[question_id].count()==0:
        my_dict[question_value] = 0
      else:
        my_dict[question_value] = df[question_id].count()
        df[question_id].value_counts().plot(kind='barh', ax = axs[current_row,current_column])
      title_wrapped = wrap(question_value, 40)
      title_wrapped = "\n".join(title_wrapped)
      axs[current_row,current_column].set_title(title_wrapped, fontsize=20)
      axs[current_row,current_column].set_ylabel("Responses", fontsize=16)
      axs[current_row,current_column].set_xlabel("Counts [#]", fontsize=16)
      axs[current_row,current_column].xaxis.set_major_formatter(FormatStrFormatter('%.0f')) # Remove decimals from x-tick labels
      
    # Bar chart of sum of all responses per question
    labels = []
    for key in my_dict.keys():
      label_wrapped = wrap(key, 20)
      label_wrapped = "\n".join(label_wrapped)
      labels.append(label_wrapped)

    axs2.bar(labels, my_dict.values())
    axs2.set_title(f"Overview {valid_votes_title}", fontsize=20)
    axs2.set_ylabel("Counts [#]", fontsize=16)
    axs2.set_xlabel("Questions", fontsize=16)
    plt.setp(axs2.get_xticklabels(), rotation=55, ha="right", rotation_mode="anchor")

    # Remove redundant ticks under 2-column chart
    axs[number_of_rows-1, 0].set_xticks([])
    axs[number_of_rows-1, 0].set_yticks([])
    axs[number_of_rows-1, 1].set_xticks([])
    axs[number_of_rows-1, 1].set_yticks([])

    # Remove redundant  subplots of empty plots
    for col in range(current_column+1, number_of_columns):
      axs[number_of_rows-2,col].set_xticks([])
      axs[number_of_rows-2,col].set_yticks([])
      axs[number_of_rows-2,col].axis('off')

    return fig

  def cohort_ws_inspection_plotly(self, num_cols): 

    """
    Function to plot bar chart with the responses to the watch surveys for the 
    entire cohort with Plotly
    
    Arguments
    ----------
      - num_cols, int, number of columns for the plot

    Returns
    -------
      - fig, ?, plotly figure object
    """
    df = self.df.copy()

    # Filter for valid votes
    valid_votes_title = "(all votes)"
    if "valid_vote" in df.columns:
      if self.valid_votes == True: 
        df = df[df["valid_vote"]==True]
        valid_votes_title = "(only valid votes)"

    number_of_questions = len(self.ws_questions)
    number_of_columns = num_cols
    number_of_rows = math.ceil(number_of_questions/number_of_columns)+1
    
    # Add column for questions for which no responses were logged for current question
    #for question in self.ws_questions:
    #  if question not in df.columns:
    #    df[question] = None

    my_dict = {}
    list_row = []
    list_col = []
    list_traces = []
    list_titles = []

    # Bar charts of responses to individual questions
    for index, (question_id, question_value) in enumerate(self.ws_questions.items()):
      current_row = math.ceil((index+1)/number_of_columns)
      current_column = index % number_of_columns+1
      #if df[question_id].count()==0:
      #  my_dict[question_value] = 0
      #  continue
      my_dict[question_value] = df[question_id].count()

      df2 = df[question_id].value_counts()

      # Add response options without recorded responses
      list_response_options_ordered = []
      for question in self.watch_survey['survey']:
        #print(question['question_id'])
        if question['question_id'] != question_id:
          continue
        
        for response_option in question['response_options']:
          list_response_options_ordered.append(response_option['text'])
          if response_option['text'] not in df2.index:
            new_value = pd.Series([0], index=[response_option['text']])
            df2 = pd.concat([df2, new_value])
      
      # Order response options according to the order in the survey
      list_response_options_ordered.reverse() # Reverse order because yaxis is filled from the bottom up
      df2 = df2.reset_index() # Reset index to make it a column
      df2.columns = ['response_option', 'count'] # Rename columns for clarity
      df2['response_option'] = pd.Categorical(df2['response_option'], categories=list_response_options_ordered, ordered=True) # Convert the 'index' column to a categorical type with the custom order
      df2 = df2.sort_values('response_option').set_index('response_option') # Sort the dataframe based on the custom order

      # Create trace
      title_wrapped = wrap(question_value, 35)
      title_wrapped = "<br>".join(title_wrapped)
      title_wrapped = title_wrapped + f'<br>(id:{question_id})'
      list_titles.append(title_wrapped)
      list_row.append(current_row)
      list_col.append(current_column)

      # Create label at the top of bars
      df2['bar_text'] = (df2['count']/df2['count'].sum()*100)
      df2['bar_text'] = df2['bar_text'].astype(int, errors='ignore')
      df2['bar_text'] = df2['bar_text'].fillna('')
      df2['bar_text'] = df2['bar_text'].astype(str)+'%)'
      df2['bar_text'] = df2['count'].astype(str) + ' (' + df2['bar_text']

      list_traces.append(go.Bar(x=df2['count'], 
                                y=df2.index, 
                                orientation='h',
                                marker_color='rgb(99,110,250)', 
                                text=df2['bar_text'],
                                textposition='auto',
                                textangle=0))
    
    # Create subplot layout  
    list_specs = []
    for i in range(1, number_of_rows):
      #list_specs.append([{}, {}])
      list_specs.append([{} for i in range(0, number_of_columns)])
    spec = [{'colspan': number_of_columns}]
    spec.extend([None for i in range(1, number_of_columns)])
    list_specs.append(spec)
    #list_specs.append([{}, {}])

    # Add title of last plot to list
    if len(list_titles)< number_of_columns*(len(list_specs)-1):
      list_titles.append('')
    list_titles.append('Total number of responses per question')

    # Create figure  
    fig = make_subplots(rows=number_of_rows, 
                        cols=number_of_columns,
                        vertical_spacing = 0.45/number_of_rows,
                        horizontal_spacing = 0.5/number_of_columns,
                        subplot_titles= list_titles,
                        specs=list_specs)  # make specs adapt to the number of questions
    
    # Add traces to figure
    for i, trace in enumerate(list_traces):
      fig.add_trace(trace, list_row[i], list_col[i])
      fig.update_xaxes(title_text='Response Count [#]', row=list_row[i], col=list_col[i])
      fig.update_yaxes(title_text='Response Options', row=list_row[i], col=list_col[i])
      if i !=len(list_traces)-1:
        # Share x-axis for all but on the last plot
        fig.update_xaxes(matches='x1', row=list_row[i], col=list_col[i])

    # Bar chart of sum of all responses per question

    # Wrap y-label (disabled because of the bad looks with too many questions.)
    labels = []
    for key in my_dict.keys():
      label_wrapped = wrap(key, 20) # 
      label_wrapped = "<br>".join(label_wrapped)
      labels.append(label_wrapped)

    #labels = list(my_dict.keys())
    values = list(my_dict.values())
    last_row = number_of_rows
    last_col = 1

    # Create label at the top of bars (for bottom chart)
    question_id_first = self.watch_survey['survey'][0]['question_id']
    value_max = df[question_id_first].count()
    bar_text = [str(value)+ ' (' + str(int(value/value_max*100)) + '%)' for value in values]

    trace2 = go.Bar(y=values, x=labels, orientation='v', marker_color='rgb(99,110,250)', text=bar_text, textposition='auto', textangle=0)
    fig.add_trace(trace2, row=last_row, col=last_col)
    fig.update_xaxes(title_text='Questions', tickangle= -45, row=last_row, col=last_col)
    fig.update_yaxes(title_text='Response Count [#]', row=last_row, col=last_col)
    height = number_of_rows*250
    width = number_of_columns*600
    fig.update_layout(height=height, width=width, showlegend=False,
                      title_text = 'Watch Survey Responses', title_x=0.5)

    return fig


  def sleep_inspection(self, id_participant=None, prefix='ws_', mode='plotly'):
    """
    Function to plot sleep data in detail for one participant

    Arguments
    ----------
      - id_participant, str, Participant ID of which the time-series data should 
      be plotted
      - prefix, str, Prefix of the sleep data columns in the DataFrame
    Returns
    -------
      - fig, plotly figure object, figure with subplots (mode=plotly)
    """

    if id_participant == None:
      id_participant = self.id_participant

    df = self.df[self.df['id_participant']==id_participant]
    # Relevant column names with sleep data without prefix
    list_sleep_columns = ["sleep_deep",
                          "sleep_core",
                          "sleep_REM",
                          "sleep_awake",
                          "sleep_unspecified",
                          "sleep_in_bed"]
    
    # Add prefix to column names
    list_sleep_columns = [prefix + x for x in list_sleep_columns]

    # Remove missing columns
    list_sleep_columns = [col for col in list_sleep_columns if col in df.columns]

    # Remove non-sleep-related columns
    df = df[list_sleep_columns]

    # Remove empty rows
    df = df.dropna(axis=0, how='all')
    
    # Check columns
    if len(list_sleep_columns)==0:
      print("No sleep data available")
      return None
    
    # Check rows
    if len(df)==0:
      print("No sleep data available")
      return None
    
    yticks = []
    x_sleep = []
    y_sleep = []
    x_in_bed = []
    y_in_bed = []
    sleep_type_available = []

    date_start = df.index[0]
    date_end = df.index[-1]

    # Create data for line chart
    for index, row in df.iterrows():
      for i, sleep_type in enumerate(list_sleep_columns):
        if sleep_type not in df.columns:
          continue
        if np.isnan(row[sleep_type]):
          continue
        #if sleep_type =="ws_sleep_in_bed":
        if sleep_type ==list_sleep_columns[-1]:
          x_in_bed.append(index)
          x_in_bed.append(index+pd.Timedelta(minutes=row[sleep_type]))
          y_in_bed.append(list_sleep_columns.index(sleep_type))
          y_in_bed.append(list_sleep_columns.index(sleep_type))
        else:
          x_sleep.append(index)
          x_sleep.append(index+pd.Timedelta(minutes=row[sleep_type]))
          y_sleep.append(list_sleep_columns.index(sleep_type))
          y_sleep.append(list_sleep_columns.index(sleep_type))

    yticks = [*range(0, len(list_sleep_columns))]

    number_of_rows = 2
    number_of_columns = 2

    list_titles = ['Sleep phases', 'Cumulative, over all', 'Cumulative, daily', 'Sleep phases, nightly']
    list_specs = [[{}, {}],
                  [{}, {}]]

    # Create figure  
    fig = make_subplots(rows=number_of_rows, 
                        cols=number_of_columns,
                        vertical_spacing = 0.35,
                        horizontal_spacing = 0.3,
                        subplot_titles= list_titles,
                        specs=list_specs)
    # Create color map
    prefix = list_sleep_columns[0].split('_')[0]
    color_map = {prefix + '_sleep_awake': 'rgb(255,138,115)',
                 prefix + '_sleep_REM': 'rgb(89,170,225)',
                 prefix + '_sleep_core': 'rgb(52,120,246)',
                 prefix + '_sleep_deep': 'rgb(53,52,157)',
                 prefix + '_sleep_unspecified': 'rgb(202,202,202)',
                 prefix + '_sleep_in_bed': 'rgb(161,235,235)'}

    # Create plot 1
    fig.add_trace(go.Scatter(x=x_sleep, y=y_sleep, line_shape='hv', name='Sleep Phase', legendgroup='plot1'), row=1, col=1)
    fig.add_trace(go.Scatter(x=x_in_bed, y=y_in_bed, line_shape='hv', name='In bed', legendgroup='plot1'), row=1, col=1)
    fig.update_xaxes(title_text='Date', tickangle= -45, row=1, col=1)
    fig.update_yaxes(title_text='Sleep phase', row=1, col=1)
    fig.update_yaxes(tickvals=list(range(0,len(list_sleep_columns))), ticktext=list_sleep_columns, row=1, col=1)

    # Create plot 2
    series = df.sum().div(60)
    fig.add_trace(go.Bar(x=series.index, y=series.values, name='Cumulative duration', showlegend=False), row=1, col=2)
    fig.update_xaxes(title_text='Sleep phase', tickangle= -45, row=1, col=2)
    fig.update_yaxes(title_text='Duration [h]', row=1, col=2)
    
    # Create plot 3
    df2 = df.groupby([pd.Grouper(freq='D')]).sum().div(60)
    df2 = df2.drop(columns=[list_sleep_columns[-1]]) # drop in_bed
    for col in df2.columns:
      fig.add_trace(go.Bar(x=df2.index, y=df2[col], name=col, marker_color=color_map[col], legendgroup=col), row=2, col=1)
    fig.update_layout(barmode='stack') # barmode is a figure-wide property ?! (https://stackoverflow.com/questions/50695971/plotly-stacked-bars-only-in-specific-subplots)
    fig.update_xaxes(title_text='Date', tickangle= -45, row=2, col=1)
    fig.update_yaxes(title_text='Duration [h]', row=2, col=1)
    fig.update_layout(height=600, width=800)

    # Create plot 4
    # Shift timestamps by back to have one bar per night
    # (moves parts of the bar left and right)
    shift_parameter = 4
    df.index = df.index + pd.to_timedelta(shift_parameter, unit='h')

    # Compute position of lower edge of bar (moves bar up and down)
    df["base"] = df.index.hour + df.index.minute/60 - shift_parameter

    for col in df.columns:
        # Do not plot some columns
        if col=='base' or col==(prefix+'sleep_in_bed'):
            continue

        # Remove empty rows of column
        df2=df[df[col].notna()]

        # Plot bars
        fig.add_trace(go.Bar(x=df2.index.date, 
                            y=df2[col].div(60), 
                            base = df2['base'],
                            name=col,
                            marker_color=color_map[col],
                            legendgroup=col,
                            showlegend=False
                            ),
                            row=2, col=2)
        fig.update_xaxes(tickvals = pd.date_range(start=df.index.date[0], end=df.index.date[-1]).tolist(),
                         tickformat= '%b %d', 
                         tickangle= -45,
                         row=2, col=2)
        fig.update_yaxes(tickvals = [-3,    -2,    -1,     0,     1,     2,     3,     4,     5,     6,     7,     8,     9,     10,     11,     12,     13,     14,     15,      16],
                         ticktext = ['9pm','10pm','11pm','12 AM','1 AM','2 AM','3 AM','4 AM','5 AM','6 AM','7 AM','8 AM','9 AM','10 AM','11 AM','12 AM','13 AM','14 AM','15 AM', '16 AM'],
                         row=2, col=2)
    
    fig.update_layout(legend_tracegroupgap=20)

    # Share x-axes
    fig.update_xaxes(matches='x', row=1, col=1)
    fig.update_xaxes(matches='x', row=2, col=1)
    fig.update_xaxes(matches='x', row=2, col=2)
    
    return fig
  

  def event_plot(self, id_participant=None, modality_list=[]):
    """
    Function to plot overview chart of all data points using Plotly
    
    Arguments
    ----------
      - id_participant, str, Participant ID of which the data should be plotted
      - modality_list, list of str, includes column names that should be 
      included in the chart
    
    Returns
    -------
      - fig, ?, plotly figure object
    """

    if id_participant == None:
      id_participant = self.id_participant
    else:
      self.id_participant = id_participant

    df = self.df.copy()
    df = df[df.id_participant==id_participant]

    # Parse modality_list
    if modality_list==[]:
      modality_list = list(df.columns)
    else:
      modality_list = [*reversed(modality_list)]

    # Remove suffixes (_trigger, _lambda)
    modality_list2 = []
    for item in modality_list:
      if "ts_" in item[:3] or "ws_" in item[:3]:
        if "_trigger" in item[-8:] or "_lambda" in item[-7:]:
          continue
      if "q_" in item[:2]:
        continue

      modality_list2.append(item)

    modality_list = modality_list2

    # Parse prefix
    #if prefix!=None:
    #  modality_list = [modality for modality in modality_list if 'ts_' in modality]

    # Create figure
    fig = go.Figure()
    cm = px.colors.qualitative.Plotly

    for i, modality in enumerate(modality_list):
      if modality not in df.columns:
        df[modality]=np.nan
      df2 = df[df[modality].notna()]
      df2[modality]=1
      width = 1
      
      # Create color map
      color = cm[i%len(cm)]
      
      # Convert color from HEX to rgba(r,g,b,a)
      if len(df2[modality])==0:
        alpha = 0.2
        color_str = color.lstrip("#")
        r = int(color_str[0:2], 16)
        g = int(color_str[2:4], 16)
        b = int(color_str[4:6], 16) 
        rgba_string = f"rgba({r},{g},{b},{alpha})"

        # Plot dashed line
        fig.add_trace(go.Scatter(x=[df.index[0], df.index[-1]], y=[i,i],
                                 mode='lines', line=dict(color=rgba_string, dash='dot', width=width)))
      else:
        # Plot solid line
        fig.add_trace(go.Scatter(x=[df.index[0], df.index[-1]], y=[i,i], line_color=color,
                                 mode='lines', line=dict(width=width),
                                 marker=dict(size=20)))
        
      # Plot markers
      fig.add_trace(go.Scatter(x=df2.index, y=i*df2[modality], line_color=color, mode='markers'))
      
      # Wrangle with figure
      fig.update_layout(yaxis_range=[-1, len(modality_list)+1])
      fig.update_yaxes(tickvals=list(range(0,len(modality_list))), ticktext=modality_list)
      fig.update_xaxes(title_text='Date')
      fig.update_yaxes(title_text='Column names')
      fig.update_layout(height=2000, width=1000, showlegend=False,
                        title_text=f'Event Plot (Participant {df.id_participant.values[0]})')

    return fig
    

  def cohort_event_plot(self, column_name, participant_list=None):
    """
    Function to plot overview chart of all data points using Plotly
    
    Arguments
    ----------
      - participant_list, list of str, Participant IDs of which the data should be plotted
      - column_name, str, includes column name that should be 
      included in the chart
    
    Returns
    -------
      - fig, ?, plotly figure object
    """

    if participant_list == None:
      participant_list = self.participant_list
    else:
      self.participant_list = participant_list

    print(participant_list)

    # Create figure
    fig = go.Figure()
    cm = px.colors.qualitative.Plotly
    df = self.df.copy()
    participant_list = self.participant_list
    modality = column_name

    for i, id_participant in enumerate(participant_list):
      df2 = df[df.id_participant==id_participant]
      if modality not in df2.columns:
        df2[modality]=np.nan
      df2 = df2[df2[modality].notna()]
      df2[modality]=1
      width = 1
      
      # Create color map
      color = cm[i%len(cm)]
      
      # Convert color from HEX to rgba(r,g,b,a)
      if len(df2[modality])==0:
        alpha = 0.2
        color_str = color.lstrip("#")
        r = int(color_str[0:2], 16)
        g = int(color_str[2:4], 16)
        b = int(color_str[4:6], 16) 
        rgba_string = f"rgba({r},{g},{b},{alpha})"

        # Plot dashed line
        fig.add_trace(go.Scatter(x=[df2.index[0], df2.index[-1]], y=[i,i],
                                 mode='lines', line=dict(color=rgba_string, dash='dot', width=width)))
      else:
        # Plot solid line
        fig.add_trace(go.Scatter(x=[df2.index[0], df2.index[-1]], y=[i,i], line_color=color,
                                 mode='lines', line=dict(width=width),
                                 marker=dict(size=20)))
        
      # Plot markers
      fig.add_trace(go.Scatter(x=df2.index, y=i*df2[modality], line_color=color, mode='markers'))
      
      # Wrangle with figure
      fig.update_layout(yaxis_range=[-1, len(participant_list)+1])
      fig.update_yaxes(tickvals=list(range(0,len(participant_list))), ticktext=participant_list)
      fig.update_xaxes(title_text='Date')
      fig.update_yaxes(title_text='Participant IDs')
      fig.update_layout(height=100+80*len(participant_list), width=1000, showlegend=False,
                        title_text=f'Event Plot (all participants, {column_name})',
                        title_x = 0.5)

    return fig
    

  def parallel_categories_plot(self, mode='plotly'):
    """
    Function to plot parallel categories plot for all watch survey responses for
    the entire cohort
    
    Arguments
    ----------
    
    Returns
    -------
      - fig, ?, plotly figure object
    """
    df = self.df
    ws_questions = self.ws_questions
    if mode != 'plotly':
      "Only 'Plotly' mode is available for this chart type."
    
    # Keep watch survey responses only
    df = df[df.ws_survey_count.notna()]

    # Wrangle with data
    dimensions = []
    for column_name, question in ws_questions.items():
      # Convert None values to 'N/A' strings
      df[column_name] = df[column_name].replace({None: 'N/A'})

      # Assemble data
      dimensions.append(dict(label = question, values = df[column_name]),)

    # Plot data
    fig = go.Figure(data=go.Parcats(dimensions=dimensions))
    fig.update_layout(width=1500,
                      title_text='Watch survey responses')

    return fig


  def sankey_plot(self, mode='plotly'):
    """
    Function to plot Sankey chart for all watch survey responses for
    the entire cohort
    
    Arguments
    ----------
    
    Returns
    -------
      - fig, ?, plotly figure object
    """
    df = self.df
    ws_questions = self.ws_questions
    if mode != 'plotly':
      "Only 'Plotly' mode is available for this chart type."
    
    # Keep watch survey responses only
    df = df[df.ws_survey_count.notna()]

    # Wrangle with data
    dimensions = []
    for column_name, question in ws_questions.items():
      # Convert None values to 'N/A' strings
      df[column_name] = df[column_name].replace({None: 'N/A'})

      # Assemble data
      dimensions.append(dict(label = question, values = df[column_name]),)

    # Plot data
    fig = go.Figure(data=go.Parcats(dimensions=dimensions))
    fig.update_layout(width=1500,
                      title_text='Watch survey responses')

    return fig

  def map_plot(self, accuracy_enabled=False):
  
    df = self.df.copy()
    df = df[df.ws_survey_count.notna()]
    df['marker_color'] = 'black'
    # Create text for hover
    df["text"] = df['id_participant'] + " "
    df["text"] = df["text"] + df.index[0].strftime('%a, %d.%m.%Y, %H:%M') + "<br>"
    for key in self.ws_questions:
      question = self.ws_questions[key]
      if key not in df.columns:
        continue
      df[key] = df[key].astype(str) # Make sure all values are strings (avoid issues with categorical data)
      df[key] = df[key].fillna('-')
      df["text"] = df["text"] + question + "  " + df[key] +"<br>"

    # Add markers to map
    trace = go.Scattermapbox(lat=df.ws_latitude, 
                             lon=df.ws_longitude,
                             mode='markers',
                             marker=dict(
                                 size=10,
                                 color='rgb(0, 128, 255)',
                                 opacity=0.8),
                             hovertemplate = "",
                             text=df['text'])

    # Define the layout for the map
    layout = go.Layout(
        #title='Scatter Map using Plotly',
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        mapbox=dict(
            style='carto-positron', #'open-street-map',
            center=dict(lat=df.ws_latitude.median(),
                        lon=df.ws_longitude.median()),
            zoom=11,
            ))
    
    fig = go.Figure(data=[trace], layout=layout)
    fig.update_layout(title_text='')
    
    if accuracy_enabled == True:
      # Source: https://stackoverflow.com/questions/68960541/obtain-coordinates-of-a-polygon-multi-polygon-around-a-point-in-python/68963478#68963478
      # need to use UTM to express radius as a distance. UTM is zoned, so if GPS coords are very widely distributed
      # distance will be incorrect.  zone is estimated from first GPS coordinate
      # returns geopandas dataframe re-projected to GPS co-ordinates
      # accuracy/radius is expressed in metres
      def circles(lonlat, accuracy):
        utm_coords = utm.from_latlon(lonlat[:, 1], lonlat[:, 0])
        utmcrs = gpd.GeoDataFrame(geometry=[shapely.geometry.Point(lonlat[0, 0], lonlat[0, 1])], crs="EPSG:4326").estimate_utm_crs()
        return gpd.GeoDataFrame(geometry=[shapely.geometry.Point(easting, northing).buffer(radius) for easting, northing, radius in zip(utm_coords[0], utm_coords[1], accuracy)], crs=utmcrs).to_crs("EPSG:4326")

      # Generate circles for horizontal accuracy
      if 'ws_location_accuracy_horizontal' not in df.columns:
        df['ws_location_accuracy_horizontal'] = np.nan
      gdf = circles(df.loc[:, ["ws_longitude", "ws_latitude"]].values, accuracy=df["ws_location_accuracy_horizontal"])

      fig.update_layout(title_text='',            
                        # Add Circles to map
                        layers= [{"source": json.loads(gdf.geometry.to_json()),
                                  "below": "traces",
                                  "type": "line",
                                  "color": "red",
                                  "line": {"width": 1.5}}],)
    return fig