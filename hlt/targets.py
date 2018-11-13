#!/usr/bin/env python3
# Python 3.6

import time
import pickle
import numpy as np
import traceback
import sys
import logging

def generate_targets(game):
    me = game.me
    game_map = game.game_map
    #TO ANYONE USING THIS, BE AWARE THE AXES GET SWAPPED DURING THE CONVERSION TO AND FROM NUMPY ARRAYS
    a = np.asarray(game_map._cells) #bad idea to use single letter variables.
    #again, probably shouldnt have used b
    b = np.asarray([i.halite_amount for i in a.flatten()]) # makes a list of all halite amounts. 
                                                       #Reshape with a.shape
    b = b.reshape(a.shape) #Take the flat array and make it a square again.
    # I think that is where the X and Y get swapped?
    #Calculate and assign distance home to a numpy array 
    d = np.asarray([ game_map.calculate_distance( i.position , me.shipyard.position) for i in a.flatten()])
    d = d.reshape(a.shape)
    dd = d*2
    v = b / (dd + 8 )
    val = v
    sorted_array = np.dstack(np.unravel_index(np.argsort(np.array(val).ravel()), np.array(val).shape))\
    .reshape(len(val.ravel()), 2) 
    # a 2D array of the indexes for squares from least to highest heuristic "value"
    correct_array= np.fliplr(sorted_array) # workaround for the flipping issue. Takes 0.04 miliseconds
    priority_list = list(correct_array)
    return priority_list


def returning_value(ship, game):
    '''The per-turn value of this ship if we decide to send it home now'''    
    game_map = game.game_map
    distance = game_map.calculate_distance(ship.position, game.me.shipyard.position)
    if distance == 0:
       return 0
    value = (ship.halite_amount/ distance) - (distance * 0.1*game_map[ship.position].halite_amount)
    # (distance * 0.1*game_map[ship.position) is an estimation of travel cost based on current cell value
    # it isn't a great estimate of travel cost, but it will skew value LOW for high value cells
    # which is what we want
    return value

def mining_value(ship, game):
    game_map = game.game_map
    distance = game_map.calculate_distance(ship.position, game.me.shipyard.position)
    if distance == 0:
        return 0
    future_halite = ship.halite_amount + 0.25*game_map[ship.position].halite_amount
    value = (future_halite / (distance+1)) - (distance * 0.075*game_map[ship.position].halite_amount)
    #discounted travel cost because we will pay less after having mined for a turn
    return value
