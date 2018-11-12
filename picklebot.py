#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import time
import hlt
import pickle
import numpy as np
import traceback
import sys
# This library contains constant values.
from hlt import constants
# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction, Position
# This library allows you to generate random numbers.
import random
# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging
""" <<<Game Begin>>> """
game = hlt.Game()
me = game.me
start_time = time.process_time()
game_map = game.game_map

with open('maplist.p','wb') as f:
    pickle.dump(game_map._cells, f)
    logging.info('pickledumped list')

#TO ANYONE USING THIS, BE AWARE THE AXES GET SWAPPED DURING THE CONVERSION TO AND FROM NUMPY ARRAYS
a = np.asarray(game_map._cells) #bad idea to use single letter variables.
#again, probably shouldnt have used b
b = np.asarray([i.halite_amount for i in a.flatten()]) # makes a list of all halite amounts. 
                                                       #Reshape with a.shape
logging.info('Calculate halite amount array')
logging.info(b)
b = b.reshape(a.shape) #Take the flat array and make it a square again.
# I think that is where the X and Y get swapped?
logging.info('reshaped b {} b[0,0] = {}'.format(b.shape, b[0,0]))
np.savetxt('halite_amount.csv', b, fmt='%-2.2d', delimiter=',')

#Calculate and assign distance home to a numpy array 
d = np.asarray([ game_map.calculate_distance( i.position , me.shipyard.position) for i in a.flatten()])
d = d.reshape(a.shape)
logging.info('Calculated and reshaped distance home for each cell')
logging.info(d)
np.savetxt('distancehome.csv', d, fmt='%-2.2d', delimiter=',')

#now lets calculate the per-turn value of every cell
#the heuristic I have decided to use is halite_amt / (2distance_home + 8)
# 8 turns mines 90% of halite in a cell. for high value cells this is alright.
# might want to reconsider for lower value cells at some point
dd = d*2 #probably not necessary but I don't want to have to worry about order of operations
v = b / (dd + 8 )
logging.info('Calculated per-turn value of each cell')
np.savetxt('mining-value.csv', d, fmt='%-2.4f', delimiter=',')
logging.info('Max value {}, min value {} mean value {}'.format(
v.max(), v.min(), v.mean()))
val = v #single character names are probably bad I should stop doing this
#values_list = list(v.flatten())
#logging.info(sorted(values_list)) #to dispactch ships to high value cells use pop()

sorted_array = np.dstack(np.unravel_index(np.argsort(np.array(val).ravel()), np.array(val).shape)).reshape(len(val.ravel()), 2) # a 2D array of the indexes for squares from least to highest "value"

priority_list = list(sorted_array) #So I can use priority_list.pop() to get a target to go after
#Right now I'm havig an issue where X and Y are flipped here. Trying to debug
#how to get a target: target_= priority_list.pop()
#target_1 = Position(*target_1[::-1]) 
# [::-1] returns a reversed view of the numpy array
# This effectively Swaps X and Y back so I don't have to figure out how they got swapped in the first palce

finish_time = time.process_time()
elapsed_time = finish_time - start_time
logging.info ('setup took {} seconds'.format(elapsed_time))
game.ready("PickleBot")
# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))
""" <<<Game Loop>>> """
assignments = {}
while True:
    #Begin turn loop here
    game.update_frame()
    me = game.me
    game_map = game.game_map
    command_queue = []

    for ship in me.get_ships():
        if ship.id in assignments:
            if ship.is_full:
               assignments[ship.id] = me.shipyard.position
            command_queue.append(
            ship.move(
            game_map.greedy_navigate(ship, game_map[assignments[ship.id]])
            ))
        else:
            target = priority_list.pop()
            target = Position(*target[::-1])        
            assignments[ship.id] = target
            command_queue.append(ship.move(game_map.greedy_navigate(ship, game_map[target])))

    if len(me.get_ships()) < 1:
        command_queue.append(me.shipyard.spawn())
    game.end_turn(command_queue)

