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
from psychopy import visual, event, core, gui, data, monitors
from JS_psychopyfunctions import *
import numpy.ma as ma

#%% =============================================================================
# functions

def num_frames(fix_dur, int_dur, mask_dur, isi_dur, framelength):
    nframe = {}
      
    nframe['fix'] = nframes(fix_dur,framelength)
    nframe['int'] = nframes(int_dur,framelength)
    nframe['stim1'] = 1
    nframe['mask1'] = nframes(mask_dur,framelength)
    nframe['mask2'] = nframes(mask_dur,framelength)
    nframe['mask3'] = nframes(mask_dur,framelength)
    nframe['mask4'] = nframes(mask_dur,framelength)
    nframe['isi'] = nframes(isi_dur,framelength)
    nframe['stim2'] = 1
    return nframe


def loadimage(base_path,trialinfo,visibility,LC):
    # loading and occluding image ready for drawing
    stimuli = {'fix' : 'grey',
               'int' : 'grey',               
               'stim1' : 'stimuli',
               'mask1' : 'masks',
               'mask2' : 'masks',
               'mask3' : 'masks',
               'mask4' : 'masks',
               'isi' : 'grey',
               'stim2' : 'stimuli'}
    draw = {}
    loaded = {}
    all_loaded = {}
    alphamask = np.array(Image.open(f'{base_path}alphamask.bmp'))
    alphamask = normalise_im(alphamask) # normalise alphamask
    # visualise: plt.imshow(alphamask, interpolation='nearest')
    # plt.gray()
    # plt.show()
    
    for curr in stimuli:
        stim_path = f'{base_path}{stimuli[curr]}/'
        if 'stim' in curr:
            image2load = 'main/' + trialinfo[curr]
        elif 'mask' in curr:
            image2load = trialinfo[curr]
        else:
            image2load = 'grey.bmp'
        loaded_image = np.array(Image.open(os.path.join(stim_path,image2load)))
        loaded_image = equalise_im(loaded_image, LC)
        #visualise: Image.fromarray(loaded_image.astype('uint8'))
        draw[curr] = loaded_image
    #if trialinfo['block'] != 'practice':
    #    draw[f'stim1'] = occlude(draw[f'stim1'],draw['int'],visibility)
    # bitmap['stim1'].setImage(draw[f'stim1'])
    # bitmap['stim1'].draw()
    # win.flip()
    backim = np.array(Image.open(os.path.join(base_path,'background',trialinfo['background'])))
    backim = equalise_im(backim, LC)
    draw[f'stim1'] = occlude(draw[f'stim1'],backim,visibility) ############### can this handle equalised images?
    for stim in draw:
        draw[stim] = equalise_im(draw[stim],LC)
        #visualise: Image.fromarray(draw[f'stim1'].astype('uint8'))
        draw[stim] = replace_background(draw[stim],draw['int'],alphamask)    
    return draw


def replace_background(equalised_image, background_image, alphamask):
        # visualise: from matplotlib import pyplot as plt
        # plt.imshow(alphamask, interpolation='nearest')
        backmask = alphamask
        facemask = 1-alphamask

        face_masked = background_image*backmask
        back_masked = equalised_image*facemask
        
        blend_im = face_masked + back_masked
        # visualise: Image.fromarray(blend_im.astype('uint8'))
        return blend_im


