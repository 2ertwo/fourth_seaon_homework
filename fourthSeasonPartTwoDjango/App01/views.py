import os

from django.shortcuts import render
from django.conf import settings
import pandas as pd

# Create your views here.
motor_list = [i for i in range(1, 21)]
col_list = ["ROUND(A.POWER,0)", 'YD15']


def get_raw_data(index_list, day_start, day_end):
    df_dict = {}
    for i in index_list:
        temp_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'App01', 'data', '%02d.csv' % int(i)),
                              parse_dates=['DATATIME'],
                              infer_datetime_format=True, dayfirst=True)
        temp_df = temp_df.drop_duplicates(keep='first')
        df_dict['%02d.csv' % int(i)] = temp_df[
            temp_df.DATATIME.gt(pd.to_datetime(str(day_start))) & temp_df.DATATIME.lt(pd.to_datetime(str(day_end)))]
    return df_dict


df1 = get_raw_data([1], 20210928, 20210930)['01.csv']


def main(request):
    return render(request, 'main.html',
                  {'APPLIED_MODELS': APPLIED_MODELS, 'motor_list': motor_list, 'col_list': col_list})


def wait(request):
    return render(request, 'wait.html')


class ModelView:
    def __init__(self, model_name, model_en_name, model_info, model_info_df: pd.DataFrame, u_df, l_df, m_df):
        self.model_name = model_name
        self.model_en_name = model_en_name
        self.model_info = model_info
        self.model_info_df = []
        for i in model_info_df.index:
            self.model_info_df.append(
                [model_info_df.iloc[i]['ModelParameters'], model_info_df.iloc[i]['TransformationParameters']])
        self.uml = u_df, m_df, l_df
        native = [i.__str__() for i in df1['DATATIME'].tolist()]
        migrate = m_df['Unnamed: 0'].tolist()
        all_data_time = native + migrate
        self.option = {
            'title': {
                'text': self.model_en_name
            },
            'tooltip': {
                'trigger': 'axis',
            },
            'legend': {
                'data': ['原值', '预测值', '上界', '下界', ]
            },
            'grid': {
                'left': '3%',
                'right': '4%',
                'bottom': '3%',
                'containLabel': 'true'
            },
            'toolbox': {
                'feature': {
                    'saveAsImage': {}
                }
            },
            'xAxis': {
                'data': all_data_time
            },
            'yAxis': {},
            'series': [
                {
                    'name': '原值',
                    'data': df1['YD15'].values.tolist() + ['Nan' for i in range(len(migrate))],
                    'type': 'line',
                },
                {
                    'name': '预测值',
                    'data': ['Nan' for i in range(len(native))] + m_df['YD15'].values.tolist(),
                    'type': 'line',
                },
                {
                    'name': '上界',
                    'data': ['Nan' for i in range(len(native))] + u_df['YD15'].values.tolist(),
                    'type': 'line',
                    'areaStyle': {
                        'color': '#ff0',
                        'opacity': 0.5
                    }
                },
                {
                    'name': '下界',
                    'data': ['Nan' for i in range(len(native))] + l_df['YD15'].values.tolist(),
                    'type': 'line',
                    'areaStyle': {
                        'color': '#f0f',
                        'opacity': 0.5
                    }
                },

            ]
        }

    def __call__(self, request):
        return render(request, 'sigal_model_template.html',
                      {'model_name': self.model_name, 'model_en_name': self.model_en_name,
                       'model_info': self.model_info, 'model_table': self.model_info_df, 'option': self.option,
                       'APPLIED_MODELS': APPLIED_MODELS})


model_detail = pd.read_csv(os.path.join(settings.BASE_DIR, 'App01', 'ats_models', 'models_csv.csv'))
model_view_list = []
temp = os.listdir(os.path.join(settings.BASE_DIR, 'App01', 'ats_models'))
model_info_csv_names = []
upper_csv_names = {}
lower_csv_names = {}
middle_csv_names = {}
for t in temp:
    tt = t.split('_')[1]
    if tt == 'l':
        ttt = t.split('_')[2]
        lower_csv_names[ttt] = t
    elif tt == 'u':
        ttt = t.split('_')[2]
        upper_csv_names[ttt] = t
    elif tt == 'm':
        ttt = t.split('_')[2]
        middle_csv_names[ttt] = t
    else:
        model_info_csv_names.append(tt)
model_info_csv_names.remove('csv.csv')

for m in model_info_csv_names:
    line = model_detail[model_detail['model_en_name'] == m.split('.')[0]]
    kk = '01csv_' + m
    df_info = pd.read_csv(os.path.join(settings.BASE_DIR, 'App01', 'ats_models', kk))
    u_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'App01', 'ats_models', upper_csv_names[m]))
    m_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'App01', 'ats_models', middle_csv_names[m]))
    l_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'App01', 'ats_models', lower_csv_names[m]))
    model_view_list.append(
        ModelView(line['model_name'].values[0], line['model_en_name'].values[0], line['model_info'].values[0],
                  df_info, u_df, l_df, m_df))

APPLIED_MODELS = {}
i = 1
for m in model_info_csv_names:
    APPLIED_MODELS[str(i) + '、' + m.split('.')[0]] = m.split('.')[0]
    i = i + 1
