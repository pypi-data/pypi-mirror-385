__author__='Richard Williams'
__author_email__='rwilliams@mbcentury.com'

import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import SpanSelector
import pathlib
from pathlib import Path
import datetime
import io
from io import BytesIO, StringIO
from contextlib import contextmanager

DEF_ENCODING = "ISO-8859-1"

@contextmanager
def opencsv(source, mode='r', encoding=DEF_ENCODING):
    """
    opencsv - Implements a file opening context manager, i.e. it can be used with the "with" statement.
    opencsv can work with a string filename, pathlib file spec, StringIO, BytesIO objects and objects derived from them.

    Parameters
    ----------
    source : str, pathlib.Path, io.StringIO, io.BytesIO
        If the file is a file spec, open it. If it is a text stream, pass along the already open stream stream.
        If it is a byte stream, decode it to a text stream and pass the text stream onwards.
    mode : str, optional
        File OOpen mode. The default is 'r'.
    encoding : str, optional
        The decoding option. The default is DEF_ENCODING.

    Raises
    ------
    TypeError
        Don't understand the source type.

    Yields
    ------
    STREAM
        Open text file stream.

    """
    file = None
    try:
        if isinstance(source, pathlib.Path):
            file = open(str(source), mode=mode, encoding=encoding)
        elif isinstance(source, str):
            # It's a file path, open it
            file = open(source, mode=mode, encoding=encoding)
        elif isinstance(source, io.TextIOBase)  and hasattr(source, 'read'):
            # It's an open text file object or stream io.StringIO
            file = source
        elif isinstance(source, io.BytesIO) and hasattr(source, 'read'):
            # must be io.BytesIO or something derived from it.
            file = StringIO(source.getvalue().decode(encoding))
            if hasattr(source, 'name'):
                file.name = source.name

        else:
            raise TypeError("Source must be a file path (str), an open file object, or a stream.")
     
        yield file  # The resource is yielded to the 'with' block
    finally:
        if file:
            if hasattr(file, 'close'):
                file.close() # Cleanup happens after the 'with' block finishes
         
        
