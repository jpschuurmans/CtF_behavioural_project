#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Wed Jan 26 14:41:32 2022-

Experiment code:
Psychophysical coarse-to-fine backward masking. 

@author: jschuurmans
"""


#%% ===========================================================================
# paths

base_path = 'C:/Users/user/Desktop/Jolien_Mrittika/CtF_behav/MainExp_code/'
# leave the next line, but comment it out, will make it easier for me to debug/edit the code
#base_path = 'C:/Users/Adminuser/Documents/03_SFmasking/Experiment/MainExp_code/'

stim_path = f'{base_path}stimuli/'
mask_path = f'{base_path}masks/'
back_path = f'{base_path}background/'
data_path = f'{base_path}data/'
asfx='.bmp'
save_path = f'{base_path}saved_images/' ####### for screenshotting a trial

#%% ===========================================================================
# imports

import os
os.chdir(base_path)
import numpy as np
#import itertools
from psychopy import visual, event, core, gui, data, monitors
from PIL import Image
import csv
import _pickle as pickle
#from itertools import islice
from functions_ctfbackwardmasking_stimDur import *
from JS_psychopyfunctions import *



#%% ===========================================================================
# different conditions in experiment

spatialfrequencies = ['LSF','HSF']
durations = ['50','67','87','114','150'] #### change however. 
#different_conditions = lis87t(itertools.product(spatialfrequencies,durations))

# for the paradigm we need more trial contitions
matching = ['same','diff']
staircases = ['1','2']

maxCeleb = 8

#desired luminance and contrast of images
LC = [0.45, 0.1] # [0.45, 0.1] if between 0 and 1
#occluded_image = (occluded_image*LC[1]) + LC[0]   # desired luminance and contrast

screennr=2 #################################

#%% ===========================================================================
# monitor setup + subject info

exp_name = 'Coarse-to-fine backward masking'
exp_info = {
        '1. subject (e.g. sub-00)' : 'sub-',
        '2. session' : ('ses-01','ses-02'),
        '3. gender' : ('female','male'),
        '4. age' : '',
        '5. screenwidth(cm)' : '49',
        '6. screenwidth(pix)' : '1920',
        '7. screenhight(pix)' : '1200', 
        '8. refreshrate(hz)' : ('120','60'), #ViewPixx - Change this (120) #################################
        '9. screendistance' : '57',
        'Prefered language' : ('fr','en'), #################################
        'Monitor' : ('VPixx020523','Dell'), #################################
        'debugging' : ('0','1','2','3')
        }
# debugging 1 skips everything / debugging 2 skips practice / debugging 3 skips prescreening
dlg = gui.DlgFromDict(dictionary=exp_info, title=exp_name)
    

# If 'Cancel' is pressed, quit
if dlg.OK == False:
    core.quit()
        
# Get date and time
exp_info['date'] = data.getDateStr()
exp_info['exp_name'] = exp_name
session = exp_info['2. session']

mon = monitors.Monitor(exp_info['Monitor']) #Pulls out photometer calibration settings by name.  
# Change this if you are using the ViewPixx (you should find the proper name in PsychoPy Monitor Center)
mon.setDistance(exp_info['9. screendistance'])
mon.setWidth(exp_info['5. screenwidth(cm)']) # Cm width
framerate = exp_info['8. refreshrate(hz)'] 
scrsize = (float(exp_info['6. screenwidth(pix)']),float(exp_info['7. screenhight(pix)'] ))
framelength = 1000/(float(framerate))
mon.setSizePix(scrsize)

language = exp_info['Prefered language'] 
debugging = int(exp_info['debugging'])

# prepare log file to write the data
if not os.path.isdir(data_path):
    os.makedirs(data_path)
logname = data_path + exp_info['1. subject (e.g. sub-00)']
    
# save file with subject info
info_name = f'{logname}_subject-info.csv'
info_file = open(info_name,'a',encoding='UTF8')

if session == 'ses-01':
    header = ''
    for key in exp_info:
        header = header + key + ','
    info_file.write(header + '\n')
info = ''
for key in exp_info:
    info = info + exp_info[key] + ','
info_file.write(info + '\n')
info_file.close()


#%% ===========================================================================
# Timing

fix_dur = 500 # fixation before trial input in ms
int_dur = 500 # time between fixation and trial
#stim_dur = 40 # duration of stimulus
tot_mask_dur = 166 # duration mask
nrmasks = 4
mask_dur = tot_mask_dur/nrmasks
isi_dur = 300 # duration between mask and stim2

nframe = num_frames(fix_dur,int_dur,mask_dur,isi_dur,framelength)

#%% ===========================================================================
# Prepare/open window

win = visual.Window(monitor = mon, size = scrsize, screen=screennr, color = [0,0,0], units ='pix', fullscr = True)

# prepare bitmaps for presenting images
# VA in 3T exp was 4.37° x 3.18°
#stimsize = [330,330] # 4.62° x 3.71°
#stimsize = [440,440] # 5.12° x 4.08° 
stimsize = [550,550] # 6.3° x 5.1°

bitmap = {'fix' : [], 'int' : [], 'stim1' : [], 'mask1' : [], 'mask2' : [], 'mask3' : [], 'mask4' : [], 'isi' : [], 'stim2' : []}

for bit in bitmap:
    bitmap[bit] = visual.ImageStim(win, size=stimsize, mask='circle',interpolate=True)
    bitmap[bit].setOri(180) # need to do this because somehow the images are inverted.....

prescreen = {}
for screennr in range(4):
    prescreen[screennr] = visual.ImageStim(win)
#    prescreen.mask = 'gauss'
#    prescreen.maskParams = {'sd': 2}


# draw fixation cross
fix_cross = visual.ShapeStim(win, 
    vertices=((0, -20), (0, 20), (0,0), (-20,0), (20, 0)),
    lineWidth=2,
    closeShape=False,
    lineColor="black"
    )


instructiontexts = load_txt_as_dict(f'{base_path}instructions_{language}.txt')
textpage = visual.TextStim(win, height=40, font="Palatino Linotype",color= 'black', alignHoriz='center', wrapWidth=scrsize[0])

timer = core.Clock()
win.mouseVisible = False

#%% ===========================================================================
# only needed for the first session
instr_pages = range(1,3)
if session == 'ses-01' and debugging == 0:
# open log file for prescreening
    data_fname = f'{logname}_precreening.csv'
    f = open(data_fname,'a',encoding='UTF8', newline='')
    
    header_names = 'subject,trial,celeb_id,celeb_name,celeb_image,celeb_pos1,celeb_pos2,rand0_name,rand0_pos1,rand0_pos2,rand1_name,rand1_pos1,rand1_pos2,rand2_name,rand2_pos1,rand2_pos2,rand3_name,rand3_pos1,rand3_pos2,answer_celeb,answer_position,correct,rt\n'
    f.write(header_names)
    instr_pages = range(1,5)
else:
    f='' #against stupid error 
    
   
# instruction screen + prescreening celebs
for page in instr_pages: 
    if page == 1:
        fix_cross.draw()
    instructions = textpage
    instructions.text = instructiontexts[f'presc_inst{page}']
    instructions.draw()
    win.flip()
    keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
    escape_check(keys,win,f)
win.flip(clearBuffer=True)
mouse= event.Mouse(visible = True, win = win)


#%% ===========================================================================
# prescreen subjects if they recognise the celebs
celeb_save = f'{logname}_selec-celeb.pickle'

    # for debugging: from functions_ctfbackwardmasking import *
    

# prepare triallist for prescreening
prestim = Stimuli(f'{stim_path}prescreening/') # prestim.list = all stim (list with all all stim)
if debugging == 0:
    # only needed for the first session
    if session == 'ses-01':
        # prepare triallist for prescreening
        prescreen_trials = presceen_trials(base_path,prestim,exp_info) #prepare trial list
        
        # prepare screens for prescreening
        answertext = {}
        answerbox = {}
        for answer in range(6):
            answertext[f'rand{answer}'] = visual.TextStim(win, height=32, font="Palatino Linotype", color = "black")
            answerbox[f'rand{answer}'] = visual.Rect(win, width = 350, height = 100, lineColor = "black", lineWidth = 3)
        
        # showing all 4 images of each celeb
        # if 4 images are recognized then put the celebs in a list and take 10 randomly.
        foundIm = []
        #Pretest
        for prescstim in prescreen_trials:
            loginfo = f"{exp_info['1. subject (e.g. sub-00)']}, {prescstim}"
            for text in prescreen_trials[prescstim]:
                loginfo = f"{loginfo}, {prescreen_trials[prescstim][text]}"
            prescreen[0].setImage(f'{stim_path}prescreening/' + prescreen_trials[prescstim]['im_path'])
            prescreen[0].pos=(0, 0)
            prescreen[0].draw()
            win.flip() #fliping the screen to show images
            core.wait(0.5) #present images for 500ms
            win.flip()

            event.clearEvents()
            mouse.clickReset()
            
            for ans_num,answers in enumerate(answertext):
                if answers == 'rand4':
                    answertext[answers].text = prescreen_trials[prescstim]['im_name']
                    answertext[answers].pos = prescreen_trials[prescstim]['im_pos']
                elif answers == 'rand5':
                    answertext[answers].text = instructiontexts['idk']
                    answerbox[answers].fillColor = "black"
                    answerbox[answers].opacity = .2
                    answertext[answers].pos = (0, 0)
                else:
                    answertext[answers].text = prescreen_trials[prescstim][f'rand{ans_num}_name']
                    answertext[answers].pos = prescreen_trials[prescstim][f'rand{ans_num}_pos']
                answertext[answers].draw()
                answerbox[answers].pos = tuple(answertext[answers].pos)
                answerbox[answers].draw()
            win.flip()
            keys = event.getKeys(keyList=['space','escape'])
            escape_check(keys,win,f)
            
            #measure responses
            timer.reset()
            Ans = False
            
            while Ans == False:
                keys = event.getKeys(keyList=['space','escape'])
                escape_check(keys,win,f)
                if mouse.getPressed() [0]==1:
                    mousepos = mouse.getPos()
                    
                    time = timer.getTime()  
                    
                    #print(mousepos)
                    #check if subject gave correct answer
                    del answers 
                    for answers in answerbox:
                        if answerbox[answers].contains(mousepos):
                            if answers == 'rand4':
                                answer_celeb = prescreen_trials[prescstim]['im_name']
                                correct = 1
                                foundIm.append(answer_celeb)
                                Ans = True
                            elif answers == 'rand5':
                                answer_celeb = 'idk'
                                correct = 0
                                Ans = True
                            elif answers == 'rand0' or answers == 'rand1' or answers == 'rand2' or answers == 'rand3':
                                answer_celeb = prescreen_trials[prescstim][f'{answers}_name']
                                correct = 0
                                Ans = True
                                
        
            toSave = f"{loginfo}, {answer_celeb}, {mousepos}, {str(correct)}, {str(time)}\n"
            f.write(toSave)
            win.flip()
    
            core.wait(0.5)
            event.clearEvents()
            mouse.clickReset() 
        
        #select the final celebirties to be used in the experiment
        final_celeb_list = select_recognised_celebs(base_path,foundIm)
        
        #pickling this final celeb dict (Pickle Rick)
        with open(celeb_save, 'wb') as file:
            file.write(pickle.dumps(final_celeb_list)) # use `pickle.load` to do the reverse
        
        if len(final_celeb_list) < maxCeleb:   
            textpage.text  = instructiontexts["oops"]
            textpage.draw()
            win.flip()
            
            keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
            escape_check(keys,win,f)
            f.close()
            win.close()
            core.quit()
        
        f.close()
            
    elif session == 'ses-02':
        #load celeb dict (unpickle it)
        with open(celeb_save, 'rb') as file:
            final_celeb_list = pickle.load(file)
elif debugging == 1 or debugging == 2 or debugging == 3:
    celeb_save = f'{data_path}debugging_selec-celeb.pickle'
    with open(celeb_save, 'rb') as file:
            final_celeb_list = pickle.load(file)
            
win.mouseVisible = False

#%% ===========================================================================
## load and organise images into a block and trial lists
alltrials_pickle = f'{logname}_alltrials-list.pickle'

# only needed for the first session
if session == 'ses-01':
    # for debugging: from functions_ctfbackwardmasking import *
    
    # get names of all images folders. Naming should be:
    # stimulus: BG01_ID01_IM01.bmp / mask: BG01_ID01_IM01_LSF.bmp / background: BG01.bmp
    # returns self.path and self.stim (list of names)
    stim = Stimuli(f'{stim_path}main/')
    
    # returns list with unique dr of IDs or IMs self.unique_nr
    stim.getuniquenr('IM', f'{stim_path}main/')
    stim.getuniquenr('BG', back_path)
    
    
    # returns self.same_list / self.diff_list / self.maxnr_trials 
    stim.list_of_combinations(final_celeb_list)
    
    # creates self.sf, self.dur, self.match, self.stair and an empty self.trial_list
    alltrials = Ordertrials(stim,maxCeleb,spatialfrequencies,durations,matching,staircases)
    
    # Creating and shuffle the trials with balanced number of conditions
    alltrials.trial_list(framelength) 
    alltrials.shuffle_trials()
    
    
    # Making sure all big blocks have equal number of each condition
    # 8 big blocks -> each have 6 miniblocks with 16 trials each
    # each miniblock has different condition (LSF50,LSF100,LSF150,HSF50,HSF100,HSF150)
    n_bigblock = 8
    miniblock_per_bigblock = len(alltrials.conditionlist)
    trials_per_block = 20 # that is 10 per staircase (used to be 16 -> 8 per staircase)
    
    # creates self.blocks['block-1']['HSF_50']['stair-1'][0] 
    # in this case: 8 blocks, 6 conditions, 2 staircases, 16 trials
    
    alltrials.make_miniblocks(n_bigblock,miniblock_per_bigblock,trials_per_block,stim.unique_nr['BG']) 
    # for debugging: aaaa = alltrials.blocks


    # make Psi Staircase for all conditions (x2)
    # making normal staircase instead!

    # nTrials is trials PER staircase
    nTrials = int(((trials_per_block/len(alltrials.stair))*n_bigblock)-10)
    signal_start = 75 # signal of blending (e.g. signal = 30, alpha = 70)
    steps = [0.5] ##### could also be 0.5 (?) play around
    steptype = 'db' ### could be 'lin' or 'log'
    nUp = 1
    nDown = 2 # will result in ~80% acc
    minVal = 1
    maxVal = 100
    #thresholdPrior=('normal',50,5) ##### change for visibility
    #thresholdPrior1=('normal',50,5) #for both staircases. 1 very visible at the beginning
    #thresholdPrior2=('normal',20,5) # second not visible at all... hope this will converge at the end
    
    # initialize a staircase for each condition
    #creates alltrials.staircases
    alltrials.prepare_staircare(nTrials,signal_start,steps,steptype,nUp,nDown,minVal,maxVal)
                          
    with open(alltrials_pickle, 'wb') as file:
        pickle.dump(alltrials, file)
        
        
else:
    #load alltrials dict (unpickle it)
    with open(alltrials_pickle, 'rb') as file:
        alltrials = pickle.load(file)

    

#%% ===========================================================================
# Open and prepare header information for log file

data_fname = f'{logname}_main-data.csv'

f = open(data_fname,'a',encoding='UTF8', newline='')


# write header if it is the first session

header_names = list(alltrials.blocks['block-1']['control']['trials'][0].keys())

writer = csv.DictWriter(f, fieldnames=header_names)


writer.writeheader()


#%% ===========================================================================
# instruction screen + preparation screen


practice_rounds = {'pract-01' : 1,
                   'pract-02' : 1}

for pracnr,practice_no in enumerate(practice_rounds):
    practicing = True
    
    if practice_no == 'pract-01':
        instr_num = range(1,5)
        show_celebs = True
    elif practice_no == 'pract-02':
        instr_num = range(1,4)
        show_celebs = False
        
    for page in instr_num: 
        instruction_pract = textpage
        instruction_pract.text = instructiontexts[f'pract{int(pracnr+1)}_inst{page}']
        instruction_pract.draw()
        if page == 1 and practice_no == 'pract-02':
            visibility = [30,50,70]
            pos_list = [(-400,-350), (0,-350), (400, -350)]
            examplestim = stim_path + 'main/' + alltrials.blocks['block-6']['control']['trials'][0]['stim1'] #################
            loaded_image = np.array(Image.open(examplestim))
            exampleback = back_path + alltrials.blocks['block-6']['control']['trials'][0]['background']
            loaded_back = np.array(Image.open(exampleback))
            for idx,signal in enumerate(visibility):
                image2draw = occlude(loaded_image, loaded_back, signal)
                image2draw = equalise_im(image2draw,LC)
                greyback = np.array(Image.open(os.path.join(base_path,'grey/grey.bmp')))
                greyback = equalise_im(greyback, LC)
                alphamask = np.array(Image.open(f'{base_path}alphamask.bmp'))
                alphamask = normalise_im(alphamask) # normalise alphamask
                image2draw = replace_background(image2draw,greyback,alphamask)
                prescreen[idx].setOri(180) # need to do this because somehow the images are inverted.....
                prescreen[idx].setMask('circle')
                prescreen[idx].setImage(image2draw)
                prescreen[idx].pos = pos_list[idx]
                prescreen[idx].draw()
        win.flip()
        keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
        escape_check(keys,win,f)
        win.flip(clearBuffer=True)
        core.wait(1)
        if page == 1 and show_celebs:
            List_pos = [(-250,-250), (250,-250), (-250, 250), (250, 250)]
            for celebid in final_celeb_list:
                stimuli = [ x for x in prestim.list if 'ID'+celebid in x ]
                for im_idx,image in enumerate(stimuli): 
                    prescreen[im_idx].setImage(f'{stim_path}prescreening/{image}')
                    prescreen[im_idx].pos=List_pos[im_idx]
                    prescreen[im_idx].mask = None
                    prescreen[im_idx].draw()
                namepage = textpage
                namepage.text = final_celeb_list[celebid]
                namepage.pos = (0, 0)
                namepage.draw()
                win.flip()
                if debugging != 0:
                    core.wait(.5) ###for debugging
                else:
                    core.wait(5)
                keys = event.getKeys(keyList=['space','escape'])
                escape_check(keys,win,f)
            win.flip(clearBuffer=True)
            escape_check(keys,win,f)
            show_celebs = False
    mouse= event.Mouse(visible = False, win = win)
    
    if debugging == 0 or debugging == 3:
        # practice trialsss
        practice_dur = 200 #500ms for target
        practice_signal = 100
        practice_maskdur = 200
        
        practice_trial_list = prepare_practice_trials(practice_no,alltrials,session,practice_dur,practice_signal,framelength)
        while practicing:   
            accuracy = 0
            for pract_trial in practice_trial_list:
                pract_trialinfo = practice_trial_list[pract_trial]
                pract_trialinfo['block'] = pract_trialinfo['block'] + '.' + str(practice_rounds[practice_no])
                bitmap['fix'].draw()
                fix_cross.setAutoDraw(True)
                
                nframe['stim1'] = pract_trialinfo['nframes']
                #load stim1, stim2 and mask
                drawed = loadimage(base_path, pract_trialinfo, pract_trialinfo['contrast'], LC)
            
                #set stim1, stim2 and mask
                for drawit in bitmap:
                    bitmap[drawit].setMask('circle')
                    bitmap[drawit].setImage(drawed[drawit])
            
                #### trial windows 
                for window in bitmap:
                    if window == 'int':
                        fix_cross.setAutoDraw(False)
                    for nFrames in range(nframe[window]):
                        bitmap[window].draw()
                        win.flip()
                timer.reset()
                                                        
                # Wait until a response, or until time limit.
                keys = event.waitKeys(keyList=['s','l','escape','p'])  
                escape_check(keys,win,f)
                if keys:
                    pract_trialinfo['rt'] = timer.getTime()
                for drawit in bitmap:
                    bitmap[drawit].clearTextures()
                pract_trialinfo['acc'] = 0
                fb_text = instructiontexts["incorrect" ]
                if keys:
                    escape_check(keys,win,f)
                    if 's' in keys and (pract_trialinfo['matching'] == 'same'): # is same
                        pract_trialinfo['acc'] = 1
                        fb_text = instructiontexts["correct" ]
                        accuracy += 1
                    elif 'l' in keys and (pract_trialinfo['matching'] == 'diff'): # is different
                        pract_trialinfo['acc'] = 1      
                        fb_text = instructiontexts["correct" ]
                        accuracy += 1
                fix_cross.setAutoDraw(False)
                fbpage = textpage
                fbpage.text = fb_text
                fbpage.draw()
                win.flip()
                core.wait(1)
                escape_check(keys,win,f)
                win.flip(clearBuffer=True)
            
                writer.writerow(pract_trialinfo)
            total_acc = int((accuracy/len(practice_trial_list))*100)

        
        
            if total_acc < 75:
                fb = 'oops'
            else:
                fb = 'great'
                
            end_practice = textpage
            text2print  = instructiontexts[f'{fb}{practice_rounds[practice_no]}_pract']
            end_practice.text = text2print.replace('{total_acc}', str(total_acc))
            end_practice.draw()
            win.flip()
            keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
            escape_check(keys,win,f) 
                
            if fb == 'oops' and practice_rounds[practice_no] == 2:
                f.close()
                win.close()
                core.quit()
            elif fb == 'oops':
                practice_rounds[practice_no] = 2
            else:
                practicing = False
        
        
            

#%% ===========================================================================
# instructions main experiment trialsss
for page in range(1,4): 
    instruction_pract = textpage
    instruction_pract.text = instructiontexts[f'main_inst{page}']
    instruction_pract.draw()
    win.flip()
    keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
    escape_check(keys,win,f)
    win.flip(clearBuffer=True)
    core.wait(1)


#%% ===========================================================================
# Main experiment code 
win.mouseVisible = False

block_order = f'{logname}_block-order.pickle'
if session == 'ses-01':
#split nblocks in 2 since there are 2 sessions
    block_keys = dict.fromkeys(alltrials.blocks)
    blocks_ses = {}
    blocks_ses['ses-01'] = []
    blocks_ses['ses-02'] = []
    for idx, blockname in enumerate(block_keys.items()):
        if idx < int(len(block_keys.items())/2):
            sesnum = 'ses-01'
        else:
            sesnum = 'ses-02'
        blocks_ses[sesnum].append(blockname[0])
    miniblock = 1 ## there will be 16 blocks ## ugly coding because this changed later
    #pickling this block_order per session (Pickle Rick)
    with open(block_order, 'wb') as file:
        file.write(pickle.dumps(blocks_ses)) # use `pickle.load` to do the reverse
else:
    with open(block_order, 'rb') as file:
        blocks_ses = pickle.load(file)
    miniblock = 9 ## there will be 16 blocks ## ugly coding because this changed later
        

# Start experiment
for bl,block in enumerate(blocks_ses[session]):
    condnr = 0 # cound conditions for block breaks
    for condnr,cond in enumerate(alltrials.blocks[block]):
        condition = alltrials.blocks[block][cond]
        for idx,trialinfo in enumerate(condition['trials']):
            fix_cross.setAutoDraw(True)
            staircase = alltrials.staircases[trialinfo['condition']][f'stair-{trialinfo["staircasenr"]}']
            nframe['stim1'] = trialinfo['nframes']
            
            #while staircase._nextIntensity == None:
            #    pass
            if idx % 5 == 0 and idx != 0:
                if idx % 10 == 0:
                    trialinfo['contrast'] = staircase._nextIntensity + 10
                    print('jitter: SNR plus 10 ')
                else:
                    trialinfo['contrast'] = staircase._nextIntensity - 10
                    print('jitter: SNR minus 10 ')
            else:
                trialinfo['contrast'] = staircase._nextIntensity
            print(f'block {miniblock}    -    {trialinfo["condition"]}    -    trial {idx}  stair {trialinfo["staircasenr"]}  -    {trialinfo["contrast"]}')
            
            #load stim1, stim2 and mask
            drawed = loadimage(base_path, trialinfo, trialinfo['contrast'], LC)
        
            #set stim1, stim2 and mask
            for drawit in bitmap:
                bitmap[drawit].setMask('circle')
                bitmap[drawit].setImage(drawed[drawit])
        
            #### trial windows 
            for window in bitmap:
                if window == 'int':
                    fix_cross.setAutoDraw(False)
                for nFrames in range(nframe[window]):
                    bitmap[window].draw()
                    win.flip()
                #win.getMovieFrame() ####### for screenshotting a trial
                #win.saveMovieFrames(f'{save_path}{window}.bmp')
            timer.reset()
                                            
            # Wait until a response
            if debugging == 1:
                esc_key = event.getKeys(keyList=['space','escape'])
                escape_check(esc_key,win,f)
                if trialinfo['matching'] == 'same': # is same
                    keys = ['s']
                elif trialinfo['matching'] == 'diff': # is different
                    keys = ['l']
            else:
                keys = event.waitKeys(keyList=['s','l','escape','p'])
                escape_check(keys,win,f)
            
            bitmap['fix'].draw()
            fix_cross.setAutoDraw(True)
            win.flip()
            if keys:
                trialinfo['rt'] = timer.getTime()
                # fixation.clearTextures()
            
            for drawit in bitmap:
                bitmap[drawit].clearTextures()
        
            trialinfo['acc'] = -1
            if keys:
                escape_check(keys,win,f)
                if 's' in keys and (trialinfo['matching'] == 'same'): # is same
                    trialinfo['acc'] = 1
                elif 'l' in keys and (trialinfo['matching'] == 'diff'): # is different
                    trialinfo['acc'] = 1         
            
            trialinfo['trialno'] = idx
            trialinfo['block'] = block
            trialinfo['session'] = session
            
            #update staircase
            if idx % 5 != 0 or idx == 0:
                staircase.addData(trialinfo['acc']) ########## Does more than the accuracy and contrast needs to be updated??
                staircase.intensities.append(trialinfo['contrast'])
                alltrials.staircases[trialinfo['condition']][f'stair-{trialinfo["staircasenr"]}'] = staircase
            writer.writerow(trialinfo)
        condnr += 1
        if condnr == round(((len(spatialfrequencies) * len(durations)) + 1) /2):
            block_break(win, mon, scrsize, screennr, f, miniblock,16,language,debugging)
            miniblock += 1
    if miniblock == 8: # end of session 
        fix_cross.setAutoDraw(False)    
        instructions = textpage
        instructions.text = instructiontexts[f"end_{session}"]
        instructions.draw()
        win.flip()
        keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
        escape_check(keys,win,f)
    else:        
        block_break(win, mon, scrsize, screennr, f, miniblock,16,language,debugging)
        miniblock += 1
with open(alltrials_pickle, 'wb') as file:
    pickle.dump(alltrials, file)
    

f.close()
win.close()
core.quit()