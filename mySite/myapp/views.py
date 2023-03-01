from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from mySite.settings import BASE_DIR
import csv
from .ml_xg_boost import xgboost

def nikkei_225(request):
    if 0:
        xgboost()
    sample_l = []
    with open(str(BASE_DIR) + "/nikkei_yosoku.csv", 'r') as f:
        reader = csv.reader(f)
        for i,line in enumerate(reader):
            sample_l.append([line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7],line[8]])
    context={
        'sample2':sample_l,
    }

    return render(request,"index.html", context)