class MbcLog:
    """
    A class to contain and manipulate MB Century downhole log data.
    
    ...
    
    Attributes
    ----------
    logDf: Pandas dataframe 
        Downhole log data as exported from Uphole Logger/Century Logger as CSV and read in using ReadMbCsv()
    logHeader: Dictionary 
        CSV header items as exported from Uphole Logger/Century Logger as CSV and read in using ReadMbCsv()
    logUnits: Dictionary 
        Column names and their units
    notesDf: Pandas dataframe 
        Notes collected during the log as exported from Century Logger as CSV and read in using ReadNotes()
    name: STRING
        Name of the dataset
    
    """
    def __init__(self):
        """
        Initialisation function for MbcData

        """
        self.logDf = pd.DataFrame()
        self.logHeader = {}
        self.logUnits = {}
        self.notesDf = pd.DataFrame()
        self.name = ''


    def ReadMbCsv(self, csvfile):
        """
        Read in an MB Century CSV file.
        Args:
            csvfile: STRING or PathLib file spec of CSV file.
    
        Sets class variables:
            logDf:      Pandas DataFrame of log data.
            logHeader:  DICTIONARY of strings containing the CSV file header items.
            logUnits:   DICTIONARY of strings containing the units of the data columns.
            name:       STRING name of dataset.
        """
        logVersion = 0
        headerLines = 0
        csvHeader = {}
        dataUnits = {}
    
        def CsvKeyVal(line):
            try:
                key = line[:line.index(":")]
                val = line[line.index(":") + 1:]
                # Strip off spaces and also strip off spurious commas at end 
                # that may have been added by Excel when it mangled the CSV file.
                val = val.strip().strip(',')   
            except(ValueError) as exc:
                raise HeaderDecodingError(f'Unable to decode header key:value pair from "{line}"') from exc
            return key, val
    
        def RenameColumns(l : list):
            """
            Rename columns from older formats to match V2.
            
            Parameters
            ----------
            l : list of STRING
                List of data names.

            Returns
            -------
            l : TYPE of STRING
                List of data names modified to replace older incorrect spellings etc.
            """           
            renameList = {
                'Timestamp': 'TIMESTAMP',
                'Cable Weight': 'TENSION',
                'WHP': 'WHP',
                'Temperature': 'PTS_TEMP',
                'Pressure': 'PTS_PRES',
                'Frequency': 'PTS_FREQ',
                'Reed 0': 'PTS_REED0',
                'Reed 1': 'PTS_REED1',
                'Reed 2': 'PTS_REED2',
                'Reed 3': 'PTS_REED3',
                'Cable Voltage': 'PTS_CHV',
                'Battery Voltage': 'PTS_V_BATT',
                'Internal Temp 1': 'PTS_INT_TEMP1',
                'Internal Temp 2': 'PTS_INT_TEMP2',
                'Internal Temp 3': 'PTS_INT_TEMP3',
                'Error Code 1': 'PTS_ERR1',
                'Error Code 2': 'PTS_ERR2',
                'Error Code 3': 'PTS_ERR3',
                'Records Saved': 'PTS_RECORDS',
                'Bad Pages': 'PTS_BAD_PGS',
                'Date': 'DATE',
                'Time': 'TIME'}
            
            for old, new in renameList.items():
                l = list(map(lambda x: x.replace(old, new), l))
                
            return l
        
        class HeaderDecodingError(Exception):
            """Exception raised when we find something unexpected in the header.
    
            Attributes:
                message -- explanation of the error
            """
    
            def __init__(self, message="Found something unexpected in the header"):
                self.message = message
                # super().__init__(self.message)
    
            def __str__(self):
                return f'{self.message}'
    
            pass

        with opencsv(csvfile, mode='r', encoding = DEF_ENCODING) as fp:
            # Read in 1st line
            line = fp.readline()
            if line.find('MBCLOG V2') >= 0:
                print('Detected MBC V2 CSV format')
                logVersion = '2'
                for i in range(1, 22):
                    line = fp.readline()
                    if line.find('ENDOFHEADER') >= 0:
                        headerLines = i + 1
                        nameLine = fp.readline()
                        names = nameLine.strip().split(',')
                        names = RenameColumns(names)
                        unitLine = fp.readline()
                        units = unitLine.strip().split(',')
                        dataUnits = dict(zip(names, units))
                        break
                    key, val = CsvKeyVal(line)
                    csvHeader[key] = val
                    if i > 200:
                        raise HeaderDecodingError('CSV V2 Header is malformed (has no ENDOFHEADER line)')
    
            else:
                # Check 1st line for V1 format
                key1, val1 = CsvKeyVal(line)
                CREATE_DATE = 'CsvFileCreationDate'
                #print('Looking for ' + CREATE_DATE)
                if CREATE_DATE in key1:       
                    headerLines = 16  # Number of header
                    csvHeader[CREATE_DATE] = val1
                    # Read in lines 2 to 17 (header key:value pairs)
                    for i in range(2, 17):
                        line = fp.readline()
                        key, val = CsvKeyVal(line)
                        csvHeader[key] = val
                    
                    if 'Impeller Pitch (inches)' not in csvHeader:
                        print('Detected MBC V1 Dummy/HTCC CSV format')
                        logVersion = '1d'
                    else:
                        print('Detected MBC V1 CSV format')
                        logVersion = '1'
                        headerLines += 1
                        line = fp.readline()
                        key, val = CsvKeyVal(line)
                        csvHeader[key] = val
                            
                    try:
                        # Read in line 18 (column names)
                        nameLine = fp.readline()
                        names = nameLine.strip().split(',')
                        names = RenameColumns(names)
                    except(ValueError) as exc:
                        raise HeaderDecodingError(f'Unexpected values in data names row "{nameLine}"') from exc
                        
                    try:
                        # Read in line 19 (units)
                        unitLine = fp.readline()
                        units = unitLine.strip().split(',')
                        dataUnits = dict(zip(names, units))
                    except(ValueError) as exc:
                        raise HeaderDecodingError(f'Unexpected values in data units row "{unitLine}"') from exc
    
                else:
                    raise HeaderDecodingError(f'Unexpected value in first line [{line}]')
        
        csvHeader['version'] = logVersion
    
        # Make a list of rows to skip when reading in the data.
        skipl = list(range(0, headerLines))  # Skip all the header rows except the names.
        skipl.append(headerLines + 1)  # Also skip the units row.
    
        # Read in the data using the names row to name the columns.
        #df = pd.read_csv(csvfile, skiprows=skipl, encoding='windows-1252')
        df = pd.read_csv(csvfile, skiprows=skipl, encoding=DEF_ENCODING)
    
        # Fix historical naming issues.
        df.columns = RenameColumns(df.columns)
        
        # Add delta time column.
        if logVersion == '2':
            df['TIMEDELTA'] = df['TIMESTAMP']
        else:
            startTime = df['TIMESTAMP'][0]
            df['TIMEDELTA'] = (df['TIMESTAMP'] - startTime) * 3600 * 24.0  # Excel timestamp is in days
            df['TIMEDELTA'] = df['TIMEDELTA'].round(5)  # Fix rounding errors.
    
        dataUnits['TIMEDELTA'] = 'SEC'
        
        # Add ISO timestamp column.
        if logVersion == '2':
            logEpoc = datetime.datetime.fromisoformat(csvHeader['logStartTime'])
        else:
            logEpoc = datetime.datetime(1899,12,30) + datetime.timedelta(df['TIMESTAMP'].iloc[0])  # Excel datetime epoc
    
        df['TIMESTAMPISO'] = df.apply(lambda row: logEpoc + datetime.timedelta(0, row.TIMEDELTA), axis=1)
        
        df['INDEX'] = df.index
        dataUnits['INDEX'] = 'COUNTS'
        
        # Remove degree signs from old format CSV's
        for u in dataUnits:
            dataUnits[u] = dataUnits[u].replace('°','')
            dataUnits[u] = dataUnits[u].replace('²','2')
        
        self.logDf = df
        self.logHeader = csvHeader
        self.logUnits = dataUnits
        if isinstance(csvfile, str):
            self.name = Path(csvfile).stem       
        elif isinstance(csvfile, pathlib.Path):
            self.name = csvfile.stem    
        else:
            if hasattr(csvfile, 'name'):
                self.name =  Path(csvfile.name).stem
        
        return 
    
    
    def ReadNotes(self, fnotes):
        """
        Read the notes file that is exported along with the data.
    
        Parameters
        ----------
        fnotes: STRING or PathLib 
            File spec of notes file..
    
        Sets class variable
        -------
        notesDf : Pandas Dataframe
            Items from the Notes file.
    
        """
        # Attempt to read notes file.
        #if notesfile == None:
            #fnotes = csvfile.parent / (csvfile.stem + '_notes' + csvfile.suffix)
        dfn = pd.read_csv(str(fnotes), header=None, names=['Type', 'Run', 'Datetime', 'Depth', 'Comment'], converters={'Type':str, 'Comment':str}, parse_dates=['Datetime'])
        self.notesDf = dfn
        return 
        
    
    def CreateRunLogNotes(self):    
        """
        Create a RUNNO column in the log Dataframe based on run numbers from the Notes csv file.

        Parameters
        ----------

        Returns
        -------
        None.

        """
        
        if self.logDf.empty:
            raise ValueError('logDf is empty. You must have data present to perform this process.')
        if self.notesDf.empty:
            raise ValueError('notesDf is empty. You must have data present to perform this process.')
        
        self.logDf['RUNNO'] = 0
        
        for run in range(1,1000):
            dfr = self.notesDf[self.notesDf.Run == run]
            if dfr.empty:
                break

            start = dfr[dfr.Type == 'S'].Datetime.iloc[0]
            stop = dfr[dfr.Type == 'E'].Datetime.iloc[0]
            i = (self.logDf.TIMESTAMPISO >= start) & (self.logDf.TIMESTAMPISO < stop)
            self.logDf.loc[i, 'RUNNO'] = run
        
    
    def CreateRunLogGuess(self, plot=False, useSpeed=True):    
        """
        Create a RUNNO column in the log Dataframe based on a guessing the 
        run start and stop positions based on the DEPTH log.

        Parameters
        ----------
        plot : BOOLEAN, optional
            Plot intermediate steps in picking the run start/stop positions. The default is False.

        Returns
        -------
        None.
        
        Creates self.logDf['RUNNO'] column.

        """
        # Get sampling frequency of dataset.
        dx = self.logDf['TIMEDELTA'].iloc[1]- self.logDf['TIMEDELTA'].iloc[0]
        fs = 1/dx
        
        if useSpeed:
            # Fix slight delay (1 sec) in SPEED and remove NAN's.
            delay = round( 1 * fs)
            speed = self.logDf.SPEED.shift(-delay).fillna(0)
        
        else:
            # Derive speed from DEPTH log
            # Due to jitter error, this method is more noisy, but still works.
            speed = np.gradient(self.logDf.DEPTH, dx)
            bc = signal.firwin(4001, 0.1, window='hann', pass_zero=True, fs=fs)
            speed = signal.filtfilt(bc, [1.0], speed)
        
        # Calculate acceleration.
        accel = np.gradient(speed, dx)
        
        # Use cross correlation to filter noise out and enhance the acceleration peaks (when the winch starts and stops).
        peakShape = np.concatenate((np.zeros(11), [1,4,7,8,8,8,8,8,7,4,1], np.zeros(11)))
        peakShape = peakShape / np.sum(peakShape)
        xcAccel = signal.correlate(accel, peakShape, mode='same')
        absAccel = np.abs(xcAccel)
        
        # Use a threshold of 0.05 m/s/s to detect peaks (i.e. exclude peaks below that).
        threshold = 0.05   # (m/s/s)
        
        # Select a minimum distance between peaks (d).  100 > d > 28 seconds. 
        # Choose to not respond to speed changes < 50 secs apart.
        d = int(4 * fs)
        accelPeaks, accelHeights = signal.find_peaks(np.abs(absAccel), height=threshold, distance=d)
        
        # Find clusters of peaks and make each cluster into one peak.
        accelPeaks1 = []        
        if len(accelPeaks) > 0:        
            # merge when peaks are closer that 50 secs apart.
            maxt = 50 * fs
            accelPeaks1 = [] 
            prev = accelPeaks[0]
            peakL = [prev]
            
            for p in accelPeaks[1:]:
                if p - prev < maxt:
                    peakL.append(p)                  
                else:
                    avg = np.mean(peakL)
                    accelPeaks1.append(np.round(np.mean(peakL)))
                    peakL = [p]
                prev = p
            accelPeaks1.append(np.round(np.mean(peakL)))

            accelPeaks1 = np.array(accelPeaks1, dtype=np.int64)
            
        if plot:
            td = self.logDf.TIMEDELTA
            accelThresh = np.full_like(absAccel, threshold)
            plt.figure()
            plt.plot(td, speed, label='speed')
            plt.plot(td, accel, label='accel')
            plt.plot(td, absAccel, label='absAccel')
            plt.plot(td, accelThresh, '--', color='lightgray', label='zca threshold')
            plt.plot(td.iloc[accelPeaks1], accelThresh[accelPeaks1], 'xr', label='zcaPeaks')
            plt.legend()    
       
        self.logDf['RUNNO'] = 0
        start = 0
        for i, end in enumerate(accelPeaks1):
            self.logDf.loc[start:end, 'RUNNO'] = i+1
            start = end
        

    
    def CombineDataFrames(self, dfs, unts, mode='unique'):
        """
        Combine similar dataframes to emable plotting of data from multiple dataframes.    
    
        Parameters
        ----------
        dfs : ARRAY OF PANDAS DATAFRAMES
            e.g. as returned from ReadMbCsv()
        unts : Units dictionary
        mode : STRING, optional
            Mode can be one of the following
            'unique'  - keep all colums unique - rename the colums so that they remain separate
            'merge' - merge colums with the same name into one column
            The default is 'unique'.
    
        Returns
        -------
        ret : DATAFRAME
            Dataframe combining all of the imput dataframes togeather.
        """    
        if mode == 'unique':        
            suf = 'A'
            newdfs = []
            units = {}
            for df in dfs:
                changes = {}
                for n in df.columns:
                    newName = n + '_' + suf
                    changes[n] = newName
                    units[newName] = unts[n]
                    
                newdfs.append(df.rename(changes, axis='columns'))
                suf = chr(ord(suf) + 1)
             
            ret = pd.concat(newdfs)
        elif mode == 'merge':
            ret = pd.concat(dfs)
            units = unts
        else:
            raise ValueError(f'Imvalid argument - mode={mode} is not allowed as an argument.')
    
        return ret, units
    
    
    def PtsWellTestAnalysis(self):
        """
        Convert Dataframe column names (from a PTS project) to format used in 
        https://github.com/ICWallis/T21-Tutorial-WellTestAnalysis
        Check that units are set to metric (defaults). If any units are unexpected, 
        raise ValueError exception. It currently does not attempt to convert units.
    
        Returns
        -------
        df1 : Pandas Dataframe
            Data colums named to match Well Test Analysis format.
    
        """
    
        headerItems = {
            'DEPTH':'depth_m',
            'SPEED': 'speed_mps',
            'TENSION': 'cweight_kg',
            'WHP': 'whp_barg',
            'PTS_TEMP': 'temp_degC',
            'PTS_PRES': 'pressure_bara',
            'PTS_FREQ': 'frequency_hz',
            'TIMEDELTA': 'timedelta_sec', 
            'TIMESTAMPISO': 'datetime'
        }
    
        checkUnits = {
            'DEPTH': 'm',
            'SPEED': 'm/s',
            'TENSION': 'kg',
            'WHP': 'barg',
            'PTS_TEMP': 'C',
            'PTS_PRES': 'bara',
            'PTS_FREQ': 'Hz',  
        }
    
        unts = self.logUnits
        df = self.logDf
    
        for u in checkUnits:
            if unts[u].upper() != checkUnits[u].upper():
                print(f'WARNING: {u} has unit {unts[u]}. Was expecting {checkUnits[u]}.')
                raise ValueError(f'{u} has unit {unts[u]}. Was expecting {checkUnits[u]}.')
        
        df1 = df.rename(columns=headerItems)
        df1 = df1[headerItems.values()]
        return df1
        
        
