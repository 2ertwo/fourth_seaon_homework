import os

from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import numpy as np
import palettable

from fourthSeasonDjango.settings import BASE_DIR


def eda(request):
    col_list = ['WINDSPEED', 'PREPOWER', 'WINDDIRECTION', 'TEMPERATURE', 'HUMIDITY', 'PRESSURE',
                "ROUND(A.WS,1)", "ROUND(A.POWER,0)", 'YD15']
    return render(request, 'control_main.html', {'motor_list': [str(i + 1) for i in range(10)], 'col_list': col_list})


def get_raw_data(index_list, day_start, day_end):
    df_dict = {}
    for i in index_list:
        temp_df = pd.read_csv(os.path.join(BASE_DIR, 'App01', 'windpower', '%02d.csv' % int(i)),
                              parse_dates=['DATATIME'],
                              infer_datetime_format=True, dayfirst=True)
        df_dict['%02d.csv' % int(i)] = temp_df[
            temp_df.DATATIME.gt(pd.to_datetime(str(day_start))) & temp_df.DATATIME.lt(pd.to_datetime(str(day_end)))]
    return df_dict


def get_data_stacked_lines(request):
    index = request.GET['index']
    start_day = request.GET['day_start']
    end_day = request.GET['day_end']
    df_dict = get_raw_data([index], start_day, end_day)
    return JsonResponse(df_to_echarts_stacked_lines(df_dict['%02d.csv' % int(index)]))


