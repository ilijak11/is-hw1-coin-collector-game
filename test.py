import config
import os
import itertools
import time

def load_map(map_name):
    try:
        with open(map_name, 'r') as f:
            ax, ay = [int(val) for val in f.readline().strip().split(',')[:2]]
            coin_distance = [[0]]
            ident = 1
            while True:
                line = f.readline().strip()
                if not len(line):
                    break
                values = [int(val) for val in line.split(',')]
                ident += 1
                for iteration, coin_sublist in enumerate(coin_distance):
                    coin_sublist.append(values[2 + iteration])
                coin_distance.append(values[2:2 + len(coin_distance)] + [0])
            return (ax, ay), coin_distance
    except Exception as e:
        raise e


class AkiTest():
    def __init__(self):
        super().__init__()

    def get_next(self, dist_vect, visited_nodes):
        #dist_vect -> list
        #visited_nodes -> curr_path

        #min == last
        min = 0xffffffff
        next = -1
        print('/////////////////')
        for ind, val in reversed(list(enumerate(dist_vect))):
           print(ind, val)
        print(visited_nodes)
        for ind, val in reversed(list(enumerate(dist_vect))):
            print(ind, val, min)
            if val != 0 and val <= min and ind not in visited_nodes:
                min = val
                next = ind

        print('min=', min)
        print('next=',next)
        print('/////////////////')
        
        return next

    def get_agent_path1(self, coin_distance):
        path = [0]
        cost = 0
        curr_pos = 0 #start
        print('-----------------')
        while len(path) < len(coin_distance):
            print(coin_distance[curr_pos])
            next = self.get_next(coin_distance[curr_pos], path)
            cost += coin_distance[curr_pos][next]
            path.append(next)
            print(path)
            print('-----------------')
            curr_pos = next
        
        cost += coin_distance[curr_pos][0]
        path.append(0)
        print(cost)
        return path

    def get_agent_path(self, coin_distance):
        start_coin = {
            'ind' : 0,
            'cost' : 0
        }
        pqueue = [start_coin]
        curr_coin = None
        path = []
        cost = 0
        while len(path) < len(coin_distance):
            curr_coin = pqueue.pop(0)
            path.append(curr_coin['ind'])
            cost += curr_coin['cost']
            pqueue = [ {
                'ind' : ind,
                'cost' : cost
            } for ind, cost in enumerate(coin_distance[curr_coin['ind']]) if ind not in path]
            pqueue.sort(key = lambda x : (x['cost'], x['ind']))

        path.append(0)
        cost += coin_distance[curr_coin['ind']][0]

        print(path)
        print(cost)

        return path

class JockeTest():
    def __init__(self):
        super().__init__()

    def calculate_path_cost(self, path, cost_matrix):
        cost = 0
        #cost from start to first
        cost += cost_matrix[0][path[0]]
        #cost from last to start
        cost += cost_matrix[path[-1]][0]

        for i in range(1, len(path)):
            cost += cost_matrix[path[i - 1]][path[i]]

        return cost
        

    def get_agent_path(self, coin_distance):
        #start
        best_path = []
        min_cost = -1
        all_paths = itertools.permutations(range(1, len(coin_distance)))
        for path in all_paths:
            cost = self.calculate_path_cost(path, coin_distance)
            if min_cost == -1:
                min_cost = cost
                best_path.append(path)
            else:
                if min_cost > cost:
                    min_cost = cost
                    best_path = []
                    best_path.append(path)
                elif min_cost == cost:
                    best_path.append(path)
                else: 
                    pass
            
        print(best_path)
        print(min_cost)

        return [0] + [i for i in best_path[0]] + [0]


class UkiTest():
    def __init__(self):
        super().__init__()


    def get_agent_path(self, coin_distance):
        # data struct touple {
        #                      0 -> ind, 
        #                      1 -> cost, 
        #                      2 -> path
        #                     }
        start_coin = {
            'ind' : 0,
            'cost' : 0,
            'path' : [0]
        }
        pqueue = [start_coin]
        curr_coin = None
        while len(pqueue) != 0:
            curr_coin = pqueue.pop(0)
            if len(curr_coin['path']) == len(coin_distance) + 1:
                break
            if len(curr_coin['path']) == len(coin_distance):
                next_coin = {
                    'ind' : 0, 
                    'cost' : curr_coin['cost'] + coin_distance[curr_coin['ind']][0], 
                    'path' : curr_coin['path'] + [0]
                }
                pqueue.append(next_coin)
                continue
            #print(curr_coin)
            dist_vect = coin_distance[curr_coin['ind']]
            for ind, cost in list(enumerate(dist_vect)):
                #look only for coins that are not visited by current path
                if ind not in curr_coin['path']:
                    #get next coin
                    next_coin = {
                        'ind' : ind, 
                        'cost' : curr_coin['cost'] + cost, 
                        'path' : curr_coin['path'] + [ind]
                    }
                    # check if new coin is better then alrady existing coins (better cost and longer path)
                    #old_coin = next((coin for coin in pqueue if coin['ind'] == next_coin['ind']), None)
                    old_coins = [coin for coin in pqueue if coin['ind'] == next_coin['ind']]
                    #print("old coins", old_coins)
                    # if old_coin is not None and next_coin['cost'] <= old_coin['cost']:
                    #     # print('old: ', old_coin)
                    #     # print('new: ', next_coin)
                    #     old_ind = pqueue.index(old_coin)
                    #     pqueue[old_ind] = next_coin
                    # else: 
                    #     pqueue.append(next_coin)
                    if old_coins is not None:
                        for old_coin in old_coins:
                            if next_coin['cost'] <= old_coin['cost'] and len(next_coin['path']) > len(old_coin['path']):
                                pqueue.remove(old_coin)
                        
                    pqueue.append(next_coin)
            
            #sotr queue
            pqueue.sort(key = lambda x :
                #sort order: cost, path(len), ind 
                (x['cost'], len(coin_distance) - len(x['path']), x['ind'])
            )

        path = curr_coin['path']
        cost = curr_coin['cost']

        print(path)
        print(cost)

        return path

        
