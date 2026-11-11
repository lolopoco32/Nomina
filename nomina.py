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

import json
import locale
import os
import re
import sys
import uuid
from collections import Counter
from datetime import datetime

import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except Exception:  # biblioteca lipsește sau nu se poate încărca
    HAS_DND = False

APP_NAME = "Nomina"
IS_WIN = os.name == "nt"
MAX_HISTORY = 100
MIN_W, MIN_H = 940, 600
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
}


# ----------------------------------------------------------------------------
# Configurare și istoric (persistente)
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
# Traduceri
# ----------------------------------------------------------------------------
STR = {
    "ro": {
        "title": "Nomina – Redenumire fișiere în masă",
        "add_files": "Adaugă fișiere", "add_folder": "Adaugă dosar",
        "subfolders": "Include subdosare",
        "remove_sel": "Scoate din listă", "clear": "Golește lista",
        "undo": "Anulează", "redo": "Refă", "rename": "Redenumește",
        "language": "Limbă",
        "layers": "Straturi (în ordinea aplicării)", "add_layer": "Adaugă strat",
        "move_up": "Sus", "move_down": "Jos", "remove_layer": "Șterge",
        "layer_settings": "Setările stratului",
        "no_layer_sel": "Adaugă sau selectează un strat.",
        "layer_enabled": "Strat activ",
        "files_preview": "Fișiere și previzualizare",
        "col_layer": "Strat", "col_details": "Detalii",
        "col_source": "Sursă", "col_dest": "Destinație",
        "col_status": "Stare", "col_folder": "Dosar",
        "st_ok": "Se redenumește", "st_same": "Neschimbat",
        "st_invalid": "Nume invalid", "st_dup": "Duplicat",
        "st_exists": "Există deja", "st_missing": "Lipsește",
        "drop_hint": "Trage aici fișiere sau dosare\nsau folosește butoanele de sus",
        "drop_hint_nodnd": "Folosește butoanele de sus pentru a adăuga fișiere.\n(Pentru drag & drop: instalează pachetul «tkdnd» sau rulează pip install tkinterdnd2)",
        "stats": "{n} fișiere · {c} de redenumit · {e} erori",
        "lt_replace": "Găsește și înlocuiește",
        "lt_digits": "Înlătură cifre / numere",
        "lt_trim": "Înlătură primele / ultimele caractere",
        "lt_add": "Adaugă la început / sfârșit",
        "lt_case": "Litere mari / mici",
        "lt_ext": "Extensie",
        "find": "Găsește:", "replace_with": "Înlocuiește cu:",
        "case_sensitive": "Sensibil la majuscule", "use_regex": "Expresie regulată (regex)",
        "regex_error": "Regex invalid: {msg}",
        "digits_all": "Toate cifrele din nume", "digits_start": "Doar cele de la început",
        "digits_end": "Doar cele de la sfârșit",
        "strip_sep": "Curăță separatorii rămași (spații _ - .)",
        "trim_first": "Primele caractere:", "trim_last": "Ultimele caractere:",
        "prefix": "La început (prefix):", "suffix": "La sfârșit (sufix):",
        "suffix_note": "Sufixul se adaugă înaintea extensiei.",
        "case_lower": "toate minuscule", "case_upper": "TOATE MAJUSCULE",
        "case_title": "Prima Literă Din Fiecare Cuvânt", "case_sentence": "Doar prima literă majusculă",
        "ext_change": "Schimbă extensia cu:", "ext_lower": "Extensie cu litere mici (.JPG → .jpg)",
        "ext_upper": "Extensie cu litere mari (.jpg → .JPG)", "ext_remove": "Înlătură extensia",
        "ext_note": "Celelalte straturi nu modifică niciodată extensia.",
        "sum_replace": "«{a}» → «{b}»", "sum_replace_re": "regex «{a}» → «{b}»",
        "sd_all": "toate cifrele", "sd_start": "cifre de la început", "sd_end": "cifre de la sfârșit",
        "sum_trim": "−{a} la început, −{b} la sfârșit",
        "sum_add": "«{a}» … «{b}»",
        "sc_lower": "minuscule", "sc_upper": "MAJUSCULE", "sc_title": "Cuvinte Capitalizate", "sc_sentence": "Prima literă mare",
        "sum_ext_change": "→ .{a}", "sum_ext_lower": "minuscule", "sum_ext_upper": "MAJUSCULE", "sum_ext_remove": "fără extensie",
        "dlg_add_files": "Alege fișiere", "dlg_add_folder": "Alege un dosar",
        "added": "{n} fișiere adăugate.",
        "err_blocked": "Nu se poate redenumi: există {n} erori în previzualizare (marcate cu roșu).",
        "nothing_to_do": "Nu există nicio modificare de aplicat.",
        "renamed_ok": "✔ {n} fișiere redenumite. Poți anula cu «Anulează».",
        "rename_failed": "Redenumirea a eșuat și a fost anulată complet (nimic nu a fost modificat):\n\n{err}",
        "undo_done": "↶ {n} fișiere restaurate.", "redo_done": "↷ {n} fișiere redenumite din nou.",
        "undo_none": "Nimic de anulat.", "redo_none": "Nimic de refăcut.",
        "undo_partial": "{k} fișiere au fost omise (mutate, șterse sau numele destinație este ocupat).",
        "undo_nothing": "Nu s-a putut aplica nicio modificare: fișierele au fost mutate, șterse sau redenumite din altă parte.",
        "op_failed": "Operația a eșuat și a fost anulată:\n\n{err}",
    },
    "en": {
        "title": "Nomina – Batch file renamer",
        "add_files": "Add files", "add_folder": "Add folder",
        "subfolders": "Include subfolders",
        "remove_sel": "Remove from list", "clear": "Clear list",
        "undo": "Undo", "redo": "Redo", "rename": "Rename",
        "language": "Language",
        "layers": "Layers (in order of application)", "add_layer": "Add layer",
        "move_up": "Up", "move_down": "Down", "remove_layer": "Delete",
        "layer_settings": "Layer settings",
        "no_layer_sel": "Add or select a layer.",
        "layer_enabled": "Layer enabled",
        "files_preview": "Files and preview",
        "col_layer": "Layer", "col_details": "Details",
        "col_source": "Source", "col_dest": "Destination",
        "col_status": "Status", "col_folder": "Folder",
        "st_ok": "Will rename", "st_same": "Unchanged",
        "st_invalid": "Invalid name", "st_dup": "Duplicate",
        "st_exists": "Already exists", "st_missing": "Missing",
        "drop_hint": "Drag files or folders here\nor use the buttons above",
        "drop_hint_nodnd": "Use the buttons above to add files.\n(For drag & drop: install the “tkdnd” package or run pip install tkinterdnd2)",
        "stats": "{n} files · {c} to rename · {e} errors",
        "lt_replace": "Find and replace",
        "lt_digits": "Remove digits / numbers",
        "lt_trim": "Remove first / last characters",
        "lt_add": "Add at start / end",
        "lt_case": "Upper / lower case",
        "lt_ext": "Extension",
        "find": "Find:", "replace_with": "Replace with:",
        "case_sensitive": "Case sensitive", "use_regex": "Regular expression (regex)",
        "regex_error": "Invalid regex: {msg}",
        "digits_all": "All digits in the name", "digits_start": "Only at the start",
        "digits_end": "Only at the end",
        "strip_sep": "Trim leftover separators (spaces _ - .)",
        "trim_first": "First characters:", "trim_last": "Last characters:",
        "prefix": "At the start (prefix):", "suffix": "At the end (suffix):",
        "suffix_note": "The suffix is added before the extension.",
        "case_lower": "all lowercase", "case_upper": "ALL UPPERCASE",
        "case_title": "Capitalize Each Word", "case_sentence": "Capitalize first letter only",
        "ext_change": "Change extension to:", "ext_lower": "Lowercase extension (.JPG → .jpg)",
        "ext_upper": "Uppercase extension (.jpg → .JPG)", "ext_remove": "Remove extension",
        "ext_note": "Other layers never touch the extension.",
        "sum_replace": "«{a}» → «{b}»", "sum_replace_re": "regex «{a}» → «{b}»",
        "sd_all": "all digits", "sd_start": "leading digits", "sd_end": "trailing digits",
        "sum_trim": "−{a} from start, −{b} from end",
        "sum_add": "«{a}» … «{b}»",
        "sc_lower": "lowercase", "sc_upper": "UPPERCASE", "sc_title": "Title Case", "sc_sentence": "Sentence case",
        "sum_ext_change": "→ .{a}", "sum_ext_lower": "lowercase", "sum_ext_upper": "UPPERCASE", "sum_ext_remove": "no extension",
        "dlg_add_files": "Choose files", "dlg_add_folder": "Choose a folder",
        "added": "{n} files added.",
        "err_blocked": "Cannot rename: there are {n} errors in the preview (marked in red).",
        "nothing_to_do": "There is nothing to apply.",
        "renamed_ok": "✔ {n} files renamed. You can revert with “Undo”.",
        "rename_failed": "Renaming failed and was fully rolled back (nothing was changed):\n\n{err}",
        "undo_done": "↶ {n} files restored.", "redo_done": "↷ {n} files renamed again.",
        "undo_none": "Nothing to undo.", "redo_none": "Nothing to redo.",
        "undo_partial": "{k} files were skipped (moved, deleted, or the target name is taken).",
        "undo_nothing": "Nothing could be applied: the files were moved, deleted or renamed elsewhere.",
        "op_failed": "The operation failed and was rolled back:\n\n{err}",
    },
    "it": {
        "title": "Nomina – Rinomina file in blocco",
        "add_files": "Aggiungi file", "add_folder": "Aggiungi cartella",
        "subfolders": "Includi sottocartelle",
        "remove_sel": "Rimuovi dalla lista", "clear": "Svuota lista",
        "undo": "Annulla", "redo": "Ripeti", "rename": "Rinomina",
        "language": "Lingua",
        "layers": "Livelli (in ordine di applicazione)", "add_layer": "Aggiungi livello",
        "move_up": "Su", "move_down": "Giù", "remove_layer": "Elimina",
        "layer_settings": "Impostazioni del livello",
        "no_layer_sel": "Aggiungi o seleziona un livello.",
        "layer_enabled": "Livello attivo",
        "files_preview": "File e anteprima",
        "col_layer": "Livello", "col_details": "Dettagli",
        "col_source": "Origine", "col_dest": "Destinazione",
        "col_status": "Stato", "col_folder": "Cartella",
        "st_ok": "Verrà rinominato", "st_same": "Invariato",
        "st_invalid": "Nome non valido", "st_dup": "Duplicato",
        "st_exists": "Esiste già", "st_missing": "Mancante",
        "drop_hint": "Trascina qui file o cartelle\noppure usa i pulsanti in alto",
        "drop_hint_nodnd": "Usa i pulsanti in alto per aggiungere file.\n(Per il drag & drop: installa il pacchetto «tkdnd» oppure esegui pip install tkinterdnd2)",
        "stats": "{n} file · {c} da rinominare · {e} errori",
        "lt_replace": "Trova e sostituisci",
        "lt_digits": "Rimuovi cifre / numeri",
        "lt_trim": "Rimuovi primi / ultimi caratteri",
        "lt_add": "Aggiungi all'inizio / alla fine",
        "lt_case": "Maiuscole / minuscole",
        "lt_ext": "Estensione",
        "find": "Trova:", "replace_with": "Sostituisci con:",
        "case_sensitive": "Distingui maiuscole", "use_regex": "Espressione regolare (regex)",
        "regex_error": "Regex non valida: {msg}",
        "digits_all": "Tutte le cifre nel nome", "digits_start": "Solo all'inizio",
        "digits_end": "Solo alla fine",
        "strip_sep": "Pulisci i separatori rimasti (spazi _ - .)",
        "trim_first": "Primi caratteri:", "trim_last": "Ultimi caratteri:",
        "prefix": "All'inizio (prefisso):", "suffix": "Alla fine (suffisso):",
        "suffix_note": "Il suffisso viene aggiunto prima dell'estensione.",
        "case_lower": "tutto minuscolo", "case_upper": "TUTTO MAIUSCOLO",
        "case_title": "Iniziale Maiuscola Per Parola", "case_sentence": "Solo la prima lettera maiuscola",
        "ext_change": "Cambia estensione in:", "ext_lower": "Estensione minuscola (.JPG → .jpg)",
        "ext_upper": "Estensione maiuscola (.jpg → .JPG)", "ext_remove": "Rimuovi estensione",
        "ext_note": "Gli altri livelli non modificano mai l'estensione.",
        "sum_replace": "«{a}» → «{b}»", "sum_replace_re": "regex «{a}» → «{b}»",
        "sd_all": "tutte le cifre", "sd_start": "cifre iniziali", "sd_end": "cifre finali",
        "sum_trim": "−{a} all'inizio, −{b} alla fine",
        "sum_add": "«{a}» … «{b}»",
        "sc_lower": "minuscolo", "sc_upper": "MAIUSCOLO", "sc_title": "Iniziali Maiuscole", "sc_sentence": "Prima maiuscola",
        "sum_ext_change": "→ .{a}", "sum_ext_lower": "minuscola", "sum_ext_upper": "MAIUSCOLA", "sum_ext_remove": "senza estensione",
        "dlg_add_files": "Scegli i file", "dlg_add_folder": "Scegli una cartella",
        "added": "{n} file aggiunti.",
        "err_blocked": "Impossibile rinominare: ci sono {n} errori nell'anteprima (in rosso).",
        "nothing_to_do": "Non c'è nessuna modifica da applicare.",
        "renamed_ok": "✔ {n} file rinominati. Puoi annullare con «Annulla».",
        "rename_failed": "La ridenominazione è fallita ed è stata annullata completamente (nulla è stato modificato):\n\n{err}",
        "undo_done": "↶ {n} file ripristinati.", "redo_done": "↷ {n} file rinominati di nuovo.",
        "undo_none": "Niente da annullare.", "redo_none": "Niente da ripetere.",
        "undo_partial": "{k} file sono stati saltati (spostati, eliminati o nome di destinazione occupato).",
        "undo_nothing": "Nessuna modifica applicabile: i file sono stati spostati, eliminati o rinominati altrove.",
        "op_failed": "L'operazione è fallita ed è stata annullata:\n\n{err}",
    },
}

