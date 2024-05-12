import json
import plotly.graph_objs as go
import plotly.subplots as ms
from plotly.subplots import make_subplots
import datetime
import pytz 

est_tz = pytz.timezone('America/New_York')
pst_tz = pytz.timezone('America/Los_Angeles')  # Using correct time zone identifier for PST

def convert_to_pst(timestamps):
  # Convert each timestamp from EST to PST
  pst_timestamps = []
  for ts in timestamps:
    est_dt = est_tz.localize(ts)
    pst_dt = est_dt.astimezone(pst_tz)
    pst_timestamps.append(pst_dt)
  return pst_timestamps

class FlowDataLoader:
  def __init__(self):
    self.__data_path = "../data/flow_data/spy-flow-data.json"
    
    self.__flow_data = self.__load_flow_data()

  def __load_flow_data(self):
    data = None
    with open(self.__data_path, 'r') as file:
      data = json.load(file)
    return data

  def __zero_dte_condition(self, row, date_str):
    condition = 'date' in row and 'date_expiration' in row and row['date'] == date_str and row['date_expiration'] == date_str
    return condition

  def __date_condition(self, row, date_str):
    condition = 'date' in row and row['date'] == date_str
    return condition

  def __get_cost_premium_list(self, data, is_bearish=False):
    # Initialize lists for cumulative cost_basis and time
    cost_basis_list = []
    time_list = []

    # Initialize running sum
    total_cost_basis = 0

    # Iterate over the data in reverse order assuming data is in descending time
    for entry in reversed(data):
      # Extract cost_basis and time from each entry
      cost_basis = float(entry['cost_basis'])
      entry_time = entry['time']
      if is_bearish:
        cost_basis = cost_basis * -1
      cost_basis_list.append(cost_basis)
      time_list.append(entry_time)
        
    return cost_basis_list, time_list

  def __get_cumulative_premium(self, data):
    # Initialize lists for cumulative cost_basis and time
    cumulative_cost_basis = []
    time = []

    # Initialize running sum
    total_cost_basis = 0

    # Iterate over the data in reverse order assuming data is in descending time
    for entry in reversed(data):
      # Extract cost_basis and time from each entry
      cost_basis = float(entry['cost_basis'])
      entry_time = entry['time']
      
      # Update running sum
      total_cost_basis += cost_basis
      
      # Append cumulative cost_basis and time to their respective lists
      cumulative_cost_basis.append(total_cost_basis)
      time.append(entry_time)
        
    return cumulative_cost_basis, time

  def get_flow_data(self):
    return self.__flow_data

  def get_data_for_date(self, date_obj):
    date_str = date_obj.strftime('%Y-%m-%d')
    filtered_rows = []
    for row in self.__flow_data:
      if self.__date_condition(row, date_str):
        filtered_rows.append(row)
    return filtered_rows

  def get_put_data_for_date(self, date_obj):
    date_str = date_obj.strftime('%Y-%m-%d')
    filtered_rows = []
    for row in self.__flow_data:
      if self.__date_condition(row, date_str) and row['put_call'] == 'PUT':
        filtered_rows.append(row)
    return filtered_rows

  def get_call_data_for_date(self, date_obj):
    date_str = date_obj.strftime('%Y-%m-%d')
    filtered_rows = []
    for row in self.__flow_data:
      if self.__date_condition(row, date_str) and row['put_call'] == 'CALL':
        filtered_rows.append(row)
    return filtered_rows

  def get_bullish_put_data(self, date_obj):
    date_str = date_obj.strftime('%Y-%m-%d')
    filtered_rows = []
    for row in self.__flow_data:
      if self.__date_condition(row, date_str) and row['put_call'] == 'PUT' and row['sentiment'] == 'BULLISH':
        filtered_rows.append(row)
    return filtered_rows

  def get_bearish_put_data(self, date_obj):
    date_str = date_obj.strftime('%Y-%m-%d')
    filtered_rows = []
    for row in self.__flow_data:
      if self.__date_condition(row, date_str) and row['put_call'] == 'PUT' and row['sentiment'] == 'BEARISH':
        filtered_rows.append(row)
    return filtered_rows

  def get_bullish_call_data(self, date_obj):
    date_str = date_obj.strftime('%Y-%m-%d')
    filtered_rows = []
    for row in self.__flow_data:
      if self.__date_condition(row, date_str) and row['put_call'] == 'CALL' and row['sentiment'] == 'BULLISH':
        filtered_rows.append(row)
    return filtered_rows

  def get_bearish_call_data(self, date_obj):
    date_str = date_obj.strftime('%Y-%m-%d')
    filtered_rows = []
    for row in self.__flow_data:
      if self.__date_condition(row, date_str) and row['put_call'] == 'CALL' and row['sentiment'] == 'BEARISH':
        filtered_rows.append(row)
    return filtered_rows

  def get_net_call_premium(self, date_obj):
    is_bearish = True
    bearish_call_data = self.get_bearish_call_data(date_obj)
    bearish_premium, bearish_time = self.__get_cost_premium_list(bearish_call_data, is_bearish)

    bullish_call_data = self.get_bullish_call_data(date_obj)
    bullish_premium, bullish_time = self.__get_cost_premium_list(bullish_call_data)
    # net_time = sorted(bullish_time + bearish_time)
    net_time = []
    # Combine premiums with negative values for bearish premiums
    net_call_premium = []
    bullish_index = 0
    bearish_index = 0
    total_cost_basis = 0
    while bullish_index < len(bullish_time) and bearish_index < len(bearish_time):
      cost_basis = None
      time_val = None 
      if bullish_time[bullish_index] <= bearish_time[bearish_index]:
        cost_basis = bullish_premium[bullish_index]
        time_val = bullish_time[bullish_index]
        bullish_index += 1
      else:
        cost_basis = bearish_premium[bearish_index]
        time_val = bearish_time[bearish_index]
        bearish_index += 1
      total_cost_basis += cost_basis
      net_call_premium.append(total_cost_basis)
      net_time.append(time_val)
    return net_call_premium, net_time

  def get_net_put_premium(self, date_obj):
    is_bearish = True
    bearish_put_data = self.get_bearish_put_data(date_obj)
    bearish_premium, bearish_time = self.__get_cost_premium_list(bearish_put_data, is_bearish)

    bullish_put_data = self.get_bullish_put_data(date_obj)
    bullish_premium, bullish_time = self.__get_cost_premium_list(bullish_put_data)
    # net_time = sorted(bullish_time + bearish_time)
    net_time = []
    # Combine premiums with negative values for bearish premiums
    net_put_premium = []
    bullish_index = 0
    bearish_index = 0
    total_cost_basis = 0
    while bullish_index < len(bullish_time) and bearish_index < len(bearish_time):
      cost_basis = None
      time_val = None 
      if bullish_time[bullish_index] <= bearish_time[bearish_index]:
        cost_basis = bullish_premium[bullish_index]
        time_val = bullish_time[bullish_index]
        bullish_index += 1
      else:
        cost_basis = bearish_premium[bearish_index]
        time_val = bearish_time[bearish_index]
        bearish_index += 1
      total_cost_basis += cost_basis
      net_put_premium.append(total_cost_basis)
      net_time.append(time_val)
    return net_put_premium, net_time

  def plot_flow_with_macd(self, df, net_call_premium, call_flow_timestamps, net_put_premium, put_flow_timestamps):
      date_str = df['timestamp_obj'].iloc[0].strftime('%Y-%m-%d')
      call_flow_timestamps = [datetime.datetime.strptime(date_str + ' ' + ts, '%Y-%m-%d %H:%M:%S') for ts in call_flow_timestamps]
      put_flow_timestamps = [datetime.datetime.strptime(date_str + ' ' + ts, '%Y-%m-%d %H:%M:%S') for ts in put_flow_timestamps]
      call_flow_timestamps = convert_to_pst(call_flow_timestamps)
      put_flow_timestamps = convert_to_pst(put_flow_timestamps)
      # Combine and sort timestamps
      all_timestamps = sorted(set(call_flow_timestamps + put_flow_timestamps))

      # Create dictionaries to map timestamps to values
      value_dict1 = dict(zip(call_flow_timestamps, net_call_premium))
      value_dict2 = dict(zip(put_flow_timestamps, net_put_premium))
      # Create lists of values corresponding to sorted timestamps
      sorted_values1 = [value_dict1.get(timestamp, None) for timestamp in all_timestamps]
      sorted_values2 = [value_dict2.get(timestamp, None) for timestamp in all_timestamps]

      # Create traces for net_call_premium and net_put_premium with straight line connection
      trace1 = go.Scatter(x=all_timestamps, y=sorted_values1, mode='lines', name='Net call premium', connectgaps=True, line=dict(color='green'))
      trace2 = go.Scatter(x=all_timestamps, y=sorted_values2, mode='lines', name='Net put premium', connectgaps=True, line=dict(color='red'))

      # Create line trace for line trace date
      line_trace = go.Scatter(x=df['timestamp_obj'],
                              y=(df['close'] + df['open']) / 2.0,
                              mode='lines',
                              name='Stock price',
                              yaxis='y2',
                              line=dict(color='blue'))  # Assign y-axis 'y2' to the line trace

      # Create trace for MACD values
      macd_trace = go.Scatter(x=df['timestamp_obj'],
                              y=df['macd'],
                              mode='lines',
                              name='MACD',
                              yaxis='y3',
                              line=dict(color='orange'))  # Assign y-axis 'y3' to the MACD trace

      # Layout
      layout = go.Layout(title='Values vs Time',
                         xaxis=dict(title='Time'),
                         yaxis=dict(title='Value'),
                         yaxis2=dict(title='Line Trace Value', overlaying='y', side='right'),
                         yaxis3=dict(title='MACD', overlaying='y', side='left'))

      # Create figure
      fig = go.Figure(data=[trace1, trace2, line_trace, macd_trace], layout=layout)

      # Show plot
      fig.show()

  def plot_flow_without_macd(self, df, net_call_premium, call_flow_timestamps, net_put_premium, put_flow_timestamps):

    date_str = df['timestamp_obj'].iloc[0].strftime('%Y-%m-%d')
    call_flow_timestamps = [datetime.datetime.strptime(date_str + ' ' + ts, '%Y-%m-%d %H:%M:%S') for ts in call_flow_timestamps]
    put_flow_timestamps = [datetime.datetime.strptime(date_str + ' ' + ts, '%Y-%m-%d %H:%M:%S') for ts in put_flow_timestamps]
    call_flow_timestamps = convert_to_pst(call_flow_timestamps)
    put_flow_timestamps = convert_to_pst(put_flow_timestamps)
    # Combine and sort timestamps
    all_timestamps = sorted(set(call_flow_timestamps + put_flow_timestamps))

    # Create dictionaries to map timestamps to values
    value_dict1 = dict(zip(call_flow_timestamps, net_call_premium))
    value_dict2 = dict(zip(put_flow_timestamps, net_put_premium))

    # Create lists of values corresponding to sorted timestamps
    sorted_values1 = [value_dict1.get(timestamp, None) for timestamp in all_timestamps]
    sorted_values2 = [value_dict2.get(timestamp, None) for timestamp in all_timestamps]

    # Create traces for net_call_premium and net_put_premium with straight line connection
    trace1 = go.Scatter(x=all_timestamps, y=sorted_values1, mode='lines', name='Net call premium', connectgaps=True, line=dict(color='green'))
    trace2 = go.Scatter(x=all_timestamps, y=sorted_values2, mode='lines', name='Net put premium', connectgaps=True, line=dict(color='red'))

    # Create line trace for line trace date
    line_trace = go.Scatter(x=df['timestamp_obj'],
                            y=(df['close'] + df['open']) / 2.0,
                            mode='lines',
                            name='Stock price',
                            yaxis='y2',
                            line=dict(color='blue'))  # Assign y-axis 'y2' to the line trace

    # Layout
    layout = go.Layout(title='Values vs Time', xaxis=dict(title='Time'), yaxis=dict(title='Value'))

    # Create figure
    fig = go.Figure(data=[trace1, trace2, line_trace], layout=layout)

    # Update layout to accommodate the new y-axis
    fig.update_layout(yaxis2=dict(title='Line Trace Value', overlaying='y', side='right'))

    # Show plot
    fig.show()
