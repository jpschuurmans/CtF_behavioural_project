# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 20:29:50 2022

Functions for CtF backward masking experiment

@author: jschuurmans

"""

#%% =============================================================================
# imports
import os
import numpy as np
from PIL import Image # this is used to manipulate images and do the alpha-blending
import itertools
import copy
import random
import numpy.random as rnd
import PsiMarginal 
from psychopy import visual, event, core, gui, data, monitors

#%% =============================================================================
# functions
def escape_check(keys,win,f):
    if 'escape' in keys:
        win.close()
        f.close()
        

def nframes(time_in_ms, framelength):
     return int(time_in_ms/framelength)


def num_frames(fix_dur, int_dur, mask_dur,framelength):
    nframe = {}
      
    nframe['fix'] = nframes(fix_dur,framelength)
    nframe['int'] = nframes(int_dur,framelength)
    nframe['stim1'] = 1
    nframe['mask'] = nframes(mask_dur,framelength)
    nframe['stim2'] = 1
    return nframe


def makePsi(nTrials,signal_start,signal_end,steps): # start_thresh is signal strength in percentage
# Image visibility ranges between 1.5 and 40, logarithmically, 40 possibilities.
    staircase = PsiMarginal.Psi(stimRange=np.geomspace(signal_start,signal_end,steps,endpoint=True),
            Pfunction='Weibull', nTrials=nTrials,
            threshold=np.geomspace(signal_start,signal_end,steps, endpoint=True), 
            thresholdPrior=('normal',5,5), slope=np.geomspace(0.5, 20, 50, endpoint=True),
            guessRate=0.5, slopePrior=('gamma',3,6), lapseRate=0.05, lapsePrior=('beta',2,20), marginalize=True)
    return staircase
# sigma is slope


def loadimage(base_path,trialinfo,visibility,LC):
    # loading and occluding image ready for drawing
    stimuli = {'fix' : 'background',
               'int' : 'background',               
               'stim1' : 'stimuli',
               'mask' : 'masks',
               'stim2' : 'stimuli'}
    draw = {}
    all_loaded = {}
    facepix = np.array(Image.open(f'{base_path}masks/facepix.bmp'))
    for curr in stimuli:
        stim_path = f'{base_path}{stimuli[curr]}/'
        if curr == 'fix' or curr == 'int':
            image2load = trialinfo['background']
        else:
            image2load = trialinfo[curr]
        loaded_image = np.array(Image.open(os.path.join(stim_path,image2load)))
        draw[curr] = equalise_im(loaded_image,LC)
    for im in range(1,3):
        occluded_image = occlude(draw[f'stim{im}'],draw['int'],visibility)
        occluded_image = equalise_im(occluded_image,LC)
        draw[f'stim{im}'] = replace_background(occluded_image,draw['int'],facepix)
    draw['mask'] = replace_background(draw['mask'],draw['int'],facepix)
    return draw

def equalise_im(loaded_image, LC):
    loaded_image = 2.*(loaded_image - np.min(loaded_image)) / np.ptp(loaded_image)-1 # equalise image
    #loaded_image = (loaded_image*LC[1]) + LC[0]   # desired luminance and contrast
    return loaded_image

def replace_background(equalised_image, background_image, facepix):
        new_im = np.empty(np.shape(equalised_image))
        for iy, ix in np.ndindex(new_im.shape):
            if facepix[iy, ix] == 0:
                new_im[iy, ix] = background_image[iy, ix]
            elif facepix[iy, ix] == 255:
                new_im[iy, ix] = equalised_image[iy, ix]               
        return new_im

def occlude(image, back, signal):
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


def block_break(win, f, block_no,maxblock):
    timer=3
    # timer=1
    blocktext = visual.TextStim(win,height=32, font="Palatino Linotype",alignHoriz='center',wrapWidth=1000)   
    timertext = visual.TextStim(win,height=32, pos=[0,-300], font="Palatino Linotype",alignHoriz='center')   
    
    
    if block_no % 6 == 0:
        timer=20
        # timer=0
        
    blocktext.text = f"""Please take a short rest before the next block.
    You can press "SPACE" to start again after {timer} seconds\n when you
    are ready.\n\n Block: {block_no}/{maxblock}"""
    
    for time in range(timer):
        timer -= 1
        blocktext.draw()
        
        timertext.text = """:""" + str(timer)
        timertext.draw()
        core.wait(1)
        win.flip()
        if timer == 0:
            timertext.text="""READY"""
            blocktext.draw()
            timertext.draw()
            win.flip()
            
    keys = event.waitKeys(keyList=['space','escape'])
    escape_check(keys,win,f)
    
    win.flip()
    core.wait(2)



#%% =============================================================================
# classes


class Stimuli:
    # Stimuli() saves self.path and self.stim (list of names)
    def __init__(self, image_path):
        # get names of all images folders
        self.path = image_path
        self.list = os.listdir(os.path.join(image_path))
        self.unique_nr = {}
        
    def getuniquenr(self,whichtype): 
        # function makes a list of unique numbers
        # if name of images are ID01_IM01.bmp
        # then 'whichtype' should be either 'ID' or 'IM'
        type_list = []
        for im in self.list:
            type_list.append(int(im.rsplit(whichtype)[1][0:2]))
        unique_nr = np.unique(np.array(type_list))
        # returns list with unique dr of IDs or IMs self.unique_nr
        self.unique_nr[whichtype] = unique_nr
        
    def list_of_combinations(self):
        # returns self.same_list / self.diff_list / self.maxnr_trials 
        same_list = []
        diff_list = []
        for idx,uniqueid in enumerate(self.unique_nr['ID']):
            nr_unique_images = len(self.unique_nr['IM'])
            list_curr_id = self.list[(idx*nr_unique_images):nr_unique_images+(idx*nr_unique_images)]
            comb_same_list = list(itertools.combinations(list_curr_id, r=2))
            same_list.append(comb_same_list)
            
            list_no_curr_id = copy.deepcopy(self.list)
            del list_no_curr_id[(idx*nr_unique_images):nr_unique_images+(idx*nr_unique_images)] # delete current id from list
            comb_diff_list = list(itertools.product(list_curr_id,list_no_curr_id))
                        #select as many combinatoins as the same list has..
            comb_diff_list = random.choices(comb_diff_list,k=len(comb_same_list))
            
            diff_list.append(comb_diff_list)

        
        self.same_list = same_list
        self.diff_list = diff_list
        self.maxnr_trials = np.shape(same_list)[0]*np.shape(same_list)[1] # nr identities times nr images
        # same_list[0] = all "same" combinations of the first identity
        # same_list[0][0] = first possible "same" combination



# =============================================================================



class Ordertrials(object):
    
    def __init__(self,stim,spatialfrequencies,durations,matching,staircases):
        self.sf = spatialfrequencies
        self.dur = durations
        self.match = matching
        self.stair = staircases
        self.stim = stim

    # Creating the trials with balanced number of conditions
    def trial_list(self,framelength):
        different_trials = ["_".join(items) for items in itertools.product(self.sf ,self.dur,self.match,self.stair)]
        self.conditionlist = ["_".join(items) for items in itertools.product(self.sf ,self.dur)]
        
        # make this a dictionary
        self.trial_list = {}
        for key in different_trials:
            self.trial_list[key] = []
            
        matchingcond = {'same' : self.stim.same_list,
                        'diff' : self.stim.diff_list}
        
        for SF in self.sf:
                for dur in self.dur:
                    ImFrame = int(int(dur)/framelength)
                    for idx,whichid in enumerate(self.stim.unique_nr['ID']): # loop through ID's
                        for trialtype in self.match: # same or different trial                        
                            triallist = matchingcond[trialtype]
                            for cmb,combi_per_id in enumerate(triallist[idx]): #all possible combinations per ID
                                for stair in self.stair: #two staircases per condition
                                    trial_name = f'{SF}_{dur}_{trialtype}_{stair}' # trial type name
                                    #the two backgrounds will alternate depening on the staircase nr
                                    #back = f'BG0{str(stair)}.bmp' ################################### if using this, also change self.trial_list
                                    num1 = round(random.random())
                                    if num1 == 0: # randomise which image is presented as image1
                                        num2 = 1 # making sure image 2 is the other image... :)
                                    else:
                                        num2 = 0
                                    # trial_list will be a dictionary with 24 keys
                                    # the conditions are SF*duration (2*3 = 6 in the example)
                                    # this is doubled to have the same/diff conditions for the matching task (2*6 = 12)
                                    # this is doubled because there are 2 staircases per condition (2*12 = 24)
                                    self.trial_list[trial_name].append({
                                        'block' : [],
                                        'trialno' : 0,
                                        'stim1' : combi_per_id[num1],
                                        'stim2' : combi_per_id[num2],
                                        'matching' : trialtype,
                                        #'mask' : f'{back[:-4]}_{combi_per_id[num1][:-4]}_{SF}.bmp',
                                        'mask' : f'{combi_per_id[num1][:-4]}_{SF}.bmp',
                                        'duration' : dur,
                                        'nframes' : ImFrame,
                                        'SF' : SF,
                                        'background' : [],
                                        'staircasenr': stair,
                                        'rt' : 0,
                                        'acc' : 0,
                                        'contrast' : 0})  
                                    
    def shuffle_trials(self):
        # here we shuffle trials from each condition within the condition block
        for cond in self.trial_list.keys(): 
            rnd.shuffle(self.trial_list[f"{cond}"])
          
            
    def make_miniblocks(self,n_bigblock,miniblock_per_bigblock,trials_per_block,unique_back):
        # to make all the blocks ready
        # big blocks containing smaller blocks (small block = one condition per block)
        # small blocks contain trails. half same, half different trials.
        self.n_bigblock = n_bigblock
        self.miniblock_per_bigblock = miniblock_per_bigblock
        self.trials_per_block = trials_per_block
        self.blocks = {}
        background_numbers = np.repeat(unique_back, int(np.ceil(n_bigblock/np.size(unique_back))))
        np.random.shuffle(background_numbers)
        mini_blocks = {}
        stair = {}
        tempblock=[]
        blocklist = {}
        for bblock in range(n_bigblock):
            name = f'block-{bblock+1}'
            for idx,cond in enumerate(self.conditionlist):
                back_num = background_numbers[idx]
                for stairnr in self.stair:
                    # for every mini block, grab 8 unique trials.. and go on to the next trial
                    for trial in range(int((trials_per_block/len(self.stair))/2)): # 8 (4same/4diff) trials of one condition per block
                        for matching in self.match:
                            trial2add = copy.deepcopy(self.trial_list[f'{cond}_{matching}_{stairnr}'][trial*(idx+1)])
                            trial2add['mask'] = f'BG0{back_num}_{trial2add["mask"]}'
                            trial2add['background'] = f'BG0{back_num}.bmp'
                            tempblock.append(trial2add)                   
                rnd.shuffle(tempblock)
                stair['trials'] = tempblock
                tempblock=[]
                mini_blocks[cond] = stair
            blocklist[name] = mini_blocks
        self.blocks = blocklist

    def prepare_staircare(self,nTrials,signal_start,signal_end,steps):
        for block in self.blocks:
            for cond in self.blocks[block]:
                for stairnr in self.stair:
                    self.blocks[block][cond][f'stair-{stairnr}'] = makePsi(nTrials,signal_start,signal_end,steps)
        

 # =============================================================================       
  
 