class MickoTest():

    def __init__(self):
        super().__init__()

    def sort_edges(self, coins, coin_distance):
        sorted = []
        edges = itertools.combinations(coins, 2)
        for e in edges:
            sorted.append((e[0], e[1], coin_distance[e[0]][e[1]]))

        #sort by cost
        sorted.sort(key = lambda x : x[2])
        return sorted



    def get_mst_cost(self, coins, coin_distance):
        if len(coins) <= 1:
            return 0

        print(coins)
        pqueue = self.sort_edges(coins, coin_distance)
        #print(pqueue)

        coin_groups = {}
        for c in coins:
          coin_groups[c] = -1
        
        added_edges = 0
        mst = []
        mst_cost = 0
        curr_group = 1
        while added_edges != len(coins) - 1:
            min_edge = pqueue.pop(0)
            #edge nos assigned
            #print(coin_groups)
            if coin_groups[min_edge[0]] == -1 and coin_groups[min_edge[1]] == -1:
                coin_groups[min_edge[0]] = curr_group
                coin_groups[min_edge[1]] = curr_group
                curr_group += 1

            elif coin_groups[min_edge[0]] != -1 and coin_groups[min_edge[1]] == -1:
                coin_groups[min_edge[1]] = coin_groups[min_edge[0]]

            elif coin_groups[min_edge[0]] == -1 and coin_groups[min_edge[1]] != -1:
                coin_groups[min_edge[0]] = coin_groups[min_edge[1]]
            
            elif coin_groups[min_edge[0]] != -1 and coin_groups[min_edge[1]] != -1 and coin_groups[min_edge[0]] != coin_groups[min_edge[1]]:
                group1 = coin_groups[min_edge[0]]
                group2 = coin_groups[min_edge[1]]
                for coin, group in coin_groups.items():
                    if group == group1:
                        coin_groups[coin] = group2
            else:
                continue

            mst_cost += min_edge[2]
            mst.append(min_edge)
            added_edges += 1
        
        #print(coin_groups)
        #print(mst)
        print(mst_cost)
        return mst_cost


    def get_agent_path(self, coin_distance):
        # data struct touple {
        #                      0 -> ind, 
        #                      1 -> cost, 
        #                      2 -> path
        #                     }
        start_coin = {
            'ind' : 0,
            'cost' : 0,
            'heur' : 0,
            'path' : [0]
        }
        pqueue = [start_coin]
        curr_coin = None
        while len(pqueue) != 0:
            curr_coin = pqueue.pop(0)
            if len(curr_coin['path']) == len(coin_distance) + 1:
                break
            if len(curr_coin['path']) == len(coin_distance):
                next_coin = {
                    'ind' : 0, 
                    'cost' : curr_coin['cost'] + coin_distance[curr_coin['ind']][0], 
                    'heur' : 0,
                    'path' : curr_coin['path'] + [0]
                }
                pqueue.append(next_coin)
                continue
            print(curr_coin)
            print('---------------------')
            dist_vect = coin_distance[curr_coin['ind']]
            for ind, cost in list(enumerate(dist_vect)):
                #look only for coins that are not visited by current path
                if ind not in curr_coin['path']:
                    #get next coin
                    heur = self.get_mst_cost([i for i in range(1, len(coin_distance)) if i not in curr_coin['path']] + [0], coin_distance)
                    next_coin = {
                        'ind' : ind, 
                        'cost' : curr_coin['cost'] + cost, 
                        'heur' : heur,
                        'path' : curr_coin['path'] + [ind]
                    }
                    print(next_coin)
                    # check if new coin is better then alrady existing coins with
                    #old_coin = next((coin for coin in pqueue if coin['ind'] == next_coin['ind']), None)
                    old_coins = [coin for coin in pqueue if coin['ind'] == next_coin['ind']]
                    #print("old coins", old_coins)
                    # if old_coin is not None and next_coin['cost'] <= old_coin['cost']:
                    #     # print('old: ', old_coin)
                    #     # print('new: ', next_coin)
                    #     old_ind = pqueue.index(old_coin)
                    #     pqueue[old_ind] = next_coin
                    # else: 
                    #     pqueue.append(next_coin)
                    if old_coins is not None:
                        for old_coin in old_coins:
                            if next_coin['cost'] <= old_coin['cost'] and len(next_coin['path']) > len(old_coin['path']):
                                print('lol')
                                pqueue.remove(old_coin)
                    pqueue.append(next_coin)
                    
            print('---------------------')
            #sotr queue
            pqueue.sort(key = lambda x :
                #sort order: cost, path(len), ind 
                (x['cost'] + x['heur'], len(coin_distance) -  len(x['path']), x['ind'])
            )

        path = curr_coin['path']
        cost = curr_coin['cost']

        print(path)
        print(cost)

        return path





if __name__ == '__main__':
    pos, matrix = load_map(os.path.join(config.MAP_FOLDER, 'map0.txt')) 
    for lst in matrix:
        print(lst)

    agent = AkiTest()
    #agent.get_mst_cost([0,1,2,3], matrix)
    #print(agent.calculate_path_cost([1,4,3,2], matrix))
    s = time.time()
    path = agent.get_agent_path1(matrix)
    e = time.time()
    print("time: ", (e - s))
    print(path)