def df_to_echarts_stacked_lines(df: pd.DataFrame):
    x_axis_data = []
    result = {}
    series = []
    legend_data = []
    for col in df.columns:
        if col == 'DATATIME':
            x_axis_data = list(df[col].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S')))
        else:
            temp_data = df[col].dropna()
            legend_data.append(col)
            temp_dict = {
                'name': col,
                'type': 'line',
                'stack': 'Total',
                'data': list(temp_data)
            }
            series.append(temp_dict)
    result['series'] = series
    result['legend'] = {
        'data': legend_data
    }
    result['xAxis'] = {
        'type': 'category',
        'boundaryGap': False,
        'data': x_axis_data
    }
    return result


def get_data_box_plot(request):
    start_day = request.GET['day_start']
    end_day = request.GET['day_end']
    temp_dict = request.GET.dict()
    del temp_dict['day_start']
    del temp_dict['day_end']
    index = []
    for i in temp_dict.values():
        index.append(i[0])
    df_dict = get_raw_data(index, start_day, end_day)
    dataset_pre = []
    dataset_add = []
    i = 0
    series = []
    max_min = pd.concat(df_dict.values(), axis=0).apply(lambda x: [min(x), max(x) - min(x)]).drop('DATATIME', axis=1)
    for name, df in df_dict.items():
        temp = []
        df = df.drop('DATATIME', axis=1)
        for col in df.columns:
            df[col] = df[col].apply(lambda x: (x - max_min[col][0]) / max_min[col][1])
            temp.append(df[col].values.tolist())
        dataset_pre.append({
            'source': temp
        })
        dataset_add.append({
            'fromDatasetIndex': i,
            'transform': {'type': 'boxplot',
                          }})
        series.append({
            'name': name[0:2] + '号风机',
            'type': 'boxplot',
            'datasetIndex': i + len(index)
        })
        i = i + 1

    dataset = dataset_pre + dataset_add

    return JsonResponse({'dataset': dataset, 'series': series})


def get_data_parallel_lines(request):
    start_day = request.GET['day_start']
    end_day = request.GET['day_end']
    temp_dict = request.GET.dict()
    del temp_dict['day_start']
    del temp_dict['day_end']
    index = []
    legend_data = []
    for i in temp_dict.values():
        index.append(i[0])
        legend_data.append(i[0] + '号风机')
    df_dict = get_raw_data(index, start_day, end_day)
    series = []
    line_style = {
        'width': 1,
        'opacity': 0.5
    }
    for name, df in df_dict.items():
        temp = []
        df = df.drop('DATATIME', axis=1)
        for j in list(df.values):
            temp.append(list(j))
        series.append({
            'name': name[0:2] + '号风机',
            'type': 'parallel',
            'lineStyle': line_style,
            'data': temp
        })

    return JsonResponse({'legend_data': legend_data, 'series': series})


def agg_by_method(agg, method, col):
    if method == 'mean':
        new_df = agg.mean()
    elif method == 'max':
        new_df = agg.max()[col]
    elif method == 'min':
        new_df = agg.min()[col]
    elif method == 'sum':
        new_df = agg.sum()
    elif method == 'std':
        new_df = agg.std()
    elif method == 'median':
        new_df = agg.median()
    else:
        new_df = agg.var()
    return new_df


def get_data_calendar(request):
    index = request.GET['index']
    method = request.GET['method']
    col = request.GET['col']
    df = pd.read_csv(os.path.join(BASE_DIR, 'App01', 'windpower', '%02d.csv' % int(index)),
                     parse_dates=['DATATIME'],
                     infer_datetime_format=True, dayfirst=True)[['DATATIME', col]]
    agg = df.groupby(df.DATATIME.dt.to_period('D'))
    new_df = agg_by_method(agg, method, col)
    if method in ['max', 'min']:
        value_max = max(new_df.values)
        value_min = min(new_df.values)
    else:
        value_max = max(new_df.values)[0]
        value_min = min(new_df.values)[0]

    year_max = new_df.index.max().year
    year_min = new_df.index.min().year
    calendar = []
    series = []
    top = 70
    calendar_index = 0
    index_df = new_df
    new_df = new_df.reset_index()
    new_df.DATATIME = new_df.DATATIME.apply(str)
    for year in range(year_min, year_max + 1):
        calendar.append({
            'top': top,
            'range': str(year),
            'cellSize': ['auto', 20]
        })
        top = top + 190
        series.append({
            'type': 'heatmap',
            'coordinateSystem': 'calendar',
            'calendarIndex': calendar_index,
            'data': new_df[index_df.index.year == year].values.tolist()
        })
        calendar_index = calendar_index + 1
    return JsonResponse({'calendar': calendar, 'series': series, 'value_max': value_max, 'value_min': value_min})


def get_3d_hist(request):
    col_1 = request.GET['col_1']
    col_2 = request.GET['col_2']
    start_day = request.GET['day_start']
    end_day = request.GET['day_end']
    temp_dict = request.GET.dict()
    del temp_dict['day_start']
    del temp_dict['day_end']
    del temp_dict['col_1']
    del temp_dict['col_2']
    index = []
    for i in temp_dict.values():
        index.append(i[0])
    df_dict = get_raw_data(index, start_day, end_day)
    scatter_series = []
    bar_series_data = []
    bar_x_axis_data = []
    for name, df in df_dict.items():
        temp = df[[col_1, col_2]]
        bar_x_axis_data.append(name[0:2] + '号风机')
        scatter_series.append({
            'type': 'scatter',
            'id': name[0:2] + '号风机',
            'dataGroupId': name[0:2] + '号风机',
            'data': temp.values.tolist()
        })
        bar_series_data.append({
            'value': temp[col_2].mean(),
            'groupId': name[0:2] + '号风机'
        })
    return JsonResponse(
        {'scatter_series': scatter_series, 'bar_x_axis_data': bar_x_axis_data, 'bar_series_data': bar_series_data})


def get_water_fall(request):
    index = request.GET['index']
    col = request.GET['col']
    day_start = request.GET['day_start']
    day_end = request.GET['day_end']
    method = request.GET['method']
    df = pd.read_csv(os.path.join(BASE_DIR, 'App01', 'windpower', '%02d.csv' % int(index)),
                     parse_dates=['DATATIME'],
                     infer_datetime_format=True, dayfirst=True)[['DATATIME', col]]
    df = df[df.DATATIME.gt(pd.to_datetime(str(day_start))) & df.DATATIME.lt(pd.to_datetime(str(day_end)))]
    agg = df.groupby(df.DATATIME.dt.to_period('D'))
    new_df = agg_by_method(agg, method, col)
    x_axis_data = list(new_df.reset_index().DATATIME.apply(str))
    if method in ['max', 'min']:
        temp = list(new_df.values)
    else:
        temp = new_df.values.transpose().tolist()[0]
    shift = [0] + temp[0:-1]
    delta = [temp[i] - shift[i] for i in range(len(temp))]
    up = []
    down = []
    placeholder = [0]
    for j in range(len(delta)):
        i = delta[j]
        if i > 0:
            up.append(round(i, 1))
            down.append('-')
            if j != 0:
                placeholder.append(temp[j - 1])
        elif i < 0:
            down.append(abs(round(i, 1)))
            up.append('-')
            if j != len(delta):
                placeholder.append(temp[j])
        else:
            up.append('-')
            down.append('-')
            placeholder.append(temp[j])
    return JsonResponse({'x_axis_data': x_axis_data, 'placeholder': placeholder, 'up': up, 'down': down})


def get_corr_matrix(request):
    index = request.GET['index']
    df = pd.read_csv(os.path.join(BASE_DIR, 'App01', 'windpower', '%02d.csv' % int(index)),
                     parse_dates=['DATATIME'],
                     infer_datetime_format=True, dayfirst=True)
    df = df.drop('DATATIME', axis=1)
    raw_corr_matrix = df.corr().values
    corr_matrix = []
    i = 0
    j = 0
    for corr_line in raw_corr_matrix:
        for corr in corr_line:
            corr_matrix.append([i, j, round(corr, 3)])
            j = j + 1
            if j == 9:
                j = 0
        i = i + 1
    return JsonResponse({'corr_matrix': corr_matrix})


def scatter_matrix(request):
    start_day = request.GET['day_start']
    end_day = request.GET['day_end']
    temp_dict = request.GET.dict()
    del temp_dict['day_start']
    del temp_dict['day_end']
    index = []
    col = []
    for i in temp_dict.keys():
        if i.startswith('has'):
            index.append(temp_dict[i])
        else:
            col.append(temp_dict[i])
    df_dict = get_raw_data(index, start_day, end_day)
    raw_data = []
    categories = []

    for name, df in df_dict.items():
        cat_name = name[0:2] + '号风机'
        temp = df[col]
        if not temp.empty:
            temp.loc[:, 'index'] = cat_name
        categories.append(cat_name)
        raw_data = raw_data + temp.dropna().values.tolist()

    colors = palettable.tableau.ColorBlind_10.hex_colors[0:len(index)]
    return JsonResponse(
        {'raw_data': raw_data, 'categories': categories, 'category_dim_count': len(col), 'category_dim': len(col),
         'colors': colors})