def block_break(win,mon, scrsize, screennr, f, block_no, maxblock, language,debugging):
    textwin = win
    #textwin.color = '#7F7F7F'
    
    
    if debugging == 1 or debugging ==2:
        timer=5
    else:
        timer=20
  
    #block_no = str(block_no)
    if language == 'en':
        rest_text = f"""Please take a short rest before the next block.\n
        You can press "SPACE" to start again after {timer} seconds\n
        when you are ready.\n\n\n\n\n\n\nBlock: {block_no}/{maxblock}"""
        ready_text = """READY"""
    elif language == 'fr':
        rest_text = f"""Veuillez vous reposer un peu avant le prochain bloc.\n
        Vous pouvez appuyer sur "ESPACE" pour recommencer après {timer} secondes\n
        lorsque vous êtes prêt.e.\n\n\n\n\n\n\nBloc : {block_no}/{maxblock}"""
        ready_text = """PRÊT.E"""
        
    #blocktext = visual.TextStim(win=textwin,height=32, pos=[0, 100], font="Palatino Linotype",alignHoriz='center',wrapWidth=1000, text=rest_text) 
    blocktext = visual.TextStim(win=textwin,height=32, pos=[0, 100], font="Palatino Linotype", text=rest_text)
    timertext = visual.TextStim(win=textwin,height=32, pos=[0,-300], font="Palatino Linotype",alignHoriz='center')     
    
    for time in range(timer):
        timer -= 1
        blocktext.draw()
        
        timertext.text = """:""" + str(timer)
        timertext.draw()
        core.wait(1)
        textwin.flip()

        if timer == 0:
            timertext.text = ready_text
            blocktext.draw()
            timertext.draw()
            textwin.flip()
            
                
    # Wait until a response
    if debugging == 0 or debugging == 2:
        keys = event.waitKeys(keyList=['s','l','escape','space'])
        escape_check(keys,win,f)
    #win.color = 'gray'        
    win.flip(clearBuffer=True)
    del blocktext, timertext
    core.wait(2)



def presceen_trials(base_path,prestim,exp_info):
    # prescreening to select celeberties welknown to the subject
    # Subject must judge if they recognise all 4 images of each celeberty 
    # if 4 images are recognized then put the celeberties in a list and take 10 randomly   
    
    # returns list with unique dr of IDs or IMs self.unique_nr
    prestim.getuniquenr('ID',f'{base_path}stimuli/main/') # prestim.unique_nr
    prestim.getuniquenr('IM', f'{base_path}stimuli/main/')
    
    
    # make list of celeberty id's
    celeb_IDlist = []
    for celeb_id in prestim.unique_nr['ID']:
        for celeb_im in prestim.unique_nr['IM']:
            celeb_IDlist.append(celeb_id)
            
            

    # make trial order
    celeb_list = load_txt_as_dict(f'{base_path}celeb_names.txt')
    #List_pos = [(0, -7),(-12, -4), (12, -4), (-8, 5), (8, 5)]
    List_pos = [(0, -400),(-550, -100), (550, -100), (-300, 300), (300, 300)]
    trial_list = list(range(1,int((len(prestim.unique_nr['ID'])*len(prestim.unique_nr['IM']))+1)))
    prescreen_trials = {}
        
    for image in prestim.list:
        celeb_id = image.rsplit('ID')[1][0:2]
        random.shuffle(trial_list)
        trialnum = trial_list.pop()
        Rand_pos = random.sample(List_pos, len(List_pos))
        celeb_info = {}
        celeb_info['celeb_id'] = celeb_id
        celeb_info['im_name'] = celeb_list[str(celeb_id)]
        celeb_info['im_path'] = image
        celeb_info['im_pos'] = Rand_pos[4]
        
        #templist
        tempID = copy.deepcopy(celeb_IDlist)
        # remove ID 1 from list
        for rep in range(len(prestim.unique_nr['IM'])):
            tempID.remove(int(celeb_id))
        rand_celebs = random.sample(list(np.unique(tempID)) , 4)
        for randnr,rand in enumerate(rand_celebs):
            tempID.remove(rand)           
            celeb_info[f'rand{randnr}_name'] = celeb_list["%02d" % (rand_celebs[randnr])]
            celeb_info[f'rand{randnr}_pos'] = Rand_pos[randnr]
        prescreen_trials[f'trial{trialnum}'] = celeb_info
    
    l = list(prescreen_trials.items())
    random.shuffle(l)
    prescreen_trials = dict(l)
    
    return prescreen_trials


