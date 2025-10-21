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
        return {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().isoformat(),
            "value": round(random.uniform(50, 150), 2)
        }
    elif chart_type in ['sequences', 'lines', 'bars']:
        return {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().isoformat(),
            "value": {
                "A": round(random.uniform(50, 150), 2),
                "B": round(random.uniform(30, 130), 2),
            }
        }
    elif chart_type == 'scatter':
        return {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().isoformat(),
            "value": [round(random.uniform(50, 150), 2), round(random.uniform(30, 130), 2)]
        }
    elif chart_type == 'area':
        dimension = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        value = [round(random.uniform(50, 150), 2) for _ in dimension]
        return {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().isoformat(),
            "value": [dimension, value]
        }
    elif chart_type == 'areas':
        dimension = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        valueA = [round(random.uniform(50, 150), 2) for _ in dimension]
        valueB = [round(random.uniform(50, 150), 2) for _ in dimension]
        series = ["A", "B"]
        value = [valueA, valueB]
        return {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().isoformat(),
            "value": [dimension, series, value]
        }
    elif chart_type == 'pie':
        dimension = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        value = [round(random.uniform(50, 150), 2) for _ in dimension]
        return {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().isoformat(),
            "value": [dimension, value]
        }
    elif chart_type == 'radar':
        dimension = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        value = [round(random.uniform(50, 150), 2) for _ in dimension]
        valueMax = [150 for _ in dimension]
        return {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().isoformat(),
            "value": [dimension, valueMax, value]
        }
    elif chart_type == 'surface':
        start, stop, step = -10, 10, 1
        xRange = [start + i * step for i in range(int(math.ceil((stop - start) / step)))]
        yRange = [start + i * step for i in range(int(math.ceil((stop - start) / step)))]
        zValues = [[x,y,3*x*x+y+random.uniform(0,1)*50] for x in xRange for y in yRange]
        axis = ["moneyness", "dte", "vega"]
        shape = [len(xRange), len(yRange)]
        return {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().isoformat(),
            "value": [axis, shape, zValues]
        }
    else:
        return None

def simulate(chart, chart_type, num=20000, freq=0.1):
    for i in range(num):
        data = generate_data(chart_type)
        chart.update(data)
        time.sleep(freq)

def simulateAll():
    sequence = Sequence('test')
    line = Line('test') 
    bar = Bar('test')
    sequences = Sequences('test')
    lines = Lines('test') 
    bars = Bars('test')
    scatter = Scatter('test')
    area = Area('test')
    areas = Areas('test')
    pie = Pie('test')
    radar = Radar('test')
    surface = Surface('test')

    sequence.execute(simulate, 'sequence')
    line.execute(simulate, 'line')
    bar.execute(simulate, 'bar')
    sequences.execute(simulate, 'sequences')
    lines.execute(simulate, 'lines')
    bars.execute(simulate, 'bars')
    scatter.execute(simulate, 'scatter')
    area.execute(simulate, 'area')
    areas.execute(simulate, 'areas')
    pie.execute(simulate, 'pie')
    radar.execute(simulate, 'radar')
    surface.execute(simulate, 'surface')

    # Keep Main Thread Running For 300 seconds
    print("\nServer is running in background.")
    try:
        time.sleep(300)
    except KeyboardInterrupt:
        print("Application shutting down.")

if __name__ == "__main__":
    simulateAll()


