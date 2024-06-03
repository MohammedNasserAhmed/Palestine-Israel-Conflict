import logging
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure, output_file
from bokeh.io import curdoc, show, output_notebook
from bokeh.palettes import  Cividis256
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.patches as patches
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from typing import List, Tuple
from pydantic import BaseModel, Field, validator
from matplotlib.lines import Line2D
import yaml
from pathlib import Path


class StackBar:
    def __init__(self, data, variable : str, save_filename : str = None):
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
            self.save_filename = save_filename
            self.title=f"{self.var} per Year/Month"
        except Exception as e:
            print(f"Error occurred during initialization: {e}")
       
        
    def reindex_columns(self, df, rename_columns=True):
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

        months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']

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
        # Aggregate data using pivot_table
        data = self.data.pivot_table(index='Year', columns='Month', values=self.var, aggfunc='sum')

        # Reindex columns
        data = self.reindex_columns(data, rename_columns=rename_columns)

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
                   theme='contrast'):
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
        p.y_range.end = max_value + max_value//8
        p.y_range.start = 1
        p.x_range.range_padding = 0.1
        p.xgrid.grid_line_color = None
        p.axis.minor_tick_line_color = "red"
        p.outline_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        p.legend.label_text_font_size = "8pt"  # Adjust label font size
        p.legend.title_text_font_size = "8pt"  # Adjust title font size (optional)
        p.legend.title_text_font_style = "bold" 
        p.legend.margin=0
        p.legend.padding=3
        p.legend.glyph_height =12
        p.background_fill_color = "#D0D4CA"
        p.title.text = self.title
        p.title.text_font_size = "15pt"
        p.title.text_color = colors[0]
        p.title.background_fill_color = "white"
        p.title.text_line_height = 20
        p.title.align = "center"
        p.xaxis.major_label_orientation = 45
        p.xaxis.axis_label="Year"
        p.xaxis.axis_label_text_color=colors[0]
        p.xaxis.axis_label_text_font = "Rockwell"
        p.xaxis.axis_label_text_font_size="14px"
        p.xaxis.major_label_text_color = colors[6]
        p.xaxis.major_label_text_font_size="10.5px"
        p.xaxis.axis_line_color="white"
        p.xaxis.axis_line_width=1
        if self.var.find("Fatalities") != -1: 
            p.yaxis.axis_label="Fatalities"
            
        else :
            p.yaxis.axis_label="Injuries"
        p.yaxis.major_label_orientation = 45
        p.yaxis.axis_label_text_color=colors[0]
        p.yaxis.axis_label_text_font_size="14px"
        p.yaxis.axis_label_text_font = "Rockwell"
        p.yaxis.major_label_text_color = colors[6]
        p.yaxis.major_label_text_font_size="10px"
        p.yaxis.axis_line_color="white"
        p.yaxis.axis_line_width=1
        if self.save_filename is not None:
            output_file(self.save_filename)
        output_notebook()
        curdoc().theme = theme
        show(p)
       
   
    def show_plot(self, height=500, width=1100, color_palette=None, theme='contrast'):
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
    
        self.draw_chart(p, months, source, max_value, colors, theme=theme)


