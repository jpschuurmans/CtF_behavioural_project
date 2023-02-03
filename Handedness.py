# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 09:13:49 2020

@author: Neper
"""



#===============
# Import modules
#===============

from psychopy import gui


exp_name = 'Handedness Edinburgh'
quest = {
    'Writing': ('Always left', 'Usually left', 'Both equally', 'Usually right', 'Always right'),
    'Drawing': ('Always left', 'Usually left', 'Both equally', 'Usually right', 'Always right'),
    'Throwing': ('Always left', 'Usually left', 'Both equally', 'Usually right', 'Always right'),
    'Using Scisors': ('Always left', 'Usually left', 'Both equally', 'Usually right', 'Always right'),
    'Using a Toothbrush': ('Always left', 'Usually left', 'Both equally', 'Usually right', 'Always right'),
    'Using a Knife (without a fork)': ('Always left', 'Usually left', 'Both equally', 'Usually right', 'Always right'),
    'Using  Spoon': ('Always left', 'Usually left', 'Both equally', 'Usually right', 'Always right'),
    'Using a Broom (upper hand)': ('Always left', 'Usually left', 'Both equally', 'Usually right', 'Always right'),
    'Stricking a Match': ('Always left', 'Usually left', 'Both equally', 'Usually right', 'Always right'),
    'Opening a Box (holding the Lid)': ('Always left', 'Usually left', 'Both equally', 'Usually right', 'Always right'),
    }

dlg = gui.DlgFromDict(dictionary=quest, title=exp_name, sortKeys=False)


# If 'Cancel' is pressed, quit
if dlg.OK == False:
    core.quit()
        

#variables
abspos = 0
absneg = 0
quotient = 0

#Score
valeur = {
    'Always left': -2,
    'Usually left': -1,
    'Both equally': 0,
    'Usually right': 1,
    'Always right': 2
    }

"""The laterality quotient (LQ) uses the answers to all the questions. 
The LQ can take values from -100 to 100, and is calculated by taking the sum of 
all positive answers subtracting the sum of absolute values of the negative answers, 
divided by the sum of both, and multiplied by 100"""

for n in quest:
    for i in valeur:
        if i == quest[n]:
           # print (str(i) + str(valeur [i]) + str(quest[n]))
            if valeur[i] < 0:
                absneg += abs(valeur[i])
              #  print (absneg)
            else:
                abspos += abs(valeur[i])
                #print (abspos)

quotient = round(( abspos - absneg ) / (abspos + absneg ) * 100)

if quotient < -50:
    print ("Quotient =" + str(quotient) + ", left domiance")
elif quotient < 0:
    print ("Quotient =" + str(quotient) + ", left preference")
elif quotient < 50:
    print ("Quotient =" + str(quotient) + ", right preference")
else:
    print ("Quotient =" + str(quotient) + ", right dominance")




