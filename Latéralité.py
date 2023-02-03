# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 09:13:49 2020

@author: Neper
"""



#===============
# Import modules
#=============== 

from psychopy import gui



exp_name = 'Latéralité Edinburgh'
quest = {
    'Ecrire': ('toujours à gauche', 'habituellement à gauche', 'sans préférence','habituellement à droite','toujours à droite'),
    'Dessiner': ('toujours à gauche', 'habituellement à gauche', 'sans préférence','habituellement à droite','toujours à droite'),
    'Lancer': ('toujours à gauche', 'habituellement à gauche', 'sans préférence','habituellement à droite','toujours à droite'),
    'Tenir une pair de ciseaux': ('toujours à gauche', 'habituellement à gauche', 'sans préférence','habituellement à droite','toujours à droite'),
    'Se brosser les dents': ('toujours à gauche', 'habituellement à gauche', 'sans préférence','habituellement à droite','toujours à droite'),
    'Tenir un couteau (sans fourchette)': ('toujours à gauche', 'habituellement à gauche', 'sans préférence','habituellement à droite','toujours à droite'),
    'Tenir une cuillère': ('toujours à gauche', 'habituellement à gauche', 'sans préférence','habituellement à droite','toujours à droite'),
    'Tenir un balai (main supérieure)': ('toujours à gauche', 'habituellement à gauche', 'sans préférence','habituellement à droite','toujours à droite'),
    'Allumer une allumetter (main tenant l\'allumette)': ('toujours à gauche', 'habituellement à gauche', 'sans préférence','habituellement à droite','toujours à droite'),
    'Ouvrir une boîte (main tenant le couvercle)': ('toujours à gauche', 'habituellement à gauche', 'sans préférence','habituellement à droite','toujours à droite')
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
    'toujours à gauche': -2,
    'habituellement à gauche': -1,
    'sans préférence': 0,
    'habituellement à droite': 1,
    'toujours à droite': 2
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
    print ("Quotient =" + str(quotient) + ", gaucher pur")
elif quotient < 0:
    print ("Quotient =" + str(quotient) + ", gaucher mixte")
elif quotient < 50:
    print ("Quotient =" + str(quotient) + ", droitier mixte")
else:
    print ("Quotient =" + str(quotient) + ", droitier pur")




