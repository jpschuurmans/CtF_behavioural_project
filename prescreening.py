# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 21:29:25 2022

@author: Adminuser
"""


# showing all 4 images of each actor
# if 4 images are recognized then put the actors in a list and take 10 randomly ? 

#%% ===========================================================================
#Instructions
instructiontexts = load_txt_as_dict(f'{base_path}instructions_{language}.txt')

textpage = visual.TextStim(win, height=32, font="Palatino Linotype", alignHoriz='center', wrapWidth=scrsize[0])

for text in list(instructiontexts.items())[:4]:  
    if text[0] == 'text1':
        fix_cross.draw()
    instructions = textpage
    instructions.text = text[1]
    instructions.draw()
    win.flip()
    keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
    escape_check(keys,win,f)
win.flip(clearBuffer=True)
core.wait(1)
mouse= event.Mouse(visible = True, win = win)

#%% ===========================================================================

def presceen_trials(base_path,exp_info):
    # prescreening to select celeberties welknown to the subject
    # Subject must judge if they recognise all 4 images of each celeberty 
    # if 4 images are recognized then put the celeberties in a list and take 10 randomly   

    stim_path = f'{base_path}stimuli/'
    data_path = f'{base_path}data/' 

    actors_fname = os.path.join(data_path, exp_info['1. subject'] + '_actors') #define file name
    prestim = Stimuli(f'{stim_path}prescreening/') # prestim.list = all stim (list with all all stim)
    
    # returns list with unique dr of IDs or IMs self.unique_nr
    prestim.getuniquenr('ID') # prestim.unique_nr
    prestim.getuniquenr('IM')
    
    
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
        celeb_id = int(image.rsplit('ID')[1][0:2])
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
            tempID.remove(celeb_id)
        rand_celebs = random.sample(list(np.unique(tempID)) , 4)
        for randnr,rand in enumerate(rand_celebs):
            tempID.remove(rand)
            celeb_info[f'rand{randnr}_name'] = celeb_list[str(rand_celebs[randnr])]
            celeb_info[f'rand{randnr}_pos'] = Rand_pos[randnr]
        prescreen_trials[f'trial{trialnum}'] = celeb_info
    
    l = list(prescreen_trials.items())
    random.shuffle(l)
    prescreen_trials = dict(l)
    
    return prescreen_trials, celeb_list

#%% ===========================================================================
# prescreening exp
answertext = {}
answerbox = {}
for answer in range(6):
    answertext[f'rand{answer}'] = visual.TextStim(win, height=32, font="Palatino Linotype", color = "black")
    answerbox[f'rand{answer}'] = visual.Rect(win, width = 350, height = 100, lineColor = "black", lineWidth = 3)
   
foundIm = []
#Pretest
for prescstim in prescreen_trials:
    loginfo = f"{exp_info['1. subject']}, {prescstim}"
    for text in prescreen_trials[prescstim]:
        loginfo = f"{loginfo}, {prescreen_trials[prescstim][text]}"
    
    print(prescreen_trials[prescstim])
    prescreen.setImage(prestim.path + prescreen_trials[prescstim]['im_path'])
    prescreen.pos=(0, 0)
    prescreen.draw()
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
            if language == 'en':
                answertext[answers].text = "I don't know"
            else:
                answertext[answers].text = "Je ne sais pas"
            answerbox[answers].fillColor = "white"
            answerbox[answers].opacity = .2
        else:
            answertext[answers].text = prescreen_trials[prescstim][f'rand{ans_num}_name']
            answertext[answers].pos = prescreen_trials[prescstim][f'rand{ans_num}_pos']
        answertext[answers].draw()
        answerbox[answers].pos = tuple(answertext[answers].pos)
        answerbox[answers].draw()
    win.flip()
    escape_check(keys,win,f)
    
    #measure responses
    timer.reset()
    Ans = False
    
    while Ans == False:
        if mouse.getPressed() [0]==1:
            mousepos = mouse.getPos()
            Ans = True
            time = timer.getTime()  
            
            #print(mousepos)
            #check if subject gave correct answer
            for answers in answerbox:
                if answerbox[answers].contains(mousepos):
                    if answers == 'rand4':
                        answer_celeb = prescreen_trials[prescstim]['im_name']
                        correct = 1
                        foundIm.append(answer_celeb)
                    elif answers == 'rand5':
                        answer_celeb = 'idk'
                        correct = 0
                    else:
                        answer_celeb = prescreen_trials[prescstim][f'{answers}_name']
                        correct = 0
    print(answer_celeb)               
    toSave = f"{loginfo}, {answer_celeb}, {mousepos}, {str(correct)}, {str(time)}\n"
    f.write(toSave)
    win.flip()
    #win.flip(clearBuffer=True)
    win.flip()
    core.wait(0.5)
    event.clearEvents()
    mouse.clickReset() 
                
                
def select_recognised_celebs(base_path,foundIm):
    celeb_list = load_txt_as_dict(f'{base_path}celeb_names.txt')
    
    FinalList = []
    FinalList3 = []
    
    #select all celebs that are recognised in all 4 photos
    for num in celeb_list:
        celeb = [im for im in foundIm if celeb_list[num] in im]
        if len(celeb) == 4:
            FinalList.append(celeb_list[num])
    # of not all photos are recognised, select them where 3 photos were.
    if len(FinalList) < 10:
        miss = 10 - len(FinalList)
        for num in celeb_list:
            actor = [im for im in foundIm if celeb_list[num] in im]
            if len(actor) == 3:
                FinalList3.append(celeb_list[num])
        final_actor_list = random.sample(FinalList, len(FinalList))
        for i in range(miss):
            l = random.sample(FinalList3, miss)
            final_actor_list.append(l[i])            
    else:    
        final_actor_list = random.sample(FinalList, 10)    
        
    return final_actor_list
    
final_actor_list = select_recognised_celebs(base_path,foundIm)

if len(final_actor_list) < 10:        
    textpage.text  = 'Not enough actors recognised..\nContact experimenter svp' 
    textpage.draw()
    win.flip()
    
    keys = event.waitKeys(keyList=['space','escape'])#core.wait(.1)
    escape_check(keys,win,f)

------------------------------------------------
with open(actors_fname, 'wb') as pickle_file:
    pickle.dump(Final_Rand, pickle_file)    
    
    
    
f.close()
win.close()