def SteamTableCurves(depth):
    def Pressure(depth=1, density=1000, g=9.80665, pa=0.9661111):
        return density * g * depth * 1E-5 + pa

    from pyXSteam.XSteam import XSteam
    steam_table = XSteam(XSteam.UNIT_SYSTEM_MKS)
    ntsat_p = np.frompyfunc(steam_table.tsat_p, 1, 1)
    tsat = ntsat_p(Pressure(depth))
    return tsat

def AddSteamTableCurves(fig):
    axs = fig.axes
    axt = axp = None
    for ax in axs:
        if ('PTS_TEMP' in ax.get_xlabel()) & ('DEPTH' in ax.get_ylabel()):
            axt = ax
        elif ('PTS_PRES' in ax.get_xlabel()) & ('DEPTH' in ax.get_ylabel()):
            axp = ax
    if axt != None:
        xlim = axt.get_xlim()
        ylim = axt.get_ylim()
        maxDepth = ylim[0]
        minDepth = 0.0
        d = np.arange(minDepth, maxDepth, 1)
        tsat = SteamTableCurves(d)
        axt.autoscale(False)
        axt.plot(tsat,d, color='grey', linestyle='dashdot', linewidth=1)
        axt.set_ylim(ylim)
        axt.set_xlim(xlim)
        
            
