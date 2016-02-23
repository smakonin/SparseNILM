#!/bin/bash
#
# RUN FOR STATUS: clear; tail -n 1 *.log
#

#BUILD SSHMM FOR TESTING
./train_SSHMM.py BigO_L01 AMPdsR1_1min_A 10 200 noisy 4 1 BME > logs/BigO_L01.log &
./train_SSHMM.py BigO_L02 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE > logs/BigO_L02.log &
./train_SSHMM.py BigO_L03 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE > logs/BigO_L03.log&
./train_SSHMM.py BigO_L04 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE > logs/BigO_L04.log &
./train_SSHMM.py BigO_L05 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE > logs/BigO_L05.log &
./train_SSHMM.py BigO_L06 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE,FRE > logs/BigO_L06.log &
./train_SSHMM.py BigO_L07 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE,FRE,GRE > logs/BigO_L07.log &
./train_SSHMM.py BigO_L08 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE,FRE,GRE,HPE > logs/BigO_L08.log &
./train_SSHMM.py BigO_L09 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE,FRE,GRE,HPE,OFE > logs/BigO_L09.log &
./train_SSHMM.py BigO_L10 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE,FRE,GRE,HPE,OFE,TVE > logs/BigO_L10.log &
./train_SSHMM.py BigO_L11 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE,FRE,GRE,HPE,OFE,TVE,WOE > logs/BigO_L11.log &
./train_SSHMM.py BigO_L12 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE,FRE,GRE,HPE,OFE,TVE,WOE,B1E > logs/BigO_L12.log

./train_SSHMM.py BigO_L13 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE,FRE,GRE,HPE,OFE,TVE,WOE,B1E,B2E > logs/BigO_L13.log &
./train_SSHMM.py BigO_L14 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE,FRE,GRE,HPE,OFE,TVE,WOE,B1E,B2E,DNE > logs/BigO_L14.log &
./train_SSHMM.py BigO_L15 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE,FRE,GRE,HPE,OFE,TVE,WOE,B1E,B2E,DNE,EBE > logs/BigO_L15.log &
./train_SSHMM.py BigO_L16 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE,FRE,GRE,HPE,OFE,TVE,WOE,B1E,B2E,DNE,EBE,EQE > logs/BigO_L16.log &
./train_SSHMM.py BigO_L17 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE,FRE,GRE,HPE,OFE,TVE,WOE,B1E,B2E,DNE,EBE,EQE,HTE > logs/BigO_L17.log &
./train_SSHMM.py BigO_L18 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE,FRE,GRE,HPE,OFE,TVE,WOE,B1E,B2E,DNE,EBE,EQE,HTE,UTE > logs/BigO_L18.log &
./train_SSHMM.py BigO_L19 AMPdsR1_1min_A 10 200 noisy 4 1 BME,CDE,CWE,DWE,FGE,FRE,GRE,HPE,OFE,TVE,WOE,B1E,B2E,DNE,EBE,EQE,HTE,UTE,UNE > logs/BigO_L19.log