LAYER_TYPES = ["replace", "digits", "trim", "add", "case", "ext"]

DEFAULT_PARAMS = {
    "replace": {"find": "", "repl": "", "case": True, "regex": False},
    "digits": {"scope": "all", "strip": True},
    "trim": {"first": 0, "last": 0},
    "add": {"prefix": "", "suffix": ""},
    "case": {"mode": "lower"},
    "ext": {"mode": "change", "ext": ""},
}


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


def apply_layer(layer, stem, ext):
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
        if p["strip"]:
            stem = re.sub(r" {2,}", " ", stem).strip(" _-.")
        return stem, ext

    if t == "trim":
        first = max(0, int(p["first"]))
        last = max(0, int(p["last"]))
        if first:
            stem = stem[first:]
        if last:
            stem = stem[:-last]
        return stem, ext

    if t == "add":
        return p["prefix"] + stem + p["suffix"], ext

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
_WIN_RESERVED = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}


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
        self.layers = []         # [{'type','enabled','params'}]
        self.rows = []           # rezultatul calculului
        self.cur_layer = None
        self._lock = False
        self._i18n = []
        self._sort_rev = False
        self.msg_kind = None

        hist = load_json(HISTORY_FILE, {})
        self.history = hist.get("batches", []) if isinstance(hist, dict) else []
        self.hist_pos = hist.get("pos", len(self.history)) if isinstance(hist, dict) else 0
        self.hist_pos = max(0, min(int(self.hist_pos), len(self.history)))

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
        self.apply_language(first=True)
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
        self.paned.add(self.left, minsize=380, stretch="never")
        self.paned.add(self.right, minsize=RIGHT_MIN, stretch="always")

        self.build_left()
        self.build_right()

    def build_left(self):
        f = self.left
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)

        row = ttk.Frame(f)
        row.grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.mb_add = ttk.Menubutton(row, image=self.icons.get("plus"), compound="left")
        self.reg(self.mb_add, "add_layer")
        self.mb_add.pack(side="left", padx=(0, 4))
        self.add_menu = tk.Menu(self.mb_add, tearoff=0)
        self.mb_add.configure(menu=self.add_menu)
        self.mkbtn(row, "move_up", "up", lambda: self.move_layer(-1)).pack(side="left", padx=4)
        self.mkbtn(row, "move_down", "down", lambda: self.move_layer(1)).pack(side="left", padx=4)
        self.mkbtn(row, "remove_layer", "delete", self.remove_layer).pack(side="left", padx=4)

        wrap = ttk.Frame(f)
        wrap.grid(row=1, column=0, sticky="nsew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)
        self.ltree = ttk.Treeview(wrap, columns=("on", "n", "layer", "details"), show="headings",
                                  selectmode="browse", height=6)
        self.ltree.column("on", width=30, minwidth=30, stretch=False, anchor="center")
        self.ltree.column("n", width=30, minwidth=30, stretch=False, anchor="center")
        self.ltree.column("layer", width=150, minwidth=90, stretch=False)
        self.ltree.column("details", width=150, minwidth=60, stretch=True)
        self.ltree.heading("on", text="")
        self.ltree.heading("n", text="#")
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.ltree.yview)
        self.ltree.configure(yscrollcommand=sb.set)
        self.ltree.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")

        self.editor = ttk.LabelFrame(f, padding=8, width=360, height=190)
        self.editor.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.editor.grid_propagate(False)
        self.editor.columnconfigure(1, weight=1)
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
        vs = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        hs = ttk.Scrollbar(wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
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

    # --- evenimente ---------------------------------------------------------
    def bind_events(self):
        self.ltree.bind("<<TreeviewSelect>>", self.on_layer_select)
        self.ltree.bind("<Button-1>", self.on_layer_click, add="+")
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
        idx = self.lang_combo.current()
        self.lang = list(LANGS.keys())[idx]
        self.apply_language()

    def apply_language(self, first=False):
        for w, opt, key in self._i18n:
            w.configure(**{opt: self.t(key)})
        self.root.title(self.t("title"))
        self.lang_combo.current(list(LANGS.keys()).index(self.lang))
        self.lang_combo.selection_clear()

        self.add_menu.delete(0, "end")
        for lt in LAYER_TYPES:
            self.add_menu.add_command(label=self.t("lt_" + lt), command=lambda x=lt: self.add_layer(x))

        self.ltree.heading("layer", text=self.t("col_layer"))
        self.ltree.heading("details", text=self.t("col_details"))
        self.tree.heading("old", text=self.t("col_source"), command=self.sort_by_source)
        self.tree.heading("new", text=self.t("col_dest"))
        self.tree.heading("status", text=self.t("col_status"))
        self.tree.heading("folder", text=self.t("col_folder"))
        self.drop_label.configure(text=self.t("drop_hint" if self.has_dnd else "drop_hint_nodnd"))

        sel = self.selected_layer()
        self.refresh_layers(select=sel)
        self.build_editor()
        self.refresh_preview(rebuild=True)
        self.update_history_buttons()
        self.set_msg("")
        self.update_minsize()

    def update_minsize(self):
        r = self.root
        r.update_idletasks()
        left_w = max(self.left.winfo_reqwidth(), 380)
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
        w, h, x, y = 1120, 700, None, None
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

    # --- straturi -----------------------------------------------------------
    def selected_layer(self):
        sel = self.ltree.selection()
        if sel:
            i = int(sel[0])
            if 0 <= i < len(self.layers):
                return i
        return None

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
        if t == "add":
            return T("sum_add", a=p["prefix"], b=p["suffix"])
        if t == "case":
            return T("sc_" + p["mode"])
        if t == "ext":
            if p["mode"] == "change":
                new = p["ext"].strip().lstrip(".")
                return T("sum_ext_change", a=new) if new else ""
            return T("sum_ext_" + p["mode"])
        return ""

    def layer_values(self, i):
        L = self.layers[i]
        return ("☑" if L["enabled"] else "☐", str(i + 1), self.t("lt_" + L["type"]), self.layer_summary(L))

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
        self.layers.append({"type": ltype, "enabled": True, "params": dict(DEFAULT_PARAMS[ltype])})
        self.refresh_layers(select=len(self.layers) - 1)
        self.build_editor()
        self.refresh_preview()

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

    # --- editorul stratului selectat ---------------------------------------
    def watch(self, var, key, cast=None):
        L = self.cur_layer

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
            L["params"][key] = val
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
            ttk.Label(ed, text=self.t("no_layer_sel"), foreground="#7a7a7a").grid(row=0, column=0, columnspan=2, sticky="w")
            return
        L = self.layers[i]
        self.cur_layer = L
        p = L["params"]

        ttk.Label(ed, text=self.t("lt_" + L["type"]), font=self._bold).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.enabled_var = tk.BooleanVar(value=L["enabled"])
        ttk.Checkbutton(ed, text=self.t("layer_enabled"), variable=self.enabled_var).grid(
            row=0, column=1, sticky="e", pady=(0, 4))
        # "enabled" nu e în params, deci îl tratăm separat
        self.enabled_var.trace_add("write", lambda *_: self._set_enabled(L))

        def entry(row, label_key, key):
            ttk.Label(ed, text=self.t(label_key)).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=3)
            var = tk.StringVar(value=p[key])
            ttk.Entry(ed, textvariable=var).grid(row=row, column=1, sticky="ew", pady=3)
            self.watch(var, key)

        def check(row, label_key, key):
            var = tk.BooleanVar(value=p[key])
            ttk.Checkbutton(ed, text=self.t(label_key), variable=var).grid(
                row=row, column=0, columnspan=2, sticky="w", pady=2)
            self.watch(var, key)

        def radios(row, key, options):
            var = tk.StringVar(value=p[key])
            for k, (value, label_key) in enumerate(options):
                ttk.Radiobutton(ed, text=self.t(label_key), variable=var, value=value).grid(
                    row=row + k, column=0, columnspan=2, sticky="w", pady=1)
            self.watch(var, key)

        def spin(row, label_key, key):
            ttk.Label(ed, text=self.t(label_key)).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=4)
            var = tk.IntVar(value=p[key])
            ttk.Spinbox(ed, from_=0, to=255, width=6, textvariable=var).grid(row=row, column=1, sticky="w", pady=4)
            self.watch(var, key, cast=lambda v: max(0, int(v)))

        t = L["type"]
        if t == "replace":
            entry(1, "find", "find")
            entry(2, "replace_with", "repl")
            check(3, "case_sensitive", "case")
            check(4, "use_regex", "regex")
            self.err_label = ttk.Label(ed, foreground="#b71c1c", wraplength=330, justify="left")
            self.err_label.grid(row=5, column=0, columnspan=2, sticky="w")
            self.check_regex(L)
        elif t == "digits":
            radios(1, "scope", [("all", "digits_all"), ("start", "digits_start"), ("end", "digits_end")])
            check(4, "strip_sep", "strip")
        elif t == "trim":
            spin(1, "trim_first", "first")
            spin(2, "trim_last", "last")
        elif t == "add":
            entry(1, "prefix", "prefix")
            entry(2, "suffix", "suffix")
            ttk.Label(ed, text=self.t("suffix_note"), foreground="#7a7a7a").grid(
                row=3, column=0, columnspan=2, sticky="w", pady=(4, 0))
        elif t == "case":
            radios(1, "mode", [("lower", "case_lower"), ("upper", "case_upper"),
                               ("title", "case_title"), ("sentence", "case_sentence")])
        elif t == "ext":
            mode_var = tk.StringVar(value=p["mode"])
            ext_var = tk.StringVar(value=p["ext"])
            ttk.Radiobutton(ed, text=self.t("ext_change"), variable=mode_var, value="change").grid(
                row=1, column=0, sticky="w", padx=(0, 8), pady=3)
            ttk.Entry(ed, textvariable=ext_var, width=12).grid(row=1, column=1, sticky="w", pady=3)
            for k, (val, lk) in enumerate([("lower", "ext_lower"), ("upper", "ext_upper"), ("remove", "ext_remove")]):
                ttk.Radiobutton(ed, text=self.t(lk), variable=mode_var, value=val).grid(
                    row=2 + k, column=0, columnspan=2, sticky="w", pady=1)
            ttk.Label(ed, text=self.t("ext_note"), foreground="#7a7a7a").grid(
                row=5, column=0, columnspan=2, sticky="w", pady=(4, 0))
            self.watch(mode_var, "mode")
            self.watch(ext_var, "ext")

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
    def compute_rows(self):
        active = [L for L in self.layers if L["enabled"]]
        rows = []
        for p in self.files:
            d, old = os.path.split(p)
            stem, ext = split_name(old)
            for L in active:
                stem, ext = apply_layer(L, stem, ext)
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

    def refresh_preview(self, rebuild=False):
        self.rows = self.compute_rows()
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
        del self.history[self.hist_pos:]
        self.history.append({"time": datetime.now().isoformat(timespec="seconds"),
                             "pairs": [list(p) for p in done]})
        if len(self.history) > MAX_HISTORY:
            del self.history[:len(self.history) - MAX_HISTORY]
        self.hist_pos = len(self.history)
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
