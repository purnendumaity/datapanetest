#https://python.plainenglish.io/sankeying-with-plotly-90500b87d8cf
#https://plotly.com/python/sankey-diagram/#:~:text=Sankey%20diagrams%20visualize%20the%20contributions,Figure(data%3D%5Bgo.
#https://plotly.com/python/renderers/
#https://github.com/datapane/datapane-docs/blob/v2/reports/blocks/layout-pages-and-selects.md


import pandas as pd
import plotly.graph_objects as go
import datapane as dp

# to make notebook work offline
#from plotly.offline import init_notebook_mode
#init_notebook_mode(connected=True)

df = pd.read_csv('merchant_txns_dummy.csv')
df.head()
#Helper function to transform regular data to sankey format
# Returns data and layout as dictionary
def genSankey(df, cat_cols=[], value_cols='', title='Sankey Diagram'):
    # maximum of 6 value cols -> 6 colors
    colorPalette = ['#4B8BBE', '#306998', '#FFE873', '#FFD43B', '#646464']
    labelList = []
    colorNumList = []
    for catCol in cat_cols:
        labelListTemp = list(set(df[catCol].values))
        colorNumList.append(len(labelListTemp))
        labelList = labelList + labelListTemp

    # remove duplicates from labelList
    labelList = list(dict.fromkeys(labelList))

    # define colors based on number of levels
    colorList = []
    for idx, colorNum in enumerate(colorNumList):
        colorList = colorList + [colorPalette[idx]] * colorNum

    # transform df into a source-target pair
    for i in range(len(cat_cols) - 1):
        if i == 0:
            sourceTargetDf = df[[cat_cols[i], cat_cols[i + 1], value_cols]]
            sourceTargetDf.columns = ['source', 'target', 'count']
        else:
            tempDf = df[[cat_cols[i], cat_cols[i + 1], value_cols]]
            tempDf.columns = ['source', 'target', 'count']
            sourceTargetDf = pd.concat([sourceTargetDf, tempDf])
        sourceTargetDf = sourceTargetDf.groupby(['source', 'target']).agg({'count': 'sum'}).reset_index()

    # add index for source-target pair
    sourceTargetDf['sourceID'] = sourceTargetDf['source'].apply(lambda x: labelList.index(x))
    sourceTargetDf['targetID'] = sourceTargetDf['target'].apply(lambda x: labelList.index(x))

    # creating the sankey diagram
    data = dict( type='sankey',
                 node=dict( pad=15,thickness=20,line=dict(color="black",width=0.5),
                 label=labelList, color=colorList ),
                 link=dict(
                            source=sourceTargetDf['sourceID'],
                            target=sourceTargetDf['targetID'],
                            value=sourceTargetDf['count'] )
                )

    layout = dict( title=title,  font=dict( size=10 ) )
    fig = dict(data=[data], layout=layout)
    return fig

# Generating regular sankey diagram
sank = genSankey(df,cat_cols=['Country','Channel','Security'],
                 value_cols='Declines',title='Merchant Transactions')
fig = go.Figure(sank)
#fig.show(renderer="browser")
#iplot(fig)

# Generating DFs for different filter options
italy = genSankey(df[df['Country']=='Italy'],
                  cat_cols=['Country','Channel','Security'],
                  value_cols='Declines',title='Merchant Transactions')
spain = genSankey(df[df['Country']=='Spain'],
                  cat_cols=['Country','Channel','Security'],
                  value_cols='Declines',title='Merchant Transactions')
all = genSankey(df,cat_cols=['Country','Channel','Security'],
                value_cols='Declines',title='Merchant Transactions')

# Constructing menus
updatemenus = [{'buttons': [{'method': 'animate',
                             'label': 'All',
                             'args': [all]
                              },
                            {'method': 'animate',
                             'label': 'Italy',
                             'args': [italy]
                             },
                            {'method': 'animate',
                             'label': 'Spain',
                             'args': [spain]
                             }
                            ] } ]

# update layout with buttons, and show the figure
sank = genSankey(df,cat_cols=['Country','Channel','Security'],value_cols='Declines',title='Merchant Transactions')
fig = go.Figure(sank)
fig.update_layout(updatemenus=updatemenus)
#fig.show(renderer="browser")
#iplot(fig)
#iplot()


app = dp.App("myApp", dp.Plot(fig, caption="Commodity Flow", responsive=False),
             dp.DataTable(df,caption="mydata"))
mypath="D:/Python-Projects/datapanetest/sankeytest.html"
app.save(path=mypath,open=False,standalone=True,cdn_base=None)
