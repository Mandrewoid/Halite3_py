#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import time
import hlt
import pickle
import numpy as np
# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()

start_time = time.process_time()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game_map = game.game_map
#logging.info(game_map._cells)
with open('maplist.p','wb') as f:
    pickle.dump(game_map._cells, f)
    logging.info('pickledumped list')

with open('shipyard.p', 'wb') as f:
    me = game.me
    pickle.dump(me,f)
logging.info(me)

a = np.asarray(game_map._cells)
#probably shouldnt have used b
b = np.asarray([i.halite_amount for i in a.flatten()]) # makes a list of all halite amounts. 
                                                       #Reshape with a.shape
logging.info('Calculate halite amount array')
logging.info(b)
b = b.reshape(a.shape)
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
dd = d*2 #probably not necessary but I don't want any orderof operations issues
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






finish_time = time.process_time()
elapsed_time = finish_time - start_time
logging.info ('setup took {} seconds'.format(elapsed_time))
game.ready("PickleBot")


assignment_dict = {} # here we will store what ships are assigned to what squares
lookahead_set = set() # use a set because checking for presence is a set is faster






# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:
    #Begin turn loop here
    game.update_frame()
    me = game.me
    game_map = game.game_map
    command_queue = []

    for ship in me.get_ships():
        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        command_queue.append(ship.stay_still())
    game.end_turn(command_queue)

