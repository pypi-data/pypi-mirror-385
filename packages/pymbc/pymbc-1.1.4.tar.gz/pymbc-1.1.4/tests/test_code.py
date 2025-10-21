from IPython.display import display
import pymbc as mbc
my_dir_path = "pymbc"

from pathlib import Path

def test_mbc():
    csvfile = Path(r'tests\_20230626_PTS__A.csv')
    mb = mbc.MbcLog()
    mb.ReadMbCsv(csvfile)
    fnotes = csvfile.parent / (csvfile.stem + '_notes' + csvfile.suffix)
    mb.ReadNotes(fnotes)
    mb.CreateRunLogGuess()
    plotdef = [mbc.PlotDefinition('TIMEDELTA', 'DEPTH', 'slategray', '-', False),
               mbc.PlotDefinition('TIMEDELTA', 'PTS_PRES', 'royalblue', '-', False),
               mbc.PlotDefinition('TIMEDELTA', 'PTS_FREQ', 'darkorange', '-', False),
               mbc.PlotDefinition('TIMEDELTA', 'PTS_TEMP', 'indianred', '--', True)]
    st,figt = mbc.PlotLog(mb, plotdef, title=mb.name, depthaxis=False)
    
    plotdef = [mbc.PlotDefinition('DEPTH', 'TIMEDELTA', 'black', '-', False),
               mbc.PlotDefinition('DEPTH', 'SPEED', 'forestgreen', '--', True),
               mbc.PlotDefinition('DEPTH', 'PTS_PRES', 'maroon', '-', False),
               mbc.PlotDefinition('DEPTH', 'PTS_TEMP', 'royalblue', '-', True)]
    sd,figd = mbc.PlotLog(mb, plotdef, title=mb.name, depthaxis=True)  
    pts = mb.PtsWellTestAnalysis()

    assert 'DEPTH' in mb.logDf.columns

