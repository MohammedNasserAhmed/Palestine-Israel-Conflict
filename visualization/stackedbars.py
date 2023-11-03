from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure, output_file
from bokeh.io import curdoc, show
from bokeh.palettes import  Cividis256
import pandas as pd
class StackBar:
    def __init__(self, data, variable : str):
        """
        Initialize the StackBar object.

        Parameters:
        - data: The input data for the stack bar chart.
        - variable: The variable to be plotted on the y-axis.
        """
        if variable not in data.columns:
            raise ValueError(f"Invalid column name: {variable}")
        try:
            self.data = data
            self.var = variable
            self.title=f"{self.var} per Year/Month"
        except Exception as e:
            print(f"Error occurred during initialization: {e}")
       
        
    def reindex_columns(self, df, months, rename_columns=True):
        """
        Reindex the columns of a DataFrame and optionally rename them.

        Args:
            df (DataFrame): The DataFrame to reindex.
            months (list): The list of column names to reindex the DataFrame with.
            rename_columns (bool): Whether to rename the columns or not. Default is True.

        Returns:
            DataFrame: The reindexed DataFrame.

        Raises:
            ValueError: If months does not have exactly 12 elements.

        """
        if df is None or df.empty:
            return df

        if len(months) != 12:
            raise ValueError("months must have exactly 12 elements")

        df = df.reindex(columns=months)

        if rename_columns:
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            rename_dict = {months[i]: month_names[i] for i in range(len(months))}
            df = df.rename(columns=rename_dict)

        return df
    def preprocees_data(self, rename_columns: bool= True):
        """
        Preprocesses the data by aggregating it based on Year and Month.

        Args:
            rename_columns (bool): Whether to rename the columns. Default is True.

        Returns:
            pandas.DataFrame: The preprocessed data.
        """
        # Get unique months
        months = self.data['Month'].unique().tolist()

        # Aggregate data using pivot_table
        data = self.data.pivot_table(index='Year', columns='Month', values=self.var, aggfunc='sum')

        # Reindex columns
        data = self.reindex_columns(data, months, rename_columns=rename_columns)

        # Remove zero rows
        data = self.remove_zero_rows(data)

        return data
    
    def remove_zero_rows(self, data : pd.DataFrame):
        """
        Remove rows from the DataFrame where all values are zero.

        Args:
            data (pd.DataFrame): The input DataFrame.

        Returns:
            pd.DataFrame: The DataFrame with zero rows removed.
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input data must be a pandas DataFrame")
        if data is None or data.empty:
            return data
        try:
            return data.loc[~(data==0).all(axis=1)]
        except Exception as e:
            raise ValueError("Error occurred during removing zero rows: {}".format(e))
    
    def _create_data_dict(self, data):
        """
        Create a dictionary from the input data.

        Args:
            data (pd.DataFrame): The input data.

        Returns:
            dict: The created dictionary.
        """
        years_dict = {'years': [str(v) for v in data.index.tolist()], 
                      **{month: list(data[month]) for month in data.columns}}
        return years_dict

    def draw_chart(self, p, months,source, max_value,colors, 
                   output_file_name="stackedbar.html", theme='contrast'):
        """
        Draw a stacked bar chart.

        Parameters:
        - p: the figure object
        - months: a list of month names
        - colors: a list of colors for each month (default: Cividis256[::21])
        - source: the data source for the chart
        - max_value: the maximum value for the y-axis
        - output_file_name: the name of the output file (default: "stackedbar.html")
        - theme: the theme for the chart (default: 'contrast')
        
        """
        renderers = p.vbar_stack(months, x='years', width=0.7, color=colors, source=source,
                                      legend_label=months, name=months)

        for r in renderers:
            hover = HoverTool(tooltips=[
                ("Month", "$name"),
                ("Year", "@years"),
                ('Count', "@$name"),
            ],
            renderers=[r])
            p.add_tools(hover)
        #self.p.add_tools(BoxSelectTool(dimensions="width"))
        p.y_range.end = max_value + max_value//3
        p.y_range.start = 1
        p.x_range.range_padding = 0.1
        p.xgrid.grid_line_color = None
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        p.background_fill_color = "#D0D4CA"
        p.title.text = self.title
        p.title.text_font_size = "16pt"
        p.title.text_color = colors[0]
        p.title.background_fill_color = "white"
        p.title.text_line_height = 20
        p.title.align = "center"
        p.xaxis.major_label_orientation = 45
        p.xaxis.axis_label="Year"
        p.xaxis.axis_label_text_color=colors[0]
        p.xaxis.axis_label_text_font_size="14px"
        p.xaxis.major_label_text_color = colors[6]
        p.xaxis.major_label_text_font_size="10px"
        p.xaxis.axis_line_color="white"
        p.xaxis.axis_line_width=1
        p.yaxis.major_label_orientation = 45
        p.yaxis.axis_label="Count"
        p.yaxis.axis_label_text_color=colors[0]
        p.yaxis.axis_label_text_font_size="14px"
        p.yaxis.major_label_text_color = colors[6]
        p.yaxis.major_label_text_font_size="10px"
        p.yaxis.axis_line_color="white"
        p.yaxis.axis_line_width=1

        output_file(output_file_name)
        curdoc().theme = theme
        show(p)
       
   
    def show_plot(self, height=500, width=1100, color_palette=None, theme='contrast', output_file_name="stackedbar.html"):
        """
        Show the plot with the specified parameters.

        Parameters:
        - height (int): The height of the figure. Default is 500.
        - width (int): The width of the figure. Default is 1100.
        - color_palette (list): The color palette to use for the plot. Default is None.
        - theme (str): The theme to use for the plot. Default is 'contrast'.
        - output_file_name (str): The name of the output file. Default is 'stackedbar.html'.
        """
        data = self.preprocees_data()
        months = list(data.columns)
        years = [str(e) for e in data.index.tolist()]
        source = ColumnDataSource(data=self._create_data_dict(data))
    
        if color_palette is None:
            colors = Cividis256[::21][0:len(months)]
        else:
            colors = color_palette[0:len(months)]
    
        max_value = data.loc[data.sum(axis=1).idxmax()].sum()

        p = figure(x_range=years, height=height, width=width,
                   toolbar_location="right",  tools="save,hover,pan,lasso_select,box_select", 
                   active_drag="lasso_select", tooltips="$name @months: @$name")
    
        self.draw_chart(p, months, source, max_value, colors, theme=theme, output_file_name=output_file_name)
        


if __name__ == "__main__":
    # Assuming data is your DataFrame
    data = pd.read_csv("E:\MyOnlineCourses\ML_Projects\palestine_israel_conflict\data\ps_il.csv")
    assert 'data' in globals(), "data is not defined"
    stackbar = StackBar(data, "Palestinians Killed")
    stackbar.show_plot()

