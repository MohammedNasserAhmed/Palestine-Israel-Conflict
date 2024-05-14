import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from typing import Dict, List
import pandas as pd
from PIL import Image
from pandas.api.types import is_numeric_dtype
import plotly.offline as py
import itertools
from enum import Enum
import pandas as pd
import  matplotlib.pyplot as plt
import random
from utils.func import make_autopct, reset_months

class Choice(Enum):
    Injuries = "Injuries"
    Fatalities = "Fatalities"


class PieChartYs:
    def __init__(self, df, title, variables: List[List[str]],
                 legend_labels: List[str], pie_labels: List[str],
                 images_path: List[str],
                 colors : List[str]=["#820300",'#F4DFC8','#053B50']):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame")
        if not isinstance(title, str):
            raise TypeError("title must be a string")
        if not isinstance(variables, list) or not all(isinstance(pair, list) and len(pair) == 2 for pair in variables):
            raise TypeError("variables must be a list of lists, each with two elements")
        if not isinstance(legend_labels, list) or len(legend_labels) != len(variables):
            raise TypeError("legend labels must be a list, and in same length of variables")
        if not isinstance(pie_labels, list) or len(pie_labels) != len(variables):
            raise TypeError("pie labels must be a list, and in same length of variables")
        if not isinstance(images_path, list) or len(images_path) != len(variables):
            raise TypeError("pie labels must be a list, and in same length of variables")

        lst=[]
        for sublist in variables:
            for val in sublist:
                if val not in df.columns:
                    raise ValueError(f"{val} is not a column in the DataFrame")
                if not is_numeric_dtype(df[val]):
                    raise ValueError(f"df[{val}] must be a numerical column")
                lst.append(val)
        self.df = df
        self.title = title
        self.vars = variables
        self.legend_labels=legend_labels
        self.pie_labels=pie_labels
        self.paths=images_path
        self.colors = colors


    def preprocess_data(self):
        # Use a loop to iterate over self.vars and create a list of dataframes
        dfs = []
        for sublist in self.vars:
            df = pd.DataFrame(self.df[sublist].sum()).reset_index().rename(columns={'index':'group',0:'sum'})
            df['group'] = self.legend_labels
            df = self.remove_zero_rows(df)
            dfs.append(df)
    
        # Calculate totals and row totals
        totals = [df['sum'].sum() for df in dfs]
        row_totals=[]
        for df in dfs :
            row_total = [df[df['group']==label]['sum'].sum() for label in self.legend_labels]
            row_totals.append(row_total)
    
        # Return the results
        return dfs, totals,  list(itertools.chain(*row_totals))


    def remove_zero_rows(self, df: pd.DataFrame):
        """
        Remove rows from a DataFrame where all values are zero.

        Parameters:
        - df: pandas DataFrame
            The DataFrame from which to remove zero rows.

        Returns:
        - pandas DataFrame
            The DataFrame with zero rows removed.
        """
        try:
            return df.loc[~(df == 0).all(axis=1)]
        except Exception as e:
            print(f'An error occurred: {e}')
            return df

    def create_charts(self,df1,df2):
        chart1 = go.Pie(labels=df1['group'], values=df1['sum'], hole=0.6,
                          name=self.pie_labels[0],textinfo='percent', texttemplate='%{percent:.0%}',
                          marker=dict(colors=self.colors[:2]))
        chart2 = go.Pie(labels=df2['group'], values=df2['sum'], hole=0.6,
                          name=self.pie_labels[1],textinfo='percent', texttemplate='%{percent:.0%}',
                          marker=dict(colors=self.colors[:2]))
        return chart1, chart2


    def create_subplot(self, chart1, chart2, rows=1, cols=2):
        """
        Create a subplot with two charts.

        Args:
            chart1 (go.Pie): The first chart to be added to the subplot.
            chart2 (go.Pie): The second chart to be added to the subplot.
            rows (int, optional): The number of rows in the subplot. Defaults to 1.
            cols (int, optional): The number of columns in the subplot. Defaults to 2.

        Returns:
            fig: The created subplot figure.
        """
        if not isinstance(chart1, go.Pie) or not isinstance(chart2, go.Pie):
            raise TypeError("chart1 and chart2 must be instances of go.Pie")
    
        fig = make_subplots(rows=rows, cols=cols, specs=[[{'type':'domain'}]*cols]*rows)
        fig.add_trace(chart1, 1, 1)
        fig.add_trace(chart2, 1, 2)
        return fig

    def update_layout(self, fig, total1, total2,df1row1, df1row2, df2row1, df2row2):
        
        df1perc1="{:,.0f}".format((df1row1/total1)*100)
        
        df1perc2="{:,.0f}".format((df1row2/total1)*100)
        total1="{:,.0f}".format(total1)
        total2="{:,.0f}".format(total2)
        df1row1="{:,.0f}".format(df1row1)
        df1row2="{:,.0f}".format(df1row2)
        X = [0.0, 0.55]
        Y = [1.15, 1.15]
        images= []
        for x, y, path in zip(X, Y, self.paths):
                image = Image.open(path)
                image_obj = go.layout.Image(
                source=image,
                xref="paper", yref="paper",
                x=x, y=y,
                sizex=0.1, sizey=0.1,
                layer="above")
                images.append(image_obj)

        fig.update_layout(images=images,
                          annotations=[dict(text=self.pie_labels[0], x=0.05, y=1.15, font_size=20, showarrow=False, font_color=self.colors[2]),
                                       dict(text=self.pie_labels[1], x=0.64, y=1.15, font_size=20, showarrow=False, font_color=self.colors[2]),
                                       dict(text='<b>{}'.format(total1), x=0.05, y=1.055, font_size=14, showarrow=False, font_color="#B31312"),
                                       dict(text='<b>{}'.format(total2), x=0.63, y=1.055, font_size=14, showarrow=False, font_color="#B31312"),
                                       dict(text=f"<b><i>You'll notice right away that the overwhelming majority of the deaths are Palestinians, and \
  have been for the almost 23 years. <br>Overall, {total1} conflict-related deaths have recorded, of which {df1row1} are Palestinian and {df1row2} Israeli.\
  That means {df1perc1} % of <br>deaths have been Palestinian and only {df1perc2} % Israeli",
                                            x=0.01,
                                            y=-0.30,
                                            showarrow=False,
                                            font=dict(
                                                size=13,
                                                color=f'{self.colors[2]}',

                                            ),
                                            align="left"
                                        ),
                                    
                                       dict(text = "aiNarabic.ai", 

                                            x = -0.1, y=1.5,
                                            showarrow=False,
                                            font=dict(
                                                size=14,
                                                color="lightgray",

                                            ),
                                            
                                            align="left")
                                       ])

        fig.update_layout(
            title={
                    'text': self.title,
                    'x': 0.5,
                    'y': 0.95,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {
                        'color': f'{self.colors[2]}',
                        'size': 24,
                        'family': 'Copper Black'
                
                    }
                },
            uniformtext_minsize=12, uniformtext_mode='hide',
            margin=dict(r=100, l=100, b=100, t=180,pad=0),
            width=1100, height=600
        )

        fig.update_xaxes(matches=None, showticklabels=True, visible=True)
        fig.update_layout(legend=dict(yanchor="top", y=1.35, xanchor="center", x=0.5,font_size=14,
                                      font_color='#5F9EA0', font_family='Rockwell'))

        names = set()
        fig.for_each_trace(
            lambda trace:
            trace.update(showlegend=False)
            if (trace.name in names) else names.add(trace.name))


        customtemplate = go.layout.Template(
            layout=go.Layout(
                paper_bgcolor='#F5F5F5',
                font_family="Rockwell"
            )
        )
        pio.templates['customtemplate'] = customtemplate
        pio.templates.default = 'customtemplate'

        fig.update_traces(textposition='inside')
        fig.update_layout(
            template='customtemplate'
            )
        return fig

    def show_plot(self, save_plot: bool = True, save_filename: str = None):
        """
        Display and save a plot of pie charts.

        Parameters:
        - colors (list): A list of color values for the pie charts. Default is ['#088395','#E55604','#053B50'].
        - save_plot (bool): Whether to save the plot as an HTML file. Default is True.
        """
        dfs, totals, row_totals = self.preprocess_data()
        df1,df2 = dfs
        total1,total2 = totals 
        df1row1,df1row2,df2row1,df2row2 = row_totals 
        chart1, chart2 = self.create_charts(df1,df2)
        fig = self.create_subplot(chart1, chart2)
        fig = self.update_layout(fig, total1, total2,df1row1,df1row2, df2row1, df2row2)
        if save_plot and save_filename is not None:
            py.plot(fig, filename=save_filename)
        fig.show()
        
        
        

         
