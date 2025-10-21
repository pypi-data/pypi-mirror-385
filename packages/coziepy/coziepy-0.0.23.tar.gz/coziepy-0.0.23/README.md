# CoziePy
CoziePy is a Python package to retrieve, process, and plot data from the [Cozie iOS app](https://github.com/cozie-app/cozie-apple/) for human comfort data collection.

## Features

TBD


## Documentation and tutorials

TBD

## Quick start

1. Installation
   ```sh
   pip install coziepy
   ```

 2. Download Cozie data using the web API and CoziePy
    ```python
    from coziepy import Cozie

    cozie = Cozie()

    df = cozie.load(
      id_experiment = "AppStore",
      participant_list = ['participant_01', 'participant_02'],
      timezone = 'Asia/Singapore',
      api_url='https://m7cy76lxmi.execute-api.ap-southeast-1.amazonaws.com/default/cozie-apple-researcher-read-influx', 
      api_key='XXX' # Please reach out to cozie.app@gmail.com for an API_KEY
    ) 
    df.head()
    ```
  
  3. Plot Cozie data using CoziePy
     ```python
     from coziepy import Cozie

     cp = CoziePlot(df=df, ws_questions=ws_questions)
    
     fig = cp.cohort_survey_count_bar(mode='plotly')
     fig.show()
     ```


## Contribute

We would love you for the contribution to our project, check the [`LICENSE`](https://github.com/cozie-app/coziepy/blob/master/LICENSE) file for more info.

