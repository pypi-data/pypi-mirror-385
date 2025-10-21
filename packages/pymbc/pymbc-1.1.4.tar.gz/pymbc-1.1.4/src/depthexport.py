# -*- coding: utf-8 -*-
"""
Created on Thu May  1 10:45:54 2025

Load in a MB Century format CSV file and export as Linewise format.

@author: RWilliams
"""

import pymbc as mbc
from pathlib import Path


if __name__ == "__main__":
    mb = mbc.MbcLog()
    csvfile = Path(r'C:\Users\RWilliams\source\repos\tricky67\pymbc\tests\_20230626_PTS__A.csv')
    mb.ReadMbCsv(csvfile) 

    plotdef = [mbc.PlotDefinition('TIMEDELTA', 'DEPTH', 'slategray', '-', False),
		   mbc.PlotDefinition('TIMEDELTA', 'PTS_PRES', 'royalblue', '-', False),
		   mbc.PlotDefinition('TIMEDELTA', 'PTS_FREQ', 'limegreen', '-', False),
		   mbc.PlotDefinition('TIMEDELTA', 'PTS_TEMP', 'tomato', '--', True)]
    st,figt = mbc.PlotLog(mb, plotdef, title=mb.name, depthaxis=False)
    
    df = mb.logDf.copy()
    depthFile = csvfile.with_stem(csvfile.stem + '_Linewise')
    df['date'] = df['TIMESTAMPISO'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df['time'] = df['TIMESTAMPISO'].apply(lambda x: x.strftime('%H:%M:%S'))
    
    # Make depth METERS
    if mb.logUnits['DEPTH'] == 'FT':
        df['DEPTH'] = df['DEPTH'] / 0.3048
        
    # Make speed M/MIN
    if mb.logUnits['SPEED'] == 'M/S':
        df['SPEED'] = df['SPEED'] * 60.0
    elif mb.logUnits['SPEED'] == 'FT/S':
        df['SPEED'] = df['SPEED'] / 0.3048
    elif mb.logUnits['SPEED'] == 'FT/MIN':
        df['SPEED'] = df['SPEED'] * 60.0 / 0.3048     
     
    # Make tension LBF
    if mb.logUnits['TENSION'] == 'KG':
        df['TENSION'] = df['TENSION'] * 2.2046226218
        
        
    with open(str(depthFile), 'w') as file:

        linewiseHeader = "LINEWISEADVANCE\n" \
        "#Version=1\n" \
        "#Client=\n" \
        f"#Field={mb.logHeader['Field']}\n" \
        f"#Well={mb.logHeader['Well']}\n" \
        "#PulsePerRevolution=\n" \
        "#WheelCircumference=\n" \
        "#WheelCorrection=\n" \
        "DATE  TIME  DEPTH(METER)  SPEED(M/MIN)  TENSION(LBF)\n"
        
        file.write(linewiseHeader)
       
    df.to_csv(str(depthFile), mode='a', header=False, index=False, encoding='utf-8', float_format='%.3f', sep=' ', columns=['date', 'time', 'DEPTH', 'SPEED', 'TENSION'])