from IPython.core.display import display, HTML, Javascript
from ipywidgets.embed import embed_minimal_html
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl 
import numpy as np
import matplotlib.lines as mlines
import matplotlib.colors as mcolors
import ipywidgets as widgets
import sys
plt.ioff()

class UI:
    def __init__(self):
        self.python_version = sys.version.split()[0] 
        self.tabnames = ["Data", "Stats", "Scatter Plot", "Box Plots", "Line Graphs", "Time Graph"]
        self.content = {}
        for i in self.tabnames:
            self.content[i] = "More to come"
            
        self.tab_content = {}
        self.Tab_Output = {}
        self.add_content()
        self.style = ""
        self.script = ""
        self.output = {}
        self.descr_style = {'description_width': '120px'}
        self.hl_color1 = "#17A5A7"
        self.hl_color2 = "#FE7C06"
        self.error_color = "#FB5661"
        
        
        self.create_UI()
        
    def adjust_alpha(self, color, alpha):
        m = list(mcolors.to_rgba(color))
        m[-1] = alpha
        m = tuple(m)
        return m

    def add_content(self):
        for i in self.tabnames:
            self.Tab_Output[i] = widgets.Output()
            self.Tab_Output[i].clear_output()
            with self.Tab_Output[i]:
                display(self.content[i])
            self.tab_content[i] = widgets.VBox([self.Tab_Output[i]])

    def create_UI(self):
        for i in self.tabnames:
            self.create_content(i)
        self.tabs = widgets.Tab([self.tab_content[i] for i in self.tabnames])
        for i in self.tabnames:
            self.tabs.set_title(self.tabnames.index(i), i)
            self.create_content(i)

        display(self.tabs)

    def create_content(self, k):

        if k == "Data":
            self.create_data(k)
        if k == "Stats":
            self.create_data(k)
            
      
    def create_data(self, k):
        self.content[k] = []
        
        if k == "Data":
            self.content[k].append(widgets.Text(description= "File", value="", style=self.descr_style) )
            self.load_data_button = widgets.Button(description="Load Data", )
            self.load_data_button.on_click(load_data)
            self.load_data_button.add_class("button")
            self.content[k].append(self.load_data_button)
            tup = tuple(i for i in self.content[k])
            self.tab_content[k].children = tup
            
            
            
        if k == "Stats":
            if  hasattr(self, 'source_column') and hasattr(self, 'dest_column'):
