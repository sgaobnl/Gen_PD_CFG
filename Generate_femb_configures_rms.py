# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Wed Sep 19 22:29:03 2018
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
#from openpyxl import Workbook
import numpy as np
import struct
import os
from sys import exit
import os.path
import math
import copy


root_path = "/Users/shanshangao/Documents/GitHub/ProtoDUNE_CFG/"
for root, dirs, files in os.walk(root_path):
    break

for f in files:
    if f == "femb_config_wr_v323_rms.cfg":
        v323_cfgs = []
        with open(root_path + f, 'r') as cf:
            for cl in cf:
                v323_cfgs.append ( cl.split(",")[0:5])
    if f == "femb_config_wr_v325c_rms.cfg":
        v325c_cfgs = []
        with open(root_path + f, 'r') as cf:
            for cl in cf:
                v325c_cfgs.append ( cl.split(",")[0:5])

precfgs_rd = []
for idir in sorted(dirs):
    if (idir.find("APA") >= 0 ):
        apano = int(idir[3])
        cfp = root_path + idir + "/" 
        for subroot, subdirs, subfiles in os.walk(cfp):
            break
        for cff in sorted(subfiles):
            cffp = cfp + cff
            if (cffp.find("step11") > 0 ) and (cffp.find("ped_FE_ADC.txt") >=0 ) and (cffp.find("ped_FE_ADC.txt.swp") <0 ): #for rms
                fembcfgs = []
                with open(cffp, 'r') as cf:
                    for cl in cf:
                        fembcfgs.append(cl) 

                if ( fembcfgs[1].find("step11")>= 0):
                    wibno  = int (fembcfgs[1][3:5])
                    fembno = int (fembcfgs[1][16])
                    hexphase0 = hex(int(fembcfgs[2].split("=")[1][0:-1], 16))
                    hexphase1 = hex(int(fembcfgs[3].split("=")[1][0:-1], 16))
                    if (int(hexphase0,16) != 0xBF) or (int(hexphase1,16) != 0xBF) :
                        print "ERROR ADC SYNC, not 0xBF, please check"
                        exit()
                    feadc_spi = []
                    for i in range(72):
                        feadc_spi.append(hex( int(fembcfgs[i+4][0:-1], 16) ))
                    precfgs_rd.append([apano, wibno, fembno, hexphase0, hexphase1, feadc_spi])
                else:
                    print "ERROR Gain and Tp setting, quit, please check"
                    exit()

#V325C_FEMBs = ["APA3WIB3FEMB1"]
#
femb_cfgs = [["APA no (1-6)", "WIB no (0-4)", "FEMB no (0-3)", "FW Version", "WR Sequence", "WR ADDR (HEX)", "WR VALUE (HEX)", "RDBK VALUE (HEX)", "Note"]            , ]


for ai in range(1,7,1):
    for wi in range(0,5,1):
        for fi in range(0,4,1):
            if (ai == 3) and (wi==3) and (fi ==1) :
                fw_ver = "V325C"
                cfgs = copy.deepcopy(v325c_cfgs)
            else:
                fw_ver = "V0323"
                cfgs = copy.deepcopy(v323_cfgs)
            for precfg in precfgs_rd:
                if (precfg[0] == ai) and (precfg[1] == wi) and (precfg[2] == fi) :
                    femb_precfgs = precfg
                    break

            for i in range(len(cfgs)):
                if (i >0):
                    wr_addr = int(cfgs[i][1],16)
                    if (wr_addr == 0x06 ):
                        cfgs[i][2] = femb_precfgs[3]
                        cfgs[i][3] = "  "  
                    elif (wr_addr == 0x0F ):
                        cfgs[i][2] = femb_precfgs[4]
                        cfgs[i][3] = "  "  
                    elif ( wr_addr in range(0x200, 0x248,1) ):
                        cfgs[i][2] =  hex( int( femb_precfgs[5][wr_addr - 0x200], 16) )
                        cfgs[i][3] =  cfgs[i][2]
                    else:
                        cfgs[i][2] =  hex( int(cfgs[i][2]  , 16) )
                        if (cfgs[i][3].find("/") < 0 ):
                            cfgs[i][3] =  hex(int(cfgs[i][3], 16))
                        else:
                            cfgs[i][3] = "  "  

            for cfg in cfgs[1:]:
                femb_cfgs.append([ai, wi, fi, fw_ver,int(cfg[0]), hex(int(cfg[1],16)), cfg[2],cfg[3],cfg[4],  ] )


csvfile =  "/Users/shanshangao/Documents/GitHub/ProtoDUNE_CFG/" + 'ProtoDUNE_SP_FEMBs_Config_rms.csv'
    
with open (csvfile, 'w') as fp:
    for x in femb_cfgs:
        fp.write(",".join(str(i) for i in x) +  "," + "\n")



