# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 12:29:25 2022

functions that could be useful for any psychopy experiment

@author: jschuurmans
"""
#%% =============================================================================
# imports
import numpy as np
import PsiMarginal 
from psychopy import visual, event, core, gui, data, monitors
from JS_psychopyfunctions import *

#%% =============================================================================
def escape_check(keys,win,f):
    # close window and logfile if escape is pressed
    if 'escape' in keys:
        win.close()
        f.close()
        

def nframes(time_in_ms, framelength):
    # calculates the number of frames based on time in ms and framerate
     return int(time_in_ms/framelength)
 

def makePsi(nTrials,signal_start,signal_end,steps): # start_thresh is signal strength in percentage
    # Image visibility ranges between signal_start and signal_end, logarithmically, 'steps' possibilities.
    staircase = PsiMarginal.Psi(stimRange=np.geomspace(signal_start,signal_end,steps,endpoint=True),
            Pfunction='Weibull', nTrials=nTrials,
            threshold=np.geomspace(signal_start,signal_end,steps, endpoint=True), 
            thresholdPrior=('normal',5,5), slope=np.geomspace(0.5, 20, 50, endpoint=True),
            guessRate=0.5, slopePrior=('gamma',3,6), lapseRate=0.05, lapsePrior=('beta',2,20), marginalize=True)
    return staircase
# sigma is slope


def equalise_im(loaded_image, LC):
    #normalises a images loaded as a NP array [min -1, max +1]
    loaded_image = 2.*(loaded_image - np.min(loaded_image)) / np.ptp(loaded_image)-1 # equalise image
    #want to add the part to give the image desired luminance and contrast.... 
    # dont know how yet..
    #loaded_image = (loaded_image*LC[1]) + LC[0]   # desired luminance and contrast
    return loaded_image


def occlude(image, back, signal):
    # alphablending
    fullAlpha = 255 # highest image pixel value
    # create Alpha channel array for the image, fill it with 255s
    imHeight, imWidth = image.shape[:]
    srcA = np.full([imHeight,imWidth], fullAlpha)
    # same for backrgound
    backHeight, backWidth = back.shape[:]
    backA = np.full([backHeight, backWidth], fullAlpha)
    
    # reduce Alpha transparency of image / background
    srcA[:, :] = fullAlpha -((100-signal)/100*fullAlpha)

    backA[:, :] = ((100-signal)/100*fullAlpha)
    
    # blend them into a single image
    blend=(image*(srcA/fullAlpha))+(back*(backA/fullAlpha))
    # visualise: Image.fromarray(blend.astype('uint8'))
    return blend





