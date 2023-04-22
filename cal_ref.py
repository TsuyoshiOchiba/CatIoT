import time
import sys
import RPi.GPIO as GPIO
from hx711py.hx711 import HX711

# 分銅の重さ
REF_OMOSA  = 184.8

# データの取得
SAMP_DATAS = [
    82357.44444444444,
    82362.44444444444,
    82379.44444444444,
    82393.44444444444,
    82407.44444444444,
    82379.44444444444,
    82426.44444444444,
    82428.44444444444,
    82407.44444444444,
    82424.44444444444,
    82442.44444444444,
    82413.44444444444,
    82440.44444444444,
    82421.44444444444,
    82418.44444444444,
    82428.44444444444,
    82461.44444444444,
    82404.44444444444,
    82418.44444444444,
    82455.44444444444,
    82462.44444444444,
    82462.44444444444,
    82436.44444444444,
    82457.44444444444,
    82447.44444444444,
    82437.44444444444,
    82440.44444444444,
    82463.44444444444,
    82418.44444444444,
    82427.44444444444,
    82420.44444444444,
    82465.44444444444,
    82451.44444444444,
    82429.44444444444,
    82444.44444444444,
    82460.44444444444,
    82423.44444444444,
    82411.44444444444,
    82455.44444444444,
    82434.44444444444,
    82454.44444444444,
    82456.44444444444,
    82438.44444444444,
    82433.44444444444,
    82448.44444444444,
    83317.44444444444,
]

print("referenceUnit is ", sum(SAMP_DATAS) / len(SAMP_DATAS) //REF_OMOSA)

hx = HX711(5, 6)

value = hx.read_average(3)
print("Tare A value:", value)
