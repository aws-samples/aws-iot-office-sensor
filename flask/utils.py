# utils.py
# These functions help process and visualize data

from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import figure
import pandas as pd


def history(dynamodb_client, table_name, metric, i, interval=50):
    """
    Returns an event's history (items in a DynamoDB table) as a DataFrame
    :param dynamodb_client: Connection to DynamoDB service
    :param table_name: Name of DynamoDB table (string)
    :param metric: Name of metric subtopic (string)
    :param i: ID of message payload (integer)
    :param interval: Interval of history (integer)
    :return: A DataFrame
    """
    records = []
    if i > interval:
        floor = i - interval
    else:
        floor = 0
    response = dynamodb_client.query(TableName=table_name, KeyConditionExpression="Metric = :metric AND ID > :floor",
                                     ExpressionAttributeValues={":metric": {"S": metric}, ":floor": {"N": str(floor)}})
    for n in range(0, interval - 1):
        record = response['Items'][n]['payload']['M']
        new_record = {}
        for key in record.keys():
            for dt in record[key]:
                new_record[key] = record[key][dt]
        records.append(new_record)
    metric_df = pd.DataFrame(records, dtype=float)
    return metric_df


def calculate_mas(metric, data, window):
    """
    Returns moving average metrics across specified interval for records of data
    :param metric: Metric of interest (string)
    :param data: Metric's DataFrame
    :param window: The sliding interval (integer)
    :return: A DataFrame
    """
    timestamp = data['Timestamp']
    obs = data[metric]
    mean = obs.rolling(window).mean()
    std = obs.rolling(window).std()
    var = obs.rolling(window).var()
    for i in range(0, window):
        if i < window:
            try:
                mean[i] = obs[0:i + 2].mean()
                std[i] = obs[0:i + 2].std()
                var[i] = obs[0:i + 2].var()
            except TypeError:
                continue
    diff_m = obs - mean
    metric_stats = pd.DataFrame.from_dict(
        {'obs': obs, 'mav': mean, 'diff_m': diff_m, 'mstd': std, 'mvar': var, 'timestamp': timestamp})
    metric_stats['timestamp'] = pd.to_datetime(metric_stats['timestamp'])
    return metric_stats


def is_anomaly(metric_data):
    """
    Checks if data point is anomalous... (e.g. populate a column with metric[key]['anomaly'] = is_anomaly(metrics))
    :param metric_data: A DataFrame of statistics for a specific metric, where 'diff_m' is the the difference in the
    observation and the moving average at time t, and 'mstd' is the moving standard deviation at time t
    :return: True if data point is anomalous, False if not
    """
    metric_data['z'] = metric_data['diff_m'] / metric_data['mstd']
    metric_data['anomaly'] = False
    for row in metric_data.index:
        if metric_data.ix[row, 'z'] >= 2 or metric_data.ix[row, 'z'] <= -2:
            metric_data.ix[row, 'anomaly'] = True
    return metric_data


def plot_data(data, anomalies, title, x_label, y_label):
    """
    Plots statistics
    :param data: The data
    :param title: Title of the graph (string)
    :param x_label: X-axis label (string)
    :param y_label: Y-axis label (string)
    :param width: Width of table (integer)
    :param height: Height of table (integer)
    :return: Bokeh Figure object
    """
    data['alpha1'] = data['mav'] + (2 * data['mstd'])
    data['alpha2'] = data['mav'] - (2 * data['mstd'])
    y_range = [min(data['mav']) - (5 * data['obs'].std()), max(data['mav']) + (5 * data['obs'].std())]
    source = ColumnDataSource(data)
    source2 = ColumnDataSource(anomalies)
    p = figure(title=title, x_axis_label=x_label, y_axis_label=y_label, plot_width=1200, plot_height=600,
               x_axis_type='datetime', y_range=y_range)
    p.circle(x='timestamp', y='obs', source=source, size=5, legend="Observation")
    p.line(x='timestamp', y='mav', source=source, line_width=1, color="purple", legend="Moving Average")
    p.line(x='timestamp', y='alpha1', source=source, line_width=2, color="red", line_dash="dashed",
           legend="95% Confidence Interval")
    p.line(x='timestamp', y='alpha2', source=source, line_width=2, color="red", line_dash="dashed")
    p.circle(x='timestamp', y='obs', source=source2, size=5, color="firebrick", legend="Anomaly")
    p.legend.label_text_font_size = "8pt"
    return p
