from sins import Data,las_df,Well
import pandas as pd
import lasio

def loaded_data():
    # get data from text files
    df_BU1ST1 = las_df("Input/BU1ST1_inhouse crossplot_rev1")
    df_BU1ST1.columns = ["DEPTH", "DEN", "DTC", "DTS", "GR", "JX_Litholog", "TVDss", "PHIT", "SWT","VCL"]
    df_H4 = las_df("Input/H4_inhouse crossplot")
    df_H4.columns = ["DEPTH", "GR", "DEN", "DTC", "DTS", "JX_Litholog", "TVDss", "PHIT", "SWT","VCL"]
    df_HL6 = las_df("Input/HL6_inhouse crossplot")
    df_HL6.columns = ["DEPTH", "GR", "DEN", "DTS", "DTC", "JX_Litholog", "TVDss", "PHIT", "SWT","VCL"]
    df_HL8 = las_df("Input/HL8_inhouse crossplot")
    df_HL8.columns = ["DEPTH", "GR", "DTC", "DTS", "DEN", "JX_Litholog", "TVDss", "PHIT", "SWT","VCL"]
    df_L2 = las_df("Input/L2_inhouse crossplot")
    df_L2.columns = ["DEPTH", "GR", "DEN", "DTC", "DTS", "JX_Litholog", "TVDss", "PHIT", "SWT","VCL"]
    # instantiate new object
    myData = Data()
    # tuples of required properties
    myData.df_depth = pd.read_csv("Input/Interval_list - All.txt",delim_whitespace=True,header=0)
    myData.intervals_inclusion = (["All"],["All"],["All"],["B-H"],["All"])
    myData.dfs_well = (df_BU1ST1, df_H4, df_HL6, df_HL8, df_L2)
    myData.wellnames = ("BU1ST1", "H4", "HL6", "HL8", "L2")
    myData.pphysics = ("GR", "PHIT", "SWT", "VCL")
    myData.elastics = ("DEN","Vp","Vs","Ip","Vp/Vs")
    
    return myData

def loaded_data_lasio():
    files = ("Input/BU1ST1_inhouse crossplot_rev1",
                "Input/H4_inhouse crossplot",
                "Input/HL6_inhouse crossplot",
                "Input/HL8_inhouse crossplot",
                "Input/L2_inhouse crossplot")

    wells = {}
    for file in files:
        lasio_obj = lasio.read(file)
        thisWell = Well(wellname = lasio_obj.well.WELL.value,
                       lasio_obj=lasio_obj)
        print(thisWell.wellname)
        wells.update({thisWell.wellname:thisWell})
    # instantiate new Dataset object
    myData = Data(wells=wells,dataset_name='My lovely dataset')
    # tuples of required properties
    myData.wellnames = tuple([well for well in myData.wells.keys()])
    myData.pphysics = ("GR", "PHIT", "SWT", "VCL")
    myData.elastics = ("DEN","Vp","Vs","Ip","Vp/Vs")
    # well specific
    myData.intervals_inclusion = (["All"],["All"],["All"],["B-H"],["All"])
    for iinc, well in zip(myData.intervals_inclusion,myData.wells.values()):
        well.intervals_inclusion = iinc
    # assigning intervals 
    myData.df_depth = pd.read_csv("Input/Interval_list - All.txt",delim_whitespace=True,header=0)
    myData.set_intervals()
    
    #original mnemonics
    #updated mnemonics
    #BU1ST1 
    old1 = ('DEPT', 'DEN', 'DTC', 'DTS', 'GR', 'JX_LITHOLOG', 'TVDSS', 'PHIT_FIN_2', 'SWT_FIN_2', 'VCL_FIN_2')
    new1 = ('DEPTH', 'DEN', 'DTC', 'DTS', 'GR', 'JX_Litholog', 'TVDss', 'PHIT', 'SWT','VCL')
    zip1 = zip(old1,new1)
    #H4 
    old2 = ('DEPT', 'GR', 'DEN_ORIGINAL', 'DTC', 'DTS', 'JX_LITHOLOG', 'TVDSS', 'PHIT_FIN_2', 'SWT_FIN_2', 'VCL_FIN_2')
    new2 = ('DEPTH', 'GR', 'DEN', 'DTC', 'DTS', 'JX_Litholog', 'TVDss', 'PHIT', 'SWT','VCL')
    zip2 = zip(old2,new2)
    #HL6 
    old3 = ('DEPT', 'GR', 'DEN_ORIGINAL', 'DTS_ORIGINAL', 'DTCO_ORIGINAL', 'JX_LITHOLOG', 'TVDSS', 'PHIT_FIN_2', 'SWT_FIN_2', 'VCL_FIN_2')
    new3 = ('DEPTH', 'GR', 'DEN', 'DTS', 'DTC', 'JX_Litholog', 'TVDss', 'PHIT', 'SWT','VCL')
    zip3 = zip(old3,new3)
    #HL8 
    old4 = ('DEPT', 'GR', 'DTC_ORIGINAL', 'DTS_ORIGINAL', 'DEN', 'JX_LITHOLOG', 'TVDSS', 'PHIT_FIN_2', 'SWT_FIN_2', 'VCL_FIN_2')
    new4 = ('DEPTH', 'GR', 'DTC', 'DTS', 'DEN', 'JX_Litholog', 'TVDss', 'PHIT', 'SWT','VCL')
    zip4 = zip(old4,new4)
    #L2 
    old5 = ('DEPT', 'GR', 'DEN_ORIGINAL', 'DTC_ORIGINAL', 'DTS_ORIGINAL', 'JX_LITHOLOG', 'TVDSS', 'PHIT_FIN_2', 'SWT_FIN_2', 'VCL_FIN_2')
    new5 = ('DEPTH', 'GR', 'DEN', 'DTC', 'DTS', 'JX_Litholog', 'TVDss', 'PHIT', 'SWT','VCL')
    zip5 = zip(old5,new5)
    news = (new1,new2,new3,new4,new5)
    for new_mnem, well in zip(news,myData.wells.values()):
        myData.wells[well.wellname].update_mnemonics2(new_mnem)
                        
    return myData