#MAYBE THIS SHOULD ALSO BE LIMITED TO NUMERIC COLUMNS. OR A CHECKBOX TO FORCE TO NUMERIC IF POSSIVLE?  MAYBE JUSE DO A DTYPE CHECK AND LIST ONLY RELEVANT?
                cols = [i for i in self.main_df.columns if i not in [self. source_column, self.dest_column]]

            else:
                return
                 #THERE SHOULD BE AN ERROR HERE.  STATS SHOULD NOT BE AN OPTION WHEN SOURCE AND DEST ARE NOT SET
            self.content[k] = []
            for i in range(3):            
                stats_col1 = widgets.Select(options=cols, value=None, description='Column %d'%(i+1), style=UI.descr_style)
                self.content[k].append(stats_col1)
            if float(self.python_version[:3]) > 3.6:
                sm = widgets.SelectMultiple(options=list(self.main_df[self.source_column].unique()),  description='Sources', style=UI.descr_style)
                self.content[k].append(sm)
            self.load_stats_button = widgets.Button(description="Load Stats", )
            self.load_stats_button.on_click(load_stats)
            self.load_stats_button.add_class("button")
            self.content[k].append(self.load_stats_button)
            tup = tuple(i for i in self.content[k])
 
            self.tab_content[k].children = tup

            
        
    def reload_data(self, k, *add):
        for a in add:
            self.content[k].append(a)
        tup = tuple(i for i in self.content[k])
        self.tab_content[k].children = tup
        self.Tab_Output[k].clear_output()
        with self.Tab_Output[k]:
            display(self.content[k])

    def build_stat_table(self, srcs, col):
        ht = "<style>"
        ht += "<head><style>#source { font-family: 'Trebuchet MS', Arial, Helvetica, sans-serif;font-szie: small; border-collapse: collapse; width: 100%; }"
        ht += "#header, #item {font-family:  Arial, Helvetica, sans-serif;border-collapse: collapse; margin-left: 0px; width: 100%;}"
        ht += "#header tr, #item tr { border-radius: 20px;}"
        ht += "#item th {padding-top: 5px; padding-bottom: 5px; text-align: center;  background-color: #503C42;color: white;}"
        ht += "#item td { border-radius: 10px;border: 2px solid #FFFFFF;padding: 5px;background-color: #d1c6b8;color: #503C42;}"
        ht += ".accordion {background-color: #A58F75;border-radius: 5px;color: #FFFFFF;cursor: pointer;padding: 2px;width: 100%;border: none;text-align: center;outline: none;font-size: 15px;transition: 0.5;}"
        ht += ".active   { color: #DF8889;  background-color: #f5f2f0; }"
        ht += ".accordion:hover {color:white;background-color: #6762AF; }"
        ht += '.accordion:after {content: "\\02795"; font-size: 13px;float: left;margin-left: 5px;}'
        ht += '.active:after { content: "\\2796"; }'
        ht += ".panel {display: none;}"
        ht += "</style>"


        for s in srcs:

            df = self.main_df[self.main_df[self.source_column] == s]
            num = len(df[self.dest_column].unique())
            strs = "<b>Soruce %s </b>"%s
            ht += "<button class='accordion'>"+strs+"</button><div class='panel'>"
            ht += "<table id='item'><tr>"
            ht += "<td colspan=%d>"%len(col)
            ht += "<b>unique dest</b>: %d"%num
            ht += "</td></tr>"
            
            for c in range(len(col)):
                ht += "<th>%s</th>"%col[c]
            ht += "<tr>"
            
            for c in col:

                mean = df[c].mean()
                median = df[c].median()
                mode = df[c].mode()[0]
                cmin = df[c].min()
                cmax = df[c].max()
                ht += "<td>"

                ht += "<b>mean</b>: %.2f</br>"%mean
                ht += "<b>median</b>: %.2f</br>"%median
                ht += "<b>mode</b>: %.2f</br>"%mode
                ht += "<b>min</b>: %.2f</br>"%cmin
                ht += "<b>max</b>: %.2f</br>"%cmax
                ht += "</td>"
            ht += "</tr>"    
            ht += "</table></div>"



      
        jht = "var acc = document.getElementsByClassName('accordion');"
        jht += "var i;"

        jht += "for (i = 0; i < acc.length; i++) {"
        jht += "  acc[i].addEventListener('click', function() {"
        jht += "    this.classList.toggle('active');"
        jht += "    var panel = this.nextElementSibling;"
        jht += "    if (panel.style.display === 'block') {"
        jht += "      panel.style.display = 'none';"
        jht += "    } else {"
        jht += "      panel.style.display = 'block';"
        jht += "    }"
        jht += "  });"
        jht += "}"

        self.stat_table = widgets.HTML(value = ht)
        self.reload_data("Stats", self.stat_table)
        display(Javascript(jht))
    
    def build_boxplots(self, srcs, col):
        plt.rcParams['figure.figsize'] = 15, 30
        median_color = "#503C42"
        median_colora = self.adjust_alpha(median_color, .3)
        mean_color = "#6762AF"
        box_color = "#DF8889"
        box_colora = self.adjust_alpha(box_color, .4)
        line_color = "#A58F75"

        nsrc = len(srcs)
        ncol = len(col)

        fig, axs = plt.subplots(nsrc, ncol, sharex=True, sharey=True)
        plt.subplots_adjust(.05, .01, 1, .96, 0,0)

        plt.suptitle("Distribution of Values for Source", x=.5)

        scnt = 0

        for src in srcs:
            df = self.main_df[self.main_df[self.source_column] == src]

            cnt = 0
            ylim_max = 0 
            for c in col:
                bp = axs[scnt][cnt].boxplot(df[c], patch_artist=True, zorder=0)
                ylim = plt.gca().get_ylim()
                if ylim[1] > ylim_max:
                    ylim_max = ylim[1]
                axs[scnt][cnt].axes.get_xaxis().set_visible(False)
                for box in bp['boxes']:
                    # change outline color
                    box.set( color=line_color, linewidth=2)
                    # change fill color
                    box.set( facecolor = box_color)

                ## change color and linewidth of the whiskers
                for whisker in bp['whiskers']:
                    whisker.set(color=line_color, linewidth=2, linestyle="--")

                ## change color and linewidth of the caps
                for cap in bp['caps']:
                    cap.set(color=line_color, linewidth=2)

                ## change color and linewidth of the medians
                for median in bp['medians']:
                    vals = median._xy
                    avg = df[c].mean()
                    med = df[c].median()
                    for v in vals:
                        v[1] = avg

                    l = mlines.Line2D([vals[0][0],vals[1][0]], [vals[0][1],vals[1][1]], zorder=1, color=mean_color)
                    axs[scnt][cnt].add_line(l)
                    median.set(color=median_color, linewidth=2)
                    axs[scnt][cnt].annotate("median: %.2f"%med, (vals[0][0]-.03, med), zorder=1, color="white", backgroundcolor=median_color, verticalalignment="center", horizontalalignment="right")
                    axs[scnt][cnt].annotate("mean: %.2f"%avg, (vals[1][0]+.03, avg), zorder=1, color="white", backgroundcolor=mean_color, verticalalignment="center", horizontalalignment="left")

                cnt += 1

            for i in range(ncol):
                axs[0][i].annotate( col[i],(1, ylim_max), backgroundcolor=box_colora, color=median_color, zorder=10, verticalalignment="bottom", horizontalalignment="center", fontsize=14)

            axs[scnt][0].annotate( srcs[scnt],(.53, 0), backgroundcolor=median_colora, color=median_color, zorder=10, verticalalignment="bottom", horizontalalignment="left", fontsize=14)
            scnt += 1

        self.Tab_Output["Box Plots"].clear_output()
        with self.Tab_Output["Box Plots"]:
            display(self.content["Box Plots"])
            display(fig)

        
        
    