class PlotDefinition:
    """
    Container for storing a plotting definition.
    """
    def __init__(self, xname, yname, color, linestyle, secAxis):
        """
        Initialisation function for PlotDefinition
        Args:
            xname: Pandas column name for x
            yname: Pandas column name for y
            color: STRING - Colour of line
            linestyle: STRING - line style specification
            secAxis: Set to True to put this plot on the secondary axis.
        """
        self.xname = xname
        self.yname = yname
        self.color = color
        self.linestyle = linestyle
        self.secAxis = secAxis


def PlotRunNo(df, fig, depthAxis, timeCol='TIMEDELTA'):
    """
    Display the run number on the chart

    Parameters
    ----------
    df : Pandas Dataframe
        log data.
    fig : MatPlotLib Figure object

    Returns
    -------
    None.

    """
    
    if 'RUNNO' not in df:
        return
    
    ax1 = fig.axes[0]
    ax2 = fig.axes[1]
    
    # Use differentiation to find the changes between runs. These will become minor ticks.
    i = df.RUNNO.diff() != 0
    minorTicks = list(df[timeCol][i])
    minorTicks.append(df[timeCol].iloc[-1])

    for i in range(len(minorTicks)-1):
        if i % 2 == 0:
            c = '#F0E0D0'
        else:
            c = '#D0F0F0'
        ax1.axvspan(minorTicks[i], minorTicks[i+1], facecolor=c, alpha=0.5)
        if not depthAxis:
            ax2.axvspan(minorTicks[i], minorTicks[i+1], facecolor=c, alpha=0.5)

    runLables = []
    majTicks = []

    
    # Find positions in between the run number changes. These become major ticks.
    for i in range(len(minorTicks)-1, 0, -1):
        mid = minorTicks[i] - (minorTicks[i] - minorTicks[i-1])/2
        majTicks.append(mid)