class Bar:
    def __init__(self, df, var = "Year", y_label="Palestinians Fatalities", y_rotate=90, figwidth=15,
                 figheight=6, colors=None, legend_labels=None):
        """
        Initialize the class instance.

        Parameters:
        - df: pandas DataFrame
            The dataframe containing the data.
        - var: str
            The variable to group data.
        - y_label: str, optional
            The variale to be plotted.
        - y_rotate: int, optional
            The rotation angle for the y-axis labels.
        - figwidth: int, optional
            The width of the figure.
        - figheight: int, optional
            The height of the figure.
        - colors: list, optional
            The colors to be used for the plot.
        - legend_labels: list, optional
            The labels for the plot legend.

        Raises:
        - TypeError: If df is not a pandas DataFrame or var is not a string.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        if not isinstance(var, str):
            raise TypeError("var must be a string")
    
        self.df = df.copy()
        self.var = var
        self.y_label = y_label
        if self.y_label.split()[1] == "Fatalities": 
            self.label = "Fatalities"
            self.title = f"{self.y_label.split()[0]} {self.label} / Year"
        else:
            self.label = "Injuries"
            self.title = f"{self.y_label.split()[0]} {self.label} / Year"
        self.y_rotate = y_rotate
        self.figwidth = figwidth
        self.figheight = figheight
        self.colors = colors or ["#113946","#BCA37F","#001524","#C70039"]
        self.labels = legend_labels or ["Greater than Average","Less than or equal to Average"]

    def validate(self):
        if not (4 < self.figheight < 8):
            raise ValueError("figsize height must be greater than 4 inch and less than 7 inch")
        if not (13 < self.figwidth < 16):
            raise ValueError("figsize width must be greater than 9 inch and less than 13 inch")

    def plot(self, save_filename : str = None):
        self.validate()
        counts = self.df.groupby(self.var)[self.y_label].sum().sort_index(ascending=True)
        average = counts.mean()
        bc = ["#113946","#BCA37F"]
        colors = list(map(lambda v: bc[1] if v <= average else bc[0], counts))
   
        fsize = self.figwidth
        fig = self.create_figure(fsize)
        ax = self.create_bar_plot(counts, colors)
        self.set_labels(fig, ax, average, fsize)
        self.annotate_bars(ax, counts, fsize)
        self.create_legend(fig, ax)
        self.add_arrows(fig, fsize)
        self.save_and_show_figure(save_filename)

    def create_bar_plot(self, counts, colors):
        return counts.plot(kind='bar', color=colors, alpha=0.9, 
                    width=0.5, edgecolor='w', linewidth=0.5, 
                    align='center')

    def create_figure(self,fsize):
        fig = plt.figure(figsize=(self.figwidth, self.figheight), layout="constrained")
        fig.suptitle(self.title, fontsize=fsize+1, color=self.colors[2])
        plt.style.use({'axes.facecolor': "#EEEEEE",
                'figure.facecolor': "#F5F5F5"})
        return fig

    def set_labels(self, fig, ax, average, fsize):
        for spine in ax.spines.values():
            spine.set_linewidth(0)
        ax.set_ylabel(self.label, fontsize=fsize-4, rotation=self.y_rotate, labelpad=30, color=self.colors[2])
        ax.set_xlabel(self.var, fontsize=fsize-4, rotation=360, labelpad=30, color=self.colors[2])
        ax.tick_params(axis='x', colors='#414A4C', rotation=45, length=1, width=1, labelsize=fsize-7)
        ax.tick_params(axis='y', colors='#414A4C', rotation=45, length=1, width=1, labelsize=fsize-7)
        fig.text(0.87, 0.96,f"Average of {self.y_label.split()[0]} {self.label} yearly : {round(average)}", 
                    color=self.colors[3], fontweight='bold', fontsize=fsize-6, 
                    va='center', ha="center")
        fig.text(0.92,0.05,"ainarabic.ai",
                    color="gray", fontsize=fsize-6, 
                    verticalalignment='top')

    def annotate_bars(self, ax, counts, fsize):
        for i, v in enumerate(counts):
            ax.text(i, v, str(v), ha='center', va='bottom',
                    fontsize=fsize-9,fontweight='bold', 
                    color="#113946") 

    def create_legend(self,fig, ax):
        bc = self.colors
        
        ax.scatter([], [], color=bc[0], marker='s')
        ax.scatter([], [], color=bc[1], marker='s')
        leg = fig.legend(self.labels,loc="upper left",  
                         fancybox=True, ncol=2, labelspacing=1.5, framealpha=1, shadow=True, 
                         borderpad=1, frameon=True, edgecolor='black', facecolor='#FFFAF0')
        for label in leg.get_texts():
            label.set_fontsize(7)  # Replace 'fontsize' with your desired size

        # Adjust legend box size (optional)
        leg.set_bbox_to_anchor((0.072, 1.015)) 
        leg.get_frame().set_linewidth(0)

    def add_arrows(self, fig, fsize):
        ec= "none"
        txt = "     "
        bbox_props_shadows = dict(boxstyle="rarrow", fc=self.colors[2], ec=ec, lw=1,
                          path_effects=[pe.withStroke(linewidth=0)])
        bbox_props = dict(boxstyle="rarrow", fc="#F5F5F5", ec=ec, lw=1, 
                          path_effects=[pe.withStroke(linewidth=0)])
        x = 0.43
        shadow = 0.0015
        num_arrows = 4
        for i in range(num_arrows):
            fig.text(x, 0.8, txt, ha="center", va="center", rotation=90,
                    size=fsize-3,bbox=bbox_props, zorder=1)
            fig.text(x-shadow, 0.8, txt, ha="center", va="center", rotation=90,
                    size=fsize-3,bbox=bbox_props_shadows, zorder=0)
            x = x + 0.05
        
    def save_and_show_figure(self, save_filename):
        if save_filename is not None : 
            plt.savefig(save_filename)
        plt.show()




class CustomBar(BaseModel):
    data: pd.DataFrame = Field(..., description="Input data should be a dataframe")
    title: str = Field(..., description="Title Input should be a string")
    box_title: str = Field("TOTAL fatalities and injuries\n           2000 - 2024", description="Left Box title input must be a string")
    gv: str = Field("Year", description="The variable to group data should be in a string dtype")
    cols: List[Tuple[str,str]] = Field([("Palestinians Injuries","Palestinians Fatalities"),("Israelis Injuries","Israelis Fatalities")], description="Columns should be a list of tuples")
    img_lbls: List[Tuple[str,str]] = Field( [("Palestinians","Israelis")], description="Images labels should be a list with a single tuple")
    lgd_lbls: List[Tuple[str,str]] = Field( [("Injuries","Fatalities")], description="Legend labels should be a list with a single tuple")
    img_paths: List[str] = Field([Path("pic\picviz\images\ps_h.png"),Path("pic\picviz\images\il_h.png"),
                                  Path("pic\picviz\images\ps_h.png"),Path("pic\picviz\images\il_h.png")], 
                                  description="Images paths should be a list of exactly four paths")
    map_img: str = Field(Path("pic\picviz\images\pmap.png"), description="Map Image path input must be a string")
    
    legend_config_path: str = Field(Path(r"pic\picviz\utils\legend_config.yaml"), description="Path to legend config yaml")
    
    @validator('data')
    def validate_dataframe(cls, data):
         if not isinstance(data, pd.DataFrame):
             raise ValueError(f'Input data should be a list of dictionaries. Got {type(data).__name__} instead.')
         return data.to_dict(orient='records')
    
    class Config:
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "dataframe": [
                    {"group_var": "A", "Column1": 1, "Column2": 6, "Column3": 7, "Column4": 12},
                    {"group_var": "B", "Column1": 2, "Column2": 5, "Column3": 8, "Column4": 11},
                    {"group_var": "C", "Column1": 3, "Column2": 4, "Column3": 9, "Column4": 10},
                    {"group_var": "A", "Column1": 4, "Column2": 3, "Column3": 10, "Column4": 9},
                    {"group_var": "B", "Column1": 5, "Column2": 2, "Column3": 11, "Column4": 8},
                    {"group_var": "C", "Column1": 6, "Column2": 1, "Column3": 12, "Column4": 7}
                ],
                "title": "Title",
                "box_title": "Box Title",
                "group_var": "group_var",
                "columns": [("Column1", "Column2"), ("Column3", "Column4")],
                "img_lbls": [("Image Label1", "Image Label2")],
                "legend_lbls": [("Legend Label1", "Legend Label2")],
                "img_paths": ["path1", "path2", "path3", "path4"],
                "map_img": "Map Image",
                "legend_config_path":"Legend Config Yaml"
                
            }
        }
    def clean_data(self):
        """
        Clean and preprocess the input data.

        Returns:
            float: The maximum value from the relevant columns.
        """
        self.data = pd.DataFrame(self.data)
        self.data = self.data.groupby(self.gv).sum().reset_index()

        relevant_columns = [element for tuple in self.cols for element in tuple]
        self.data[relevant_columns] = self.data[relevant_columns].fillna(0)
        max_value = self.data[relevant_columns].max().max()

        return max_value

    def compute_statistics(self):
        """
        Compute statistics based on the input data.

        Returns:
            Tuple: A tuple containing the grouped data and the total values for each column.
        """
        (v1, v2),(v3, v4) = self.cols
        total1 = self.data[v1].sum()
        total2 = self.data[v2].sum()
        total3 = self.data[v3].sum()
        total4 = self.data[v4].sum()
        grouped = self.data[self.gv].unique().tolist()
        return grouped, total1, total2, total3, total4

    def create_plot(self):
        """
        Create a new plot for visualization.

        Returns:
            Tuple: A tuple containing the figure and axis objects.
        """
        plt.style.use('fivethirtyeight')
        fig, ax = plt.subplots(figsize=(14, 12))
        logging.info("Plot created")
        return fig, ax

    def draw_plot(self, ax, grouped, total1, total2, total3, total4, max_value):
        """
        Draw the customized bar plot.

        Args:
            ax: The axis object to draw the plot on.
            grouped: The grouped data.
            total1: The total value for column 1.
            total2: The total value for column 2.
            total3: The total value for column 3.
            total4: The total value for column 4.
            max_value: The maximum value from the relevant columns.
        """
        ax.set_xlim(0, max_value+(max_value//2))
        ax.set_ylim(0, 100)
        axx= max_value+(max_value//8)
        axy= max_value+(max_value//5)
        ax.axvline(x=axx,ymin=0, ymax=0.7885, color='#3D0C11', linestyle='-',linewidth=1)
        ax.axvline(x=axy, ymin=0, ymax=0.7885,color='#3D0C11', linestyle='-', linewidth=1)
        height = 2.5
        y = 3
        for _,val in enumerate(grouped):
          fontsize = 10
          #========== Palestinians Injuries============
          v00 = self.data[self.data[self.gv]==val][self.cols[0][0]].values[0]

          #========== Israelis Injuries============
          v01 = self.data[self.data[self.gv]==val][self.cols[0][1]].values[0]

          #========== Palestinians Injuries============
          v10 = self.data[self.data[self.gv]==val][self.cols[1][0]].values[0]

          #========== Israelis Killed============
          v11 = self.data[self.data[self.gv]==val][self.cols[1][1]].values[0]

          #========================= Palestinians =======================
          if v00 == 0:
            v00x=axx
          else:
            v00x = axx-v00
          if v01 == 0:
            v01x=axx
          else:
            v01x = axx-v01
          if v00 > v01:
            xmn = v00x
          else :
            xmn = v01x
          if v00+v01 >10000:
            ax.text(xmn-(0.068*axx), y+height/2, '{:,.0f}'.format(v00+v01), fontsize=fontsize, verticalalignment='center', color='black')
          elif v00+v01 >1000:
            ax.text(xmn-(0.057*axx), y+height/2, '{:,.0f}'.format(v00+v01), fontsize=fontsize, verticalalignment='center', color='black')
          elif v00+v01 <100:
            ax.text(xmn-(0.032*axx), y+height/2, '{:,.0f}'.format(v00+v01), fontsize=fontsize, verticalalignment='center', color='black')
          else:
            ax.text(xmn-(0.43*axx), y+height/2, '{:,.0f}'.format(v00+v01), fontsize=fontsize, verticalalignment='center', color='black')

          width = axx-v00x
          rect = patches.Rectangle((v00x-(0.005*axx), y), width, height, linewidth=1, edgecolor='#D80032', facecolor='#CD1818')
          ax.add_patch(rect)
          width = axx-v01x
          rect = patches.Rectangle((v01x-(0.005*axx), y), width+(0.005*axx), height, linewidth=1, edgecolor='#3D0C11', facecolor='#3D0C11')
          ax.add_patch(rect)
          ax.text(axx+350, y+height/2, str(val), fontsize=12, verticalalignment='center', color='#7D7C7C')

          #=================== iIsraelis ========================
          if v10 == 0:
            v10x=axy
          else:
            v10x = axy+v10
          if v11 == 0:
            v11x=axy
          else:
            v11x = axy+v11
          if v10 > v11:
            xmn = v10x
          else :
            xmn = v11x
          if v10+v11 >10000:
            ax.text(xmn+(0.01*axx), y+height/2, '{:,.0f}'.format(v10+v11), fontsize=fontsize, verticalalignment='center', color='black')
          elif v10+v11 >1000:
            ax.text(xmn+(0.01*axx), y+height/2, '{:,.0f}'.format(v10+v11), fontsize=fontsize, verticalalignment='center', color='black')
          elif v10+v11 <100:
            ax.text(xmn+(0.01*axx), y+height/2, '{:,.0f}'.format(v10+v11), fontsize=fontsize, verticalalignment='center', color='black')
          else:
            ax.text(xmn+(0.01*axx), y+height/2, '{:,.0f}'.format(v10+v11), fontsize=fontsize, verticalalignment='center', color='black')

          width = v10
          rect = patches.Rectangle((v10x-v10, y), width+(0.0025*axx), height, linewidth=1, edgecolor='#D80032', facecolor='#CD1818')
          ax.add_patch(rect)
          width=v11
          rect = patches.Rectangle((v11x-v11, y), width+(0.0025*axx), height, linewidth=1, edgecolor='#3D0C11', facecolor='#3D0C11')
          ax.add_patch(rect)
          y+=3.2
       #================== flags ================

        X = [0.985*axx, 1.085*axx, 0.16*axx, 0.16*axx]
        Y = [84.5, 84.5, 27, 20]

        def getImage(path, zoom = .07):
          return OffsetImage(plt.imread(path, format="png"), zoom=zoom)
        for x, y, path in zip(X, Y, self.img_paths):
          ab = AnnotationBbox(getImage(path), (x, y), frameon=False)
          ax.add_artist(ab)

        ax.text(0.83*axx, 84.5, self.img_lbls[0][0], fontsize=14, verticalalignment='center', color='black')
        ax.text(1.115*axx, 84.5, self.img_lbls[0][1], fontsize=14, verticalalignment='center', color='black')
        
        
        #===total deaths and injuries===
        rect = patches.Rectangle((0.11*axx, 17), 0.27*axx, 20, linewidth=1, edgecolor='none', facecolor='none')
        ax.add_patch(rect)
        rect = patches.Rectangle((0.11*axx, 32.1), 0.27*axx, 5, linewidth=1, edgecolor='none', facecolor='gray')
        ax.add_patch(rect)
        ax.text(0.19*axx, 28, '{:,.0f}'.format(int(total1)), fontsize=10.5, verticalalignment='center',fontweight='bold', color='#3D0C11')
        ax.text(0.19*axx, 26, '{:,.0f}'.format(int(total2)), fontsize=9.5, verticalalignment='center',fontweight='bold', color='#CD1818')
        ax.text(0.19*axx, 21, '{:,.0f}'.format(int(total3)), fontsize=10.5, verticalalignment='center', fontweight='bold', color='#3D0C11')
        ax.text(0.19*axx, 19, '{:,.0f}'.format(int(total4)),fontsize=10, verticalalignment='center', fontweight='bold',  color='#CD1818')
        ax.text(0.125*axx, 34.5,self.box_title , fontsize=10, verticalalignment='center',fontweight='bold', color='w')

        rect = patches.Rectangle((0.11*axx, 32), 5300, 0.3, linewidth=1, facecolor='#352F44')
        ax.add_patch(rect)

        #================= AnnotationBox Background ====================
        # Display the image as the background of the plot
        try:
            img = mpimg.imread(self.map_img)
        except FileNotFoundError:
            logging.error("Map image file not found.")
            return
        ax.imshow(img, extent=[0.29*axx, 0.38*axx, 14, 32], aspect='auto',cmap='gray')

        # ====================== Title and signature =============================

        ax.text(0.14*axx, 95,self.title, verticalalignment='center',
                fontsize=20,weight='bold', fontname='sans-serif', color="#001524")
        ax.text(1.15*axx, 4,"ainarabic.ai",alpha=0.9, verticalalignment='center',
                fontsize=9, color="#CD8D7A", fontstyle='italic')
        ax.text(1.15*axx, 1,"DATA SOURCE : UN",alpha=0.9, verticalalignment='center',
                fontsize=8, color="#3559E0", fontstyle='italic')
        rect = patches.Rectangle((0.04*axx, 95), 0.03*axx, 5, linewidth=1,edgecolor="none", facecolor='black')
        ax.add_patch(rect)
        rect = patches.Rectangle((0.04*axx, 90), 0.03*axx, 5, linewidth=1, edgecolor="none", facecolor='green')
        ax.add_patch(rect)
        trngle = patches.Polygon([[0.04*axx, 100], [0.04*axx, 90], [0.11*axx, 95]], closed=True, edgecolor="none", facecolor='red')
        ax.add_patch(trngle)

        ax= plt.gca()
        for spine in ax.spines.values():
            spine.set_linewidth(0)
        ax.tick_params(axis='x', colors='#414A4C',length=3, width=3, labelsize=8)  # Set the color of the x-axis tick marks and labels
        ax.tick_params(axis='y', colors='#414A4C', length=3, width=3, labelsize=8)
        self._customize_legend(ax) 
        
    def _customize_legend(self, ax) -> None:
        """
         Inputs
         `ax`: The axis object to draw the plot on.
        ___
         Pipeline
        1. Define the colors for the legend markers.
        2. Define the labels for the legend.
        3. Define the markers for the legend.
        4. Define the size of the markers.
        5. Create a list of Line2D objects representing the legend handles.
        6. Load the legend configuration from a YAML file.
        7. Create the legend using the handles, labels, and legend configuration.
        8. Remove the frame around the legend.
        ___
         Outputs
        None. The method modifies the input `ax` object to customize the legend of the plot.
        """
        bc = ["#CD1818", "#3D0C11"]
        labels = [self.lgd_lbls[0][0], self.lgd_lbls[0][1]]
        markers = ['s', 's']
        markersize = 10 
        handles = [Line2D([0], [0], marker=marker, linestyle='None', color=color, markersize=markersize) for marker, color in zip(markers, bc)]
        with open(self.legend_config_path, 'r') as file:
            legend_config = yaml.safe_load(file)
        leg = ax.legend(handles, labels ,**legend_config)
        leg.get_frame().set_linewidth(0)
    
    
    def show_plot(self, save_filename:str = None):
        """
        Show the customized bar plot.

        Args:
            save_filename (str, optional): The filename to save the plot. Defaults to None.
        """
        try:
            max_value = self.clean_data()
            grouped, total1, total2, total3, total4 = self.compute_statistics()
            _, ax = self.create_plot()
            self.draw_plot(ax, grouped, total1, total2, total3, total4, max_value)
            plt.axis('off')
            if save_filename is not None:
                plt.savefig(save_filename)
            plt.show()
        except Exception as e:
            logging.error(f"An error occurred while showing the plot: {str(e)}")
        else:
            logging.info("Plot shown")
            
  
          
                
                


 
