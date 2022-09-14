#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Wed Jan 26 14:41:32 2022

Experiment code:
Psychophysical coarse-to-fine backward masking. 

@author: jschuurmans
"""


#%% ===========================================================================
# paths

base_path = 'C:/Users/Adminuser/Documents/03_SFmasking/Experiment/MainExp_code/'

stim_path = f'{base_path}stimuli/'
mask_path = f'{base_path}masks/'
back_path = f'{base_path}background/'
data_path = f'{base_path}data/'
asfx='.bmp'


#%% ===========================================================================
# imports

import os
os.chdir(base_path)
import numpy as np
import itertools
from psychopy import visual, event, core, gui, data, monitors
from PIL import Image
import csv
from functions_ctfbackwardmasking import *
from JS_psychopyfunctions import *


#%% ===========================================================================
# different conditions in experiment

spatialfrequencies = ['LSF','HSF']
durations = ['50','100','150']
#different_conditions = list(itertools.product(spatialfrequencies,durations))

# for the paradigm we need more trial contitions
matching = ['same','diff']
staircases = ['1','2']

#desired luminance and contrast of images
LC = [.225, .9] # [0.45, 0.1] if between 0 and 1
#occluded_image = (occluded_image*LC[1]) + LC[0]   # desired luminance and contrast



#%% ===========================================================================
# monitor setup + subject info

exp_name = 'Coarse-to-fine backward masking'
exp_info = {
        '1. subject' : 'sub-',
        '2. gender' : ('female','male'),
        '3. age' : '',
        '4. screenwidth(cm)' : '59',
        '5. screenwidth(pix)' : '1920',
        '6. screenhight(pix)' : '1200', # '1080',
        '7. refreshrate(hz)' : '60', #ViewPixx - Change this (120)
        '8. screendistance' : '57'
        }
dlg = gui.DlgFromDict(dictionary=exp_info, title=exp_name)
    

# If 'Cancel' is pressed, quit
if dlg.OK == False:
    core.quit()
        
# Get date and time
exp_info['date'] = data.getDateStr()
exp_info['exp_name'] = exp_name

mon = monitors.Monitor('Dell') #Pulls out photometer calibration settings by name.  
# Change this if you are using the ViewPixx (you should find the proper name in PsychoPy Monitor Center)
mon.setDistance(exp_info['8. screendistance'])
mon.setWidth(exp_info['4. screenwidth(cm)']) # Cm width
framerate = exp_info['7. refreshrate(hz)'] 
scrsize = (float(exp_info['5. screenwidth(pix)']),float(exp_info['6. screenhight(pix)'] ))
framelength = 1000/(float(framerate))
mon.setSizePix(scrsize)


#%% ===========================================================================
# Timing

fix_dur = 500 # fixation before trial input in ms
int_dur = 500 # time between fixation and trial  
mask_dur = 200 # duration mask

nframe = num_frames(fix_dur,int_dur,mask_dur,framelength)


#%% ===========================================================================
## load and organise images into a block and trial lists

# get names of all images folders. Naming should be:
# stimulus: ID01_IM01.bmp / mask: BG01_ID01_IM01_LSF.bmp / background: BG01.bmp
# returns self.path and self.stim (list of names)
stim = Stimuli(stim_path)
back = Stimuli(back_path)

# returns list with unique dr of IDs or IMs self.unique_nr
stim.getuniquenr('ID')
stim.getuniquenr('IM')
back.getuniquenr('BG')

# returns self.same_list / self.diff_list / self.maxnr_trials 
stim.list_of_combinations()



# creates self.sf, self.dur, self.match, self.stair and an empty self.trial_list
alltrials = Ordertrials(stim,spatialfrequencies,durations,matching,staircases)

# Creating and shuffle the trials with balanced number of conditions
alltrials.trial_list(framelength)
alltrials.shuffle_trials()



# Making sure all big blocks have equal number of each condition
# 8 big blocks -> each have 6 miniblocks with 16 trials each
# each miniblock has different condition (LSF50,LSF100,LSF150,HSF50,HSF100,HSF150)
n_bigblock = 8
miniblock_per_bigblock = len(alltrials.conditionlist)
trials_per_block = 16 # that is 8 per staircase

# creates self.blocks['block-1']['HSF_50']['stair-1'][0] 
# in this case: 8 blocks, 6 conditions, 2 staircases, 16 trials
alltrials.make_miniblocks(n_bigblock,miniblock_per_bigblock,trials_per_block,back.unique_nr['BG'])
    


#%% ===========================================================================
# make Psi Staircase for all conditions (x2)

# nTrials is trials PER staircase
nTrials = int((trials_per_block/len(alltrials.stair))*n_bigblock)
signal_start = 30 # signal of blending (e.g. signal = 30, alpha = 70)
signal_end = 60
steps = 30

# initialize a staircase for each condition
alltrials.prepare_staircare(nTrials,signal_start,signal_end,steps)


#%% ===========================================================================
# open file csv log file to write the data

if not os.path.isdir(data_path):
    os.makedirs(data_path)

data_fname = exp_info['1. subject'] + '_' + exp_info['2. gender'] +  exp_info['3. age'] + '_' + exp_info['date'] + '.csv'
data_fname = os.path.join(data_path, data_fname)
f = open(data_fname,'w',encoding='UTF8', newline='')

header_names = list(alltrials.blocks['block-1']['HSF_100']['trials'][0].keys())

writer=csv.DictWriter(f, fieldnames=header_names)
writer.writeheader()

                           
#%% ===========================================================================
# Prepare/open window
win = visual.Window(monitor = mon, size = scrsize, color ='grey', units ='pix', fullscr = True)



# prepare bitmaps for presenting images
stimsize = [550,550]

bitmap = {'fix' : [], 'int' : [], 'stim1' : [], 'mask' : [], 'stim2' : []}

for bit in bitmap:
    bitmap[bit] = visual.ImageStim(win, size=stimsize, interpolate=True)
    bitmap[bit].setOri(180) # need to do this because somehow the images are inverted.....

# draw fixation cross
fix_cross = visual.ShapeStim(win, 
    vertices=((0, -0.3), (0, 0.3), (0,0), (-0.3,0), (0.3, 0)),
    lineWidth=30,
    closeShape=False,
    lineColor="black"
    )

#%% ===========================================================================
# instruction screen

textpage = visual.TextStim(win, height=32, font="Palatino Linotype", alignHoriz='center', wrapWidth=scrsize[0])

instructiontexts = {
    1 : """In this experiment, you will see two faces displayed
    one after another.\n\n Your task is to report whether the two 
    faces have the same identity.""",
    2 : """If both pictures are of the SAME person press "S".\n
    If they are different people, press "L".\n\n 
    Press SPACE key to continue.""",
    3 : """ READY """
    }

for text in instructiontexts:
    instructions = textpage
    instructions.text = instructiontexts[text]
    instructions.draw()
    win.flip()

    keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
    escape_check(keys,win,f)

# Hide cursor when window is open
win.mouseVisible=False
# win.mouseVisible=True

# for debugging: win.close()


#%% ===========================================================================
change_clock = core.Clock()
rt_clock = core.Clock()

#from functions_ctfbackwardmasking import *

# Start experiment
for bl,block in enumerate(alltrials.blocks):
    if bl > 0:
        block_break(win,f,bl,len(alltrials.blocks))
    for cond in alltrials.blocks[block]:
        print(cond)
        condition = alltrials.blocks[block][cond]
        for idx,trialinfo in enumerate(condition['trials']):
            fix_cross.setAutoDraw(True)
            staircase = condition[f'stair-{trialinfo["staircasenr"]}']
            nframe['stim1'] = trialinfo['nframes']
            
            while staircase.xCurrent == None:
                pass
            trialinfo['contrast'] = staircase.xCurrent
            
            #load stim1, stim2 and mask
            drawed = loadimage(base_path, trialinfo, trialinfo['contrast'], LC)

            #set stim1, stim2 and mask
            for drawit in bitmap:                    
                bitmap[drawit].setImage(drawed[drawit])

            #### trial windows 
            for window in bitmap:
                if window == 'int':
                    fix_cross.setAutoDraw(False)
                for nFrames in range(nframe[window]):
                    bitmap[window].draw()
                    win.flip()

            
            change_clock.reset()
            rt_clock.reset()
                                            
            # Wait until a response, or until time limit.
            # keys = event.waitKeys(maxWait=timelimit, keyList=['s','l', 'escape'])
            keys = event.waitKeys(keyList=['s','l','escape','p'])    
            bitmap['fix'].draw()
            fix_cross.setAutoDraw(True)
            win.flip()
            if keys:
                trialinfo['rt'] = rt_clock.getTime()
                # fixation.clearTextures()
            
            for drawit in bitmap:
                bitmap[drawit].clearTextures()

            trialinfo['acc'] = 0
            if keys:
                escape_check(keys,win,f)
                if 's' in keys and (trialinfo['matching'] == 'same'): # is same
                    trialinfo['acc'] = 1
                elif 'l' in keys and (trialinfo['matching'] == 'diff'): # is different
                    trialinfo['acc'] = 1         
            
            trialinfo['trialno'] = idx
            trialinfo['block'] = block
            
            #update staircase
            staircase.addData(trialinfo['acc'])
            
            writer.writerow(trialinfo)

f.close()
win.close()


#%% =============================================================================
