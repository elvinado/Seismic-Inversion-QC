import pandas as pd
import numpy as np

def velocity(slowness):
    """Returning Velocity with slowness as input"""
    return 0.3048 / ((slowness * (10**(-6))))

def impedance(dtc, density):
    """Returning impedance with compressional slowness and densitiy as input"""
    return (0.3048 / (dtc * (10**-6))) * density

def keyword_line_no(filename, keyword='~ascii'):
    """
    Returns line number of the first keyword encountered.
    
    Keyword arguments:
    String -- full path to the ascii file
    String -- search keyword (default '~Ascii')
    """
    count = 1
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.lower()
            if keyword not in line:
                count += 1
                continue
            else:
                break
    return count

def las_df(filename):
    """
    Returns pandas dataframe of las ascii values with depth as index
    
    Accepts one argument:
    string -- full path to the ascii file
    """
    skiprows = keyword_line_no(filename)
    return pd.read_csv(filename,delim_whitespace=True,skiprows=skiprows,header=None)

def dfs_filter01(sinsData):
    """Remove nulls and calculate variables
    Input - sins.Data Object
    Returns - sins.Data Object
    """
    tempData = []
    for name,df_well in zip (sinsData.wellnames,sinsData.dfs_well):
        #print(f"Before: {name},{len(df_well)}")
        df_well = df_well.drop(columns=["DEPTH","JX_Litholog"])
        df_well = df_well.replace({-999.25:np.NaN})
        df_well = df_well.replace({-9999.00:np.NaN})
        df_well = df_well.dropna()
        df_well["Vp"] = velocity(df_well["DTC"])
        df_well["Vs"] = velocity(df_well["DTS"])
        df_well["Vp/Vs"] = df_well["Vp"] / df_well["Vs"]
        df_well["Ip"] = impedance(df_well["DTC"], df_well["DEN"])
        df_well["Wellname"] = name
        df_well["Interval"] = None
        tempData.append(df_well)
        #print(f"After: {name},{len(df_well)}")
    # THIS REPLACES THE ORIGINAL INSTANCE
    sinsData.dfs_well = tuple(tempData) 
    return sinsData

def dfs_filter02(sinsData):
    """Filter based on df_depth file
    Input - sins.Data Object
    Returns - sins.Data Object
    """   
    tempData = []
    df_depth = sinsData.df_depth
    for name,intervals,df_well in zip (sinsData.wellnames,sinsData.intervals_inclusion,sinsData.dfs_well):
        #print(f"Before: {name},{len(df_well)}")
        df_temp = pd.DataFrame()
        if "All" in intervals:
            df_temp = df_temp.append(df_well)
        else:
            for interval in intervals:
                row = df_depth[(df_depth.Well == name) & (df_depth.Interval == interval)].iloc[0]
                depth_range = (df_well.TVDss >= row.Top) & (df_well.TVDss <= row.Bottom)
                if df_temp.empty:
                    df_temp = df_well[depth_range]
                else:
                    df_temp = df_temp.append(df_well[depth_range])
        tempData.append(df_temp)
        #print(f"After: {name},{len(df_temp)}")
    # THIS REPLACES THE ORIGINAL INSTANCE
    sinsData.dfs_well = tuple(tempData)   
    return sinsData

def set_interval_name(sinsData):
    """Set value Interval values based on df_depth
    Input - sins.Data Object
    Returns - sins.Data Object
    """
    tempData = []
    df_depth = sinsData.df_depth
    for name,df_well in zip (sinsData.wellnames,sinsData.dfs_well):
        for index, row in df_depth[df_depth["Well"] == name].iterrows():
            df_well.loc[((df_well['TVDss'] >= row.Top) & (df_well['TVDss'] <= row.Bottom)), "Interval"] = row.Interval
        tempData.append(df_well)
    # THIS REPLACES THE ORIGINAL INSTANCE
    sinsData.dfs_well = tuple(tempData) 
    return sinsData