def select_recognised_celebs(base_path,foundIm):
    celeb_list = load_txt_as_dict(f'{base_path}celeb_names.txt')
    
    FinalList = []
    FinalList3 = []
    
    #select all celebs that are recognised in all 4 photos
    for num in celeb_list:
        celeb = [im for im in foundIm if celeb_list[num] in im]
        if len(celeb) == 4:
            FinalList.append(celeb_list[num])
    
    # if not all photos are recognised, select them where 3 photos were.
    ''' We're going to be more strict, so this part is commented out
    if len(FinalList) < 10:
        miss = 10 - len(FinalList)
        for num in celeb_list:
            actor = [im for im in foundIm if celeb_list[num] in im]
            if len(actor) == 3:
                FinalList3.append(celeb_list[num])
        final_actor_list = random.sample(FinalList, len(FinalList))
        
        if len(FinalList3) > 0 and len(FinalList3) >= miss:  ####only thing I added was 'and len(FinalList3) >= miss:'
            for i in range(miss):
                l = random.sample(FinalList3, miss)
                final_actor_list.append(l[i])            
    else:    
        final_actor_list = random.sample(FinalList, 10) '''  
    
    if len(FinalList) < 9:
        final_actor_list = FinalList
        #convert list to dict with keys
    else:
        final_actor_list = random.sample(FinalList, 8)
    
    #convert list to dict with keys
    actor_dict = {}
    for actor in final_actor_list:
        actor_dict[[i for i in celeb_list if celeb_list[i]==actor][0]] = actor
        
    return actor_dict



def prepare_practice_trials(practice_no,alltrials,session,practice_dur,signal,framelength):
    practice_trial_list = {}
    conditions = alltrials.blocks[f'block-{random.randint(1, 8)}']
    for trial_no,cond in enumerate(conditions):
        trial = copy.deepcopy(alltrials.blocks[f'block-{random.randint(1, 8)}'][cond]['trials'][random.randint(0, 15)])
        
        if trial_no % 2 == 0:  ## this is just to make sure half of the practice trials
            matchtype = 'diff' ## have 2 same identities and half are different
        else:
            matchtype = 'same'
        while matchtype != trial['matching']:
            trial = copy.deepcopy(alltrials.blocks[f'block-{random.randint(1, 8)}'][cond]['trials'][random.randint(0, 15)])
            
        trial['session'] = session
        trial['block'] = practice_no
        trial['trialno'] = trial_no
        trial['contrast'] = random.randint(int(signal/2), signal)
        
        if practice_no == 'pract-01':
            trial['duration'] = random.randint(int(practice_dur/2), practice_dur)
            trial['nframes'] = nframes(practice_dur,framelength)
            trial['contrast'] = signal
           
        practice_trial_list[trial_no] = trial
        

            
    keys = list(practice_trial_list.keys())
    random.shuffle(keys)
    shuff_practice_trial_list = dict()
    for key in keys:
        shuff_practice_trial_list.update({key: practice_trial_list[key]})
    practice_trial_list = shuff_practice_trial_list
        
    return practice_trial_list

#%% =============================================================================
# classes


