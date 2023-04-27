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
import json

#%% =============================================================================
def escape_check(keys,win,f):
    # close window and logfile if escape is pressed
    if 'escape' in keys:
        win.close()
        f.close()
        
def load_txt_as_dict(path):
    with open(path, 'r', encoding='utf-8') as f:
        instructions = f.read()
    instructiontexts = json.loads(instructions)
    return instructiontexts

def nframes(time_in_ms, framelength):
    # calculates the number of frames based on time in ms and framerate
     return int(time_in_ms/framelength)
 

def makePsi(nTrials,signal_start,signal_end,steps,thresholdPrior): # start_thresh is signal strength in percentage
    # Image visibility ranges between signal_start and signal_end, logarithmically, 'steps' possibilities.
    staircase = PsiMarginal.Psi(stimRange=np.linspace(signal_start,signal_end,steps,endpoint=True),
            Pfunction='Weibull', nTrials=nTrials,
            threshold=np.linspace(signal_start,signal_end,steps, endpoint=True), 
            thresholdPrior=thresholdPrior, slope=np.geomspace(0.5, 20, 50, endpoint=True),
            guessRate=0.5, slopePrior=('gamma',3,6), lapseRate=0.05, lapsePrior=('beta',2,20), marginalize=True)
    return staircase
# sigma is slope


def equalise_im(loaded_image, LC):
    if np.ptp(loaded_image) == 0:
        loaded_image = (loaded_image - np.min(loaded_image))
    else:
        #normalises a images loaded as a NP array 
        equalised = normalise_im(loaded_image)
        #loaded_image = (loaded_image*LC[1]) + LC[0]   # desired luminance and contrast
        #but image needs to be equalised between [min -1, max +1]
        #loaded_image = 2.*(loaded_image - np.min(loaded_image)) / np.ptp(loaded_image)-1 # equalise image
        loaded_image = (equalised - np.min(equalised)) / np.ptp(equalised)-.5 # equalise image
    return loaded_image

def normalise_im(loaded_image):
    normalised = (loaded_image - np.min(loaded_image)) / np.ptp(loaded_image)
    return normalised


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





