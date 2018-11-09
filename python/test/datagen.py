import random
import numpy as np
# Number of transactions 交易數量
D = 100000
# Average size of the transactions 交易的平均規模
T = 10
# Average size of the maximal potentially large itemsets 最大可能大物品集的平均大小
I = 4
# Number of maximal potentially large itemsets  最大可能大物品集的數量
L = 2000
# Number of items 物品的個數
N = 1000

trans_size = np.random.poisson(T)

items_pool = list(range(N))

itemsets = []

def random_pop(ls:list, k:int=1):
    nls = ls
    pop = []
    for _ in range(k):
        i = random.choice(nls)
        pop.append(i)
        nls.remove(i)
    return nls, pop

# for i in range(1, L):
#     itemset = {}
#     itemset['size'] = np.random.poisson(I)
#     items = []
#     for 
#     itemsets.append(itemset)

ls = list(range(10))
ls, pop = random_pop(ls, 3)
print(pop)
ls, pop = random_pop(ls, 3)
print(pop)
print(ls)