class Stimuli:
    # Stimuli() saves self.path and self.stim (list of names)
    def __init__(self,image_path):
        # get names of all images folders
        self.path = image_path
        self.list = os.listdir(os.path.join(image_path))
        self.unique_nr = {}
    def getuniquenr(self,whichtype, stim_path): 
        # function makes a list of unique numbers
        # if name of images are ID01_IM01.bmp
        # then 'whichtype' should be either 'ID' or 'IM'
        type_list = []
        for im in os.listdir(os.path.join(stim_path)):
            type_list.append(int(im.rsplit(whichtype)[1][0:2]))
        unique_nr = np.unique(np.array(type_list))
        # returns list with unique dr of IDs or IMs self.unique_nr
        self.unique_nr[whichtype] = unique_nr
        
    def list_of_combinations(self,actor_dict):
        # returns self.same_list / self.diff_list / self.maxnr_trials 
        same_list = {}
        diff_list = {}
        self.stim_list = []
        # select the celebs for current subject
        actor_id_list = ['ID'+s for s in list(actor_dict.keys())]
        for celebid in actor_id_list:
            self.stim_list.extend([ x for x in self.list if celebid in x ])
        self.list = self.stim_list

        same_list = []
        diff_list = []
        for idx,uniqueid in enumerate(actor_dict.keys()):
            nr_unique_images = len(self.unique_nr['IM'])
            #stimuluslist = [s for s in stim.stim_list if f'BG0{background}' in s]
            list_curr_id = self.stim_list[(idx*nr_unique_images):nr_unique_images+(idx*nr_unique_images)]
            comb_same_list = list(itertools.combinations(list_curr_id, r=2))
            same_list.append(comb_same_list)
            
            list_no_curr_id = copy.deepcopy(self.stim_list)
            del list_no_curr_id[(idx*nr_unique_images):nr_unique_images+(idx*nr_unique_images)] # delete current id from list
            comb_diff_list = list(itertools.product(list_curr_id,list_no_curr_id))
            #select as many combinatoins as the same list has..
            comb_diff_list = random.choices(comb_diff_list,k=len(comb_same_list))
            diff_list.append(comb_diff_list)

        self.same_list = same_list
        self.diff_list = diff_list
        # same_list[0] = all "same" combinations of the first identity
        # same_list[0][0] = first possible "same" combination


# =============================================================================