def load_stats(sender):
    UI.stat_col = []
    sa = 0
    for wid in UI.content["Stats"]:
        if "Select" in str(type(wid)):
            if wid.value != None and "Sources" not in wid.description:
                UI.stat_col.append(wid.value)
            if "Sources" in wid.description:
                srcs = list(wid.value)
                sa = 1
        if "HTML" in str(type(wid)):
            ind = UI.content["Stats"].index(wid)
            del UI.content["Stats"][ind]
            
    if sa == 0: 
        srcs = list(UI.main_df[UI.source_column].unique())
    UI.build_stat_table(srcs, UI.stat_col)
    UI.build_boxplots(srcs, UI.stat_col)
    
        
       
def load_data(sender):
    for i in UI.content["Data"]:
        if "Text" in str(type(i)):
            if i.description == "File":
                load_datafile(i.value)
    new0 = widgets.HTML(value = "<div align='center'><h3><font color='%s'>Select Columns of the Source and Destination</font> </b3></div>"%(UI.hl_color2))

    new = widgets.Select(options=UI.main_df.columns, value=None, description='Source Column', style=UI.descr_style)
    new.observe(save_source, names="value")
    UI.reload_data("Data", new0, new)

def save_source(sender):
    UI.source_column  = sender["new"]
    val = "Source Column set to"
    if sender["old"] == None:

        new1 = Widget = widgets.HTML(value = "<b><font color='%s'>%s: </font> </b>%s<br><br>"%(UI.hl_color1, val, sender["new"]))

        new2 = widgets.Select(options=UI.main_df.columns, value=None, description='Destination Column', style=UI.descr_style)    
        new2.observe(save_dest, names="value")
        UI.reload_data("Data",  new1, new2)
    else:
        for i in UI.content["Data"]:
            if "HTML" in str(type(i)):
                if val in i.value:
                    text=sender["new"]
                    i.value = "<b><font color='%s'>%s: </font></b>%s<br><br>"%(UI.hl_color1, val, sender["new"])
        UI.reload_data("Data")

        
    
def save_dest(sender):

    UI.dest_column  = sender["new"]
    val =  "Destination Column set to"
    if sender["old"] == None:
        new = widgets.HTML(value="<b><font color='%s'>%s: </font></b>%s<br><br>"%(UI.hl_color1, val, sender["new"]))
        UI.reload_data("Data", new)
    else:
        for i in UI.content["Data"]:
            if "HTML" in str(type(i)):
                if val in i.value:
                    i.value = "<b><font color='%s'>%s: </font></b>%s<br><br>"%(UI.hl_color1, val, sender["new"])   

    UI.create_content("Stats")
    UI.reload_data("Stats")

                              
#expecting a csv
def load_datafile(f, header=None):
    UI.main_df = pd.read_csv(f)
    if header != None:
        if len(UI.main_df.columns) == len(header):
            UI.main_df.columns = header


    
    
UI = UI() 
    
    
        
        
        
        