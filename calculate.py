import sys
import itertools

import numpy as np
import pandas as pd

def calc_sal_ranges(num_players, max_salary):
    return np.array(list(range(3500*num_players, max_salary+100, 100)))

def combine_single_position(position, num_players, max_salary, df):
    posdf = df[df.pos == position]
    posdf_indicies = posdf.index.values
    points = posdf['pts'].values
    sals = posdf['sal'].values

    #splitting the data fram into the necessary fields
    ids_comb = np.array(list(itertools.combinations(posdf_indicies, num_players)))
    points_comb = np.array(list(itertools.combinations(points, num_players)))
    sal_comb = np.array(list(itertools.combinations(sals, num_players)))

    sal_ranges = calc_sal_ranges(num_players, max_salary)

    return restrict_and_merge(ids_comb, points_comb, sal_comb, sal_ranges)

def combine_multiple_positions(pos1, pos2, max_salary):

    #pos1 varaibles don't have a 1 at the end, pos 2 variables do at the beginning

    _, ids, points, sals = pos1
    _, ids2, points2, sals2 = pos2

    _, inds = np.unique(points, return_index=True)
    _, inds2 = np.unique(points2, return_index=True)

    #shrinking the data to remove repeats. Again, we're wanting to keep them all the same length
    #so the same ids reference the correct data
    shrunk_sals = sals[inds]
    shrunk_sals2 = sals2[inds2]
    shrunk_points = points[inds]
    shrunk_points2 = points2[inds2]
    shrunk_ids = ids[inds]
    shrunk_ids2 = ids2[inds2]

    #combine the status using the product
    sals_comb = np.array(list(itertools.product(shrunk_sals, shrunk_sals2)))
    points_comb = np.array(list(itertools.product(shrunk_points, shrunk_points2)))
    ids_comb = np.array([ np.concatenate((x,y)) for x,y in  list(itertools.product(shrunk_ids, shrunk_ids2))   ] )

    num_players = ids.shape[1] + ids2.shape[1]
    sal_ranges = calc_sal_ranges(num_players, max_salary)

    return restrict_and_merge(ids_comb, points_comb, sals_comb, sal_ranges)


def combine_all_positions(tops_array, max_salary):
    tops_array_len = len(tops_array)
    if tops_array_len == 1:
        return tops_array[0]
    else:
        half_len = tops_array_len // 2 #we want this non floating
        half1 = tops_array[:half_len]
        half2 = tops_array[half_len:]
        half1top = combine_all_positions(half1, max_salary)
        half2top = combine_all_positions(half2, max_salary)

        players_in_first = len(half1top[1][1])
        players_in_second = len(half2top[1][1])
        players_in_combo = players_in_first + players_in_second
        print('Players in combining combo:', players_in_combo)

        return combine_multiple_positions(half1top, half2top, max_salary)


def restrict_and_merge(ids_comb, points_comb, sal_comb, sal_ranges):

    player_combination_size, num_ids_size = ids_comb.shape
    sal_ranges_size = sal_ranges.size #used to know how big to make the arrays

    sal_ranges_full = np.broadcast_to(sal_ranges,(player_combination_size, sal_ranges_size)).T

    #creating an array where we add the sals together to get a 1d array
    sal_sum = sal_comb.sum(axis=1)
    points_sum = points_comb.sum(axis=1)

    sal_sum_full = np.broadcast_to(sal_sum,(sal_ranges_size, player_combination_size))
    #adding the points of the combinations and making them zero if the salary sum is
    #higher than the max_salary
    points_sum_full = np.broadcast_to(points_sum,(sal_ranges_size, player_combination_size))

    #used to snag the best players who've been selected
    ids_comb_full = np.broadcast_to(ids_comb, (sal_ranges_size, player_combination_size, num_ids_size))

    under_sal_limit = sal_sum_full <= sal_ranges_full

    calculated_points = points_sum_full * under_sal_limit

    #we're finding the max indicies
    #argmax() returns the index of the max value
    top_inds = calculated_points.argmax(axis=1)

    #now that we know the index of the maximum, we return the relevant info
    row_selectors = np.arange(sal_ranges_size)
    max_points = points_sum_full[row_selectors, top_inds]
    max_sals = sal_sum_full[row_selectors, top_inds]
    max_inds = ids_comb_full[row_selectors, top_inds]
    return sal_ranges, max_inds, max_points, max_sals

def solve(combo_positions_dict, max_salary, df):

    print(f'Solving with {max_salary}')
    tops={}
    for position, num_players in combo_positions_dict.items():
        print(f"Calculating initial positions for {position}")
        if num_players == 0:
            continue
        tops[position] = combine_single_position(position, num_players, max_salary, df)

    tops_array = [vals for pos, vals in tops.items()]
    return combine_all_positions(tops_array, max_salary)