class Data:
    def __init__(self,wells = None,**kwargs):
        self._wellnames = None
        self._intervals = None
        self._pphysics = None
        self._elastics = None
        self._intervals_inclusion = None
        self._df_depth = None
        self._dfs_well = None
        self._df_merged = None
        self._dfs_well_dict = None
        self._wells = wells
        # for the **kwargs
        for key, value in kwargs.items():
            setattr(self,key,value)
 
    @property
    def wellnames(self):
        """A tuple of wellnames string
        E.g. --> ("BU1ST1", "H4", "HL6", "HL8", "L2")"""
        return self._wellnames   
    @wellnames.setter
    def wellnames(self,value):
        self._wellnames = value    
    @wellnames.deleter
    def wellnames(self):
        del self._wellnames    
    
    @property
    def intervals(self):
        """A tuple of unique intervals name string
        E.g. --> ('Beryl', 'B-H', 'P1', 'P1a', 'P2c')"""
        return self._intervals   
    @intervals.setter
    def intervals(self,value):
        self._intervals = value   
    @intervals.deleter
    def intervals(self):
        del self._intervals   
    
    @property
    def pphysics(self):
        """A tuple of unique petrophysical properties
        E.g. --> ("GR", "PHIT", "SWT", "VCL")"""
        return self._pphysics  
    @pphysics.setter
    def pphysics(self,value):
        self._pphysics = value 
    @pphysics.deleter
    def pphysics(self):
        del self._pphysics
        
    @property
    def elastics(self):
        """A tuple of unique elastic properties
        E.g. --> ("DEN","Vp","Vs","Ip","Vp/Vs")"""
        return self._elastics  
    @elastics.setter
    def elastics(self,value):
        self._elastics = value 
    @elastics.deleter
    def elastics(self):
        del self._elastics

    @property
    def intervals_inclusion(self):
        """A tuples of list of included intervals.
        Must have the same length with wellnames.
        E.g. --> (['All'],['itvs1','itvs2'],['itvs1']) """
        return self._intervals_inclusion  
    @intervals_inclusion.setter
    def intervals_inclusion(self,value):
        self._intervals_inclusion = value 
    @intervals_inclusion.deleter
    def intervals_inclusion(self):
        del self._intervals_inclusion
        
    @property
    def df_depth(self):
        """A pandas dataframe of Well, Interval, Top, & Bottom.
        Exact Header Name Required
        E.g. --> 
        idx| Well   | Interval | Top    | Bottom
        ===|========|==========|========|========
        0  | BU1ST1 | Ber      | 1000   | 1200      
        1  | H4     | H        | 800    | 4000
        2  | HL6    | P1       | 3000   | 4000"""
        return self._df_depth
    @df_depth.setter
    def df_depth(self,value):
        self._df_depth = value 
        self._intervals= tuple(value.Interval.unique())
    @df_depth.deleter
    def df_depth(self):
        del self._df_depth
    
    def set_intervals(self):
        """set intervals value for each well based on df_depth dataframe
        """
        for wellname in self.wellnames:
            myIntervals = {}
            awell = self.df_depth[self.df_depth['Well'] == wellname]
            for idx, row in awell.iterrows():
                itvs = Interval(row.Interval,row.Top,row.Bottom)
                myIntervals.update({itvs.name:itvs})
            self.wells[wellname]._intervals = myIntervals
    
    @property
    def dfs_well(self):
        """A tuples of pandas dataframe of log data.
        Must have the same length with wellnames.
        E.g. --> (dataframe_well_1, dataframe_well_2, dataframe_well_3) """
        return self._dfs_well  
    @dfs_well.setter
    def dfs_well(self,value):
        self._dfs_well = value 
    @dfs_well.deleter
    def dfs_well(self):
        del self._dfs_well
        
    @property
    def df_merged(self):
        """A pandas dataframe of merged dataframes.
        Merging dataframes when dfs_well is not empty
        """
        if not self._dfs_well is None:
            self._df_merged = pd.concat(self._dfs_well,sort=False)
        return self._df_merged  
    @df_merged.setter
    def df_merged(self,value):
        self._df_merged = value 
    @df_merged.deleter
    def df_merged(self):
        del self._df_merged

    @property
    def dfs_well_dict(self):
        """A dictionary of pandas dataframe of log data with wellname as key.
        E.g. -->
        {"well_1":dataframe_well_1,
        "well_2":dataframe_well_2,
        "well_3":dataframe_well_3} """
        self._dfs_well_dict = {name:df_well for name,df_well in zip(self.wellnames,self.dfs_well)}
        return self._dfs_well_dict
    @dfs_well_dict.setter
    def dfs_well_dict(self,value):
        self._dfs_well_dict = value 
    @dfs_well_dict.deleter
    def dfs_well_dict(self):
        del self._dfs_well_dict

    @property
    def wells(self):
        """A dictionary of wells of type sins.Well with wellname as key
        E.g. -->
        {'well_1':well_1,
        'well_2':well_2,
        'well_3':well_3}"""
        return self._wells  
    @wells.setter
    def wells(self,value):
        self._wells = value 
    @wells.deleter
    def wells(self):
        del self._wells
        
    @property
    def dataset_name(self):
        """A string of Dataset Name
        E.g. --> 'Todays Dataset'"""
        return self._dataset_name  
    @dataset_name.setter
    def dataset_name(self,value):
        self._dataset_name = value 
    @dataset_name.deleter
    def dataset_name(self):
        del self._dataset_name
        