#        runLables.append(f'Run\N{NO-BREAK SPACE}{i}')
        runLables.append(f'{i}')
    
    def DrawRunNoAxis(ax):        
        axa = ax.twiny()
        axa.set_xticks(majTicks)
        axa.set_xticks(minorTicks, minor=True)
        
        # Hide the major ticks. The run number will show at the missing ticks.
        axa.tick_params(axis='x', which='major', top=False)
        axa.tick_params(axis='x', which='minor', length=5, width=2)
        axa.grid(axis = 'x', which='minor', color = 'gray', linestyle = '--', linewidth = 1.0)
        axa.set_xlim(ax.get_xlim())
        axa.set_xticklabels(runLables)
        axa.set_xlabel('Run No.', fontsize=9)
        return axa

    ax1a = DrawRunNoAxis(ax1)
    
    ax2a = None
    if not depthAxis:
        ax2a = DrawRunNoAxis(ax2)
            
    return ax2a


def PlotLog(mbcLog, defs : [PlotDefinition], title=None, depthaxis=False, style='interactive', plotRunNos=True):
    """
    Generic data plotting function.
    Args:
        mbcLog:     Instance of MbcLog containing containing data to plot.
        defs:       LIST - Plot definitions (column name, units, colour etc)
        title:      STRING - Title to put on the top of the plot. Default is stem of CSV filename.
        depthaxis:  True if plotting against depth, False for time. Defaults to False.
        style:      The style of the plot can be 'interactive' or 'report'

    Returns:
        Span:       MatPlotLib span
        fig:        MatPlotLib figure
    """
    if isinstance(mbcLog, MbcLog):
        df = mbcLog.logDf
        units = mbcLog.logUnits
    else:
        raise AttributeError('mbcLog argument should be of type MbcLog')
            
    # Create figure window with top and bottom subplots.
    if depthaxis:
        if style == 'interactive':
            fig = plt.figure(figsize=(8,9))
            (ax1, ax2) = fig.subplots(1, 2, gridspec_kw={'width_ratios': [1.5, 3]})    
        elif style == 'report':
            fig = plt.figure(figsize=(6,9))
            (ax2) = fig.subplots(1, 1, gridspec_kw={'width_ratios': [3]})
            ax1 = None
        else:
            raise ValueError(f'{style} is an invalid option for style')
    else:
        if style == 'interactive':
            fig = plt.figure(figsize=(10,6))
            (ax1, ax2) = fig.subplots(2, 1, gridspec_kw={'height_ratios': [1, 3]})    
        elif style == 'report':
            fig = plt.figure(figsize=(10,6))
            (ax1, ax2) = fig.subplots(2, 1, gridspec_kw={'height_ratios': [1, 3]})
        else:
            raise ValueError(f'{style} is an invalid option for style')
            
    fig.tight_layout(pad=6.0)
    text_rotation= 0

    # Plot first definition on top subplot.
    x = defs[0].xname
    y = defs[0].yname
    if depthaxis:
        x = defs[0].yname
        y = defs[0].xname
        if ax1 != None:        
            ax1.invert_yaxis()
        ax2.invert_yaxis()
        text_rotation= 90

    if y in units:
        yUnit = units[y]
    else:
        yUnit = ''
    if x in units:
        xUnit = units[x]
    else:
        xUnit = ''

    if ax1 != None:        
        ax1.plot(df[x], df[y], defs[0].linestyle, color=defs[0].color)
        ax1.set_ylabel(f'{y} ({yUnit})')
        ax1.set_xlabel(f'{x} ({xUnit})')
        ax1.minorticks_on()
        ax1.grid(visible=True, which='major', color='darkgray', linestyle='--')
        ax1.grid(visible=True, which='minor', color='lightgray', linestyle='--')
       
    if style == 'interactive':
        # Draw the word SELECTOR on the first graph.
        textx = sum(ax1.get_xlim())/2
        texty = sum(ax1.get_ylim())/2
        title_font = {'fontname':'Arial', 'size':'25', 'color':'white', 'weight':'normal'} 
        ax1.text(textx,texty,' S E L E C T O R ', bbox={'facecolor':'lightgray','alpha':0.4,'edgecolor':'none','pad':3}, 
              horizontalalignment='center', verticalalignment='center', alpha=0.6,
              rotation_mode='anchor', rotation=text_rotation, **title_font)
    
    # Plot other definitions on bottom subplot.
    
    # Any secondary axis in definition list?
    secAxis = any([d.secAxis for d in defs])
    
    if secAxis:
        if depthaxis:
            ax2a = ax2.twiny()
        else:
            ax2a = ax2.twinx()
    
    def AppendLabel(ax, xlabel, ylabel):
        def FontSize(s):
            fontSize = 'medium'
            if len(s) > 30:
                fontSize = 'small'
            if len(s) > 50:
                fontSize = 'x-small'
            return fontSize
        
        y = ax.get_ylabel()
        if ylabel not in y:
            if len(y) == 0:
                yNew = ylabel
            else:
                yNew = y + ', ' + ylabel       
            ax.set_ylabel(yNew, fontsize=FontSize(yNew))
            
        x = ax.get_xlabel()
        if xlabel not in x:
            if len(x) == 0:
                xNew = xlabel
            else:          
                xNew = x + ', ' + xlabel
            ax.set_xlabel(xNew, fontsize=FontSize(xNew))
            
    for i in defs[1:]:
        if depthaxis:
            x = i.yname
            y = i.xname
        else:
            x = i.xname
            y = i.yname
            
        if y in units:
            yUnit = units[y]
        else:
            yUnit = ''
        if x in units:
            xUnit = units[x]
        else:
            xUnit = ''        
                      
        yLabel = f'{y} ({yUnit})'
        xLabel = f'{x} ({xUnit})'
        
        if i.secAxis == False:
            ax2.plot(df[x], df[y], i.linestyle, color=i.color, label=i.yname)
            AppendLabel(ax2, xLabel, yLabel)
        else:
            ax2a.plot(df[x], df[y], i.linestyle, color=i.color, label=i.yname)
            AppendLabel(ax2a, xLabel, yLabel)

    ax2.minorticks_on()
    ax2.grid(visible=True, which='major', color='darkgray', linestyle='--')
    ax2.grid(visible=True, which='minor', color='lightgray', linestyle='--')
    
    #if depthaxis:
        # Draw Steam table curves
        
    # Draw legends
    if depthaxis:
        ax2.legend(loc='lower right', framealpha = 0.5)
        if secAxis:
            ax2a.legend(loc='upper right', framealpha = 0.5)
    else:
        ax2.legend(loc='upper left', framealpha = 0.5)
        if secAxis:
            ax2a.legend(loc='upper right', framealpha = 0.5)
    
    # Draw title at top of figure
    fig.suptitle(f'{title}', fontsize=15)

    if (not depthaxis) and plotRunNos:
        ax2a = PlotRunNo(df, fig, depthaxis, x)

    span = None
    
    if style == 'interactive':
    # Use Span Selector to zoom in on data.
        def onselect(xmin, xmax):
            if xmin == xmax:
                return
            else:
                print(f'selected range is {xmin:.3f} to {xmax:.3f} sec.')
            
            if depthaxis:
                x = defs[0].yname
            else:
                x = defs[0].xname
                if x == 'TIMESTAMPISO':
                    # matplot has it own internal datetime format that needs converting.
                    tz = df.TIMESTAMPISO.dt.tz
                    if tz == None:
                        ds = df.TIMESTAMPISO.dt.tz_localize('UTC')
                        df.TIMESTAMPISO = ds
    
                    xmin = mdates.num2date(xmin)
                    xmax = mdates.num2date(xmax)      
           
            indmin, indmax = np.searchsorted(df[x], (xmin, xmax))
            indmax = min(len(df[x]) - 1, indmax)
            thisx = df[x][indmin:indmax].to_numpy()
            if depthaxis:
                ax2.set_ylim(thisx[-1], thisx[0])
            else:
                ax2.set_xlim(thisx[0], thisx[-1])
                if ax2a != None:
                    ax2a.set_xlim(thisx[0], thisx[-1])
                
            fig.canvas.draw_idle()
    
        if depthaxis:
            select_direction = 'vertical'
        else:
            select_direction = 'horizontal'
            
        # set useblit True on gtkagg for enhanced performance
        span = SpanSelector(ax1, onselect, select_direction, useblit=True,
                            props=dict(alpha=0.5, facecolor='red'))
        
    plt.tight_layout()
    plt.show()
    return span, fig


