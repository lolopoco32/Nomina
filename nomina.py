#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nomina - batch file renamer (Tkinter)

Dependențe: doar biblioteca standard (Tkinter).
Opțional, pentru drag & drop (oricare dintre variante):
    sudo apt install tkdnd          (extensia Tcl nativă, pentru orice arhitectură)
    pip install tkinterdnd2         (o aduce cu ea)
Linux (Debian/Ubuntu), dacă lipsește Tk:   sudo apt install python3-tk
"""

import copy
import json
import locale
import math
import os
import re
import subprocess
import sys
import time
import unicodedata
import uuid
from collections import Counter
from datetime import datetime

import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, simpledialog, ttk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except Exception:  # biblioteca lipsește sau nu se poate încărca
    HAS_DND = False

APP_NAME = "Nomina"
IS_WIN = os.name == "nt"
MAX_HISTORY = 100
MIN_W, MIN_H = 940, 660
RIGHT_MIN = 420

LANGS = {"ro": "Română", "en": "English", "it": "Italiano"}

ICONS_B64 = {
    "file_add": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAD4ElEQVR42pVVW2hcVRRd+56bO5N5ZWaSqYba5EctEW2tYOkDLbU2"
        "NTVqUZKi+ChFU20V24+kEZWb+RGFQhEsYlRSTL9MsNKKNfUjQlSq0Q9bjRGjjWKSZmzm0dyZuXfmnrP9yDSdPCi4YcOBs19rsfY5"
        "hDkjAAyAdh3ojOZsh2WhQKU7CMNgn9dDnw70Wxgbc1paWkRfX5/EMjaXZJraM+MwrKpir2EYW5RblAwS18KYAWJfZWUyMXP5jc+7"
        "j54wTVOPx+Pu0pLMBAAth8xo68FXnV8v/s2JVJoTyRQnkul5n55J8YWxcT7a28/3PLFvDwC0tbVVLC6nXz3kbIf9Hn12RTQcjYaC"
        "PD99meVtWzVuXg+hUY+UEt3d3ccXw9cX5WjFoksAoJQiIiqBYBAR8k5BZGYtvn/T3UpK1RMJh1Xfe0c+Mk1Ti8fjCgC0JaQSQQGQ"
        "XO4EyYDPWwmfx0ukGI2b16O2Jvr2tqcOVHd1dTGXqNOXUjrXRRNLeqGuNoa62hgAUDZvwym4IZc5QkQzpmlqAHhBQakYAY+GgREL"
        "n51PIerXoZjnuCBCKueisSGI5jVhSMXQNFJSsVrA2XJCYgDTV4qYSBfxT2rOJ9JFTF9xwWWhQiOqCgbEVbgLZPPgC52R3YdeS07+"
        "m2RmVnwdk1KqjGXxrhcPuwBiADA4OKgv4dCVjFClwJlfLJz6KYlqvw5ZGkkQkMxJ7Lw9iOY7whTy+7ljz9PU/9abLWcnzny49dat"
        "DjNr+rLrQ8CM5aIoUeIKEERwXIWV4QDO/XEO3/35A3k9FRAz2WNNtzTtY+ZWIvrtf0M+/nU33/DyTTzw85f8xfmzHN4fKxwbepeZ"
        "eTTJyarrQo4FdFzOSmxv8OPhNRF8O/Y9Oj6OA2CsCMYQC9Yg6A1UdJzoLK6rv3P1xlUb9i6rQ6EBmbwEAcjYChUaQWiEH/8aRu9z"
        "PYj4I6ivqYchDHzyUh+SVlIMjX7DG1dt2LGgoNAIliPR2BBCY0OgvA2YGcwSGmmoDkRhCAO6EIj6o0hn05BKAoBYPKGqEIIBsCoT"
        "qQJBI+Cu+nV47J3d8BmVdPrgScQCNWg80oSp9JQ61X5SB/DVvLB9Xg8B7LfyecrZjpbP25SzHcrZDtm2Q7PZHG1ZfS+98lA7pbMZ"
        "NZ1JqJHJUXUpfck9/Ei7vu3m+yYBvE9gJnR1UfMUvB5v8XQoENyklKuIr20REaHgurgxFkXH3ie1kfQFY/jiMFzpYm3dWuy87YFx"
        "AK1ENEzlX0Bzm+ljyq20sllmKRe8h4bHg5Gx3+n5xx8Vr+9/dgeA7SVWhizL+iAYDCaYWfsPc/slDBasey0AAAAASUVORK5CYII="
    ),
    "folder_add": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAADMUlEQVR42sWUXUjdZRzHP7/n/3he9BxNPb7MNkerZHPDlTfVRghJ"
        "W1vEiK0i66IXy6teEFZExLQRI6ioqy5aMK2bWrVeLoKulA2WOnuhllbDjcWcUzlqM8/xnP/z/Lqw3BzGDIJ+8PBc/B6+z+/lwxf+"
        "45C/76Z9+4LlHvR2dDhElP8rBODJ9vbUmWx563QuGoVwIeMNyZhzVfHJ984lEucqf8KM1+P/Sai3s9MBagFGsiWt99SlDzTEfyav"
        "BQBYyTGSX8dnQ9eU9b7e2b7SCi2AESKZufkwnffhvHcWFaKB92MXs2YqG2va+ugrHUZEvOqSWYqqGhshbucmq6tOv9vV2TVvAaKa"
        "17P5UmviFag3VgRUhaLSLI9UDzUGBZHG5arxCmJCTs/UcuLUdcXAAQuQzhTyQO0vPLT1K5iLw+JSBcAjfvnZOYGiTPjlYJPtPdmw"
        "7lLLQM4FMBcjl40RLKXE/HUu+8QAgvNCxATMO2tFfG5RcLEWowSiVwpeoe3x+SkUB95AmEVwiBTIEsGrA2bAZfEYzOqHoeRWAg0g"
        "/Jr8yVHmMhdFVWWFggZ8Fo1UYeoPcnw0ZOCb7wi94+ba3dy5q47v04dzIqJmZex7vAqyqZu3+3/k3je3s76ikobqa7nvrZ2ma7Cb"
        "/c883qyqJWYlrfr8DKZmD32jjs6PnkYxVBavYkPNRgqjCfPiBy+547/1bQQes4uEKuAXNrdoGQDG4LzHJrfQ920/3U8corQoxdrU"
        "WiJBhE+eOkx6Ni3Hho/pbWtu2W4XADU2al1IYSaMCJdxCEhAEGQg5gi9M0aMKU+UEQki2CCgrKiM6T+mCb0DCCxAMjp/YTi92n46"
        "cLtVX7DErUQCspkprncZttx4E3e/us0XxRLmi2ePUJFIse21HZyfPu8/33vEAj0WkA3xmUODvxaXHx1urFXnvOolkI2B0Kus+uGs"
        "//CNlh37H3x5zXPvvxBemBk3E79PMjY95p/ftdc233DHKPCO/BuvU9U64OOeU72b+kdO4HzI5trN7Ky/6wxwv4gMXNWxAeiBlpYa"
        "aWtryw9NTCTXp1KtQDMQAEdnZ2cPJpPJcVU1fwIFpky6KU0TnAAAAABJRU5ErkJggg=="
    ),
    "undo": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAACg0lEQVR42tVUUUuTURh+3vN9c03FZihsI73XSFcNyrrRi4KuulK6"
        "CQKpyCgIdGY331YUKrPyQsh/EPMnSGoX1UVq4lIiCMOwTTTZltvavu+ctwt1uM0MwZuey/O+POd5zvO+B9gXTDgkEAwWh0O1i6i2"
        "61PlwZUUkE3qCLZZAODq+zxMZjYerdh4DEAHWi2cAKOD5IFucPlnGtwPFl/X9SfZ3TPfW9LQHtbAf3/brYJhCCAgPJnINdZsL0jY"
        "qqAsyVb2DZOYACsSNodD5VLLsdCp0TzxWIcsJWxnDWMk3f65e5qzflglolDKMglsE45qCMdRMDNICKh0HNLc7BLJzfCPkbM/YRgC"
        "waAqVkgwDDq2cbnS7ii/A1H2iATprKSENGdB/AGkaVDSYhIturPutEzGvgvOXl8Z8E7AYIEgqb1DAeDujlyAro3ozuPNufWl3tVQ"
        "82C+5p+/CJsjJHR7k8rE46auN64/bYjBCNCOUlGccjR08i020uetX7FXRKiGManj7hc7bk7booNN41r64zmVSbzXqlxO3TSvAsRA"
        "6z4z2x7W8on3zdYWbMz9dw4A8PREeur6E9LtnxvNj9s29BLCsQ4Jg/UzHtDMLVrbap4CotOE574MACjCJWHlBEgs7T/Y/4Cne74F"
        "9vInEKKNc+nfyrIaV4e832Aw7QRTqJCZEAC5UpEbouxIPZvZFEMJEBGYmVld0RxHfTK1nmSWnatD3qXilPWCHSZSNQ8XXVp51UtR"
        "UQNIE6BtE0oBQkAmVsYtK3N7LeT7WkxWanlboTuz0Amb3Uu5tGJiAQgm0hh6mWQr8Sw64FvevfeH+iMVQ9/zNMwaFqb2CKwVQEAV"
        "2/y/8AcbVRzJBecjUAAAAABJRU5ErkJggg=="
    ),
    "redo": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAACgElEQVR42tWUz0tUURTHv+fe92YcR8bJFOdpStCmEkUsN20yo/6C"
        "HNoHBbmwHzpaUePblKQgBBUWQtAmjBatWkSMm5JgtBkrWwamzkRio+VMM/PePS1U0pkmFdz0Xd4fn/vlfs85wLbFhB1XkAWAnQFX"
        "nP9QkgPeoM1fGWGJjyBgVANgGctl11l3euO39nesQEMazGPWFr6KCW0jMnfZ6JrsrulbYqNn6pUvMH5gaw7bRiSe+m0A8HW+Oycc"
        "7lqVTaVAgolVK2nOoxCaZJVdIjt7Yc5V/xjoVTBNlQ8MBgVMU1W1v92tPCV+qZfcE8VesFIgIqjUIlTqOxiUFULTRakBOzHdEbvd"
        "eAdtLCkvPZNUdXekVZHzkfT4aqzElwliNQYhNbBtg6kZUm8iISUrtqAyN9Kp5N2Fshc/YZqsbXQGLr86ZSjLeiaK3F57eX6SgJ5Y"
        "f+PLtWOVndGAw7un2UrMRGHZ7bGBhtfrPf0BokUAZGnZ6GlZanjtpa9jMvvp+MygP4WzYR1Oj0DZrE1J7LJ+xJ9gIXkm9uBwsnDK"
        "wZAGAEYgMlTTt2hXdb3vAgBcfONa3yG+KxMVG8LLkZYHJvGZrYxQhJMA+jF4ZMWhMcpACHGz6duhIdbH58AwySpcNiuBcOXlyF6h"
        "aVPkKC6CUiGkk9fmBhrGttpJf03ZF4ieIukYlu5yj52YDTPRcxARmJkgFOlOt8r8mo676x+iFwwiLlzYq9CKzvA+XXPdl6XVJ6AU"
        "IMRaBwFSh1qeR9pKVs3fPBhbu1O4U1aTM7rDtaSVXoKVkcw2AYqISbGjWCCbjsRcdcO5DjcbUdvWv6dNMCiAXgGM5u/VtTD8ZOO/"
        "02/5XBZN3/KLYAAAAABJRU5ErkJggg=="
    ),
    "apply": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAD4ElEQVR42nWUX4iUVRjGn/d9v+/bGcddy2h3CepiUwvyz0y1uxrB"
        "KoWiXgV9onSRQYZhDQjCVqbjuEqBIZREfy4SsqTdgeretnUhVFL3j9sOC1JmIl6ka+TM7OzMd963C51Jd9cXzs05Dz/Ocx7OA8w1"
        "GTAyYNxvDBSGocx1RDM3wjCUXC7nACC5v3OxauVpc/Q4gxisf0K84dG9Z8dnaucE1gRP7Um2e8L7TLFWGsQjvi0zM+i0mjENoqI9"
        "Fw4O/YwMGFlojVG3Ffbdhi3fk0x7npxiTzbA4EVTkasWq1G1WI2iUuRMjURotRf3+1fsfSaLLDTs+9++1G+Wzbmlu1Nve4ngE51W"
        "0kgdEfGsBYKLnLtV+tdijbE1zStb/YF0f38YhpLP541qNpe//2yKfDtnzgwKAs0OhYjgVMFE6GzrsJEro24a0x4brR3JnD8R9oXC"
        "CGvBuQ/ZYzY1mwtWAxbKBby7sRtfbv2M3tvYTcVy0cjxoTAMJTeeM85tyrnUO6lFxPSCKzsTFmFiMN3L9NjDjcIkdq5LY3PnJgDA"
        "H39fEquakU8rJhb/3o4slAEgCrhdGkQA6FR1ikqVEkqVEoQZBoMnHq4XbuCVlZuRfvEtAMDxM9/hyE+fojHWqPBgJPRcPWVWtLEI"
        "pipT1tnWga+3HcW6pWtxvTCJuB/HZPEm1jzZhexLGQDAwMRJ7PtxP5riTTAzmIEAbQMA7/b7gZkI5WoZG5avR2dbB5KProCZoffX"
        "PnS2deDwlo8QSIDfro5j5/FdCPwATAxnDjVGHQjgsnMOTfEmfHziCJa0LkbqsSQObzmE+bEEtj7/KhYmHsS1f65hx7E0ylEZ84I4"
        "nOqdsGBsfLluWaBno2lnvvgyWZjEtqPbMXrlAnzx8cHLB/FE6xIUp4vY8U0aV29eRSKYV4cBYI2MnKMzAMCZTIaHDwxPmNNT8EHx"
        "IO6KlSJe/+oNjPw1CgBQU+zq7cbw5REsmLcAkda+rzkJhFwluqhB6TQMJM3NzZzP57Wl65GLLPSac04bpIGKlSL15wfQ2tSCY6e/"
        "xffnf8BDiYV3wWAGOGkQ0arbPt4zNtaFLo/uLoVlu1P7/EY/Uy1UI2amyDkpVYoQ9jC/IQE1raHUAPUbA696q/rF2IGh7TWGAEA+"
        "n7ewL5SBdP/Aw6tafIl5q4nArNBYEHeB+OpMFYASAPaFJSYcTUWfj/UMvXkHprP7MAwFuZxbtie5nkWyxNTOHsPqXw/QSKHOxqHa"
        "c2H/cC8MdIdicxZsDQoAqWz7KjPXoYpFgDGILhHo3AMn5/8yODgYzezC+8796v0eTd/cmv8AgGHcm7RYOQEAAAAASUVORK5CYII="
    ),
    "up": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABmUlEQVR42u2TS0tbQRTH/2cy98YriKEg5NWVK11IaUJBcWFwF1dC"
        "u3Lvrgg+oK6m1y6T5gP0I3TrA1Qwu0QkkXZjv8GFdlGy0IS5d7ynC/Pwlahtl/5Xw8w5v/Mc4Fn3SikBxeL/wbrnf4W++xoBgNT7"
        "4/TYem38+t1fZFaWABBfO51MfDj7ldj80UysfpttZyr7uYm+MDdn4iv1CbKGDigixwjkIDq0nVyvT8Ml0wn4MPA6zHEOhT2cYr91"
        "wcZvkLRjLIf3rqC5e6E0CEZWNMWXgaZAL0DwbxbRMkXsUTZ+g0wz7xUzVSiWcMncBSoWcCm8ATO+Do1++7PwagcAkqsnM2yP7JK0"
        "Y1fQIO8Vp6od317JSgl8BMc36llynH2St2CKJRRLr/SmQqaZ75Vv7SQ3vs/DBXdWqt3DOQEiJlhbMpZ+yUb3YMs1Cy6ZziC8YqZK"
        "fmuBjW7I0fiLEPgMEN8aylwIACGocKnPj9j4S13Yl2zQbUt7EF7pdSUM9CIH+gjMnx65hwN+xYA36mvYbvKjoA/ZPutJ+gPJQ8+/"
        "KoqpFgAAAABJRU5ErkJggg=="
    ),
    "down": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABmklEQVR42u2TPS9DURjH/89xz22LSGPQ9l5foJEgiChLG5vBxNAv"
        "YBXcSljqklgIuw/QwWLBYrBILK6mGhE7FZFILbgc5xhuSW+0BJv4b+d5+Z1znhfgX78V+U5ZxdABwikUbJKfZn4n9j2hri/Lvkj2"
        "AmKZQo9pl3KRmXzSs+9rH2M9mzl13GUuXuUimWKqmlG5KckqBVhiwZY044EtY/p4EHZK+KDZfQ12SkRnnbjUAztMb0oTqTXPuQAA"
        "qAQnJaCIZHFdlC8GSNNbFWjHsJyRkt17+A61UyI66cSJhfZIC5ji7vIBCsvVvSBfzWyShnWSUBrfJU0PK/FUJnE/UlrtPQSA6KQT"
        "p1Boj3jAVOLJlcIdu17p3n7LrdFl70uG5SSU1uhBX57LEO6wZPotIxwQ1/2wiSOOjb7n2mNTA8p4KCwf724UyG0INrdL4daF1Qb6"
        "oCcJxfkuEQtDSSiQK8VjXdhXc6gBQMzKD8Xmzu6N+XNlZAqjAICJI/6zPRrfbACANsvpjMzm+6ttP1f1xny2Pd+G/vplf1av5G++"
        "mwrAnSsAAAAASUVORK5CYII="
    ),
    "plus": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAC2UlEQVR42qWVTYscVRSGn3PqdlV1V3VrZ3Dj+AsEP8jEtVkFIbrM"
        "IiuRmHUILsSFtlkI4kh+QIyBgNvoQsk6QhxGUBhC0iIMLiLTSyeaidOp+3Fc9Exn+sNscqEK6l54zn3f81HwZAnPtuTwJYABvPbx"
        "2mlavI5PYqZPDZCIqMtAZHhn8Mu3BwyRwWCgl7jEK/H41Vbt3rMEModSzRAgpjizbwaSCf6h/37/hX/ObP+17eXwZlnlfvCPGo8t"
        "St8b72EY3bK7TGdq9fLc/x3ev/PZr1/rJJKdwCxhiIi4w0dVXUjBnX/znLt46oJLZu7ouYg4A03Bkqm9AeAARCQCCqSpTBHG4TEv"
        "Pb/KR29/CMDt7Q227m9R5RXJ0owrIhY5gGBzMkUERMgko4me3X93iSlSZDnY5FzmjD5kuEVPhCY0qCo+eZrYICJkmuGjxyePj56Q"
        "InnWWvB0AdjEhtX+Kk1oaGJDv9NHRQHotXusVMeoiprC5YwejJCDswWgasbeeJfzJ89x8dQF9psxIoKK0C0m2b18dp0QA2ZGO29z"
        "/adv+OLmOsfqkjAPlEm2qfKKslVStsoFOXVRz3x3yxozW37DmCLddpcrP17l9vYGedbCp8BzZY/LZ9epi5pPvvuUe6Mh7VaHmALD"
        "0W9URUVM6f89zDRj6/4WIPjYsFKtENJE0L2dIZt//ExddDFLlHm5kG23rE+rvEJE8DGnKirMjJginbxDXdTUxaQOkyWMJZJFZneT"
        "JRQhpEDhCvqdPgDB4hQ0V9hThjsYHe5ol0ygRp7l7DwYceXWV9Rll+HOkHbexuZgQMLETYFJuJupqCDBzMJcT/H5zS/BjKqoUFHS"
        "rKCoTlxMcndSLQN07cW1rPnTbuS91jvJz84vAVR1asVslRjqFP/Qbzwel2/93tl49GTAniF79eUT76J2HJ/E5Gh/61TZNJBhOEWQ"
        "Ybvrrm1+sLm/bPQ98y/gP3ArPXeom2S+AAAAAElFTkSuQmCC"
    ),
    "delete": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAACW0lEQVR42rWUzU8TURTFz7t902kxCjFhA2qMdiYzo2FDNBIaGoyr"
        "xp3Qfwf9d9gZiR8xpAwtNAGUSGI6gbU7JWCCpdOZe13AS6akRePHXU0m5/3ee+fed4D/XUsALQH0T3QCqMw3XQYbtGYgbNNxJldL"
        "pbsAsAzkLurMv3qpdKPhOHcuQsnsqADZCYJbIPo0all7Ddct14C0XqloI65XKroGpOtBEFzR+qOt9eeW604pQMyNdN/2SlkArmml"
        "LJvoVdPzquUwbBnofBgma47jF5nfaaLxVASJ1oU+RNaXFwC3XLdMRCsFotEu81EMVMtR1AKANcfxR3K59zbR5Clz3GOulff3X8rZ"
        "DbkPaPypAWnT82bywGubaKwncnwi8jgvcpgj2rCVmohFurHIwmwUrZg1fR6aMp6Vo6gVA9VY5HuBaFQDb1OlmiNEEz3mXucctjM9"
        "bWVhQ8t41vC86S3f/7Lt+7Ll+7LteYcN33+S1VysSwdTi3wDEAsAFgGUSlSSfL1sDQ06nekmEW0WiW7HzD9S4NgmGs9rvd70vJn5"
        "MEwGnXJgU7LdjJnjWKkqgEMbqFtK9XV/aFOWAKoBacP37xUNTKTbAZ7Ntturs+327glztct8ZBONWcAbM/zZp6gM7DkgH4LgZi9N"
        "dwu53PVEpNsRWZiLopXsYJuRsojGeswdTtOZRwcHewIoBXCWLDGQB3CVRdBlrs2dj8Z8GCbGs3IUtU6ZnybMHU1UZMA+e85DwmHD"
        "8+6HjvMQAJYXF4eGw7rrTm247oPfSpxfxZf8TnxlxYNi6091f10/ATGjKrvXaKghAAAAAElFTkSuQmCC"
    ),
    "clear": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAADKklEQVR42r1UzWtcVRw9v/vue28mrdpx0fiBKS3YwhOptIgiigj9"
        "CyqZlTsXwU0WulEU3szCNpsuKm4ibty4CQh25aILRYQQcGNloKJFqKZNJmY6mTcv7737cVxMEmcmqTs9q7u4v8M5v48D/AvSNFVp"
        "miqQAlJISpqmCv8n5J8nJU1b0ul0pNG4pHq9m94/dfY1HeolV5o6BAyjyFRFeVVt/Po1kARAxyVJwnarRYhwivAw3lz84EoYxu+4"
        "qvqCoOgovlyZ8ruvPrn61kMVpmmq2u22v7z40bNBIJ/TuQqAB0hSzimlTnnvewCgAnmMzm9C8BMgAgCB1sd8Zd9d+fTKWpqmSu8z"
        "a7gY0HMQ0d77GSWiRFDA+7si0ABA74cQaIG85AEKkImIgrAOAJ1ORw5Znl/88FUoWTbGRCQDEgpC7rVZlIiH0IVhCNC9t3J96cZ4"
        "/YHCi8vL4Y8LC6afDV9+8cL55PULz8OT0FqD9AAEIgJrDbQKsPrzbXy/uvoGgBv7tQBwsFNnbjY8AFSmvOut5dnTc6Yeh/xj/R4H"
        "2ZCDQcY/791nHIY8d+aUUSBLY34HIMfX13lIIbAymhKD7k6WyXCYB/3BUG798hueeWIWlTXo9QeIwhBzT85KP8tElOoC4MnOc0cR"
        "7o1dqa08z1lZq+IwRC2OEccRRAlmajHCUMNYp/K8gHeyOV1/YDlJEgKAquFBURTGOAcISHqQBEl4PxJirJU8zxF4bo+7myBst1sE"
        "gAbq/crYnaoykKklIAgRYWWt5MWucVpvj4uZINw/mvlLFzNj7U5RGQRKkZyyJILKWBhjs+Mz9f64mClCEKQ0m01nvd8uygpKqQnL"
        "5EhhWRkYY3eefuF0Nh0JE1E032wqAHDWdfOihHUOQRCAJAKlQAJhqJnvFjDO/vXZwoIBKQCOnvJmkggAOOe7eVHYV84n9uTjDWod"
        "ABBYa9E48ahbu3WbznELANJWS9oPI9xHFOnunfUN/c0Pa9p5P2EpUKLv9/qIIr0FAN+OXPoj8nB0rIDw7cWPZzfMg/eL3TIe/R3v"
        "jEe9VuMjJ45d+3KpfYekyF4W/if4GwJGtJiRCEubAAAAAElFTkSuQmCC"
    ),
    "app": (
        "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAGNklEQVR42s2aS2xcVxnHf985547nYafxI2mcRKKJBTRQ01ZkgUoX"
        "7KtCrWJXLJCKGggvIYEIbTY4RlUkpwgWBCkogLroakwS2rIvuwhVBfLARYCNCElslPrteMa+95yPxbWTOLEnMx6/zvbe+c/3O+f/"
        "ndd3oWJTofc9R1Etm9261dL7nkNVKr22+sPuomWgx99lUTn42vCORG6bjYxbGpr0Pzw2TZ+EZTAD4qsHWAx+//eLuZB98kuqoUvV"
        "fwYNuwCLVkRfW7urGUTsRyJmEHinpLfPT/QfnqJXzTKoVQEWg9/zo0tfFpt93bjMJwHUL6DBb4p7xFjERiAGjcvX1Mc/GTnV+ZsU"
        "AgXRlQGKaukRv+fYlZM213Rck3k0LvnF12QD+r3SeCig4jJOMgV8eersaH/nN9IO7g5LEPJAzx+7dNIWWo+HuYkEDQYRw1Y21YCI"
        "N/mWyM/e+u3oT59+5d78TAGKRUtPj28/dvkFk9txIczPxqh3IML2abHJt0T+9kffGn3jqTNLMQuooLD/Bxez3hUGJcp+TOOybnnP"
        "rzQSNgPBT5GUPzHys8NjqGLo/aNFRIPLf9FkdzymcTlsu+ABRAx+IZhcU7Pa6KuAcvQDZxj8gqZLlulWlmf4yjrgjOCMrIvBatIT"
        "EfWJIrwIQPtnffqTXjXtpct/F5f9eKURMAKxV2bmAygUGgxZJ3hdW/Ar6TU4IeiqNlJsJBrisVgzB8beODTjAA6Wh5vmoJXgV13c"
        "jEApVloLlq8/20bkhHN/nuTa+AI7spYkaM3Br6R3fWKBfMasDCGAekTlERfm24AUIJHbBl3d9yIQe2gtWN75dgeP78kCcOTzbfSc"
        "/TeXb5RoyVviKoeikt7zvxzivxMLZJygq8qp0cgIQFXJakWYLnteOtzC43uyzCeB2Cv7dkacP3qAzr1ZJuY8ka0uKVbSKyeBfTsj"
        "jjzbxux8wFaZYDXNNi0FS1CwRois4IPy6I6IC9/s4IkaIe7Xcybt8cjWtvrUBOA19e6dnjRLEG5NEPfricBkKVSwTp0AK4VVD4Ss"
        "ktw1TQbrscbUOxL1tLoBVLnj462AqBtAJB123SKINQMsLTQX/jrJ0K15RMAH3XSIOgBSgkvXSzx/eohbs8md4DcTom4LNecdH46U"
        "ePFXw/xvevMh6gZIgtKYd1y5UaLrzFBVEG4dIdZlGk280px3XL1ZrhIiWTeIdTu4pBC2KojOfTlm5xKcke0DAOnevhqIc0cPcqg9"
        "x8Rcsr0AqoXY1eh497sdPLk/t7h9kO0DUA2EKnTsaqDrqZ1r2v9sOMDDIETShVCV7WehaiGMrM+t04Zfn1SC2PRpVCvsidYLolau"
        "mgCsLPetKjQ1mKqsUA1ELXprApiZD4ik24dkMRmXzrL12Cn2a9OrGsCr0thg+N0HE4xMxWSdIesM0yXPmxfHFu9xtCaIKzfLdJ0Z"
        "ZmQqJrKyZj0HIA1eKVmtdOpqcML1iQWeOz3Ey8+0krHCW38a5+rNEo0Npibvxl5pzln+NlLiudNDfO2ZVqJa9AQVm7mnPlBU2/7+"
        "pX9IlDv4sKvFcqLMzaeVnlzGkIuEtU4o1gilOFSvd+dqMZnIS+HAcH/HlKE7rcogZhCbUXiwDnXvDJF1Qlujo63R1RU8pCe4mvRE"
        "gtiMCvqv4f6OKVTF8KnF+pH350UkrRc85Ci5lMTrMZXXpKeq4iJReBsgvV7vw4NKeWH+XChPj+IaBNXAdmuL9vGlmTkXhzfT6/V3"
        "vQFRigNm/Befmw5Bj5tMwSDi2X4tNtlHrJC8fv3nT9+gWLT09YUHi3w//MtZ27j7SJgbi1F1yBbXyVQVSEyhNfJz42+PnursonvA"
        "MNATWO53lcUHfu+rl38tueZXtDyN+iRBRFA1m1pkFQmoKsY6k9uJL03+viXLS4MMJJw4ocj9ZdYliN4TQl9f2Pvq1e9g3I8lyu3W"
        "EKPJAugmOUvSQre4DGGhNEXwp0b6P30yXQGUpeBXu19lqay/+3sXH7X55q+AvoD6Q6g2o2GDP/wwQY1MirH/BP5A8G+N9D9x7a5b"
        "ltfwKnzssfwDi9Zjt5qizExL8LMbCiBx0MKupvHh1zqmVoullgRKP7fp7TVbkLxV/ff/Ab+08zLPlyOfAAAAAElFTkSuQmCC"
    ),
    "bulb": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAC9klEQVR42r2UzWvcVRSGn3PvbyaZCWmS0tEWcaE2xraQlRtLm0nA"
        "rfgBmYhFC0IRqriwdlXw1yzEhQp+oFvBQKGZP0CDi3YKbowLP/pho0FR0yhtbNJ0xsnMvee4yEyNaQaqC9/Vhfu+z7nn3MuFDrJp"
        "/H/ZSzoFpES0d3d3hYIbE3RYES+4C8s1zkjp8qqlOJlEN2elE6z+8e7Hkry85bf5B+lp2f404rL+0qjGE/nD81Ntb0dg27A29UAp"
        "25+cZoeDxCIOA0ARonhWjNpv8eWew9+/vxl6C2gpjkmsdmpoVybRS5l7fS9ZIlFaY7F1u7NIhOaColUd7n72h4sb23e3jjdadAIm"
        "QZ/P7Eq2kSESJMEiaL3FbEJQT4JldnoP8lI728ZsAFbWK3hGyGLgBL0B/Qdh8ENY+xXuewMGRiCsCokzvO03QxitxNuBtObkbACH"
        "IAJmUJiAvgNw/5vQtx/qPwFdgpjg6aOME8GsNb6/geX1tahcQZ0RVqHvIPQMwzePwt3PwfUzcPNrSPKGmaH8Tgk1Wy//T2ChKAAa"
        "7VPqJvis0liAuSNQ/xkuPgUL70HSDwSlgVjgMwHjbNHf3vJYJZoh3d3ZqcZC40dCNkNYDFS/hcx2qM1BuA4+iTTJNK+EP2JX9gMz"
        "hLMV3fodGk4EbZwaeli6dCa5J9muhjlTQRyYGQ4Ji1oPtfhE7tD8TDuz1aUgglqKyz5z+cu4FB7RNfuKvKBeFGeqOYdG5hvX4oHc"
        "ofkZm8ZvhHWUnd+bBQjnHnrF5vaYzQ42bXawaXN7zD4fenujZ7PclsR9+6KlOK96qV7rjrVmjlojZ/W1XIzRn7cUx9WC3vFvUyqP"
        "U54s64mB46UdhR5fvbECQL63l6Wl6sTrky98lJ4cBSp3Btx7YdwAgrkvrq7IzupNf5cTqKksxejPAcJJ/p2KxTQBePzoq+88fSy1"
        "iWOv2ZMvHj8NkKap65STjsQ0dSnw3XIYkUxmDKDZCLNucfiT8vS4ImL8H/oLcSJl+pJEDVIAAAAASUVORK5CYII="
    ),
    "preset": (
        "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAACvklEQVR42q2Vz2tcVRTHP+fc+2beTJJJptJiKIJUEhEhVqLdFac7"
        "XbjTinXlyqVQ6Nhdmq07ty1Cd4JZCP4BNsWu2gZspMWCv1BDjL8mMZNMMr33HhdvJjGdTnTRA3dz77ufe77nfO+7Qj/mTFldcq9M"
        "ztq515dkluHx3mVYmtw05s8EHmuYycNTnjc/dSycjcc/+LoRSrXGOBvp4zcqWsshJFCFlGAiV3IPv2+ZvfuZyY9/7q60RK4wZ8o8"
        "BmIFsH5CgWjIa65Sb2qK1MbHmKgKIQEGeSZcvd3l7lri/OkSed7BVaocv7g8tTIvzSIpYgHci7SVtv8KkXbYWA+e3QJoBmNl4fq9"
        "Hb74NvL2cxViZ5e0ZSa1iQuTza9Y/fBks8hUku6VA1FEPOBV5MAQFZ858SUv3ol4QTxYljobD3Tk6IUnm8vnmZfE3DXvH1XraPsD"
        "g+2u8c6LGa8+66mVhZAMESmaEkIS44X9puwpTjiF7Q68//kOqoVcKZjkXvAKV293WWsbmeutCwrSGQT2uQarm8bgvGGAE8hcAY/R"
        "euUyHQoE2O4mQrJD7AdOoVZ2DPrwXyFASMa5U3WmjuWYGQ871wARYaXV5ZObreFAVSVEmKg6PnrrKcpO/vOi3PiuzQ+biVyHZNiv"
        "0W6AW8t3+XntD0pZhlkhX0R4EAJPjI/RePkkTgU7THJfuKXES89PMTN9otjU2yVSNMc7RYcIGAAahnPK8v37/PJbi1LmBzI8Uhvl"
        "9OzM3kGPBAqWMAuKhBgTM9PPMP10QKXvxOKrhFHyxSEqhIJqaQBoMKLVusfwoxWHw5GXy4d3pTTitTqKtdtj+8DW96l3l2+47np9"
        "bXMjLn7ztzszPUpMhd8OGLz3S7uzssNPv67HrBRcTPJlsdpIPO6QA08AKCxilxr/a3Pj0iLXacC9BWPhbAT4B+4eLKxBOyhnAAAA"
        "AElFTkSuQmCC"
    ),
}


# ----------------------------------------------------------------------------
# Configurare, istoric, presetări (persistente)
# ----------------------------------------------------------------------------
def config_dir():
    if IS_WIN:
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    path = os.path.join(base, APP_NAME)
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    return path


CONFIG_FILE = os.path.join(config_dir(), "config.json")
HISTORY_FILE = os.path.join(config_dir(), "history.json")
PRESETS_FILE = os.path.join(config_dir(), "presets.json")


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)
    except Exception:
        pass


def detect_lang():
    for var in ("LC_ALL", "LC_MESSAGES", "LANGUAGE", "LANG"):
        code = os.environ.get(var, "")[:2].lower()
        if code in LANGS:
            return code
    try:
        code = (locale.getlocale()[0] or "")[:2].lower()
        if code in LANGS:
            return code
    except Exception:
        pass
    return "en"


# ----------------------------------------------------------------------------
# Traduceri: cheie -> (română, engleză, italiană)
# ----------------------------------------------------------------------------
_T = {
    # --- general
    "title": ("Nomina – Redenumire fișiere în masă", "Nomina – Batch file renamer", "Nomina – Rinomina file in blocco"),
    "add_files": ("Adaugă fișiere", "Add files", "Aggiungi file"),
    "add_folder": ("Adaugă dosar", "Add folder", "Aggiungi cartella"),
    "subfolders": ("Include subdosare", "Include subfolders", "Includi sottocartelle"),
    "remove_sel": ("Scoate din listă", "Remove from list", "Rimuovi dalla lista"),
    "clear": ("Golește lista", "Clear list", "Svuota lista"),
    "undo": ("Anulează", "Undo", "Annulla"),
    "redo": ("Refă", "Redo", "Ripeti"),
    "rename": ("Redenumește", "Rename", "Rinomina"),
    "language": ("Limbă", "Language", "Lingua"),
    "layers": ("Straturi (în ordinea aplicării)", "Layers (in order of application)", "Livelli (in ordine di applicazione)"),
    "add_layer": ("Adaugă strat", "Add layer", "Aggiungi livello"),
    "presets": ("Presetări", "Presets", "Preset"),
    "suggest": ("Sugerează", "Suggest", "Suggerisci"),
    "move_up": ("Sus", "Up", "Su"),
    "move_down": ("Jos", "Down", "Giù"),
    "remove_layer": ("Șterge", "Delete", "Elimina"),
    "clear_layers": ("Golește toate straturile", "Clear all layers", "Svuota tutti i livelli"),
    "layer_settings": ("Setările stratului", "Layer settings", "Impostazioni del livello"),
    "no_layer_sel": ("Adaugă sau selectează un strat.", "Add or select a layer.", "Aggiungi o seleziona un livello."),
    "layer_enabled": ("Strat activ", "Layer enabled", "Livello attivo"),
    "files_preview": ("Fișiere și previzualizare", "Files and preview", "File e anteprima"),
    "col_layer": ("Strat", "Layer", "Livello"),
    "col_details": ("Detalii", "Details", "Dettagli"),
    "col_source": ("Sursă", "Source", "Origine"),
    "col_dest": ("Destinație", "Destination", "Destinazione"),
    "col_status": ("Stare", "Status", "Stato"),
    "col_folder": ("Dosar", "Folder", "Cartella"),
    "st_ok": ("Se redenumește", "Will rename", "Verrà rinominato"),
    "st_same": ("Neschimbat", "Unchanged", "Invariato"),
    "st_invalid": ("Nume invalid", "Invalid name", "Nome non valido"),
    "st_dup": ("Duplicat", "Duplicate", "Duplicato"),
    "st_exists": ("Există deja", "Already exists", "Esiste già"),
    "st_missing": ("Lipsește", "Missing", "Mancante"),
    "drop_hint": ("Trage aici fișiere sau dosare\nsau folosește butoanele de sus",
                  "Drag files or folders here\nor use the buttons above",
                  "Trascina qui file o cartelle\noppure usa i pulsanti in alto"),
    "drop_hint_nodnd": ("Folosește butoanele de sus pentru a adăuga fișiere.\n(Pentru drag & drop: instalează pachetul «tkdnd» sau rulează pip install tkinterdnd2)",
                        "Use the buttons above to add files.\n(For drag & drop: install the “tkdnd” package or run pip install tkinterdnd2)",
                        "Usa i pulsanti in alto per aggiungere file.\n(Per il drag & drop: installa il pacchetto «tkdnd» oppure esegui pip install tkinterdnd2)"),
    "stats": ("{n} fișiere · {c} de redenumit · {e} erori", "{n} files · {c} to rename · {e} errors", "{n} file · {c} da rinominare · {e} errori"),

    # --- tipuri de straturi
    "lt_replace": ("Găsește și înlocuiește", "Find and replace", "Trova e sostituisci"),
    "lt_digits": ("Înlătură cifre / numere", "Remove digits / numbers", "Rimuovi cifre / numeri"),
    "lt_trim": ("Înlătură primele / ultimele caractere", "Remove first / last characters", "Rimuovi primi / ultimi caratteri"),
    "lt_brackets": ("Înlătură paranteze și conținutul lor", "Remove brackets and their content", "Rimuovi parentesi e contenuto"),
    "lt_special": ("Înlătură caractere speciale", "Remove special characters", "Rimuovi caratteri speciali"),
    "lt_diacritics": ("Înlătură diacriticele", "Remove diacritics", "Rimuovi i segni diacritici"),
    "lt_add": ("Adaugă la început / sfârșit", "Add at start / end", "Aggiungi all'inizio / alla fine"),
    "lt_insert": ("Inserează text la o poziție", "Insert text at a position", "Inserisci testo in una posizione"),
    "lt_number": ("Numerotare", "Numbering", "Numerazione"),
    "lt_date": ("Dată și oră", "Date and time", "Data e ora"),
    "lt_parent": ("Numele dosarului părinte", "Parent folder name", "Nome della cartella superiore"),
    "lt_case": ("Litere mari / mici", "Upper / lower case", "Maiuscole / minuscole"),
    "lt_style": ("Stil de denumire (snake_case…)", "Naming style (snake_case…)", "Stile di denominazione (snake_case…)"),
    "lt_ext": ("Extensie", "Extension", "Estensione"),

    # --- editoare: comune
    "position": ("Poziția:", "Position:", "Posizione:"),
    "pos_start": ("La început", "At the start", "All'inizio"),
    "pos_end": ("La sfârșit", "At the end", "Alla fine"),
    "pos_from_start": ("După primele N caractere", "After the first N characters", "Dopo i primi N caratteri"),
    "pos_from_end": ("Înainte de ultimele N caractere", "Before the last N characters", "Prima degli ultimi N caratteri"),
    "pos_n": ("Caractere (N):", "Characters (N):", "Caratteri (N):"),
    "ps_start": ("la început", "at start", "all'inizio"),
    "ps_end": ("la sfârșit", "at end", "alla fine"),
    "ps_from_start": ("după {n} car.", "after {n} chars", "dopo {n} car."),
    "ps_from_end": ("înainte de ultimele {n}", "before last {n}", "prima degli ultimi {n}"),
    "apply_to": ("Se aplică la:", "Apply to:", "Applica a:"),
    "fl_all": ("toate fișierele", "all files", "tutti i file"),
    "fl_ext": ("doar extensiile", "only extensions", "solo le estensioni"),
    "fl_not_ext": ("fără extensiile", "all but extensions", "tranne le estensioni"),
    "fl_has": ("numele conține", "name contains", "il nome contiene"),
    "fl_not_has": ("numele nu conține", "name lacks", "il nome non contiene"),
    "fsum_ext": ("[doar: {x}]", "[only: {x}]", "[solo: {x}]"),
    "fsum_not_ext": ("[fără: {x}]", "[except: {x}]", "[tranne: {x}]"),
    "fsum_has": ("[conține: {x}]", "[contains: {x}]", "[contiene: {x}]"),
    "fsum_not_has": ("[nu conține: {x}]", "[lacks: {x}]", "[non contiene: {x}]"),
    "strip_sep": ("Curăță separatorii rămași (spații _ - .)", "Trim leftover separators (spaces _ - .)", "Pulisci i separatori rimasti (spazi _ - .)"),

    # --- găsește și înlocuiește
    "find": ("Găsește:", "Find:", "Trova:"),
    "replace_with": ("Înlocuiește cu:", "Replace with:", "Sostituisci con:"),
    "case_sensitive": ("Sensibil la majuscule", "Case sensitive", "Distingui maiuscole"),
    "use_regex": ("Expresie regulată (regex)", "Regular expression (regex)", "Espressione regolare (regex)"),
    "regex_error": ("Regex invalid: {msg}", "Invalid regex: {msg}", "Regex non valida: {msg}"),
    "sum_replace": ("«{a}» → «{b}»", "«{a}» → «{b}»", "«{a}» → «{b}»"),
    "sum_replace_re": ("regex «{a}» → «{b}»", "regex «{a}» → «{b}»", "regex «{a}» → «{b}»"),

    # --- cifre, tăiere
    "digits_all": ("Toate cifrele din nume", "All digits in the name", "Tutte le cifre nel nome"),
    "digits_start": ("Doar cele de la început", "Only at the start", "Solo all'inizio"),
    "digits_end": ("Doar cele de la sfârșit", "Only at the end", "Solo alla fine"),
    "sd_all": ("toate cifrele", "all digits", "tutte le cifre"),
    "sd_start": ("cifre de la început", "leading digits", "cifre iniziali"),
    "sd_end": ("cifre de la sfârșit", "trailing digits", "cifre finali"),
    "trim_first": ("Primele caractere:", "First characters:", "Primi caratteri:"),
    "trim_last": ("Ultimele caractere:", "Last characters:", "Ultimi caratteri:"),
    "sum_trim": ("−{a} la început, −{b} la sfârșit", "−{a} from start, −{b} from end", "−{a} all'inizio, −{b} alla fine"),

    # --- paranteze
    "br_round": ("Rotunde ( )", "Round ( )", "Tonde ( )"),
    "br_square": ("Pătrate [ ]", "Square [ ]", "Quadre [ ]"),
    "br_curly": ("Acolade { }", "Curly { }", "Graffe { }"),
    "br_angle": ("Unghiulare < > (taguri)", "Angle < > (tags)", "Angolari < > (tag)"),
    "br_content": ("Înlătură și conținutul dintre ele", "Also remove what is inside them", "Rimuovi anche il contenuto"),
    "sum_br_content": ("cu tot cu conținut", "with content", "con contenuto"),
    "sum_br_only": ("doar semnele", "symbols only", "solo i simboli"),

    # --- caractere speciale, diacritice
    "sp_unsafe": ("Caractere interzise în nume (\\ / : * ? \" < > |)", "Characters forbidden in names (\\ / : * ? \" < > |)", "Caratteri vietati nei nomi (\\ / : * ? \" < > |)"),
    "sp_symbols": ("Simboluri (rămân litere, cifre, spațiu _ - .)", "Symbols (keeps letters, digits, space _ - .)", "Simboli (restano lettere, cifre, spazio _ - .)"),
    "sp_nonascii": ("Tot ce nu este ASCII", "Everything that is not ASCII", "Tutto ciò che non è ASCII"),
    "sp_custom": ("Doar caracterele din câmpul de jos", "Only the characters in the field below", "Solo i caratteri nel campo qui sotto"),
    "sp_chars": ("Caractere:", "Characters:", "Caratteri:"),
    "sps_unsafe": ("interzise", "forbidden", "vietati"),
    "sps_symbols": ("simboluri", "symbols", "simboli"),
    "sps_nonascii": ("non-ASCII", "non-ASCII", "non-ASCII"),
    "sps_custom": ("personalizat", "custom", "personalizzato"),
    "dia_note": ("ă â î ș ț → a a i s t (la fel pentru toate literele cu accent: é ü ñ ç ø ß…). Nu are setări.",
                 "ă â î ș ț → a a i s t (same for every accented letter: é ü ñ ç ø ß…). No settings.",
                 "ă â î ș ț → a a i s t (lo stesso per ogni lettera accentata: é ü ñ ç ø ß…). Nessuna impostazione."),

    # --- adaugă, inserează
    "prefix": ("La început (prefix):", "At the start (prefix):", "All'inizio (prefisso):"),
    "suffix": ("La sfârșit (sufix):", "At the end (suffix):", "Alla fine (suffisso):"),
    "suffix_note": ("Sufixul se adaugă înaintea extensiei.", "The suffix is added before the extension.", "Il suffisso viene aggiunto prima dell'estensione."),
    "sum_add": ("«{a}» … «{b}»", "«{a}» … «{b}»", "«{a}» … «{b}»"),
    "insert_text": ("Text de inserat:", "Text to insert:", "Testo da inserire:"),
    "sum_pos": ("«{a}», {b}", "«{a}», {b}", "«{a}», {b}"),

    # --- numerotare
    "num_start": ("Începe de la:", "Start at:", "Inizia da:"),
    "num_step": ("Pas:", "Step:", "Passo:"),
    "num_digits": ("Cifre (1, 01, 001):", "Digits (1, 01, 001):", "Cifre (1, 01, 001):"),
    "text_before": ("Text înainte:", "Text before:", "Testo prima:"),
    "text_after": ("Text după:", "Text after:", "Testo dopo:"),
    "num_per_folder": ("Repornește numărătoarea în fiecare dosar", "Restart numbering in each folder", "Riavvia la numerazione in ogni cartella"),

    # --- dată și oră
    "date_source": ("Data:", "Date:", "Data:"),
    "ds_created": ("crearea fișierului", "file creation", "creazione del file"),
    "ds_modified": ("ultima modificare", "last modification", "ultima modifica"),
    "ds_now": ("data și ora curentă", "current date and time", "data e ora correnti"),
    "date_format": ("Format:", "Format:", "Formato:"),
    "date_hint": ("Exemplu: {ex}\n%Y an · %m lună · %d zi · %H oră · %M min · %S sec\nDacă data creării nu e disponibilă, se folosește cea a modificării.",
                  "Example: {ex}\n%Y year · %m month · %d day · %H hour · %M min · %S sec\nIf the creation date is unavailable, the modification date is used.",
                  "Esempio: {ex}\n%Y anno · %m mese · %d giorno · %H ora · %M min · %S sec\nSe la data di creazione non è disponibile, si usa quella di modifica."),

    # --- dosar părinte
    "parent_format": ("Format:", "Format:", "Formato:"),
    "parent_level": ("Nivel (1 = dosarul părinte):", "Level (1 = parent folder):", "Livello (1 = cartella superiore):"),
    "parent_case": ("Litere:", "Letters:", "Lettere:"),
    "ca_asis": ("ca în original", "as is", "come l'originale"),
    "sc_lower": ("minuscule", "lowercase", "minuscolo"),
    "sc_upper": ("MAJUSCULE", "UPPERCASE", "MAIUSCOLO"),
    "parent_hint": ("Folosește {} pentru numele dosarului, ex.: [{}]  ({})  {} - ",
                    "Use {} for the folder name, e.g.: [{}]  ({})  {} - ",
                    "Usa {} per il nome della cartella, es.: [{}]  ({})  {} - "),

    # --- litere, stil, extensie
    "case_lower": ("toate minuscule", "all lowercase", "tutto minuscolo"),
    "case_upper": ("TOATE MAJUSCULE", "ALL UPPERCASE", "TUTTO MAIUSCOLO"),
    "case_title": ("Prima Literă Din Fiecare Cuvânt", "Capitalize Each Word", "Iniziale Maiuscola Per Parola"),
    "case_sentence": ("Doar prima literă majusculă", "Capitalize first letter only", "Solo la prima lettera maiuscola"),
    "sc_title": ("Cuvinte Capitalizate", "Title Case", "Iniziali Maiuscole"),
    "sc_sentence": ("Prima literă mare", "Sentence case", "Prima maiuscola"),
    "style_note": ("Cuvintele se despart la spații, _ - . și la trecerea de la literă mică la mare. Ex.: raport vanzari martie → raport_vanzari_martie",
                   "Words are split at spaces, _ - . and at lower→upper case changes. E.g.: sales report march → sales_report_march",
                   "Le parole si separano a spazi, _ - . e al passaggio da minuscola a maiuscola. Es.: rapporto vendite marzo → rapporto_vendite_marzo"),
    "ext_change": ("Schimbă extensia cu:", "Change extension to:", "Cambia estensione in:"),
    "ext_lower": ("Extensie cu litere mici (.JPG → .jpg)", "Lowercase extension (.JPG → .jpg)", "Estensione minuscola (.JPG → .jpg)"),
    "ext_upper": ("Extensie cu litere mari (.jpg → .JPG)", "Uppercase extension (.jpg → .JPG)", "Estensione maiuscola (.jpg → .JPG)"),
    "ext_remove": ("Înlătură extensia", "Remove extension", "Rimuovi estensione"),
    "ext_note": ("Celelalte straturi nu modifică niciodată extensia.", "Other layers never touch the extension.", "Gli altri livelli non modificano mai l'estensione."),
    "sum_ext_change": ("→ .{a}", "→ .{a}", "→ .{a}"),
    "sum_ext_lower": ("minuscule", "lowercase", "minuscola"),
    "sum_ext_upper": ("MAJUSCULE", "UPPERCASE", "MAIUSCOLA"),
    "sum_ext_remove": ("fără extensie", "no extension", "senza estensione"),

    # --- presetări
    "preset_save": ("Salvează straturile ca presetare…", "Save layers as preset…", "Salva i livelli come preset…"),
    "preset_delete": ("Șterge presetarea", "Delete preset", "Elimina preset"),
    "preset_none": ("(nicio presetare salvată)", "(no saved presets)", "(nessun preset salvato)"),
    "preset_name_prompt": ("Numele presetării:", "Preset name:", "Nome del preset:"),
    "preset_overwrite": ("Presetarea «{name}» există deja. O înlocuiești?", "Preset “{name}” already exists. Replace it?", "Il preset «{name}» esiste già. Sostituirlo?"),
    "preset_saved": ("Presetarea «{name}» a fost salvată.", "Preset “{name}” saved.", "Preset «{name}» salvato."),
    "preset_loaded": ("Presetarea «{name}» a fost încărcată.", "Preset “{name}” loaded.", "Preset «{name}» caricato."),
    "preset_deleted": ("Presetarea «{name}» a fost ștearsă.", "Preset “{name}” deleted.", "Preset «{name}» eliminato."),
    "preset_empty": ("Nu ai niciun strat de salvat.", "There are no layers to save.", "Non ci sono livelli da salvare."),
    "preset_replace_confirm": ("Încarci presetarea «{name}»? Straturile curente vor fi înlocuite.", "Load preset “{name}”? The current layers will be replaced.", "Caricare il preset «{name}»? I livelli attuali verranno sostituiti."),
    "preset_delete_confirm": ("Ștergi presetarea «{name}»?", "Delete preset “{name}”?", "Eliminare il preset «{name}»?"),

    # --- sugestii
    "suggest_nofiles": ("Adaugă mai întâi fișiere în listă.", "Add some files to the list first.", "Aggiungi prima dei file alla lista."),
    "suggest_none": ("N-am găsit nimic de îmbunătățit în numele fișierelor.", "I found nothing to improve in the file names.", "Non ho trovato nulla da migliorare nei nomi dei file."),
    "suggest_ask": ("Ai deja straturi în listă.\n\nDa – le înlocuiesc cu cele sugerate (pe baza numelor originale)\nNu – adaug sugestiile după straturile existente\nAnulează – nu fac nimic",
                    "You already have layers.\n\nYes – replace them with the suggested ones (based on the original names)\nNo – add the suggestions after the existing layers\nCancel – do nothing",
                    "Hai già dei livelli.\n\nSì – sostituiscili con quelli suggeriti (in base ai nomi originali)\nNo – aggiungi i suggerimenti dopo i livelli esistenti\nAnnulla – non fare nulla"),
    "suggest_done": ("Am adăugat {n} straturi pe baza numelor de fișiere:\n\n{list}\n\nVerifică previzualizarea, apoi apasă «Redenumește» dacă ești mulțumit.",
                     "I added {n} layers based on the file names:\n\n{list}\n\nCheck the preview, then press “Rename” if you are happy with it.",
                     "Ho aggiunto {n} livelli in base ai nomi dei file:\n\n{list}\n\nControlla l'anteprima, poi premi «Rinomina» se va bene."),
    "sg_site": ("Adrese de site eliminate ({n} fișiere)", "Website addresses removed ({n} files)", "Indirizzi di siti rimossi ({n} file)"),
    "sg_brackets": ("Text între paranteze eliminat ({n} fișiere)", "Bracketed text removed ({n} files)", "Testo tra parentesi rimosso ({n} file)"),
    "sg_special": ("Caractere problematice eliminate ({n} fișiere)", "Problematic characters removed ({n} files)", "Caratteri problematici rimossi ({n} file)"),
    "sg_spaces": ("Spații multiple sau separatori la margini curățate ({n} fișiere)", "Repeated spaces and edge separators cleaned ({n} files)", "Spazi ripetuti e separatori ai bordi puliti ({n} file)"),
    "sg_caps": ("Nume scrise cu MAJUSCULE trecute în Title Case ({n} fișiere)", "ALL-CAPS names converted to Title Case ({n} files)", "Nomi in MAIUSCOLO convertiti in Title Case ({n} file)"),
    "sg_ext": ("Extensii cu majuscule trecute în litere mici ({n} fișiere)", "Uppercase extensions made lowercase ({n} files)", "Estensioni maiuscole rese minuscole ({n} file)"),

    # --- dialoguri și mesaje
    "dlg_add_files": ("Alege fișiere", "Choose files", "Scegli i file"),
    "dlg_add_folder": ("Alege un dosar", "Choose a folder", "Scegli una cartella"),
    "added": ("{n} fișiere adăugate.", "{n} files added.", "{n} file aggiunti."),
    "err_blocked": ("Nu se poate redenumi: există {n} erori în previzualizare (marcate cu roșu).",
                    "Cannot rename: there are {n} errors in the preview (marked in red).",
                    "Impossibile rinominare: ci sono {n} errori nell'anteprima (in rosso)."),
    "nothing_to_do": ("Nu există nicio modificare de aplicat.", "There is nothing to apply.", "Non c'è nessuna modifica da applicare."),
    "renamed_ok": ("✔ {n} fișiere redenumite. Poți anula cu «Anulează».", "✔ {n} files renamed. You can revert with “Undo”.", "✔ {n} file rinominati. Puoi annullare con «Annulla»."),
    "rename_failed": ("Redenumirea a eșuat și a fost anulată complet (nimic nu a fost modificat):\n\n{err}",
                      "Renaming failed and was fully rolled back (nothing was changed):\n\n{err}",
                      "La ridenominazione è fallita ed è stata annullata completamente (nulla è stato modificato):\n\n{err}"),
    "undo_done": ("↶ {n} fișiere restaurate.", "↶ {n} files restored.", "↶ {n} file ripristinati."),
    "redo_done": ("↷ {n} fișiere redenumite din nou.", "↷ {n} files renamed again.", "↷ {n} file rinominati di nuovo."),
    "undo_none": ("Nimic de anulat.", "Nothing to undo.", "Niente da annullare."),
    "redo_none": ("Nimic de refăcut.", "Nothing to redo.", "Niente da ripetere."),
    "undo_partial": ("{k} fișiere au fost omise (mutate, șterse sau numele destinație este ocupat).",
                     "{k} files were skipped (moved, deleted, or the target name is taken).",
                     "{k} file sono stati saltati (spostati, eliminati o nome di destinazione occupato)."),
    "undo_nothing": ("Nu s-a putut aplica nicio modificare: fișierele au fost mutate, șterse sau redenumite din altă parte.",
                     "Nothing could be applied: the files were moved, deleted or renamed elsewhere.",
                     "Nessuna modifica applicabile: i file sono stati spostati, eliminati o rinominati altrove."),
    "op_failed": ("Operația a eșuat și a fost anulată:\n\n{err}", "The operation failed and was rolled back:\n\n{err}", "L'operazione è fallita ed è stata annullata:\n\n{err}"),
}
for _k, _v in _T.items():
    assert len(_v) == 3, _k
STR = {code: {k: v[i] for k, v in _T.items()} for i, code in enumerate(("ro", "en", "it"))}


# ----------------------------------------------------------------------------
# Definiția straturilor
# ----------------------------------------------------------------------------
LAYER_GROUPS = [
    ["replace", "digits", "trim", "brackets", "special", "diacritics"],
    ["add", "insert", "number", "date", "parent"],
    ["case", "style"],
    ["ext"],
]
LAYER_TYPES = [t for g in LAYER_GROUPS for t in g]

POS_MODES = ["start", "end", "from_start", "from_end"]
FILTER_MODES = ["all", "ext", "not_ext", "has", "not_has"]
DATE_SOURCES = ["created", "modified", "now"]
CASE_ASIS = ["asis", "lower", "upper"]
STYLES = ["snake", "snake_upper", "kebab", "camel", "pascal"]
STYLE_LABELS = {"snake": "snake_case", "snake_upper": "UPPER_SNAKE_CASE", "kebab": "kebab-case",
                "camel": "camelCase", "pascal": "PascalCase"}
BRACKETS = {"round": ("(", ")"), "square": ("[", "]"), "curly": ("{", "}"), "angle": ("<", ">")}

DATE_FORMATS = ["%Y-%m-%d", "%Y%m%d", "%d-%m-%Y", "%d.%m.%Y", "%Y.%m.%d", "%y%m%d",
                "%Y-%m-%d_%H-%M-%S", "%Y%m%d_%H%M%S", "%Y-%m-%d %H.%M", "%d-%m-%Y_%H-%M"]
PARENT_FORMATS = ["{} - ", "{}_", "{}-", "{} ", "{}", "[{}]", "[{}] ", "({})", "({}) ",
                  " - {}", "_{}", "-{}", " [{}]", " ({})"]

DEFAULT_PARAMS = {
    "replace": {"find": "", "repl": "", "case": True, "regex": False},
    "digits": {"scope": "all", "strip": True},
    "trim": {"first": 0, "last": 0},
    "brackets": {"round": True, "square": True, "curly": False, "angle": False, "content": True, "strip": True},
    "special": {"mode": "symbols", "chars": "", "repl": "", "strip": True},
    "diacritics": {},
    "add": {"prefix": "", "suffix": ""},
    "insert": {"text": "", "pos": "start", "n": 5},
    "number": {"start": 1, "step": 1, "digits": 2, "before": "", "after": "", "pos": "start", "n": 5, "per_folder": True},
    "date": {"src": "created", "fmt": "%Y-%m-%d", "before": "", "after": "_", "pos": "start", "n": 5},
    "parent": {"fmt": "{} - ", "case": "asis", "level": 1, "pos": "start", "n": 5},
    "case": {"mode": "lower"},
    "style": {"style": "snake"},
    "ext": {"mode": "change", "ext": ""},
}

ENUMS = {
    ("digits", "scope"): ["all", "start", "end"],
    ("special", "mode"): ["unsafe", "symbols", "nonascii", "custom"],
    ("case", "mode"): ["lower", "upper", "title", "sentence"],
    ("style", "style"): STYLES,
    ("ext", "mode"): ["change", "lower", "upper", "remove"],
    ("date", "src"): DATE_SOURCES,
    ("parent", "case"): CASE_ASIS,
    ("insert", "pos"): POS_MODES, ("number", "pos"): POS_MODES,
    ("date", "pos"): POS_MODES, ("parent", "pos"): POS_MODES,
}


def make_layer(ltype):
    return {"type": ltype, "enabled": True, "params": copy.deepcopy(DEFAULT_PARAMS[ltype]),
            "filter": {"mode": "all", "text": ""}}


def _coerce(default, val):
    if isinstance(default, bool):
        return bool(val)
    if isinstance(default, int):
        try:
            return int(val)
        except (TypeError, ValueError):
            return default
    return default if val is None else str(val)


def normalize_layer(d):
    """Validează un strat citit dintr-o presetare; întoarce None dacă nu e valid."""
    if not isinstance(d, dict) or d.get("type") not in DEFAULT_PARAMS:
        return None
    layer = make_layer(d["type"])
    src = d.get("params") if isinstance(d.get("params"), dict) else {}
    for k, default in DEFAULT_PARAMS[d["type"]].items():
        if k in src:
            layer["params"][k] = _coerce(default, src[k])
        allowed = ENUMS.get((d["type"], k))
        if allowed and layer["params"][k] not in allowed:
            layer["params"][k] = default
    layer["enabled"] = bool(d.get("enabled", True))
    flt = d.get("filter") if isinstance(d.get("filter"), dict) else {}
    if flt.get("mode") in FILTER_MODES:
        layer["filter"]["mode"] = flt["mode"]
    layer["filter"]["text"] = str(flt.get("text", ""))
    return layer


# ----------------------------------------------------------------------------
# Logica de redenumire (independentă de interfață)
# ----------------------------------------------------------------------------
def nc(path):
    return os.path.normcase(path)


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def split_name(name):
    """Separă numele în (nume, extensie); extensia include punctul."""
    return os.path.splitext(name)


def insert_text(stem, text, mode, n):
    n = max(0, int(n))
    if mode == "start":
        i = 0
    elif mode == "end":
        i = len(stem)
    elif mode == "from_start":
        i = min(n, len(stem))
    else:  # from_end
        i = max(0, len(stem) - n)
    return stem[:i] + text + stem[i:]


def tidy(stem):
    """Comprimă spațiile și curăță separatorii rămași la margini."""
    stem = re.sub(r"\s{2,}", " ", stem)
    return re.sub(r"^[\s_-]+|[\s_.-]+$", "", stem)


_SPECIAL_LETTERS = str.maketrans({
    "ß": "ss", "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE", "ø": "o", "Ø": "O",
    "đ": "d", "Đ": "D", "ł": "l", "Ł": "L", "þ": "th", "Þ": "TH", "ð": "d", "Ð": "D",
    "ı": "i", "ħ": "h", "Ħ": "H",
})


def remove_diacritics(s):
    s = unicodedata.normalize("NFD", s.translate(_SPECIAL_LETTERS))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return unicodedata.normalize("NFC", s)


def split_words(s):
    """Împarte în cuvinte: la separatori și la trecerea mică→MARE (camelCase)."""
    words = []
    for tok in re.split(r"[\W_]+", s):
        if not tok:
            continue
        start = 0
        for i in range(1, len(tok)):
            prev, cur = tok[i - 1], tok[i]
            nxt = tok[i + 1] if i + 1 < len(tok) else ""
            if (prev.islower() or prev.isdigit()) and cur.isupper():
                cut = True
            elif prev.isupper() and cur.isupper() and nxt.islower():
                cut = True
            else:
                cut = False
            if cut:
                words.append(tok[start:i])
                start = i
        words.append(tok[start:])
    return words


def convert_style(stem, style):
    words = split_words(stem)
    if not words:
        return stem
    cap = lambda w: w[:1].upper() + w[1:].lower()
    if style == "snake":
        return "_".join(w.lower() for w in words)
    if style == "snake_upper":
        return "_".join(w.upper() for w in words)
    if style == "kebab":
        return "-".join(w.lower() for w in words)
    if style == "camel":
        return words[0].lower() + "".join(cap(w) for w in words[1:])
    return "".join(cap(w) for w in words)  # pascal


def special_pattern(p):
    mode = p["mode"]
    if mode == "unsafe":
        return r'[\\/:*?"<>|\x00-\x1f]'
    if mode == "symbols":
        return r"[^\w\s.\-]"
    if mode == "nonascii":
        return r"[^\x00-\x7f]"
    return "[" + re.escape(p["chars"]) + "]" if p["chars"] else None


_BIRTH_CACHE = {}


def file_created(path, st):
    """Data creării. Linux: prin `stat -c %W` (Python nu o expune); altfel data modificării."""
    b = getattr(st, "st_birthtime", None)
    if b:
        return b
    if IS_WIN:
        return st.st_ctime
    key = (path, st.st_mtime_ns)
    if key not in _BIRTH_CACHE:
        value = st.st_mtime
        if sys.platform.startswith("linux"):
            try:
                out = subprocess.run(["stat", "-c", "%W", "--", path], capture_output=True,
                                     text=True, timeout=3).stdout.strip()
                if int(out) > 0:
                    value = int(out)
            except Exception:
                pass
        _BIRTH_CACHE[key] = value
    return _BIRTH_CACHE[key]


def file_time(path, src, now):
    if src == "now":
        return now
    try:
        st = os.stat(path)
    except OSError:
        return None
    return st.st_mtime if src == "modified" else file_created(path, st)


def passes_filter(layer, orig_stem, orig_ext):
    flt = layer.get("filter") or {}
    mode, text = flt.get("mode", "all"), (flt.get("text") or "").strip()
    if mode == "all" or not text:
        return True
    if mode in ("ext", "not_ext"):
        wanted = {e.lstrip(".").lower() for e in re.split(r"[,;\s]+", text) if e.strip(".")}
        hit = orig_ext.lstrip(".").lower() in wanted
        return hit if mode == "ext" else not hit
    hit = text.lower() in orig_stem.lower()
    return hit if mode == "has" else not hit


def apply_layer(layer, stem, ext, ctx, st):
    """ctx: {'path','dir','now'}; st: starea mutabilă a stratului (contoare)."""
    t, p = layer["type"], layer["params"]

    if t == "replace":
        find = p["find"]
        if not find:
            return stem, ext
        repl = p["repl"]
        try:
            if p["regex"]:
                flags = 0 if p["case"] else re.IGNORECASE
                return re.sub(find, repl, stem, flags=flags), ext
            if p["case"]:
                return stem.replace(find, repl), ext
            return re.sub(re.escape(find), lambda m: repl, stem, flags=re.IGNORECASE), ext
        except Exception:
            return stem, ext

    if t == "digits":
        pattern = {"all": r"\d+", "start": r"^\d+", "end": r"\d+$"}.get(p["scope"], r"\d+")
        stem = re.sub(pattern, "", stem)
        return (tidy(stem) if p["strip"] else stem), ext

    if t == "trim":
        first, last = max(0, int(p["first"])), max(0, int(p["last"]))
        if first:
            stem = stem[first:]
        if last:
            stem = stem[:-last]
        return stem, ext

    if t == "brackets":
        for key, (o, c) in BRACKETS.items():
            if not p[key]:
                continue
            if p["content"]:
                pat = re.compile(re.escape(o) + "[^" + re.escape(o + c) + "]*" + re.escape(c))
                for _ in range(10):  # paranteze imbricate
                    new = pat.sub("", stem)
                    if new == stem:
                        break
                    stem = new
            else:
                stem = stem.replace(o, "").replace(c, "")
        return (tidy(stem) if p["strip"] else stem), ext

    if t == "special":
        pat = special_pattern(p)
        if pat:
            repl = p["repl"]
            stem = re.sub(pat, lambda m: repl, stem)
            if p["strip"]:
                stem = tidy(stem)
        return stem, ext

    if t == "diacritics":
        return remove_diacritics(stem), ext

    if t == "add":
        return p["prefix"] + stem + p["suffix"], ext

    if t == "insert":
        return insert_text(stem, p["text"], p["pos"], p["n"]), ext

    if t == "number":
        key = nc(ctx["dir"]) if p["per_folder"] else ""
        k = st.get(key, 0)
        st[key] = k + 1
        num = p["start"] + k * p["step"]
        digits = str(abs(num)).zfill(max(1, p["digits"]))
        if num < 0:
            digits = "-" + digits
        return insert_text(stem, p["before"] + digits + p["after"], p["pos"], p["n"]), ext

    if t == "date":
        ts = file_time(ctx["path"], p["src"], ctx["now"])
        if ts is None:
            return stem, ext
        try:
            text = datetime.fromtimestamp(ts).strftime(p["fmt"])
        except Exception:
            return stem, ext
        return insert_text(stem, p["before"] + text + p["after"], p["pos"], p["n"]), ext

    if t == "parent":
        parts = [x for x in os.path.normpath(ctx["dir"]).split(os.sep) if x]
        level = max(1, int(p["level"]))
        name = parts[-level] if len(parts) >= level else ""
        if not name:
            return stem, ext
        if p["case"] == "lower":
            name = name.lower()
        elif p["case"] == "upper":
            name = name.upper()
        return insert_text(stem, p["fmt"].replace("{}", name), p["pos"], p["n"]), ext

    if t == "case":
        mode = p["mode"]
        if mode == "lower":
            stem = stem.lower()
        elif mode == "upper":
            stem = stem.upper()
        elif mode == "title":
            stem = re.sub(r"[^\W_]+(?:'[^\W_]+)*", lambda m: m.group(0).capitalize(), stem)
        elif mode == "sentence":
            stem = stem[:1].upper() + stem[1:].lower()
        return stem, ext

    if t == "style":
        return convert_style(stem, p["style"]), ext

    if t == "ext":
        mode = p["mode"]
        if mode == "change":
            new = p["ext"].strip().lstrip(".")
            if new:
                ext = "." + new
        elif mode == "lower":
            ext = ext.lower()
        elif mode == "upper":
            ext = ext.upper()
        elif mode == "remove":
            ext = ""
        return stem, ext

    return stem, ext


_WIN_BAD = set('<>:"/\\|?*') | {chr(i) for i in range(32)}
_WIN_RESERVED = {"CON", "PRN", "AUX", "NUL"} | {"COM%d" % i for i in range(1, 10)} | {"LPT%d" % i for i in range(1, 10)}


def name_problem(name):
    if not name or name in (".", ".."):
        return True
    if "/" in name or "\0" in name:
        return True
    if IS_WIN:
        if any(c in _WIN_BAD for c in name) or name[-1] in " .":
            return True
        if name.split(".")[0].upper() in _WIN_RESERVED:
            return True
        return len(name) > 255
    return len(name.encode("utf-8", "surrogateescape")) > 255


def compute_preview(files, layers):
    """Aplică straturile active fiecărui fișier și verifică conflictele."""
    active = [L for L in layers if L["enabled"]]
    states = {id(L): {} for L in active}
    now = time.time()
    rows = []
    for p in files:
        d, old = os.path.split(p)
        ostem, oext = split_name(old)
        stem, ext = ostem, oext
        ctx = {"path": p, "dir": d, "now": now}
        for L in active:
            if passes_filter(L, ostem, oext):
                stem, ext = apply_layer(L, stem, ext, ctx, states[id(L)])
        rows.append({"src": p, "dir": d, "old": old, "new": stem + ext, "stem": stem})

    vacating = {nc(r["src"]) for r in rows if r["new"] != r["old"]}
    counts = Counter(nc(os.path.join(r["dir"], r["new"])) for r in rows)
    for r in rows:
        dst = os.path.join(r["dir"], r["new"])
        if not os.path.lexists(r["src"]):
            r["st"] = "missing"
        elif r["new"] == r["old"]:
            r["st"] = "same"
        elif r["stem"] == "" or name_problem(r["new"]):
            r["st"] = "invalid"
        elif counts[nc(dst)] > 1:
            r["st"] = "dup"
        elif os.path.lexists(dst) and nc(dst) not in vacating:
            r["st"] = "exists"
        else:
            r["st"] = "ok"
    return rows


# ----------------------------------------------------------------------------
# Recomandări automate
# ----------------------------------------------------------------------------
SITE_RE = (r"(?:^|[\s\[\(_-])www\.[\w-]+(?:\.[A-Za-z]{2,})+"
           r"|^[\w-]+\.(?:com|net|org|info|biz|ro|it|eu|tv|me|io)(?=[\s_-])")
SUSPICIOUS = "#%&$!'`@+=~^;,*?\":|<>\\"


def suggest_layers(names):
    """Analizează numele și propune straturi. Întoarce (straturi, [(cheie_motiv, nr_fișiere)])."""
    n = len(names)
    if not n:
        return [], []
    parts = [split_name(x) for x in names]
    stems = [s for s, _ in parts]
    exts = [e for _, e in parts]
    thr = max(1, math.ceil(0.3 * n))
    layers, reasons = [], []

    def mk(ltype, **kw):
        layer = make_layer(ltype)
        layer["params"].update(kw)
        return layer

    # 1) adrese de site lipite în nume
    c = sum(1 for s in stems if re.search(SITE_RE, s, re.IGNORECASE))
    site = c > 0
    if site:
        layers.append(mk("replace", find=SITE_RE, repl="", case=False, regex=True))
        reasons.append(("sg_site", c))

    # 2) text între paranteze (doar tipurile care apar suficient de des)
    chosen, hit_files = {}, set()
    for key, (o, cl) in BRACKETS.items():
        pat = re.escape(o) + "[^" + re.escape(o + cl) + "]*" + re.escape(cl)
        hits = {i for i, s in enumerate(stems) if re.search(pat, s)}
        chosen[key] = len(hits) >= thr
        if chosen[key]:
            hit_files |= hits
    if hit_files:
        layers.append(mk("brackets", content=True, strip=True, **chosen))
        reasons.append(("sg_brackets", len(hit_files)))

    # 3) caractere problematice (doar cele care apar efectiv)
    found, c = set(), 0
    for s in stems:
        bad = [ch for ch in s if ch in SUSPICIOUS]
        if bad:
            c += 1
            found.update(bad)
    if c:
        layers.append(mk("special", mode="custom", chars="".join(sorted(found)), repl="", strip=True))
        reasons.append(("sg_special", c))

    # 4) spații multiple / separatori la margini
    c = sum(1 for s in stems if re.search(r"\s{2,}|^[\s_-]|[\s_.-]$", s))
    if c:
        reasons.append(("sg_spaces", c))
    if c or site:
        layers.append(mk("replace", find=r"\s{2,}", repl=" ", case=True, regex=True))
        layers.append(mk("replace", find=r"^[\s_-]+|[\s_.-]+$", repl="", case=True, regex=True))

    # 5) titluri scrise integral cu majuscule
    multiword = [s for s in stems if " " in s and any(ch.isalpha() for ch in s)]
    caps = sum(1 for s in multiword if s == s.upper())
    if multiword and caps >= math.ceil(0.5 * len(multiword)):
        layers.append(mk("case", mode="title"))
        reasons.append(("sg_caps", caps))

    # 6) extensii cu majuscule
    c = sum(1 for e in exts if e and e != e.lower())
    if c:
        layers.append(mk("ext", mode="lower"))
        reasons.append(("sg_ext", c))

    return layers, reasons


# ----------------------------------------------------------------------------
# Redenumire propriu-zisă (cu rollback) și undo
# ----------------------------------------------------------------------------
def perform_renames(pairs):
    """
    Redenumește în două faze (prin nume temporare), deci merge și pentru
    schimburi/cicluri (a->b, b->a). Dacă ceva eșuează, totul este adus înapoi.
    Returnează (perechi_aplicate, eroare_sau_None).
    """
    staged, finalized = [], set()
    try:
        for src, dst in pairs:
            tmp = os.path.join(os.path.dirname(src), ".nomina-%s.tmp" % uuid.uuid4().hex)
            os.rename(src, tmp)
            staged.append((src, tmp, dst))
        for src, tmp, dst in staged:
            if os.path.lexists(dst):
                raise FileExistsError("%s: %s" % (os.strerror(17), dst))
            os.rename(tmp, dst)
            finalized.add(src)
    except Exception as e:
        for src, tmp, dst in reversed(staged):
            try:
                os.rename(dst if src in finalized else tmp, src)
            except Exception:
                pass
        return [], e
    return [(s, d) for s, _, d in staged], None


def filter_applicable(pairs):
    """Pentru undo/redo: păstrează doar perechile care se mai pot aplica."""
    vacating = {nc(s) for s, _ in pairs}
    ok, skipped = [], []
    for s, d in pairs:
        if os.path.lexists(s) and (not os.path.lexists(d) or nc(d) in vacating):
            ok.append((s, d))
        else:
            skipped.append((s, d))
    return ok, skipped


# ----------------------------------------------------------------------------
# Interfața
# ----------------------------------------------------------------------------
class NominaApp:
    def __init__(self):
        self.cfg = load_json(CONFIG_FILE, {})
        lang = self.cfg.get("lang")
        self.lang = lang if lang in LANGS else detect_lang()

        # Drag & drop: "py" = tkinterdnd2 (pip), "native" = extensia Tcl tkdnd din sistem
        self.dnd_mode = None
        try:
            if HAS_DND:
                self.root = TkinterDnD.Tk()
                self.dnd_mode = "py"
            else:
                self.root = tk.Tk()
        except Exception:
            self.root = tk.Tk()
        if self.dnd_mode is None:
            try:
                self.root.tk.call("package", "require", "tkdnd")
                self.dnd_mode = "native"
            except Exception:
                pass
        self.has_dnd = self.dnd_mode is not None

        self.files = []          # căi absolute
        self.layers = []         # [{'type','enabled','params','filter'}]
        self.rows = []           # rezultatul calculului
        self.cur_layer = None
        self._lock = False
        self._i18n = []
        self._sort_rev = False

        hist = load_json(HISTORY_FILE, {})
        old_batches = hist.get("batches", []) if isinstance(hist, dict) else []
        old_pos = hist.get("pos", len(old_batches)) if isinstance(hist, dict) else 0
        # Păstrăm numai ultima operație efectuată, suficientă pentru undo după repornire.
        self.history = [old_batches[old_pos - 1]] if old_batches and old_pos > 0 else []
        self.hist_pos = 1 if self.history else 0
        self._layer_drag_iid = None

        presets = load_json(PRESETS_FILE, {})
        self.presets = presets if isinstance(presets, dict) else {}

        self.icons = {k: tk.PhotoImage(data=v) for k, v in ICONS_B64.items()}
        if "app" in self.icons:
            try:
                self.root.iconphoto(True, self.icons["app"])
            except Exception:
                pass

        self.recursive_var = tk.BooleanVar(value=bool(self.cfg.get("recursive", False)))

        self.setup_style()
        self.build_ui()
        self.restore_geometry()
        self.apply_language()
        self.bind_events()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # --- utilitare ----------------------------------------------------------
    def t(self, key, **kw):
        s = STR[self.lang].get(key) or STR["en"].get(key, key)
        return s.format(**kw) if kw else s

    def reg(self, widget, key, option="text"):
        self._i18n.append((widget, option, key))
        widget.configure(**{option: self.t(key)})
        return widget

    def setup_style(self):
        st = ttk.Style(self.root)
        st.configure("Treeview", rowheight=24)
        st.configure("Treeview.Heading", padding=(4, 3))
        bold = tkfont.nametofont("TkDefaultFont").copy()
        bold.configure(weight="bold")
        self._bold = bold
        st.configure("Accent.TButton", font=bold, padding=(14, 6))

        # remediu pentru culorile de tag din Treeview în unele versiuni de Tk
        def fixed_map(option):
            return [e for e in st.map("Treeview", query_opt=option) if e[:2] != ("!disabled", "!selected")]
        st.map("Treeview", foreground=fixed_map("foreground"), background=fixed_map("background"))

    def add_tooltip(self, widget, key):
        """Afișează eticheta localizată la trecerea mouse-ului peste un buton."""
        state = {"window": None}

        def show(_event=None):
            if state["window"] is not None:
                return
            tip = tk.Toplevel(widget)
            tip.wm_overrideredirect(True)
            tip.attributes("-topmost", True)
            label = ttk.Label(tip, text=self.t(key), padding=(6, 3), relief="solid")
            label.pack()
            x = widget.winfo_rootx() + widget.winfo_width() + 6
            y = widget.winfo_rooty() + widget.winfo_height() + 2
            tip.wm_geometry(f"+{x}+{y}")
            state["window"] = tip

        def hide(_event=None):
            tip = state.pop("window", None)
            if tip is not None:
                try:
                    tip.destroy()
                except tk.TclError:
                    pass
            state["window"] = None

        widget.bind("<Enter>", show, add="+")
        widget.bind("<Leave>", hide, add="+")
        widget.bind("<ButtonPress>", hide, add="+")

    def mkbtn(self, parent, key, icon, command, style=None):
        b = ttk.Button(parent, image=self.icons.get(icon), compound="left", command=command)
        if style:
            b.configure(style=style)
        return self.reg(b, key)

    # --- construire UI ------------------------------------------------------
    def build_ui(self):
        r = self.root

        # bara de sus
        self.toolbar = ttk.Frame(r, padding=(10, 10, 10, 4))
        self.toolbar.pack(fill="x")
        tb = self.toolbar
        self.mkbtn(tb, "add_files", "file_add", self.add_files_dialog).pack(side="left", padx=(0, 4))
        self.mkbtn(tb, "add_folder", "folder_add", self.add_folder_dialog).pack(side="left", padx=4)
        self.reg(ttk.Checkbutton(tb, variable=self.recursive_var), "subfolders").pack(side="left", padx=(6, 6))
        ttk.Separator(tb, orient="vertical").pack(side="left", fill="y", padx=8, pady=2)
        self.btn_undo = self.mkbtn(tb, "undo", "undo", self.undo)
        self.btn_undo.pack(side="left", padx=4)
        self.btn_redo = self.mkbtn(tb, "redo", "redo", self.redo)
        self.btn_redo.pack(side="left", padx=4)

        self.lang_combo = ttk.Combobox(tb, state="readonly", width=10, values=list(LANGS.values()))
        self.lang_combo.pack(side="right")
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_lang_selected)
        self.reg(ttk.Label(tb), "language").pack(side="right", padx=(0, 6))

        # bara de jos
        self.bottom = ttk.Frame(r, padding=(10, 6, 10, 10))
        self.bottom.pack(side="bottom", fill="x")
        self.btn_rename = self.mkbtn(self.bottom, "rename", "apply", self.do_rename, style="Accent.TButton")
        self.btn_rename.pack(side="right")
        self.stats_var = tk.StringVar()
        ttk.Label(self.bottom, textvariable=self.stats_var).pack(side="left")
        self.msg_var = tk.StringVar()
        self.msg_label = ttk.Label(self.bottom, textvariable=self.msg_var, foreground="#1b5e20")
        self.msg_label.pack(side="left", padx=18)

        # zona centrală
        self.paned = tk.PanedWindow(r, orient="horizontal", sashwidth=7, sashrelief="flat",
                                    bd=0, showhandle=False, opaqueresize=True)
        self.paned.pack(fill="both", expand=True, padx=10, pady=4)

        self.left = ttk.LabelFrame(self.paned, padding=8)
        self.right = ttk.LabelFrame(self.paned, padding=8)
        self.reg(self.left, "layers")
        self.reg(self.right, "files_preview")
        self.paned.add(self.left, minsize=400, stretch="never")
        self.paned.add(self.right, minsize=RIGHT_MIN, stretch="always")

        self.build_left()
        self.build_right()

    def build_left(self):
        f = self.left
        f.columnconfigure(0, weight=1)
        f.rowconfigure(2, weight=1)

        row = ttk.Frame(f)
        row.grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.mb_add = ttk.Menubutton(row, image=self.icons.get("plus"), takefocus=True)
        self.mb_add.pack(side="left", padx=(0, 4))
        self.add_menu = tk.Menu(self.mb_add, tearoff=0)
        self.mb_add.configure(menu=self.add_menu)
        self.add_tooltip(self.mb_add, "add_layer")

        self.mb_presets = ttk.Menubutton(row, image=self.icons.get("preset"), takefocus=True)
        self.mb_presets.pack(side="left", padx=4)
        self.preset_menu = tk.Menu(self.mb_presets, tearoff=0, postcommand=self.build_presets_menu)
        self.mb_presets.configure(menu=self.preset_menu)
        self.add_tooltip(self.mb_presets, "presets")

        self.btn_suggest = ttk.Button(row, image=self.icons.get("bulb"), command=self.suggest)
        self.btn_suggest.pack(side="left", padx=4)
        self.add_tooltip(self.btn_suggest, "suggest")

        self.btn_clear_layers = ttk.Button(row, image=self.icons.get("clear"), command=self.clear_layers)
        self.btn_clear_layers.pack(side="left", padx=4)
        self.add_tooltip(self.btn_clear_layers, "clear_layers")

        wrap = ttk.Frame(f)
        wrap.grid(row=2, column=0, sticky="nsew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)
        self.ltree = ttk.Treeview(wrap, columns=("on", "n", "layer", "details"), show="headings",
                                  selectmode="browse", height=5)
        self.ltree.column("on", width=30, minwidth=30, stretch=False, anchor="center")
        self.ltree.column("n", width=30, minwidth=30, stretch=False, anchor="center")
        self.ltree.column("layer", width=170, minwidth=90, stretch=False)
        self.ltree.column("details", width=150, minwidth=60, stretch=True)
        self.ltree.heading("on", text="")
        self.ltree.heading("n", text="#")
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.ltree.yview)
        self.ltree.configure(yscrollcommand=sb.set)
        self.ltree.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        self.layer_menu = tk.Menu(self.ltree, tearoff=0)
        self.layer_menu.add_command(label="↑  " + self.t("move_up"), command=lambda: self.move_layer(-1))
        self.layer_menu.add_command(label="↓  " + self.t("move_down"), command=lambda: self.move_layer(1))
        self.layer_menu.add_command(label="✖  " + self.t("remove_layer"), command=self.remove_layer)

        self.editor = ttk.LabelFrame(f, padding=8, width=420, height=300)
        self.editor.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        self.editor.grid_propagate(False)
        self.editor.columnconfigure(0, weight=1)
        self.editor.rowconfigure(1, weight=1)
        self.reg(self.editor, "layer_settings")

    def build_right(self):
        f = self.right
        f.columnconfigure(0, weight=1)
        f.rowconfigure(0, weight=1)

        wrap = ttk.Frame(f)
        wrap.grid(row=0, column=0, sticky="nsew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(wrap, columns=("old", "new", "status", "folder"), show="headings",
                                 selectmode="extended")
        self.tree.column("old", width=210, minwidth=80)
        self.tree.column("new", width=210, minwidth=80)
        self.tree.column("status", width=110, minwidth=70, stretch=False)
        self.tree.column("folder", width=160, minwidth=60)
        self.preview_columns_all = ("old", "new", "status", "folder")
        saved_columns = self.cfg.get("preview_columns", list(self.preview_columns_all))
        if not isinstance(saved_columns, list):
            saved_columns = list(self.preview_columns_all)
        visible_columns = [c for c in self.preview_columns_all if c in saved_columns]
        if not visible_columns:
            visible_columns = list(self.preview_columns_all)
        self.preview_column_vars = {
            c: tk.BooleanVar(value=(c in visible_columns)) for c in self.preview_columns_all
        }
        self.tree["displaycolumns"] = visible_columns
        self.preview_columns_menu = tk.Menu(self.tree, tearoff=0)
        vs = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        hs = ttk.Scrollbar(wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Button-3>", self.show_preview_columns_menu)
        self.tree.bind("<Button-2>", self.show_preview_columns_menu)
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        self.tree.tag_configure("same", foreground="#8a8a8a")
        self.tree.tag_configure("ok", foreground="#1b5e20")
        self.tree.tag_configure("err", foreground="#b71c1c", background="#ffebee")

        self.drop_label = ttk.Label(wrap, justify="center", foreground="#7a7a7a", anchor="center", wraplength=360)

        row = ttk.Frame(f)
        row.grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.mkbtn(row, "remove_sel", "delete", self.remove_selected_files).pack(side="left", padx=(0, 4))
        self.mkbtn(row, "clear", "clear", self.clear_files).pack(side="left", padx=4)

    def show_preview_columns_menu(self, event):
        # Meniul apare numai când se face clic dreapta pe antetul coloanelor.
        if self.tree.identify_region(event.x, event.y) != "heading":
            return
        menu = self.preview_columns_menu
        menu.delete(0, "end")
        # Numele interne ale coloanelor (old/new) sunt independente de etichetele
        # afișate; meniul folosește aceleași chei localizate ca antetele tabelului.
        column_labels = {
            "old": "col_source",
            "new": "col_dest",
            "status": "col_status",
            "folder": "col_folder",
        }
        for col in self.preview_columns_all:
            menu.add_checkbutton(
                label=self.t(column_labels[col]),
                variable=self.preview_column_vars[col],
                command=lambda c=col: self.set_preview_column_visibility(c),
            )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
        return "break"

    def set_preview_column_visibility(self, changed_col):
        visible = [c for c in self.preview_columns_all if self.preview_column_vars[c].get()]
        # Păstrăm cel puțin o coloană vizibilă.
        if not visible:
            self.preview_column_vars[changed_col].set(True)
            visible = [changed_col]
        self.tree["displaycolumns"] = visible
        self.cfg["preview_columns"] = visible
        save_json(CONFIG_FILE, self.cfg)

    # --- evenimente ---------------------------------------------------------
    def bind_events(self):
        self.ltree.bind("<<TreeviewSelect>>", self.on_layer_select)
        self.ltree.bind("<Button-1>", self.on_layer_click, add="+")
        self.ltree.bind("<Button-3>", self.show_layer_context_menu)
        self.ltree.bind("<Button-2>", self.show_layer_context_menu)
        self.ltree.bind("<ButtonPress-1>", self.layer_drag_start, add="+")
        self.ltree.bind("<B1-Motion>", self.layer_drag_motion)
        self.ltree.bind("<ButtonRelease-1>", self.layer_drag_end, add="+")
        self.tree.bind("<Delete>", lambda e: self.remove_selected_files())
        self.tree.bind("<Control-a>", self.select_all_files)
        self.root.bind_all("<Control-z>", lambda e: self.shortcut(self.undo))
        self.root.bind_all("<Control-y>", lambda e: self.shortcut(self.redo))
        self.root.bind_all("<Control-o>", lambda e: self.shortcut(self.add_files_dialog))

        if self.has_dnd:
            for w in (self.root, self.left, self.right, self.tree, self.drop_label):
                self.register_drop(w)

    def register_drop(self, w):
        try:
            if self.dnd_mode == "py":
                w.drop_target_register(DND_FILES)
                w.dnd_bind("<<Drop>>", self.on_drop)
            else:
                w.tk.call("tkdnd::drop_target", "register", w._w, "DND_Files")
                cmd = self.root.register(self.on_native_drop)
                w.tk.call("bind", w._w, "<<Drop>>", cmd + " %D")
        except Exception:
            pass

    def on_native_drop(self, *args):
        data = args[0] if len(args) == 1 else " ".join(args)
        paths = [data] if os.path.exists(data) else self.root.tk.splitlist(data)
        self.add_paths(paths)
        return "copy"

    def shortcut(self, func):
        w = self.root.focus_get()
        if isinstance(w, (tk.Entry, ttk.Entry, tk.Spinbox, ttk.Spinbox, ttk.Combobox)):
            return None  # nu deranjăm editarea textului
        func()
        return "break"

    def select_all_files(self, _e=None):
        self.tree.selection_set(self.tree.get_children())
        return "break"

    # --- limbă --------------------------------------------------------------
    def on_lang_selected(self, _e=None):
        self.lang = list(LANGS.keys())[self.lang_combo.current()]
        self.apply_language()

    def apply_language(self):
        for w, opt, key in self._i18n:
            w.configure(**{opt: self.t(key)})
        self.root.title(self.t("title"))
        self.lang_combo.current(list(LANGS.keys()).index(self.lang))
        self.lang_combo.selection_clear()

        self.add_menu.delete(0, "end")
        for gi, group in enumerate(LAYER_GROUPS):
            if gi:
                self.add_menu.add_separator()
            for lt in group:
                self.add_menu.add_command(label=self.t("lt_" + lt), command=lambda x=lt: self.add_layer(x))
        self.build_presets_menu()
        self.layer_menu.entryconfigure(0, label="↑  " + self.t("move_up"))
        self.layer_menu.entryconfigure(1, label="↓  " + self.t("move_down"))
        self.layer_menu.entryconfigure(2, label="✖  " + self.t("remove_layer"))

        self.ltree.heading("layer", text=self.t("col_layer"))
        self.ltree.heading("details", text=self.t("col_details"))
        self.tree.heading("old", text=self.t("col_source"), command=self.sort_by_source)
        self.tree.heading("new", text=self.t("col_dest"))
        self.tree.heading("status", text=self.t("col_status"))
        self.tree.heading("folder", text=self.t("col_folder"))
        self.drop_label.configure(text=self.t("drop_hint" if self.has_dnd else "drop_hint_nodnd"))

        self.refresh_layers(select=self.selected_layer())
        self.build_editor()
        self.refresh_preview(rebuild=True)
        self.update_history_buttons()
        self.set_msg("")
        self.update_minsize()

    def update_minsize(self):
        r = self.root
        r.update_idletasks()
        left_w = max(self.left.winfo_reqwidth(), 400)
        minw = max(MIN_W, self.toolbar.winfo_reqwidth(), self.bottom.winfo_reqwidth() + 20,
                   left_w + RIGHT_MIN + 40)
        r.minsize(minw, MIN_H)
        try:
            self.paned.paneconfigure(self.left, minsize=left_w)
        except tk.TclError:
            pass
        if r.winfo_width() < minw or r.winfo_height() < MIN_H:
            r.geometry("%dx%d" % (max(r.winfo_width(), minw), max(r.winfo_height(), MIN_H)))

    # --- geometrie ----------------------------------------------------------
    def restore_geometry(self):
        r = self.root
        r.update_idletasks()
        w, h, x, y = 1140, 740, None, None
        m = re.match(r"^(\d+)x(\d+)\+(-?\d+)\+(-?\d+)$", self.cfg.get("geometry", "") or "")
        sw = r.winfo_vrootwidth() or r.winfo_screenwidth()
        sh = r.winfo_vrootheight() or r.winfo_screenheight()
        vx, vy = r.winfo_vrootx(), r.winfo_vrooty()
        if m:
            w, h, x, y = (int(v) for v in m.groups())
            if not (vx - w + 100 <= x <= vx + sw - 100 and vy <= y <= vy + sh - 100):
                x = y = None
        w, h = min(w, sw), min(h, sh)
        if x is None:
            x = vx + (sw - w) // 2
            y = vy + max(0, (sh - h) // 3)
        r.geometry("%dx%d+%d+%d" % (w, h, x, y))

    def on_close(self):
        self.cfg["lang"] = self.lang
        self.cfg["recursive"] = bool(self.recursive_var.get())
        try:
            self.cfg["geometry"] = self.root.geometry()
        except Exception:
            pass
        save_json(CONFIG_FILE, self.cfg)
        self.save_history()
        self.root.destroy()

    # --- straturi: listă ----------------------------------------------------
    def selected_layer(self):
        sel = self.ltree.selection()
        if sel:
            i = int(sel[0])
            if 0 <= i < len(self.layers):
                return i
        return None

    def pos_summary(self, p):
        return self.t("ps_" + p["pos"], n=p["n"])

    def layer_summary(self, L):
        t, p = L["type"], L["params"]
        T = self.t
        if t == "replace":
            if not p["find"]:
                return ""
            return T("sum_replace_re" if p["regex"] else "sum_replace", a=p["find"], b=p["repl"])
        if t == "digits":
            return T({"all": "sd_all", "start": "sd_start", "end": "sd_end"}[p["scope"]])
        if t == "trim":
            return T("sum_trim", a=p["first"], b=p["last"])
        if t == "brackets":
            symbols = " ".join(BRACKETS[k][0] + BRACKETS[k][1] for k in BRACKETS if p[k])
            return "%s · %s" % (symbols, T("sum_br_content" if p["content"] else "sum_br_only")) if symbols else ""
        if t == "special":
            if p["mode"] == "custom":
                return "«%s»" % p["chars"] if p["chars"] else ""
            return T("sps_" + p["mode"])
        if t == "diacritics":
            return "ă â î ș ț → a a i s t"
        if t == "add":
            return T("sum_add", a=p["prefix"], b=p["suffix"])
        if t == "insert":
            return T("sum_pos", a=p["text"], b=self.pos_summary(p)) if p["text"] else ""
        if t == "number":
            sample = p["before"] + str(p["start"]).zfill(max(1, p["digits"])) + p["after"]
            return T("sum_pos", a=sample, b=self.pos_summary(p))
        if t == "date":
            return T("sum_pos", a=p["fmt"], b=self.pos_summary(p))
        if t == "parent":
            return T("sum_pos", a=p["fmt"], b=self.pos_summary(p))
        if t == "case":
            return T("sc_" + p["mode"])
        if t == "style":
            return STYLE_LABELS[p["style"]]
        if t == "ext":
            if p["mode"] == "change":
                new = p["ext"].strip().lstrip(".")
                return T("sum_ext_change", a=new) if new else ""
            return T("sum_ext_" + p["mode"])
        return ""

    def filter_summary(self, L):
        flt = L["filter"]
        if flt["mode"] == "all" or not flt["text"].strip():
            return ""
        return self.t("fsum_" + flt["mode"], x=flt["text"].strip())

    def layer_values(self, i):
        L = self.layers[i]
        details = (self.layer_summary(L) + " " + self.filter_summary(L)).strip()
        return ("☑" if L["enabled"] else "☐", str(i + 1), self.t("lt_" + L["type"]), details)

    def refresh_layers(self, select=None):
        self._lock = True
        try:
            self.ltree.delete(*self.ltree.get_children())
            for i in range(len(self.layers)):
                self.ltree.insert("", "end", iid=str(i), values=self.layer_values(i))
            if select is not None and 0 <= select < len(self.layers):
                self.ltree.selection_set(str(select))
                self.ltree.focus(str(select))
                self.ltree.see(str(select))
        finally:
            self._lock = False

    def update_layer_rows(self):
        for i in range(len(self.layers)):
            if self.ltree.exists(str(i)):
                self.ltree.item(str(i), values=self.layer_values(i))

    def add_layer(self, ltype):
        self.layers.append(make_layer(ltype))
        self.refresh_layers(select=len(self.layers) - 1)
        self.build_editor()
        self.refresh_preview()

    def clear_layers(self):
        if not self.layers:
            return
        self.layers.clear()
        self.cur_layer = None
        self.refresh_layers()
        self.build_editor()
        self.refresh_preview()

    def show_layer_context_menu(self, event):
        iid = self.ltree.identify_row(event.y)
        if not iid:
            return "break"
        self.ltree.selection_set(iid)
        self.ltree.focus(iid)
        self.build_editor()
        self.layer_menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def layer_drag_start(self, event):
        iid = self.ltree.identify_row(event.y)
        self._layer_drag_iid = iid if iid else None

    def layer_drag_motion(self, event):
        if self._layer_drag_iid is None:
            return
        target = self.ltree.identify_row(event.y)
        if not target or target == self._layer_drag_iid:
            return
        src_i, dst_i = int(self._layer_drag_iid), int(target)
        if not (0 <= src_i < len(self.layers) and 0 <= dst_i < len(self.layers)):
            return
        layer = self.layers.pop(src_i)
        self.layers.insert(dst_i, layer)
        self._layer_drag_iid = str(dst_i)
        self.refresh_layers(select=dst_i)
        self.refresh_preview()

    def layer_drag_end(self, _event):
        self._layer_drag_iid = None

    def remove_layer(self):
        i = self.selected_layer()
        if i is None:
            return
        del self.layers[i]
        self.refresh_layers(select=min(i, len(self.layers) - 1) if self.layers else None)
        self.build_editor()
        self.refresh_preview()

    def move_layer(self, delta):
        i = self.selected_layer()
        if i is None:
            return
        j = i + delta
        if not 0 <= j < len(self.layers):
            return
        self.layers[i], self.layers[j] = self.layers[j], self.layers[i]
        self.refresh_layers(select=j)
        self.refresh_preview()

    def on_layer_select(self, _e=None):
        if not self._lock:
            self.build_editor()

    def on_layer_click(self, e):
        if self.ltree.identify_region(e.x, e.y) != "cell" or self.ltree.identify_column(e.x) != "#1":
            return
        iid = self.ltree.identify_row(e.y)
        if iid:
            L = self.layers[int(iid)]
            L["enabled"] = not L["enabled"]
            self.update_layer_rows()
            self.refresh_preview()
            if self.cur_layer is L and hasattr(self, "enabled_var"):
                self.enabled_var.set(L["enabled"])

    # --- presetări ----------------------------------------------------------
    def build_presets_menu(self):
        m = self.preset_menu
        m.delete(0, "end")
        for child in m.winfo_children():
            child.destroy()
        m.add_command(label=self.t("preset_save"), command=self.save_preset)
        m.add_separator()
        names = sorted(self.presets, key=lambda s: s.lower())
        if not names:
            m.add_command(label=self.t("preset_none"), state="disabled")
            return
        for name in names:
            m.add_command(label=name, command=lambda n=name: self.load_preset(n))
        m.add_separator()
        sub = tk.Menu(m, tearoff=0)
        for name in names:
            sub.add_command(label=name, command=lambda n=name: self.delete_preset(n))
        m.add_cascade(label=self.t("preset_delete"), menu=sub)

    def save_preset(self):
        if not self.layers:
            messagebox.showinfo(APP_NAME, self.t("preset_empty"), parent=self.root)
            return
        name = simpledialog.askstring(APP_NAME, self.t("preset_name_prompt"), parent=self.root)
        name = (name or "").strip()
        if not name:
            return
        if name in self.presets and not messagebox.askyesno(
                APP_NAME, self.t("preset_overwrite", name=name), parent=self.root):
            return
        self.presets[name] = copy.deepcopy(self.layers)
        save_json(PRESETS_FILE, self.presets)
        self.set_msg(self.t("preset_saved", name=name))

    def load_preset(self, name):
        data = self.presets.get(name)
        if not isinstance(data, list):
            return
        if self.layers and not messagebox.askyesno(
                APP_NAME, self.t("preset_replace_confirm", name=name), parent=self.root):
            return
        self.layers = [L for L in (normalize_layer(d) for d in data) if L]
        self.refresh_layers(select=0 if self.layers else None)
        self.build_editor()
        self.refresh_preview()
        self.set_msg(self.t("preset_loaded", name=name))

    def delete_preset(self, name):
        if messagebox.askyesno(APP_NAME, self.t("preset_delete_confirm", name=name), parent=self.root):
            self.presets.pop(name, None)
            save_json(PRESETS_FILE, self.presets)
            self.set_msg(self.t("preset_deleted", name=name))

    # --- recomandări --------------------------------------------------------
    def suggest(self):
        if not self.files:
            messagebox.showinfo(APP_NAME, self.t("suggest_nofiles"), parent=self.root)
            return
        replace = True
        names = [r["old"] for r in self.rows]
        if self.layers:
            ans = messagebox.askyesnocancel(APP_NAME, self.t("suggest_ask"), parent=self.root)
            if ans is None:
                return
            replace = bool(ans)
            if not replace:  # analizez numele rezultate din straturile existente
                names = [r["new"] for r in self.rows if r["st"] in ("ok", "same")]
        new_layers, reasons = suggest_layers(names)
        if not new_layers:
            messagebox.showinfo(APP_NAME, self.t("suggest_none"), parent=self.root)
            return
        first = 0 if replace else len(self.layers)
        if replace:
            self.layers = []
        self.layers.extend(new_layers)
        self.refresh_layers(select=first)
        self.build_editor()
        self.refresh_preview()
        lines = "\n".join("• " + self.t(key, n=count) for key, count in reasons)
        messagebox.showinfo(APP_NAME, self.t("suggest_done", n=len(new_layers), list=lines), parent=self.root)

    # --- editorul stratului selectat ---------------------------------------
    def watch(self, var, key, L, cast=None, target=None):
        target = L["params"] if target is None else target

        def cb(*_):
            try:
                val = var.get()
            except tk.TclError:
                return
            if cast:
                try:
                    val = cast(val)
                except Exception:
                    return
            target[key] = val
            self.after_param_change(L)
        var.trace_add("write", cb)

    def after_param_change(self, L):
        self.update_layer_rows()
        self.refresh_preview()
        if L["type"] == "replace":
            self.check_regex(L)

    def check_regex(self, L):
        p = L["params"]
        msg = ""
        if p["regex"] and p["find"]:
            try:
                re.sub(p["find"], p["repl"], "x")
            except Exception as ex:
                msg = self.t("regex_error", msg=str(ex))
        if hasattr(self, "err_label") and self.err_label.winfo_exists():
            self.err_label.configure(text=msg)

    def build_editor(self):
        ed = self.editor
        for w in ed.winfo_children():
            w.destroy()
        self.cur_layer = None
        i = self.selected_layer()
        if i is None:
            ttk.Label(ed, text=self.t("no_layer_sel"), foreground="#7a7a7a").grid(row=0, column=0, sticky="w")
            return
        L = self.layers[i]
        self.cur_layer = L
        p = L["params"]
        T = self.t

        # antet: titlul stratului + bifa de activare
        head = ttk.Frame(ed)
        head.grid(row=0, column=0, sticky="ew")
        head.columnconfigure(0, weight=1)
        ttk.Label(head, text=T("lt_" + L["type"]), font=self._bold).grid(row=0, column=0, sticky="w")
        self.enabled_var = tk.BooleanVar(value=L["enabled"])
        ttk.Checkbutton(head, text=T("layer_enabled"), variable=self.enabled_var).grid(row=0, column=1, sticky="e")
        self.enabled_var.trace_add("write", lambda *_: self._set_enabled(L))

        # parametrii stratului (4 coloane: etichetă, câmp, etichetă, câmp)
        pf = ttk.Frame(ed)
        pf.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        pf.columnconfigure(1, weight=1)
        pf.columnconfigure(3, weight=1)

        def lab(row, key, col=0):
            ttk.Label(pf, text=T(key)).grid(row=row, column=col, sticky="w", padx=(0, 6), pady=2)

        def note(row, text, color="#7a7a7a"):
            lbl = ttk.Label(pf, text=text, foreground=color, wraplength=390, justify="left")
            lbl.grid(row=row, column=0, columnspan=4, sticky="w", pady=(4, 0))
            return lbl

        def entry(row, label_key, key, col=0, span=None, width=None):
            lab(row, label_key, col)
            var = tk.StringVar(value=p[key])
            e = ttk.Entry(pf, textvariable=var, **({"width": width} if width else {}))
            e.grid(row=row, column=col + 1, columnspan=span or (3 if col == 0 else 1), sticky="ew", pady=2)
            self.watch(var, key, L)
            return e

        def check(row, label_key, key, col=0, span=None):
            var = tk.BooleanVar(value=p[key])
            ttk.Checkbutton(pf, text=T(label_key), variable=var).grid(
                row=row, column=col, columnspan=span or (4 if col == 0 else 2), sticky="w", pady=1)
            self.watch(var, key, L)

        def radios(row, key, options):
            var = tk.StringVar(value=p[key])
            for k, (value, text) in enumerate(options):
                ttk.Radiobutton(pf, text=text, variable=var, value=value).grid(
                    row=row + k, column=0, columnspan=4, sticky="w", pady=1)
            self.watch(var, key, L)

        def spin(row, label_key, key, lo, hi, col=0, width=7):
            lab(row, label_key, col)
            var = tk.IntVar(value=p[key])
            ttk.Spinbox(pf, from_=lo, to=hi, width=width, textvariable=var).grid(
                row=row, column=col + 1, sticky="w", pady=2)
            self.watch(var, key, L, cast=lambda v: max(lo, min(hi, int(v))))

        def pos_rows(row):
            lab(row, "position")
            cb = ttk.Combobox(pf, state="readonly", values=[T("pos_" + m) for m in POS_MODES])
            cb.current(POS_MODES.index(p["pos"]))
            cb.grid(row=row, column=1, columnspan=3, sticky="ew", pady=2)
            lab(row + 1, "pos_n")
            nvar = tk.IntVar(value=p["n"])
            sp = ttk.Spinbox(pf, from_=0, to=255, width=7, textvariable=nvar)
            sp.grid(row=row + 1, column=1, sticky="w", pady=2)
            self.watch(nvar, "n", L, cast=lambda v: max(0, min(255, int(v))))

            def refresh_state():
                sp.state(["!disabled"] if p["pos"] in ("from_start", "from_end") else ["disabled"])

            def selected(_e=None):
                p["pos"] = POS_MODES[cb.current()]
                refresh_state()
                self.after_param_change(L)
            cb.bind("<<ComboboxSelected>>", selected)
            refresh_state()

        def enum_combo(row, label_key, key, values, labels, editable_var=None):
            lab(row, label_key)
            cb = ttk.Combobox(pf, state="readonly", values=labels)
            cb.current(values.index(p[key]))
            cb.grid(row=row, column=1, columnspan=3, sticky="ew", pady=2)

            def selected(_e=None):
                p[key] = values[cb.current()]
                self.after_param_change(L)
            cb.bind("<<ComboboxSelected>>", selected)

        def editable_combo(row, label_key, key, presets):
            lab(row, label_key)
            var = tk.StringVar(value=p[key])
            ttk.Combobox(pf, textvariable=var, values=presets).grid(
                row=row, column=1, columnspan=3, sticky="ew", pady=2)
            self.watch(var, key, L)
            return var

        t = L["type"]
        if t == "replace":
            entry(0, "find", "find")
            entry(1, "replace_with", "repl")
            check(2, "case_sensitive", "case")
            check(3, "use_regex", "regex")
            self.err_label = note(4, "", "#b71c1c")
            self.check_regex(L)
        elif t == "digits":
            radios(0, "scope", [("all", T("digits_all")), ("start", T("digits_start")), ("end", T("digits_end"))])
            check(3, "strip_sep", "strip")
        elif t == "trim":
            spin(0, "trim_first", "first", 0, 255)
            spin(1, "trim_last", "last", 0, 255)
        elif t == "brackets":
            check(0, "br_round", "round", 0, 2)
            check(0, "br_square", "square", 2, 2)
            check(1, "br_curly", "curly", 0, 2)
            check(1, "br_angle", "angle", 2, 2)
            check(2, "br_content", "content")
            check(3, "strip_sep", "strip")
        elif t == "special":
            radios(0, "mode", [(m, T("sp_" + m)) for m in ("unsafe", "symbols", "nonascii", "custom")])
            entry(4, "sp_chars", "chars", 0, 1, 12)
            entry(4, "replace_with", "repl", 2, 1, 8)
            check(5, "strip_sep", "strip")
        elif t == "diacritics":
            note(0, T("dia_note"))
        elif t == "add":
            entry(0, "prefix", "prefix")
            entry(1, "suffix", "suffix")
            note(2, T("suffix_note"))
        elif t == "insert":
            entry(0, "insert_text", "text")
            pos_rows(1)
        elif t == "number":
            spin(0, "num_start", "start", 0, 999999, 0, 8)
            spin(0, "num_step", "step", 1, 9999, 2, 6)
            spin(1, "num_digits", "digits", 1, 10)
            entry(2, "text_before", "before", 0, 1, 10)
            entry(2, "text_after", "after", 2, 1, 10)
            pos_rows(3)
            check(5, "num_per_folder", "per_folder")
        elif t == "date":
            enum_combo(0, "date_source", "src", DATE_SOURCES, [T("ds_" + s) for s in DATE_SOURCES])
            fmt_var = editable_combo(1, "date_format", "fmt", DATE_FORMATS)
            hint = note(2, "")
            entry(3, "text_before", "before", 0, 1, 10)
            entry(3, "text_after", "after", 2, 1, 10)
            pos_rows(4)

            def show_example(*_):
                try:
                    sample = datetime.now().strftime(fmt_var.get())
                except Exception:
                    sample = "?"
                hint.configure(text=T("date_hint", ex=sample))
            fmt_var.trace_add("write", show_example)
            show_example()
        elif t == "parent":
            editable_combo(0, "parent_format", "fmt", PARENT_FORMATS)
            spin(1, "parent_level", "level", 1, 10)
            enum_combo(2, "parent_case", "case", CASE_ASIS, [T("ca_asis"), T("sc_lower"), T("sc_upper")])
            pos_rows(3)
            note(5, T("parent_hint"))
        elif t == "case":
            radios(0, "mode", [(m, T("case_" + m)) for m in ("lower", "upper", "title", "sentence")])
        elif t == "style":
            radios(0, "style", [(s, STYLE_LABELS[s]) for s in STYLES])
            note(5, T("style_note"))
        elif t == "ext":
            mode_var = tk.StringVar(value=p["mode"])
            ext_var = tk.StringVar(value=p["ext"])
            ttk.Radiobutton(pf, text=T("ext_change"), variable=mode_var, value="change").grid(
                row=0, column=0, columnspan=2, sticky="w", pady=3)
            ttk.Entry(pf, textvariable=ext_var, width=12).grid(row=0, column=2, columnspan=2, sticky="w", pady=3)
            for k, (val, lk) in enumerate([("lower", "ext_lower"), ("upper", "ext_upper"), ("remove", "ext_remove")]):
                ttk.Radiobutton(pf, text=T(lk), variable=mode_var, value=val).grid(
                    row=1 + k, column=0, columnspan=4, sticky="w", pady=1)
            note(4, T("ext_note"))
            self.watch(mode_var, "mode", L)
            self.watch(ext_var, "ext", L)

        # filtrul „se aplică la…” (la fel pentru toate tipurile de straturi)
        ff = ttk.Frame(ed)
        ff.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        ff.columnconfigure(1, weight=1)
        ff.columnconfigure(2, weight=1)
        flt = L["filter"]
        ttk.Label(ff, text=T("apply_to")).grid(row=0, column=0, sticky="w", padx=(0, 6))
        fcb = ttk.Combobox(ff, state="readonly", width=18, values=[T("fl_" + m) for m in FILTER_MODES])
        fcb.current(FILTER_MODES.index(flt["mode"]))
        fcb.grid(row=0, column=1, sticky="ew")
        fvar = tk.StringVar(value=flt["text"])
        fent = ttk.Entry(ff, textvariable=fvar, width=12)
        fent.grid(row=0, column=2, sticky="ew", padx=(6, 0))
        self.watch(fvar, "text", L, target=flt)

        def filter_state():
            fent.state(["!disabled"] if flt["mode"] != "all" else ["disabled"])

        def filter_selected(_e=None):
            flt["mode"] = FILTER_MODES[fcb.current()]
            filter_state()
            self.after_param_change(L)
        fcb.bind("<<ComboboxSelected>>", filter_selected)
        filter_state()

    def _set_enabled(self, L):
        try:
            L["enabled"] = bool(self.enabled_var.get())
        except tk.TclError:
            return
        self.update_layer_rows()
        self.refresh_preview()

    # --- fișiere ------------------------------------------------------------
    def add_files_dialog(self):
        paths = filedialog.askopenfilenames(parent=self.root, title=self.t("dlg_add_files"))
        if paths:
            self.add_paths(self.root.tk.splitlist(paths) if isinstance(paths, str) else paths)

    def add_folder_dialog(self):
        d = filedialog.askdirectory(parent=self.root, title=self.t("dlg_add_folder"), mustexist=True)
        if d:
            self.add_paths([d])

    def on_drop(self, event):
        self.add_paths(self.root.tk.splitlist(event.data))
        return event.action if hasattr(event, "action") else None

    def scan_folder(self, folder):
        found = []
        if self.recursive_var.get():
            for dp, dns, fns in os.walk(folder):
                dns[:] = sorted((d for d in dns if not d.startswith(".")), key=natural_key)
                for fn in sorted(fns, key=natural_key):
                    if not fn.startswith("."):
                        found.append(os.path.join(dp, fn))
        else:
            try:
                names = sorted(os.listdir(folder), key=natural_key)
            except OSError:
                names = []
            for fn in names:
                p = os.path.join(folder, fn)
                if not fn.startswith(".") and os.path.isfile(p):
                    found.append(p)
        return found

    def add_paths(self, paths):
        new = []
        for p in paths:
            p = os.path.abspath(p)
            if os.path.isdir(p):
                new += self.scan_folder(p)
            elif os.path.isfile(p):
                new.append(p)
        known = {nc(x) for x in self.files}
        added = 0
        for p in new:
            k = nc(p)
            if k not in known:
                known.add(k)
                self.files.append(p)
                added += 1
        self.refresh_preview(rebuild=True)
        self.set_msg(self.t("added", n=added) if added else "")

    def remove_selected_files(self):
        idx = sorted((int(i) for i in self.tree.selection()), reverse=True)
        if not idx:
            return
        for i in idx:
            if 0 <= i < len(self.files):
                del self.files[i]
        self.refresh_preview(rebuild=True)

    def clear_files(self):
        self.files.clear()
        self.refresh_preview(rebuild=True)

    def sort_by_source(self):
        self._sort_rev = not self._sort_rev
        self.files.sort(key=lambda p: (natural_key(os.path.basename(p)), p), reverse=self._sort_rev)
        self.refresh_preview(rebuild=True)

    # --- previzualizare -----------------------------------------------------
    def refresh_preview(self, rebuild=False):
        self.rows = compute_preview(self.files, self.layers)
        tree = self.tree
        children = tree.get_children()
        if rebuild or len(children) != len(self.rows):
            tree.delete(*children)
            for i, r in enumerate(self.rows):
                tree.insert("", "end", iid=str(i), values=self.row_values(r), tags=(self.row_tag(r),))
        else:
            for i, r in enumerate(self.rows):
                tree.item(str(i), values=self.row_values(r), tags=(self.row_tag(r),))

        if self.rows:
            self.drop_label.place_forget()
        else:
            self.drop_label.place(relx=0.5, rely=0.5, anchor="center")
            self.drop_label.lift()

        n = len(self.rows)
        c = sum(1 for r in self.rows if r["st"] == "ok")
        e = sum(1 for r in self.rows if r["st"] in ("invalid", "dup", "exists", "missing"))
        self.stats_var.set(self.t("stats", n=n, c=c, e=e))
        self.btn_rename.state(["!disabled"] if c > 0 else ["disabled"])

    def row_values(self, r):
        key = {"ok": "st_ok", "same": "st_same", "invalid": "st_invalid", "dup": "st_dup",
               "exists": "st_exists", "missing": "st_missing"}[r["st"]]
        return (r["old"], r["new"], self.t(key), r["dir"])

    @staticmethod
    def row_tag(r):
        return {"ok": "ok", "same": "same"}.get(r["st"], "err")

    def set_msg(self, text, error=False):
        self.msg_var.set(text)
        self.msg_label.configure(foreground="#b71c1c" if error else "#1b5e20")

    # --- aplicare, undo, redo ----------------------------------------------
    def do_rename(self):
        errors = [r for r in self.rows if r["st"] in ("invalid", "dup", "exists", "missing")]
        if errors:
            messagebox.showerror(APP_NAME, self.t("err_blocked", n=len(errors)), parent=self.root)
            return
        changes = [r for r in self.rows if r["st"] == "ok"]
        if not changes:
            messagebox.showinfo(APP_NAME, self.t("nothing_to_do"), parent=self.root)
            return
        pairs = [(r["src"], os.path.join(r["dir"], r["new"])) for r in changes]
        done, err = perform_renames(pairs)
        if err is not None:
            messagebox.showerror(APP_NAME, self.t("rename_failed", err=err), parent=self.root)
            self.refresh_preview(rebuild=True)
            return
        self.history = [{"time": datetime.now().isoformat(timespec="seconds"),
                         "pairs": [list(p) for p in done]}]
        self.hist_pos = 1
        self.save_history()
        self.sync_files(done)
        self.refresh_preview(rebuild=True)
        self.update_history_buttons()
        self.set_msg(self.t("renamed_ok", n=len(done)))

    def sync_files(self, applied):
        """applied: [(vechi, nou)] -> actualizează lista de fișiere."""
        index = {nc(p): i for i, p in enumerate(self.files)}
        for old, new in applied:
            i = index.pop(nc(old), None)
            if i is not None:
                self.files[i] = new
                index[nc(new)] = i
            elif nc(new) not in index:
                self.files.append(new)
                index[nc(new)] = len(self.files) - 1

    def undo(self):
        if self.hist_pos <= 0:
            self.set_msg(self.t("undo_none"), error=True)
            return
        batch = self.history[self.hist_pos - 1]
        self._replay([(d, s) for s, d in batch["pairs"]], delta=-1, done_key="undo_done")

    def redo(self):
        if self.hist_pos >= len(self.history):
            self.set_msg(self.t("redo_none"), error=True)
            return
        batch = self.history[self.hist_pos]
        self._replay([(s, d) for s, d in batch["pairs"]], delta=+1, done_key="redo_done")

    def _replay(self, pairs, delta, done_key):
        ok, skipped = filter_applicable(pairs)
        if not ok:
            messagebox.showwarning(APP_NAME, self.t("undo_nothing"), parent=self.root)
            return
        done, err = perform_renames(ok)
        if err is not None:
            messagebox.showerror(APP_NAME, self.t("op_failed", err=err), parent=self.root)
            return
        self.hist_pos += delta
        self.save_history()
        self.sync_files(done)
        self.refresh_preview(rebuild=True)
        self.update_history_buttons()
        if skipped:
            messagebox.showwarning(APP_NAME, self.t("undo_partial", k=len(skipped)), parent=self.root)
        self.set_msg(self.t(done_key, n=len(done)))

    def update_history_buttons(self):
        self.btn_undo.state(["!disabled"] if self.hist_pos > 0 else ["disabled"])
        self.btn_redo.state(["!disabled"] if self.hist_pos < len(self.history) else ["disabled"])

    def save_history(self):
        save_json(HISTORY_FILE, {"pos": self.hist_pos, "batches": self.history})

    def run(self):
        self.root.mainloop()


def main():
    NominaApp().run()


if __name__ == "__main__":
    main()
