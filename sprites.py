import math
import random

import pygame
import os
import config
import itertools


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name, transparent_color=None, wid=config.SPRITE_SIZE, hei=config.SPRITE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (wid, hei))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Surface(BaseSprite):
    def __init__(self):
        super(Surface, self).__init__(0, 0, 'terrain.png', None, config.WIDTH, config.HEIGHT)


class Coin(BaseSprite):
    def __init__(self, x, y, ident):
        self.ident = ident
        super(Coin, self).__init__(x, y, 'coin.png', config.DARK_GREEN)

    def get_ident(self):
        return self.ident

    def position(self):
        return self.rect.x, self.rect.y

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class CollectedCoin(BaseSprite):
    def __init__(self, coin):
        self.ident = coin.ident
        super(CollectedCoin, self).__init__(coin.rect.x, coin.rect.y, 'collected_coin.png', config.DARK_GREEN)

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.RED)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, x, y, file_name):
        super(Agent, self).__init__(x, y, file_name, config.DARK_GREEN)
        self.x = self.rect.x
        self.y = self.rect.y
        self.step = None
        self.travelling = False
        self.destinationX = 0
        self.destinationY = 0

    def set_destination(self, x, y):
        self.destinationX = x
        self.destinationY = y
        self.step = [self.destinationX - self.x, self.destinationY - self.y]
        magnitude = math.sqrt(self.step[0] ** 2 + self.step[1] ** 2)
        self.step[0] /= magnitude
        self.step[1] /= magnitude
        self.step[0] *= config.TRAVEL_SPEED
        self.step[1] *= config.TRAVEL_SPEED
        self.travelling = True

    def move_one_step(self):
        if not self.travelling:
            return
        self.x += self.step[0]
        self.y += self.step[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if abs(self.x - self.destinationX) < abs(self.step[0]) and abs(self.y - self.destinationY) < abs(self.step[1]):
            self.rect.x = self.destinationX
            self.rect.y = self.destinationY
            self.x = self.destinationX
            self.y = self.destinationY
            self.travelling = False

    def is_travelling(self):
        return self.travelling

    def place_to(self, position):
        self.x = self.destinationX = self.rect.x = position[0]
        self.y = self.destinationX = self.rect.y = position[1]

    # coin_distance - cost matrix
    # return value - list of coin identifiers (containing 0 as first and last element, as well)
    def get_agent_path(self, coin_distance):
        pass


class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        random.shuffle(path)
        return [0] + path + [0]


class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        random.shuffle(path)
        print(path)
        return [0] + path + [0]

#my agents


class Aki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

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

class Jocke(Agent):

    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

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
        best_path = None
        min_cost = -1
        all_paths = itertools.permutations(range(1, len(coin_distance)))
        for path in all_paths:
            cost = self.calculate_path_cost(path, coin_distance)
            if min_cost == -1:
                min_cost = cost
                best_path = path
            else:
                if min_cost > cost:
                    min_cost = cost
                    best_path = path
            
        best_path = [0] + [i for i in best_path] + [0]
        print(best_path)
        print(min_cost)

        return best_path
    

class Uki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)


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
                    # check if new coin is better then alrady existing coins (better cost, loner path)
                    old_coins = [coin for coin in pqueue if coin['ind'] == next_coin['ind']]
                    if old_coins is not None:
                        for old_coin in old_coins:
                            if next_coin['cost'] <= old_coin['cost'] and len(next_coin['path']) > len(old_coin['path']):
                                pqueue.remove(old_coin)

                    pqueue.append(next_coin)
            
            #sotr queue
            pqueue.sort(key = lambda x :
                #sort order: cost, path(len), ind 
                (x['cost'], len(coin_distance) -  len(x['path']), x['ind'])
            )

        path = curr_coin['path']
        cost = curr_coin['cost']

        print(path)
        print(cost)

        return path

class Micko(Agent):

    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

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

        pqueue = self.sort_edges(coins, coin_distance)

        coin_groups = {}
        for c in coins:
          coin_groups[c] = -1
        
        added_edges = 0
        mst_cost = 0
        curr_group = 1
        while added_edges != len(coins) - 1:
            min_edge = pqueue.pop(0)
            #edge nos assigned
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
            added_edges += 1
        
        #print(coin_groups)
        #print(mst_cost)
        return mst_cost


    def get_agent_path(self, coin_distance):
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
            # print(curr_coin)
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
                    # check if new coin is better then alrady existing coins (better cost, loner path)
                    old_coins = [coin for coin in pqueue if coin['ind'] == next_coin['ind']]
                    if old_coins is not None:
                        for old_coin in old_coins:
                            if next_coin['cost'] <= old_coin['cost'] and len(next_coin['path']) > len(old_coin['path']):
                                pqueue.remove(old_coin)

                    pqueue.append(next_coin)
            
            #sotr queue
            pqueue.sort(key = lambda x :
                #sort order: cost + heur, path(len), ind 
                (x['cost'] + x['heur'], len(coin_distance) -  len(x['path']), x['ind'])
            )

        path = curr_coin['path']
        cost = curr_coin['cost']

        print(path)
        print(cost)

        return path