def ResampleTime(df, newSampleRate, dp=0, tolerance=1.1):
    """
    Resample with new time based sample rate. Currently this function only 
    reduces sample rate.

    Parameters
    ----------
    df : DATAFRAME
        Dataframe from CSV file, e.g. mbc.logDf.
    newSampleRate : FLOAT
        Required sample rate (seconds).
    dp : INTEGeR, optional
        The number of decimal places required in the resampled time. The default is 0.
    tolerance : FLOAT, optional
        Each time slot will get filled with the nearest sample up to this many 
        samples away (from the newSampleRate). Outside this, 
        the row will be considered to have no data and get filled with nans. 
        The default is 1.

    Returns
    -------
    DATAFRAME
        Resampled version of the input dataframe.

    """
    startTime = np.round(df.TIMEDELTA.iloc[0], dp)
    stopTime = np.round(df.TIMEDELTA.iloc[-1], dp)

    df = df.drop_duplicates(subset=['TIMEDELTA'])
    df = df.set_index('TIMEDELTA')
    newIndex = np.arange(startTime, stopTime, newSampleRate)
    return df.reindex(newIndex, method='nearest', tolerance=np.abs(newSampleRate) * tolerance)

def Test():
#    %matplotlib qt
    import pymbc as mbc
    from pathlib import Path
    import importlib
    importlib.reload(mbc)
    mb = mbc.MbcLog()
    csvfile = Path(r'C:\Users\RWilliams\source\repos\tricky67\pymbc\tests\_20230626_PTS__A.csv')
    mb.ReadMbCsv(csvfile) 
    #fnotes = csvfile.parent / (csvfile.stem + '_notes' + csvfile.suffix)
    #mb.ReadNotes(fnotes)
    #mb.CreateRunLog()
    mb.CreateRunLogGuess()
    plotdef = [mbc.PlotDefinition('TIMEDELTA', 'DEPTH', 'slategray', '-', False),
		   mbc.PlotDefinition('TIMEDELTA', 'PTS_PRES', 'royalblue', '-', False),
		   mbc.PlotDefinition('TIMEDELTA', 'PTS_FREQ', 'limegreen', '-', False),
		   mbc.PlotDefinition('TIMEDELTA', 'PTS_TEMP', 'tomato', '-', True)]
    st,figt = mbc.PlotLog(mb, plotdef, title=mb.name, depthaxis=False)
    
    plotdef = [mbc.PlotDefinition('DEPTH', 'TIMEDELTA', 'black', '-', False),
		   mbc.PlotDefinition('DEPTH', 'PTS_FREQ', 'limegreen', '--', True),
		   mbc.PlotDefinition('DEPTH', 'PTS_PRES', 'royalblue', '-', False),
		   mbc.PlotDefinition('DEPTH', 'PTS_TEMP', 'tomato', '-', True)]
    sd,figd = mbc.PlotLog(mb, plotdef, title=mb.name, depthaxis=True)    