class PieChartMs:
    def __init__(self, df, choice:Choice, title:str = None, colors : List[str]=['#088395','#E55604','#053B50']):
        """
        Initialize the class with the given parameters.

        Args:
            df (pd.DataFrame): The pandas DataFrame containing the data.
            choice (Choice): The choice value indicating whether to consider 'Injuries' or 'Fatalities'.
            save_filename_without_extension (str, optional): The filename without extension to save the data. Defaults to None.

        Raises:
            TypeError: If df is not a pandas DataFrame or choice is not a valid Choice value.
            ValueError: If df is empty or if it doesn't contain the necessary columns based on the choice value.
            TypeError: If save_filename_without_extension is not a string or None.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        if not isinstance(choice, Choice):
            raise TypeError("Invalid choice value. Allowed values are 'Injuries' and 'Fatalities'.")
        if df.empty:
            raise ValueError("df cannot be empty")
        if choice == Choice.Injuries and not all(col in df.columns for col in ["Palestinians Injuries", "Israelis Injuries"]):
            raise ValueError("Missing necessary columns for choice 'Injuries'")
        if choice == Choice.Fatalities and not all(col in df.columns for col in ["Palestinians Fatalities", "Israelis Fatalities"]):
            raise ValueError("Missing necessary columns for choice 'Fatalities'")
        self.df = df
        self.choice = choice
        self.colors = colors
        if title is None :
            self.title = "<i>Human-Cost of the Palestine-Israel Conflict (2000 - April 2024)</i>"
        else:
            self.title = title
    def preprocess_data(self):
        columns_mapping = {
            "Injuries": ["Palestinians Injuries", "Israelis Injuries"],
            "Fatalities": ["Palestinians Fatalities", "Israelis Fatalities"]
        }
        cols = columns_mapping[self.choice.value]
        df = self.df.groupby(["Year"])[cols].sum().sort_index(ascending=True)
        df = self.remove_zero_rows(df)
        df = df.reset_index()
        return df, cols

    def remove_zero_rows(self, df):
        """
        Remove rows from the DataFrame where all values are zero.

        Args:
            df (pandas.DataFrame): The DataFrame to remove zero rows from.

        Returns:
            pandas.DataFrame: The DataFrame with zero rows removed.
        """
        try:
            return df.loc[~(df == 0).all(axis=1)]
        except Exception as e:
            print(f"Error occurred: {e}")
            return df

    def create_charts(self, df, cols, hole=0.6, textinfo='percent', texttemplate='%{percent:.0%}', sort=False, showlegend=True):
        """
        Create pie charts based on the given dataframe and columns.

        Args:
            df (DataFrame): The dataframe containing the data.
            cols (list): The list of column names to create pie charts for.
            hole (float, optional): The size of the hole in the center of the pie chart. Defaults to 0.6.
            textinfo (str, optional): The type of information to display on the pie chart. Defaults to 'percent'.
            texttemplate (str, optional): The template for displaying the text on the pie chart. Defaults to '%{percent:.0%}'.
            sort (bool, optional): Whether to sort the pie chart. Defaults to False.
            showlegend (bool, optional): Whether to show the legend on the pie chart. Defaults to True.

        Returns:
            list: A list of pie charts.
        """
        charts = []
        for col in cols:
            chart = go.Pie(labels=df['Year'], values=df[col],
                                    hole=hole, name=col, sort=sort ,showlegend=showlegend,
                                    textinfo=textinfo, texttemplate=texttemplate)
            charts.append(chart)

        return charts

    def create_subplot(self, charts, rows=1, cols=2):
        """
        Create a subplot with the given charts.

        Args:
            chart1 (go.Pie): The first chart to add to the subplot.
            chart2 (go.Pie): The second chart to add to the subplot.
            rows (int, optional): The number of rows in the subplot. Defaults to 1.
            cols (int, optional): The number of columns in the subplot. Defaults to 2.

        Returns:
            plotly.graph_objects.Figure: The created subplot.
        """
        try:
            # Create a subplot with the specified number of rows and columns
            fig = make_subplots(rows=rows, cols=cols, specs=[[{'type':'domain'}]*cols]*rows)
            for i, chart in enumerate(charts):
                if not isinstance(chart, go.Pie):
                    raise TypeError("chart1 must be an instance of go.Pie")
                fig.add_trace(chart, 1, i+1)
            return fig
        except Exception as e:
            raise Exception("Failed to create subplot: " + str(e))

    def update_layout(self, fig, title_text=None, title_x=0.435, title_y=0.87, title_xanchor='center', 
                      title_yanchor='top', 
                      title_font_size=24, title_font_family='Arial', 
                      margin_l=50, margin_r=50, margin_b=50, margin_t=200, margin_pad=0, 
                      xaxes_matches=None, xaxes_showticklabels=True, xaxes_visible=True, legend_yanchor="top", 
                      legend_y=1.28, legend_xanchor="center", legend_x=0.485, legend_font_size=14, 
                      legend_font_color='#5F9EA0', legend_font_family='Rockwell', 
                      template_paper_bgcolor='#F0F0F0', template_font_family='Rockwell'):
        """
        Update the layout of the figure.

        Parameters:
        - fig: the figure to update
        - title_text: the text of the title (default: f'{self.choice} per Year')
        - title_x: the x position of the title (default: 0.45)
        - title_y: the y position of the title (default: 0.95)
        - title_xanchor: the x anchor of the title (default: 'center')
        - title_yanchor: the y anchor of the title (default: 'top')
        - title_font_color: the color of the title font (default: '#5F9EA0')
        - title_font_size: the size of the title font (default: 22)
        - title_font_family: the font family of the title (default: 'Arial')
        - annotations: the annotations to add (default: [dict(text='Palestine', x=0.18, y=1.0, font_size=20, showarrow=True, font_color="#C70039"), dict(text='Israel', x=0.75, y=1.0, font_size=20, showarrow=True, font_color='#C70039')])
        - margin_l: the left margin (default: 50)
        - margin_r: the right margin (default: 50)
        - margin_b: the bottom margin (default: 50)
        - margin_t: the top margin (default: 108)
        - margin_pad: the padding of the margins (default: 0)
        - xaxes_matches: the matches property of the x axes (default: None)
        - xaxes_showticklabels: whether to show tick labels on the x axes (default: True)
        - xaxes_visible: whether the x axes are visible (default: True)
        - legend_yanchor: the y anchor of the legend (default: "top")
        - legend_y: the y position of the legend (default: 1.15)
        - legend_xanchor: the x anchor of the legend (default: "center")
        - legend_x: the x position of the legend (default: 0.485)
        - legend_font_size: the size of the legend font (default: 14)
        - legend_font_color: the color of the legend font (default: '#5F9EA0')
        - legend_font_family: the font family of the legend (default: 'Rockwell')
        - template_paper_bgcolor: the background color of the template (default: '#F0F0F0')
        - template_font_family: the font family of the template (default: 'Rockwell')

        Returns:
        - the updated figure
        """
        fig.update_layout(
            title={
                'text': title_text if title_text is not None else f'{self.choice.value} per Year',
                'x': title_x,
                'y': title_y,
                'xanchor': title_xanchor,
                'yanchor': title_yanchor,
                'font': {
                    'color': "#750E21",
                    'size': title_font_size,
                    'family': title_font_family
                }
            },
            margin=dict(
                l=margin_l,
                r=margin_r,
                b=margin_b,
                t=margin_t,
                pad=margin_pad
            ),
            xaxis=dict(matches=xaxes_matches, showticklabels=xaxes_showticklabels, visible=xaxes_visible),
            legend=dict(yanchor=legend_yanchor, y=legend_y, xanchor=legend_xanchor, x=legend_x,
                        font_size=legend_font_size, font_color=legend_font_color, font_family=legend_font_family),
            width=1100, height=600
        )
        customtemplate = go.layout.Template(
            layout=go.Layout(
                paper_bgcolor=template_paper_bgcolor,
                font_family=template_font_family
            )
        )
        fig.update_traces(textfont_size=10,textposition='inside',
                          direction='clockwise', rotation = 45)
        
        pio.templates['customtemplate'] = customtemplate
        pio.templates.default = 'customtemplate'

        fig.update_traces(textposition='inside')
        fig.update_layout(
             annotations =[dict(text = "aiNarabic.ai",
                            x = 0.0, y=1.5,
                            showarrow=False,
                            font=dict(
                                size=14,
                                color="lightgray"

                            ),align="left"),
                           
                           dict(text = self.title,
                                x = 0.5, y=1.5,
                            showarrow=False,
                            font=dict(
                                size=24,
                                color=self.colors[0]

                            ),align="center"),
                           dict(text='Palestine', x=0.18, y=1.0, font_size=20, showarrow=True, font_color=self.colors[2]),
                           dict(text='Israel', x=0.75, y=1.0, font_size=20, showarrow=True, font_color=self.colors[2])],
             
             
            template='customtemplate'
        )
        return fig

    def show_plot(self, save_plot: bool =True, save_filename: str =None):
        """
        Orchestrates the tasks of preprocessing data, creating charts, creating subplots, updating layout, and showing the figure.
        """
        df, cols = self.preprocess_data()
        charts = self.create_charts(df, cols)
        subplot = self.create_subplot(charts)
        layout = self.update_layout(fig = subplot)
        if save_plot and save_filename is not None:
            py.plot(layout, filename=save_filename)
        self.show_figure(layout)

 
    def show_figure(self, fig):
        """
        Shows the figure.
        """
        fig.show()
        
        
def pie_chart_mf(data, csv_features, Project_Path=None):
    """
    Create a pie chart based on the given data.

    Parameters:
    - data: The input data.
    - feature: The feature to be plotted.
    - colors: The colors for the pie chart.
    - key: The key for grouping the data (optional).
    - savefilename: The filename to save the chart as an image file (optional).

    Returns:
    None
    """
   
    monthly_data = data.drop('Year', axis=1).groupby('Month').sum().sort_index(ascending=False)
    monthly_data = reset_months(monthly_data)
    
   
    colors = ['#92C7CF','#AAD7D9','#FBF9F1','#E5E1DA','#DBA979','#ECCA9C','#E8EFCF','#AFD198',
            '#FF407D','#FFCAD4','#FEC7B4','#FC819E','#FFCF96','#F6FDC3','#CDFAD5','#F2AFEF','#C499F3']
    for feature in csv_features:
        values = monthly_data[feature].values
        
        i = random.randint(12, 18)
        j = i - 12
        
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(aspect='equal'))
        wedge_properties = {'linewidth': 1, 'edgecolor': 'white'}
        ax.pie(values, labels=monthly_data.index, colors=colors[j:i], autopct=make_autopct(values), labeldistance=0.8, pctdistance=1.15, shadow=True,
            counterclock=True, wedgeprops=wedge_properties, rotatelabels=True,
            textprops={'fontsize': 7})

        plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.95)
        center_circle = plt.Circle((0, 0), 0.5, fc='white')
        fig.gca().add_artist(center_circle)
        fig.suptitle(f'{feature} per Months (2000- April 2024)')

        # Save the chart as an image file
        if Project_Path is not None:
            savefilename = Project_Path+f'\outputs\{feature.replace(" ", "_")}_per_months.png'
            plt.savefig(savefilename, bbox_inches='tight')

        plt.show()
    
def pie_chart_sf(data, csv_features, Project_Path=None):
    """
    Create a pie chart based on the given data.

    Parameters:
    - data: The input data.
    - feature: The feature to be plotted.
    - colors: The colors for the pie chart.
    - key: The key for grouping the data (optional).
    - savefilename: The filename to save the chart as an image file (optional).

    Returns:
    None
    """
    

    # Create a pie chart
   
    season_map = {
        'JANUARY': 'Winter', 'FEBRUARY': 'Winter', 'MARCH': 'Spring', 'APRIL': 'Spring',
        'MAY': 'Spring', 'JUNE': 'Summer', 'JULY': 'Summer', 'AUGUST': 'Summer',
        'SEPTEMBER': 'Autumn', 'OCTOBER': 'Autumn', 'NOVEMBER': 'Autumn', 'DECEMBER': 'Winter'
    }
    
    # Add a 'Season' column to the DataFrame
    data['Season'] = data['Month'].map(season_map)
    columns = ['Year', 'Season', 'Month', "Palestinians Fatalities","Israelis Fatalities","Palestinians Injuries","Israelis Injuries"]
    data = data[columns]
    seasonly_data = data.drop(['Year','Month'], axis=1).groupby('Season').sum().sort_index(ascending=False)
   
    colors = ['#92C7CF','#AAD7D9','#FBF9F1','#E5E1DA','#DBA979','#ECCA9C','#E8EFCF','#AFD198',
            '#FF407D','#FFCAD4','#FEC7B4','#FC819E','#FFCF96','#F6FDC3','#CDFAD5','#F2AFEF','#C499F3']
    for feature in csv_features:
        values = seasonly_data[feature].values
        i = random.randint(4, 13)
        j = i - 4
        
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(aspect='equal'))
        wedge_properties = {'linewidth': 1, 'edgecolor': 'white'}
        ax.pie(values, labels=seasonly_data.index, colors=colors[j:i], autopct=make_autopct(values), labeldistance=0.6, pctdistance=1.15, shadow=True,
            counterclock=True, wedgeprops=wedge_properties, rotatelabels=True,
            textprops={'fontsize': 7})

        plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.95)
        center_circle = plt.Circle((0, 0), 0.5, fc='white')
        fig.gca().add_artist(center_circle)
        fig.suptitle(f'{feature} per seasons (2000- April 2024)')

        # Save the chart as an image file
        if Project_Path is not None:
            savefilename = Project_Path+f'\outputs\{feature.replace(" ", "_")}_per_seasons.png'
            plt.savefig(savefilename, bbox_inches='tight')

        plt.show()

