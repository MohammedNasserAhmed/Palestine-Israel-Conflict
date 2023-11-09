import plotly.io as pio
import pandas as pd
import plotly.graph_objects as go
import math
import time
import plotly.express as px
from typing import List 
from pydantic import BaseModel, validator, Field
import matplotlib.pyplot as plt
import logging


class Histogram:
    def __init__(self, data: pd.DataFrame, variable: str, colors: List[str] = ["#BCA37F", "#113946", '#053B50']):
        """
        Initialize the Histogram class.

        Parameters:
        - data (pd.DataFrame): The input data for creating the histogram.
        - variable (str): The variable to be plotted on the y-axis of the histogram.
        - colors (List[str]): The list of colors to be used for the histogram bars.

        Raises:
        - TypeError: If data is not a pandas DataFrame.
        - ValueError: If data is empty or contains NaN values.
        - TypeError: If colors is not a list.
        - ValueError: If colors has less than 2 elements.
        - ValueError: If any element in colors is not a string.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")
        if data.empty:
            raise ValueError("Data cannot be empty")
        if data.isnull().values.any():
            raise ValueError("Data contains NaN values")

        self.data = data
        if not isinstance(variable, str):
            raise TypeError("Variable Input should be a string")
        self.variable = variable
        if not isinstance(colors, list):
            raise TypeError("Colors must be a list")
        if len(colors) < 2:
            raise ValueError("Colors must have at least 2 elements")
        if not all(isinstance(color, str) for color in colors):
            raise ValueError("All elements in colors must be strings")

        self.colors = colors

    def create_histogram(self, width, height):
        """
        Create a histogram plot using Plotly Express.

        Raises:
        - IndexError: If self.colors has less than 2 elements.
        """
        columns = ["Year", self.variable, "Group"]
        if len(self.colors) >= 2:
            color_discrete_sequence = self.colors[:2]
        else:
            color_discrete_sequence = self.colors
        fig = px.histogram(data_frame=self.data[columns], x="Year", y=self.variable, color="Group",
                           hover_data=columns, color_discrete_sequence=color_discrete_sequence)

        fig.update_layout(
            
            title={
                'text': self.variable,
                'font': {
                    'size': 24,
                    'color': self.colors[2],
                    'family': 'bold'
                },
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis=dict(
                title={
                    'font': {
                        'size': 18,
                        'color': self.colors[2],
                        'family': 'bold'
                    }
                },
                gridcolor='#F1EFEF',
                gridwidth=3,
                tickangle=-45,
                automargin=True
            ),
            yaxis=dict(
                title={
                    'font': {
                        'size': 18,
                        'color': self.colors[2],
                        'family': 'bold'
                    }
                },
                gridcolor='#F1EFEF',
                gridwidth=3,
                tickangle=-45,
                automargin=True
            ),
            paper_bgcolor='#F1EFEF',
            plot_bgcolor='white',
            width=width,
            height=height
        )
        return fig

    def show(self, width: int = 1000, height: int = 500):
        """
        Show the histogram plot.

        Parameters:
        - width (int): The width of the histogram plot.
        - height (int): The height of the histogram plot.
        """
        fig = self.create_histogram(width, height)
        fig.show()



class PXScatter(BaseModel):
    df: List[dict] = Field(..., description="Input data should be a dictionary")
    var: str =  Field(..., description="Input variable should be a string and a column in data")

    @validator('df')
    def validate_df(cls, df):
        if not isinstance(df, list):
            raise ValueError('df must be a dictionary')
        for item in df:
            if not isinstance(item, dict):
                raise ValueError('Each item in df must be a dictionary')
        df = pd.DataFrame(df)
        return df

    @classmethod
    @validator('var')
    def validate_var(cls, var: str, df: pd.DataFrame)-> str:
        """
        Validates the input variable.

        Args:
            var (str): The input variable to be validated.

        Returns:
            str: The validated input variable.

        Raises:
            TypeError: If the input variable is not a string.
            KeyError: If the input variable is not a column in the dataframe.
        """
        if not isinstance(var, str):
            raise TypeError('The input variable must be a string.')
        if var not in df.columns:
            raise KeyError('The input variable must be a column in the dataframe.')
        return var

    def log_execution_time(func):
        def wrapper(*args, **kwargs):
            logging.info(f'Starting to execute {func.__name__}')
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logging.info(f'Finished executing {func.__name__} in {execution_time} seconds')
            return result
        return wrapper

    @log_execution_time
    def plot_scatter(self):
        try:
            logging.info('Starting to plot scatter')
            
            config = {
                'x': self.df.index,
                'y': self.var,
                'color': self.var,
                'size_max': 40,
                'size': self.df[self.var],
                'color_continuous_scale': 'Turbid',
                'hover_data': [self.var]
            }
            
            fig = px.scatter(self.df, **config)
            
            fig.update_xaxes(title_text='', tickfont=dict(size=8, color='#414A4C'))
            fig.update_yaxes(title_text=self.var, tickfont=dict(size=8, color='#414A4C'))
        
            # Customize the colorbar
            fig.update_coloraxes(colorbar=dict(tickfont=dict(size=8, color='#414A4C')))
        
            # Customize the title
            fig.update_layout(
                title_text=self.var, 
                title_font=dict(size=14, 
                                color='#0039A6'),
                title_x = 0.5,
                width=800,  # Set the width of the figure
                height=400
            )
            fig.show()
            logging.info('Finished plotting scatter')
        except Exception as e:
            logging.error(f'Error plotting scatter: {str(e)}')
            raise

class Bubbles:
    def __init__(self, data, colors, required_columns=['Year', 'Month', 'Deaths', 'Injuries', 'Group']):
        """
        Initialize the class with data, colors, and optional required columns.

        Args:
            data (pd.DataFrame): The input data as a pandas DataFrame.
            colors (list): The list of colors.
            required_columns (list, optional): The list of required columns. Defaults to ['Year', 'Month', 'Deaths', 'Injuries', 'Group'].
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")
        if data.empty:
            raise ValueError("Data cannot be empty")
        if data.isnull().values.any():
            raise ValueError("Data contains NaN values")

        self.data = data

        if not isinstance(colors, list):
            raise TypeError("Colors must be a list")
        if len(colors) < 2:
            raise ValueError("Colors must have at least 2 elements")
        if not all(isinstance(color, str) for color in colors):
            raise ValueError("All elements in colors must be strings")

        self.colors = colors or  ['#088395','#E55604','#053B50']

        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Data is missing the following required columns: {', '.join(missing_columns)}")
    
        self.create_text_and_sizes()
    def create_text_and_sizes(self):
        """
        Create text and size columns
        """
        self.data['text'] = self.data.apply(lambda row: ('Year: {year}<br>'+
                                                         'Month: {month}<br>'+
                                                         'Deaths: {deaths}<br>'+
                                                         'Injuries: {injuries}<br>').format(year=row['Year'],
                                                                                            month=row['Month'],
                                                                                            deaths=row['Deaths'],
                                                                                            injuries=row['Injuries']), axis=1)
        self.data['size'] = self.data['Injuries'].apply(math.sqrt)

    def create_figure(self):
        """
        Create a scatter plot from the DataFrame
        """
        max_size = max(self.data['size'])
        sizeref = 2. * max_size / (100 * 50)

        # Dictionary with dataframes for each group
        groups = self.data['Group'].value_counts().index.tolist()
        groups_data = {group: self.data[self.data['Group'] == group] for group in groups}

        fig = go.Figure()

        fig.add_traces([go.Scatter(
            x=group['Deaths'], y=group['Injuries'],
            name=group_name, text=group['text'],
            marker_size=group['size'],
            marker_color=self.colors[2] if group_name == 'Israel' else self.colors[1]
        ) for group_name, group in groups_data.items()])

        # Tune marker appearance and layout
        fig.update_traces(mode='markers', marker=dict(sizemode='area',
                                                      sizeref=sizeref, line_width=0.5))
        fig.update_xaxes(showline=False, overwrite=False)

        fig.update_layout(
            title={
                'text': 'Deaths v. Injuries',
                'font': {
                    'size': 24,
                    'color': self.colors[2],
                    'family': 'bold'
                },
                'x': 0.5,
                'y': 0.9,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis=dict(
                title={
                    'text': 'Deaths',
                    'font': {
                        'size': 18,
                        'color': self.colors[2],
                        'family': 'bold'
                        # 'Courier New, monospace'
                    }
                },
                gridcolor='#F1EFEF',
                type='log',
                gridwidth=3,
                tickangle=-45  # Rotate tick labels by -45 degrees
            ),
            yaxis=dict(
                title={
                    'text': 'Injuries',
                    'font': {
                        'size': 18,
                        'color': self.colors[2],
                        'family': 'bold'
                    }
                },
                gridcolor='#F1EFEF',
                gridwidth=3,
                tickangle=-45
            ),

            paper_bgcolor='#F1EFEF',
            plot_bgcolor='white',

            width=1000,
            height=500  #

        )

        return fig

    def show(self, filename='bubblechart.html', save=True):
        """
        Display the plot
        Args:
            filename (str, optional): The filename for the plot. Defaults to 'bubblechart.html'.
        """

        fig = self.create_figure()
        if fig is None:
            raise ValueError("Failed to create the plot")
        if not isinstance(filename, str) or not filename.endswith('.html'):
            raise ValueError("Invalid filename. Filename must be a string and end with '.html'")
        if save:
            pio.write_html(fig, file=filename)
        fig.show()


data = pd.read_csv("E:\MyOnlineCourses\ML_Projects\palestine_israel_conflict\data\ps_il.csv")
data=data.to_dict(orient="records")
scatter_plot = PXScatter(df=data, var="Israelis Injuries")
scatter_plot.plot_scatter()