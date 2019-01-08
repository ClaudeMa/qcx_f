#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyaudio, numpy
import matplotlib.pyplot as plt

chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=chunk)

lastc = -1
lastfreq=0
delay = 5
cnt = 0         # counting symbols
zerocount = 0 # for counting zeros

while True:
    data = stream.read(chunk)   # read data and convert to signed 16b int
    buf=[ numpy.fromstring(data[q:q+2], 'Int16') for q in range(0,len(data), 2)]
    for i in range(0,len(buf)-1):   # for all samples
        if buf[i] == 0 and zerocount < 100: # count 100 samples with '0'
            zerocount = zerocount + 1
            if zerocount == 100:    # if 100 zero samples
                print "Z"           # stop TX
                cnt = 0             # reset symbol counter
        if buf[i] < 0 and buf[i+1] >= 0:    # zero crossing
            zerocount = 0                   # clean 0-sample counter
            crossing = i + float(-buf[i])/(-buf[i]+buf[i+1])    # calculate 0-crossing with sub-sample resolution
            if lastc > 0:   # if there already was a crossing...
                if lastc > crossing:    # crossing in the previous buffer?
                    lastc = lastc-1024  # subtract buffer length
                freq = RATE/(crossing-lastc)    # calculate sine frequency
                if abs(freq-lastfreq) > 1 and abs(freq-lastfreq) < 50: # changed?
                    delay = 5   # wait for 5 more crossings
                if delay == 1:  # print new frequency..
                    print cnt, "---", (lastfreq+freq)/2 # .. as average from last 2 crossings
                    cnt = cnt+1     # increment symbol counter
                if delay > 0:   # waiting
                    delay = delay -1
                lastfreq = freq    # memorize last frequency
            lastc = crossing    # ..and position of last zero-crossing

stream.stop_stream()
stream.close()
p.terminate()