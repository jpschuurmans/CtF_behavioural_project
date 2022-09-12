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

base_path = 'C:/Users/Adminuser/Documents/03_SFmasking/MainExp/'

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


#%% ===========================================================================
# different conditions in experiment

spatialfrequencies = ['LSF','HSF']
durations = ['50','100','150']
#different_conditions = list(itertools.product(spatialfrequencies,durations))

# for the paradigm we need more trial contitions
matching = ['same','diff']
staircases = ['1','2']


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

# returns list with unique dr of IDs or IMs self.unique_nr
stim.getuniquenr('ID')
stim.getuniquenr('IM')

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
alltrials.make_miniblocks(n_bigblock,miniblock_per_bigblock,trials_per_block)
    


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

header_names = list(alltrials.blocks['block-1']['HSF_100']['stair-1'][0].keys())

writer=csv.DictWriter(f, fieldnames=header_names)
writer.writeheader()

                           
#%% ===========================================================================
# prepare clock
change_clock = core.Clock()
rt_clock = core.Clock()

#%% ===========================================================================
# Prepare/open window
win = visual.Window(monitor = mon, size = scrsize, color ='grey', units ='pix', fullscr = True)


textpage = visual.TextStim(win, height=32, font="Palatino Linotype", alignHoriz='center' )

