import sys, os
import math
import json
import time
import random
from datetime import datetime
from .api import *

def generate_data(chart_type: str):
    """generate dynamic data according to chart_type"""
    if chart_type in ['sequence', 'line', 'bar']:
        return round(random.uniform(50, 150), 2)
    elif chart_type in ['sequences', 'lines', 'bars']:
        return {"A": round(random.uniform(50, 150), 2),
                "B": round(random.uniform(30, 130), 2)}
    elif chart_type == 'scatter':
        return [round(random.uniform(50, 150), 2), round(random.uniform(30, 130), 2)]
    elif chart_type == 'area':
        dimension = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        value = [round(random.uniform(50, 150), 2) for _ in dimension]
        return [dimension, value]
    elif chart_type == 'areas':
        dimension = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        valueA = [round(random.uniform(50, 150), 2) for _ in dimension]
        valueB = [round(random.uniform(50, 150), 2) for _ in dimension]
        series = ["A", "B"]
        value = [valueA, valueB]
        return [dimension, series, value]
    elif chart_type == 'pie':
        dimension = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        value = [round(random.uniform(50, 150), 2) for _ in dimension]
        return [dimension, value]
    elif chart_type == 'radar':
        dimension = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        value = [round(random.uniform(50, 150), 2) for _ in dimension]
        valueMax = [150 for _ in dimension]
        return [dimension, valueMax, value]
    elif chart_type == 'surface':
        start, stop, step = -10, 10, 1
        xRange = [start + i * step for i in range(int(math.ceil((stop - start) / step)))]
        yRange = [start + i * step for i in range(int(math.ceil((stop - start) / step)))]
        zValues = [[x,y,3*x*x+y+random.uniform(0,1)*50] for x in xRange for y in yRange]
        axis = ["moneyness", "dte", "vega"]
        shape = [len(xRange), len(yRange)]
        return [axis, shape, zValues]
    else:
        return None

def simulate(chart, chart_type, num=20000, freq=0.1):
    for i in range(num):
        data = generate_data(chart_type)
        chart.fresh(data)
        time.sleep(freq)

def simulate_all():
    """API Server must be initialized before call this function."""
    chart_obj_list = [Sequence, Line, Bar, Sequences, Lines, Bars, Scatter, Area, Areas, Pie, Radar, Surface]
    key_word_list = ['test' for _ in chart_obj_list]
    chart_type_list = ['sequence', 'line', 'bar', 'sequences', 'lines', 'bars', 'scatter', 'area', 'areas', 'pie', 'radar', 'surface']

    for chart_obj, key_word, chart_type in zip(chart_obj_list, key_word_list, chart_type_list):
        obj = chart_obj(key_word)
        obj.execute(simulate, chart_type)


