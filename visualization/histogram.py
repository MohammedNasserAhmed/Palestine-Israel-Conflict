import pandas as pd
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



class ScatterPlot(BaseModel):
    df: List[dict] = Field(..., description="Input data should be a dictionary")
    var: str =  Field(..., description="Input variable should be a string and a column in data")

    @validator('df')
    def validate_df(cls, df):
        if not isinstance(df, list):
            raise ValueError('df must be a ditionary')
        return df

    @validator('var')
    def validate_var(cls, var):
        if not isinstance(var, str):
            raise ValueError('var must be a string')
        return var

    def plot_scatter(self):
        self.df=pd.DataFrame(self.df)
        logging.info('Starting to plot scatter')
        fig = px.scatter(self.df, x=self.df.index, y=self.var, 
                         color=self.var, size_max=40,size=self.df[self.var],
                          color_continuous_scale='Turbid', hover_data=[self.var],
                          )
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

# Usage


# Create an instance of the DataVisualizer class
data = pd.read_csv("E:\MyOnlineCourses\ML_Projects\palestine_israel_conflict\data\ps_il.csv")
data=data.to_dict(orient="records")
scatter_plot = ScatterPlot(df=data, var="Israelis Injuries")
scatter_plot.plot_scatter()