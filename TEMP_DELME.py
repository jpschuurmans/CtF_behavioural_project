# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 11:45:03 2022

@author: Adminuser
"""
unique_back = back.unique_nr['BG']
import copy
        background_numbers = np.repeat(unique_back, int(np.ceil(n_bigblock/np.size(unique_back))))
        np.random.shuffle(background_numbers)
        mini_blocks = {}
        stair = {}
        tempblock=[]
        blocklist = {}
        for bblock in range(n_bigblock):
            name = f'block-{bblock+1}'
            for idx,cond in enumerate(alltrials.conditionlist):
                back_num = background_numbers[idx]
                for stairnr in alltrials.stair:
                    # for every mini block, grab 8 unique trials.. and go on to the next trial
                    for trial in range(int((trials_per_block/len(alltrials.stair))/2)): # 8 (4same/4diff) trials of one condition per block
                        for matching in alltrials.match:
                            
                            trial2add = copy.deepcopy(alltrials.trial_list[f'{cond}_{matching}_{stairnr}'][trial*(idx+1)])
                            trial2add['mask'] = f'BG0{back_num}_{trial2add["mask"]}'
                            trial2add['background'] = f'BG0{back_num}.bmp'
                            tempblock.append(trial2add)                   
                            print(trial2add['mask'])
                            trial2add = []
                rnd.shuffle(tempblock)
                stair['trials'] = tempblock
                tempblock=[]
                mini_blocks[cond] = stair
            blocklist[name] = mini_blocks
            #  blocklist[name][cond]['trials'][ii]['mask']
        #alltrials.blocks = blocklist