instructiontexts = {
    1 : """In this experiment, you will see two faces displayed
    one after another.\n Your task is to report whether the two 
    faces have the same identity.""",
    2 : """If both pictures are of the SAME person, press "S",\n
    if they  are different people, press "L"\n\n 
    Press SPACE key to continue."""
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


# for debugging: win.close()

#%% ===========================================================================
# draw fixation Cross
fixation = visual.ShapeStim(win, 
    vertices=((0, -0.3), (0, 0.3), (0,0), (-0.3,0), (0.3, 0)),
    lineWidth=3,
    closeShape=False,
    lineColor="black"
    )

# prepare bitmaps for presenting images
stimsize = [7.05,8.38]
bitmap1 = visual.ImageStim(win, size=stimsize, interpolate=True) 
bitmap2 = visual.ImageStim(win, size=stimsize, interpolate=True) 
bitmap_mask = visual.ImageStim(win, size=stimsize, interpolate=True)



#%% ===========================================================================


trialinfo = alltrials.blocks['block-1']['HSF_100']['stair-1'][0]
visibility = alltrials.blocks['block-1']['HSF_100']['stair-1_Psi']

draw = loadimage(base_path, trialinfo, visibility)

############################# blending mask is missing !





# Start experiment
i=0
block_no = -1
for block in final_blocks:
    block_no += 1
    if block_no > 0:
        block_break(block_no)
    for trial in block:
        if trial['ori']=='up':
            ori=180
            if trial['cond'][0] == 's' :
                while sameup.xCurrent == None:
                    pass # hang in this loop until the psi calculation has finished
                visibility = sameup.xCurrent
            elif trial['cond'][0] == 'd':
                while diffup.xCurrent == None:
                    pass
                visibility = diffup.xCurrent
            elif trial['cond'][0] == 'i':
                while isoup.xCurrent == None:
                    pass
                visibility = isoup.xCurrent
        else:
            ori=0
            if trial['cond'][0] == 's':
                while sameinv.xCurrent == None:
                    pass # hang in this loop until the psi calculation has finished
                visibility = sameinv.xCurrent
            elif trial['cond'][0] == 'd':
                while diffinv.xCurrent == None:
                    pass
                visibility = diffinv.xCurrent
            elif trial['cond'][0] == 'i':
                while isoinv.xCurrent == None:
                    pass
                visibility = isoinv.xCurrent
            
        im1=np.array(Image.open(os.path.join(stim_path,trial['im1name'])))
        im2=np.array(Image.open(os.path.join(stim_path,trial['im2name'])))
        mask=(np.array(Image.open(os.path.join(mask_path,trial['mask']))))/256
        im1us=occlude(im1,visibility)
        im1=(im1us-127.5)/127.5
        im2us=occlude(im2,visibility)
        im2=(im2us-127.5)/127.5
        mask_occluded=occlude(mask, visibility)
        maskfinal=(mask_occluded-127.5)/127.5 # .5 is the midvalue so you'd do (x-.5)/.5
        
        bitmap1.setOri(ori)
        bitmap2.setOri(ori)
        bitmap_mask.setOri(ori)
        
        # you don't need this
        if trial['ori']== 'up':
            eyeleveling=-1.18 
            # eyeleveling=-1.38
        else:
            eyeleveling=1.18
            # eyeleveling=1.38
        
        bitmap1.pos=(0,eyeleveling) #142+284/2 (5.1 is equal to 142 pixels, then we add half of the horizontal size (7/2) because pos. takes the center to the defined location.)
        bitmap2.pos=(0,eyeleveling)
        bitmap_mask.pos=(0,eyeleveling)
        
        
        
        
         
        bitmap1.setImage(im1)
        bitmap2.setImage(im2)
        bitmap_mask.setImage(maskfinal)
        
        for nFrames in range(FixFrame): # 600 ms.
                fixation.draw()
                win.flip()
                
        for nFrames in range(IntFrame):  # 500 ms
                win.flip()
            
        for nFrames in range(ImFrame): # 500 ms
                bitmap1.draw()
                win.flip()
                    
        for nFrames in range(MaskFrame): # 200 ms
               bitmap_mask.draw() # We don't have a mask right now
               win.flip()
               
               
        bitmap2.draw()
        win.flip()
        change_clock.reset()
        rt_clock.reset()
                                        
        # Wait until a response, or until time limit.
        # keys = event.waitKeys(maxWait=timelimit, keyList=['s','l', 'escape'])
                 
        keys = event.waitKeys(keyList=['s','l','escape','p'])     
        if keys:
            rt = rt_clock.getTime()
            # fixation.clearTextures()
            
        bitmap1.clearTextures()
        bitmap2.clearTextures()
        win.flip()
        
        if not keys:
            keys = event.waitKeys(keyList=['s','l','escape'])
            rt = rt_clock.getTime()
                           
        acc = 0
        if keys:
            if 'escape' in keys:
                f.close()
                win.close()
                # exTrials.saveAsWideText('Exp_full' + '.csv', delim=',')
                win.mouseVisible=True
                break
            elif 's' in keys and (trial['cond'] == 'ss' or trial['cond'] == 'ds' or trial['cond'] == 'isos'): # is same
                acc = 1
            elif 'l' in keys and (trial['cond'] == 'sd' or trial['cond'] == 'dd' or trial['cond'] == 'isod'): # is different
                acc = 1         
                
        trial['acc']=acc
        trial['rt']=rt
        trial['contrast']=visibility
        trial['trialno']=i
        # exTrials.addData('acc', acc)
        # exTrials.addData('rt', rt)
        # exTrials.addData('visib',visibility)
        i+=1

        # Update staircase        
        
        ''' elegantere shii dan een if else loop
        obj = {
            's': samup.addDaga(acc)
            'd':  diffup.addData(acc)
            }
        
        obj['s']
        '''
        
        if ori==180:
            if trial['cond'][0] == 's' :
                sameup.addData(acc)
            elif trial['cond'][0] == 'd':
                diffup.addData(acc)
            elif trial['cond'][0] == 'i':
                isoup.addData(acc)
        else:
            if trial['cond'][0] == 's':
                sameinv.addData(acc)
            elif trial['cond'][0] == 'd':
                diffinv.addData(acc)
            elif trial['cond'][0] == 'i':
                isoinv.addData(acc)
        writer.writerow(trial)

f.close()
# exTrials.saveAsWideText('Exp_full' + '.csv', delim=',')
win.close()
win.mouseVisible=True


#%% =============================================================================
