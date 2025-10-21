# MB Century Downhole Data Toolkit

https://www.mbcentury.com/services 

This toolkit provides easy access to data that has been exported from one of MB Century's data logging applications. It is primarily used to access downhole data that has been collected using MB Century's data collection systems.


## Example use

Use pip to import the package.

```ccs
pip import pymbc
```

## Example python code

Open a CSV file containing PTS data, plot it against depth and time, and convert it to Well Test Analysis format.
```css
import pymbc as mbc
from pathlib import Path

csvfile = Path(r'tests\_20230626_PTS__A.csv')
mb = mbc.MbcLog()
mb.ReadMbCsv(csvfile)
fnotes = csvfile.parent / (csvfile.stem + '_notes' + csvfile.suffix)
mb.ReadNotes(fnotes)
mb.CreateRunLogGuess()
plotdef = [mbc.PlotDefinition('TIMEDELTA', 'DEPTH', 'slategray', '-', False),
		   mbc.PlotDefinition('TIMEDELTA', 'PTS_PRES', 'royalblue', '-', False),
		   mbc.PlotDefinition('TIMEDELTA', 'PTS_FREQ', 'limegreen', '-', False),
		   mbc.PlotDefinition('TIMEDELTA', 'PTS_TEMP', 'tomato', '--', True)]
st,figt = mbc.PlotLog(mb, plotdef, title=mb.name, depthaxis=False)

plotdef = [mbc.PlotDefinition('DEPTH', 'TIMEDELTA', 'black', '-', False),
		   mbc.PlotDefinition('DEPTH', 'PTS_FREQ', 'limegreen', '--', True),
		   mbc.PlotDefinition('DEPTH', 'PTS_PRES', 'royalblue', '-', False),
		   mbc.PlotDefinition('DEPTH', 'PTS_TEMP', 'tomato', '-', True)]
sd,figd = mbc.PlotLog(mb, plotdef, title=mb.name, depthaxis=True) 
pts = mb.PtsWellTestAnalysis()
	
```      

