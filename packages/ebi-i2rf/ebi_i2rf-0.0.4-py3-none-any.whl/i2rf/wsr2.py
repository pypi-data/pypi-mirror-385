import numpy as np
import pandas as pd
import os

class i2rf():
    def __init__(self) -> None:
        path = os.path.abspath(f"{__file__}/../i2rf_data/WSR_RefData.dat")
        self.data = pd.read_csv(path, sep=" ", header=0)
        self.dataFull = self.data.set_index('mDot')
        self.species = self.dataFull.drop(['tR', 'T'], axis=1)
        self.T = self.dataFull['T']
        self.tR = self.dataFull['tR']
        
    def getAll(self)->list:
        '''
        Returns numpy arrays for 
        - mDot
        - All species concentration at for all mDot
        - All temperatures at for all mDot
        - All residence times for all mDot 
        - Species names as they are ordered in the respective numpy array
        '''
        mDot = np.array(self.species.index)
        species = self.species.values
        T = self.T.values
        tR = self.tR.values
        speciesNames = np.array(self.species.columns, dtype=str)
        return [mDot, species, T, tR, speciesNames]

    def getSpecies(self, specific:list=None)->np:
        '''
        Return numpy arrays for:
        - mDot
        - Specific Species defined by list of str
            - else: all species
        '''
        mDot = np.array(self.species.index)

        if not specific: return [mDot, self.species.values]
        else: return [mDot, self.species[specific].values]
    
    def getTemperature(self):
        '''
        Return numpy arrays for:
        - mDot
        - Temperature
        '''
        mDot = np.array(self.species.index)
        return [mDot, self.T.values]
    
    def getResidenceTime(self):
        '''
        Return numpy arrays for:
        - mDot
        - Residence Time
        '''
        mDot = np.array(self.species.index)
        return [mDot, self.tR.values]
        
    
if __name__ == '__main__':
    d = i2rf()
    # print(d.getAll())
    # print(d.getSpecies())
    t = d.getTemperature()
    print(t)
    pass
    # print(d.getTemperature)
    # print(d.getResidenceTime)

