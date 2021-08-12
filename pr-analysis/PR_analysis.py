import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange
from graphql_query import get_PR_data


def createDateColumn(dataframe):
    """This function will create a date column in
    the data frame which will have datetime type rather
    than a string type"""

    newDatecol = []
    format_str = r"%Y-%m-%dT%H:%M:%SZ"
    for i in dataframe['node.mergedAt']:
        if (i is not None):
            # making the string to a datetime format
            newdate = datetime.strptime(i, format_str)
            # appending to the list as a date
            newDatecol.append(newdate.date())
        if (i is None):
            newDatecol.append("None")
    dataframe['Date Merged'] = newDatecol

    return dataframe


def numPRMerged_graph(df):
    """This function will create a graph for Num of Pr merged"""

    # get oldest and youngest dates from the list
    datelist = df['dates']
    oldest = min(datelist)
    youngest = max(datelist)
    timegap = 12
    dates = mdates.drange(oldest, youngest, timedelta(weeks=timegap))
    # data
    counts = df['counts']
    # Set up the axes and figure
    fig, ax = plt.subplots()
    # (To use the exact code below, you'll need to convert your sequence
    # of datetimes into matplotlib's float-based date format.
    # Use "dates = mdates.date2num(dates)" to convert them.)
    dates = mdates.date2num(dates)
    width = np.diff(dates).min()

    # Make a bar plot. Note that I'm using "dates" directly instead of plotting
    # "counts" against x-values of [0,1,2...]
    ax.bar(datelist, counts.tolist(), align='center', width=width, ec='blue')

    # Tell matplotlib to interpret the x-axis values as dates
    ax.xaxis_date()

    # Make space for and rotate the x-axis tick labels
    fig.autofmt_xdate()
    plt.ylabel('Counts')
    plt.xlabel('Dates')
    plt.title('Number of PRs merged over time')
    plt.savefig('PRmergeRates.png', dpi=400)
    plt.show()


def computeMergetime(created_at, merged_at):
    """This function will calculate the merge time"""

    format_str = r"%Y-%m-%dT%H:%M:%SZ"
    date_created = datetime.strptime(created_at, format_str)
    date_merged = datetime.strptime(merged_at, format_str)
    # return diff in days [86400 secs in a day]
    time_diff = (date_merged - date_created).total_seconds() / 86400
    return int(time_diff)


def addlabels(x, y):
    """create labels for bars in bar chart"""

    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha='center')


def avgMergetime_graph(df):
    """This function will create a graph for avg merge time"""

    x = df['Merged_YM']
    y = df['mergetime']
    fig, ax = plt.subplots()
    x_pos = np.arange(len(x))  # <--
    plt.bar(x_pos, y)
    plt.xticks(x_pos, x)  # <--
    # Make space for and rotate the x-axis tick labels
    fig.autofmt_xdate()
    ax.xaxis_date()
    addlabels(x, y)
    plt.xlabel("Dates")
    plt.ylabel("Merge Time in Days")
    plt.title("Avg Merge Times")
    plt.savefig('AvgMergeTimes.png', dpi=400)
    plt.show()


def avgMergetime(df):
    """ This function will be called to calculate
    the avg mergetime and produce a graph"""

    # 1. calculate the mergetime for each PR and add to the dataframe
    mergetime_ = []

    for index, row in df.iterrows():
        if (row.loc['node.mergedAt'] is not None):
            mergetime = computeMergetime(row.loc['node.createdAt'],
                                         row.loc['node.mergedAt'])
            mergetime_.append(mergetime)
        else:
            mergetime_.append("None")
    df['mergetime'] = mergetime_

    # 2. calculate the average merge time for each month
    df['Merged_YM'] = pd.to_datetime(df['node.mergedAt']).dt.to_period('M')
    new_df = df.filter(['Merged_YM', 'mergetime'], axis=1)
    group_mean = new_df.groupby('Merged_YM')['mergetime'].mean()
    mean_df = group_mean.reset_index()
    # change from float to int
    mean_df['mergetime'] = mean_df.mergetime.astype(int)

    # 3. create a bar graph
    avgMergetime_graph(mean_df)


def getMonthlyPRinfo(df):
    """Retrieve the info of PRs merged in
    each month in history and create csv file"""

    new_df = df.filter(['Merged_YM', 'node.title', 'node.url'], axis=1)
    new_df.groupby('Merged_YM')
    new_df.to_csv('PR_Info_Monthly.csv', index=False)


def process_data(dataframe):
    """This function will be called in the main()
    to process the data gathered from the query
    and create a dataframe"""

    # add a new column for just the date in date format
    dataframe = createDateColumn(dataframe)
    # get the frequency of each date
    frequency = dataframe['Date Merged'].value_counts()
    # converting to df and assigning new names to the columns
    df_value_counts = pd.DataFrame(frequency)
    df_value_counts = df_value_counts.reset_index()
    # change column names
    df_value_counts.columns = ['dates', 'counts']
    # delete the the row with None
    dateFreq = df_value_counts.loc[df_value_counts["dates"] != "None"]

    # 1. Create a graph for number of PRs merged over time
    numPRMerged_graph(dateFreq)
    # 2. Create a graph for avg PR merge time
    avgMergetime(dataframe)
    # 3. A table with PR info for each month
    getMonthlyPRinfo(dataframe)


def main():
    # get data from the graphql query
    pr_cursor = None
    res_data = get_PR_data(pr_cursor)
    process_data(res_data)


main()