class Well:
    def __init__(self,wellname=None,lasio_obj=None,**kwargs):
        self._wellname = wellname
        self._lasio_obj = lasio_obj
        self._intervals_inclusion = None
        self._intervals = None
        self._new_mnemonics = None
         # for the **kwargs
        for key, value in kwargs.items():
            setattr(self,key,value)
    
    def __repr__(self):
        return f"{Well.__name__}({self.wellname})"
    
    def __str__(self):
        return f"Wellname: {self.wellname}"
    
    @property
    def wellname(self):
        """A string
        E.g. --> 'BU1ST1'"""
        return self._wellname  
    @wellname.setter
    def wellname(self,value):
        self._wellname = value 
    @wellname.deleter
    def wellname(self):
        del self._wellname
        
    @property
    def lasio_obj(self):
        """A lasio object
        E.g. --> 'BU1ST1'"""
        return self._lasio_obj  
    @lasio_obj.setter
    def lasio_obj(self,value):
        self._lasio_obj = value 
    @lasio_obj.deleter
    def lasio_obj(self):
        del self._lasio_obj
        
    def update_mnemonics(self,mnem_tuples):
        for mnem in mnem_tuples:
            self.lasio_obj.curves[mnem[0]].mnemonic = mnem[1]
            
    def update_mnemonics2(self,new_mnemonics):
        old_mnemonics = [m.mnemonic for m in self.lasio_obj.curves]
        zipped = zip(old_mnemonics,new_mnemonics)
        self.update_mnemonics(zipped)  
    
    @property
    def new_mnemonics(self,mnemonics):
        """A tuples of new mnemonics in correct order
        E.g. --> ('DEPTH', 'GR', 'DEN', 'DTC', 'DTS')"""
        return self._new_mnemonics  
    @new_mnemonics.setter
    def new_mnemonics(self,value):
        self._new_mnemonics = value 
    @new_mnemonics.deleter
    def new_mnemonics(self):
        del self._new_mnemonics
    
    @property
    def intervals_inclusion(self):
        """A tuples included intervals.
        E.g. --> ('All') or
        ('interval_1','interval_2','interval_3')"""
        return self._intervals_inclusion  
    @intervals_inclusion.setter
    def intervals_inclusion(self,value):
        self._intervals_inclusion = value 
    @intervals_inclusion.deleter
    def intervals_inclusion(self):
        del self._intervals_inclusion
    
    #def add_intervals_inclusion(self):
    #    pass
    
    @property
    def intervals(self):
        """A dictionary of interval object
        E.g. -->
        {'interval_1':interval_1,'interval_2':interval_2,'interval_3':interval_3}
        """
        return self._intervals  
    @intervals.setter
    def intervals(self,value):
        self._intervals = value 
    @intervals.deleter
    def intervals(self):
        del self._intervals
        
    def add_intervals(self,name,top,bottom,**kwargs):
        new_interval = Interval(name,top,bottom)
        self._intervals.update({name:new_interval})
    
    
        
class Interval:
    def __init__(self,name,top,bottom):
        self._name = name
        self._top = top
        self._bottom = bottom
    
    def __repr__(self):
        return f"{Interval.__name__}(name={self._name}, top={self._top}, bottom={self._bottom})"
    
    def __str__(self):
        return f"Interval Name: {self.name}, Top:{self._top}, Bottom:{self._bottom}"
    
    @property
    def name(self):
        """A String of interval name
        E.g. --> 'interval_1'
        """
        return self._name  
    @name.setter
    def name(self,value):
        self._name = value 
    @name.deleter
    def name(self):
        del self._name
        
    @property
    def top(self):
        """A Number of interval top
        E.g. --> 1052.25
        """
        return self._top  
    @top.setter
    def top(self,value):
        self._top = value 
    @top.deleter
    def top(self):
        del self._top
        
    @property
    def bottom(self):
        """A Number of interval bottom
        E.g. --> 5842.52
        """
        return self._bottom  
    @bottom.setter
    def bottom(self,value):
        self._bottom = value 
    @bottom.deleter
    def bottom(self):
        del self._bottom
