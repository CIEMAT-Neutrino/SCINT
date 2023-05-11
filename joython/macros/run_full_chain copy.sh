#!/bin/bash
#Pedestal & channel parallelized computation, $1 is the week as string argument to analyze

( time cat RUN.txt | ~/parallel --joblog out.txt -j8 "python3 01_Process_Pedestal_and_peak.py -w $1 -r" ) &&
( time cat RUN.txt | ~/parallel --joblog out.txt -j8 "python3 03_Raw_Charges.py -w $1 -r" )