class Ordertrials(object):
    
    def __init__(self,stim,maxCeleb,spatialfrequencies,durations,matching,staircases):
        self.sf = spatialfrequencies
        self.dur = durations
        self.match = matching
        self.stair = staircases
        self.stim = stim
        self.maxCeleb = maxCeleb
    # Creating the trials with balanced number of conditions
    def trial_list(self,framelength):
        backgrounds = [f'BG0{str(x)}' for x in list(self.stim.unique_nr['BG'])]
        different_trials = ["_".join(items) for items in itertools.product(self.sf ,self.dur,self.match,self.stair,backgrounds)]
        different_trials.extend(["_".join(items) for items in itertools.product(['control'],self.match,self.stair,backgrounds)])
        self.conditionlist = ["_".join(items) for items in itertools.product(self.sf ,self.dur)]
        self.conditionlist.extend(['control'])
        # make this a dictionary
        self.trial_list = {}
        for key in different_trials:
            self.trial_list[key] = []
        matchingcond = {'same' : self.stim.same_list,
                        'diff' : self.stim.diff_list}     
       
        for SF in self.sf:
            for dur in self.dur:
                ImFrame = int(int(dur)/framelength)
                condname = f'{SF}_{dur}'
                masking = 1
                self.makelist(matchingcond, backgrounds, ImFrame, condname, SF, dur, masking)
        condname = 'control'
        SF = ''
        dur = 200 ##################changed
        ImFrame = nframes(dur,framelength) ##################changed
        masking = 0
        self.makelist(matchingcond, backgrounds, ImFrame, condname, SF, dur, masking)
                
    def makelist(self, matchingcond, backgrounds, ImFrame, condname, SF, dur, masking):           
        for whichid in range(self.maxCeleb): # loop through ID's
            for trialtype in self.match: # same or different trial                        
                triallist = matchingcond[trialtype]
                for bgnr,backgroundnr in enumerate(backgrounds):
                    for cmb,combi_per_id in enumerate(triallist[whichid]):
                        #all possible combinations per ID
                        for stair in self.stair: #two staircases per condition
                            trial_name = f'{condname}_{trialtype}_{stair}_{backgroundnr}' # trial type name
                            num1 = round(random.random())
                            if num1 == 0: # randomise which image is presented as image1
                                num2 = 1 # making sure image 2 is the other image... :)
                            else:
                                num2 = 0
                            if condname == 'control': #ugly coded, because late minute added to experiment
                                maskname1 = 'grey.bmp'
                                maskname2 = 'grey.bmp'
                                maskname3 = 'grey.bmp'
                                maskname4 = 'grey.bmp'
                                duration = 200 ##################changed
                            else:
                                maskname1 = f'{combi_per_id[num1][:-5]}1_{SF}.bmp'
                                maskname2 = f'{combi_per_id[num1][:-5]}2_{SF}.bmp'
                                maskname3 = f'{combi_per_id[num1][:-5]}3_{SF}.bmp'
                                maskname4 = f'{combi_per_id[num1][:-5]}4_{SF}.bmp'
                                duration = dur ##################changed
                            # trial_list will be a dictionary with 24 keys
                            # the conditions are SF*duration (2*3 = 6 in the example)
                            # this is doubled to have the same/diff conditions for the matching task (2*6 = 12)
                            # this is doubled because there are 2 staircases per condition (2*12 = 24)
                            self.trial_list[trial_name].append({
                                'session' : [],
                                'block' : [],
                                'trialno' : 0,
                                'stim1' : combi_per_id[num1],
                                'stim2' : combi_per_id[num2],
                                'matching' : trialtype,
                                'mask1' : maskname1,
                                'mask2' : maskname2,
                                'mask3' : maskname3,
                                'mask4' : maskname4,
                                'duration' : duration,
                                'condition' : condname,
                                'nframes' : ImFrame,
                                'SF' : SF,
                                'background' : f'{backgroundnr}.bmp',
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
            #mini_blocks = [] ############################################# changing the miniblocks to shuffle big blocksgfdfs
            name = f'block-{bblock+1}'
            backrgoundnr = f'BG0{bblock+1}'
            for idx,cond in enumerate(self.conditionlist):
                #tempblock=[]
                for stairnr in self.stair:
                    # for every mini block, grab 8 unique trials.. and go on to the next trial
                    for trial in range(int((trials_per_block/len(self.stair))/2)): # 8 (4same/4diff) trials of one condition per block
                        for matchit in self.match:
                            trial2add = copy.deepcopy(self.trial_list[f'{cond}_{matchit}_{stairnr}_{backrgoundnr}'][trial*(idx+1)])
                            #trial2add['mask'] = trial2add["mask"]
                            tempblock.append(trial2add)                   
                rnd.shuffle(tempblock)
                stair['trials'] = tempblock
                tempblock=[]
                mini_blocks[cond] = copy.deepcopy(stair)               
                #mini_blocks.extend(copy.deepcopy(tempblock))
            #shuffeling the mini block order
            #random.shuffle(mini_blocks)
            #blocklist[name] = mini_blocks
            keys = list(mini_blocks.keys())
            random.shuffle(keys)
            shuffled_miniblocks = dict()
            for key in keys:
                shuffled_miniblocks.update({key: mini_blocks[key]})
            blocklist[name] = shuffled_miniblocks            
        #shuffeling the big block order
        bkeys = list(blocklist.keys())
        random.shuffle(bkeys)
        shuffled_bigblocks = dict()
        for key in bkeys:
            shuffled_bigblocks.update({key: blocklist[key]})
        self.blocks = shuffled_bigblocks


    def prepare_staircare(self,nTrials,signal_start,steps,steptype,nUp,nDown,minVal,maxVal):
        #preallocating for the staircases
        self.staircases = {}
        for cond in self.conditionlist:
            self.staircases[cond] = {}
            #self.blocks['block-1'][cond][f'stair-1'] = makePsi(nTrials,signal_start,signal_end,steps,thresholdPrior1)
            #self.blocks['block-1'][cond][f'stair-2'] = makePsi(nTrials,signal_start,signal_end,steps,thresholdPrior2)
            self.staircases[cond]['stair-1'] = data.StairHandler(startVal = signal_start,
                                                                         stepType = steptype, stepSizes=steps,
                                                                         nUp=nUp, nDown=nDown,  # will home in on the 80% threshold
                                                                         nTrials=nTrials,
                                                                         minVal=minVal,maxVal=maxVal)
            self.staircases[cond]['stair-2'] = data.StairHandler(startVal = signal_start,
                                                                         stepType = steptype, stepSizes=steps,
                                                                         nUp=nUp, nDown=nDown,  # will home in on the 80% threshold
                                                                         nTrials=nTrials,
                                                                         minVal=minVal,maxVal=maxVal)           
            
              
        

 # =============================================================================       
  