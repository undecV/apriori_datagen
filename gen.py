# -*- coding: UTF-8 -*-

import math
import random

# from glob_h import *  # FUCK YOU WILDCARD IMPORT WANNING
from glob_h import Item, Cid
from dist import poisson_dist, exp_dist

INIT_SEED = -1  # dist.h


# ===== Parameters =====

class PatternPar:
    """
    Parameters used for StringSet
    StringSet can be either large itemsets, or sequences
    """
    def __init__(self):
        self.npats = 10000  # LINT  # number of patterns
        self.patlen = 4.0   # FLOAT # average length of pattern
        self.corr = 0.25    # FLOAT # correlation between consecutive patterns
        self.conf = 0.75    # FLOAT # average confidence in a rule
        self.conf_var = 0.1 # FLOAT # variation in the confidence
        self.seed = 0       # LINT

    def write(self, fp):
        print("\tNumber of patterns = " + self.npats, file = fp)
        print("\tAverage length of pattern = " + self.patlen, file = fp)
        print("\tCorrelation between consecutive patterns = " + self.corr, file = fp)
        print("\tAverage confidence in a rule = " + self.conf, file = fp)
        print("\tVariation in the confidence = " + self.conf_var, file = fp)


class TransPar:
    """
    Parameters used to generate transactions
    """
    def __init__(self):
        self.ntrans = 1000000       # LINT          # number of transactions in database
        self.tlen = 10.0            # FLOAT         # average transaction length
        self.nitems = 100000        # LINT          # number of items
        self.lits = PatternPar()    # PatternPar    # parameters for potentially large itemsets
        self.ascii_ = False         # BOOLEAN       # Generate in ASCII format
        self.seed = INIT_SEED       # LINT          # LINT Seed to initialize RandSeed with before x-act generation

    def write(self, fp):
        print("Number of transactions in database = " + self.ntrans, file = fp)
        print("Average transaction length = " + self.tlen, file = fp)
        print("Number of items = " + self.nitems, file = fp)
        print("Large Itemsets:", file = fp)
        self.lits.write(fp)
        print(file = fp)


class TaxPar(TransPar):
    """
    Parameters used to generate transactions
    """
    def __init__(self):
        self.nroots = 0         # LINT  # number of roots
        self.fanout = 0.0       # FLOAT # average fanout at each interiori node
        self.nlevels = 0.0      # FLOAT # average number of levels
        self.depth_ratio = 1.0  # FLOAT # affects ratio of itemsets chosen from higher levels

    def calc_values(self):
        """
        calculates nroots, given nlevels
        default values: nroots = 250, fanout = 5
        """
        nset = 0
        if self.nlevels != 0: nset += 1
        if self.fanout != 0: nset += 1
        if self.nroots != 0: nset += 1
        
        # switch (nset) case
        if nset == 0:
            self.nroots = 250
            self.fanout = 5.0
            return

        elif nset == 1:
            if self.nlevels == 0: raise ValueError('assert (nlevels == 0);') # assert
            if self.fanout == 0:
                self.fanout = 5
            elif self.nroots == 0:
                self.nroots = 250
            return

        elif nset == 2:
            if self.nlevels == 0:   # all set!
                return
            if (self.fanout != 0):   # calculate nroots
                self.nroots = self.nitems / (1 + pow(self.fanout, self.nlevels - 1))
                if self.nroots < 1: 
                    self.nroots = 1
            elif self.nroots != 0:   # calculate fanout
                temp = self.nitems / self.nroots - 1
                temp = math.log(temp) / (self.nlevels - 1)
                self.fanout = math.exp(temp)
            return

        elif nset == 3: # all set!
            return

    def write(self, fp):
        print("Number of transactions in database = " + self.ntrans, file=fp)
        print("Average transaction length = " + self.tlen, file=fp)
        print("Number of items = " + self.nitems, file=fp)
        print("Number of roots = " + self.nroots, file=fp)
        print("Number of levels = " + self.nlevels, file=fp)
        print("Average fanout = " + self.fanout, file=fp)
        print("Large Itemsets:", file=fp)
        self.lits.write(fp)
        print(file=fp)


class SeqPar: 
    """
    Parameters used to generate sequences
    """
    def __init__(self):
        self.ncust = 100000 # LINT  # number of customers in database
        self.slen = 10.0    # FLOAT # average sequence length
        self.tlen = 2.5     # FLOAT # average transaction length
        self.nitems = 10000 # LINT  # number of items

        self.rept = 0.0     # FLOAT # repetition-level (between 0 and 1)
        self.rept_var = 0.1 # FLOAT # variation in repetition-level

        self.ascii_ = False # BOOLEAN   # Generate in ASCII format

        self.lits = PatternPar()    # PatternPar    # parameters for potentially large itemsets
        self.lseq = PatternPar()    # PatternPar    # parameters for potentially large sequences

        self.lits.npats = 25000
        self.lseq.npats = 5000
        self.lits.patlen = 1.25
        self.lseq.patlen = 4.0

    def write(self, fp):
        print("Number of customers in database = " + self.ncust, file=fp)
        print("Average sequence length = " + self.slen, file=fp)
        print("Average transaction length = " + self.tlen, file=fp)
        print("Number of items = " + self.nitems, file=fp)
        print("Repetition-level = " + self.rept, file=fp)
        print("Variation in repetition-level = " + self.rept_var, file=fp)

        print("Large Itemsets:", file=fp)
        self.lits.write(fp)
        print("Large Sequences:", file=fp)
        self.lseq.write(fp)
        print(file=fp)


# ===== Taxonomy ===== 

class Taxonomy:
    # friend class TaxStat;
    def __init__(self, nitems: int, nroots: int, fanout: float, depth_ratio: float):
    # private:
        self.nitems = nitems        # LINT  # number of items
        self.nroots = nroots        # LINT  # number of roots
        self.depth = depth_ratio    # FLOAT # used when assigning probabilities to items

        # DONE: Pointer? YES
        # allocate memory
        self.par = [-1] * self.nroots           # LINT[nitems]
        self.child_start = [None] * self.nroots # LINT[nitems]
        self.child_end = [None] * self.nroots   # LINT[nitems]

        self.item_len = None    # static const LINT  # ASCII field-width of item-id

        next_child = self.nroots

        # DONE: dist
        # PoissonDist nchildren(fanout-1);        # string length
        nchildren = poisson_dist(fanout - 1)

        # initialize parents (or lack thereof) for roots
        # self.par = [-1] * self.nroots
        #   just N line before...
        
        # set up all the interior nodes
        i = 0
        j = next_child
        while i < self.nitems and next_child < self.nitems:
            self.child_start[i] = next_child
            next_child += nchildren + 1   # PoissonDist
            if  next_child > self.nitems:
                next_child = self.nitems
            self.child_end[i] = next_child
            while j < next_child:
                self.par[j] = i
                j += 1
            i += 1

    # public:
    def write(self, fp):                # TODO: BINARY OUTPUT
        "write taxonomy to file"
        for i in range(self.nitems):
            if self.par[i] >= 0:
                if i != self.par[i]: raise ValueError('assert(i != par[i]);') # assert
                fp.write(i)             # TODO: Size of write?
                fp.write(self.par[i])   # TODO: Size of write?

    def write_asc(self, fp):
        "write taxonomy to ASCII file"
        for i in range(self.nitems):
            if self.par[i] >= 0:
                if i != self.par[i]: raise ValueError('assert(i != par[i]);') # assert
                fp.write('{} {}\n'.format(i, self.par[i]))    # TODO: Format?

    def display(self, fp):
        "display taxonomy (for user)"
        fp.write('Taxonomy: \n')
        i = 0
        while i < self.nitems and self.child_start[i] > 0:
            fp.write('{} {} {}\n'.format(i, self.child_start[i], self.child_end[i] - 1))
            i += 1
        fp.write('\n')

    def depth_ratio(self) -> float:
        return self.depth

    def num_roots(self) -> int:
        return self.nroots
    
    def root(self, itm: Item) -> int:
        return self.par[itm] == -1

    def num_children(self, itm: Item) -> int:
        return self.child_end[itm] - self.child_start[itm]

    def child(self, itm: Item, n: int) -> int:
        "returns the n'th child of itm"
        return self.child_start[itm] + n

    def first_child(self, itm: Item) -> int:
        return self.child_start[itm]

    def last_child(self, itm: Item) -> int:
        return self.child_end[itm] - 1

    def parent(self, itm: Item) -> Item:
        "-1 => no parent"
        return self.par[itm]

# ===============

class ItemSet:
    """
    0 is a valid item here (get rid of it when actually adding item
    """
    # DONE: Taxonomy *tax <- just a point to tax
    # ItemSet(LINT nitems, Taxonomy *tax = NULL);
    def __init__(self, nitems: int, tax: Taxonomy = None):
        # nitems: number of items
        # tax: taxonomy (optional)
    # private:
        self.nitems = nitems    # LINT      # number of items
        self.tax = tax          # Taxonomy* # taxonomy (optional)
        self.cum_prob = None    # FLOAT*    # cumulative probability
        self.tax_prob = None    # FLOAT*    # cumulative probability of choosing a child
        # TODO: UniformDist()
        self.rand = None        # UniformDist
    
        # ExpDist freq;
        freq = exp_dist

        self.cum_prob = [freq()] * nitems       # FLOAT
        if tax is not None:
            self.tax_prob = [None] * nitems     # FLOAT

        # for(i = 0; i < nitems; i++){ cum_prob[i] = freq(); }
        # prob. that this pattern will be picked

        if tax is not None:
            # weight(itm) += wieght(children)
            # normalize probabilities for the roots and for children
            self.normalize(self.cum_prob, 0, self.tax.num_roots()-1)
            i = 0
            while i < self.nitems and self.tax.num_children(i) > 0:
                self.normalize(self.cum_prob, self.tax.first_child(i), self.tax.last_child(i))
                i += 1

            # calulate cumulative probabilities for children
            for i in range(self.nitems):
                self.tax_prob[i] = self.cum_prob[i]
            for i in range(1, self.nitems):
                if self.tax.num_children(i) > 0:
                    for j in range(self.tax.first_child(i), self.tax.last_child(i)):
                        self.tax_prob[j+1] += self.tax_prob[j]
    
            # set real probabilities
            for i in range(self.tax.num_roots(), self.nitems):
                self.cum_prob[i] *= self.cum_prob[ self.tax.parent(i) ] * self.tax.depth_ratio()

        # normalize probabilites (why -- see get_pat)
        self.normalize(self.cum_prob, 0, self.nitems-1)
        for i in range(1, self.nitems):  # calulate cumulative probabilities
            self.cum_prob[i] += self.cum_prob[i-1]

    def normalize(self, prob: list, low: int, high: int):
        # prob: list of float
        """normalize probabilities between low and high"""
        tot = 0.0  # FLOAT
        # normalize probabilites
        for i in range(low, high+1):
            tot += prob[i]
        for i in range(low, high+1):
            prob[i] /= tot

    def get_item(self) -> Item:
        """
        gen.h: returns a random item (weighted)
        gen.c: returns a pattern chosen at random
        """
        r = 0.0  # FLOAT
        i = 0  # LINT

        # find the desired pattern using cum_prob table
        r = random.random()  # TODO: unknown RAND_MAX
        # want item i such that cum_prob[i-1] < r <= cum_prob[i];
        i = r * self.nitems  # guess location of item
        i += (r - self.cum_prob[i]) * self.nitems  # refine guess
        if i >= self.nitems:  # check boundaries
            i = self.nitems-1
        if i < 0:
            i = 0
        while i < (self.nitems-  1) and r > self.cum_prob[i]:  # find item
            i += 1
        while i > 0 and r <= self.cum_prob[i-1]:
            i -= 1
        return i
    
    def specialize(self, itm: Item) -> Item:
        "if no taxonomy, returns itm"
        r = 0.0  # FLOAT
        i = 0  # LINT
        nchildren = 0  # LINT
        first = Item()  # Item
        last = Item()  # Item

        if self.tax is None:  # no taxonomy
            return itm
        
        nchildren = self.tax.num_children(itm)
        if nchildren == 0:  # no children
            return itm 
        first = self.tax.child(itm, 0)
        last = self.tax.child(itm, nchildren - 1)

        # find the desired pattern using cum_prob table
        r = random.random()  # TODO: unknown RAND_MAX
        i = first + r * nchildren
        if i == last:
            i -= 1
        while i < last and r > self.tax_prob[i]: 
            i += 1
        while i > first and r < self.tax_prob[i-1]:
            i -= 1
        return self.specialize(i)

    def weight(self, itm: Item) -> float:
        "returns prob. of choosing item"
        if itm == 0: 
            return self.cum_prob[itm]
        else:
            return self.cum_prob[itm] - self.cum_prob[itm-1]

    # public:
    def display(self, fp):
        # if (tax != NULL)
        #     tax->display(fp);
        print("Items:", file=fp)
        # fp << setprecision(3);
        
        if self.tax is not None:
            if self.cum_prob[0] * self.nitems > 10:
                print("{}  {} {} {}".format(0, self.cum_prob[0] * self.nitems, 
                    self.tax.first_child(0), self.tax.last_child(0)), file=fp)
            for i in range(1, self.nitems):
                if (self.cum_prob[i] - self.cum_prob[i-1]) * self.nitems > 10:
                    print("{}  {} {} {}".format(
                        i, 
                        (self.cum_prob[i]-self.cum_prob[i-1]) * self.nitems, 
                        self.tax.first_child(0), 
                        self.tax.last_child(0)
                        ), file=fp)
        else: 
            if self.cum_prob[0] * self.nitems > 5: 
                print("{}  {}".format(0, self.cum_prob[0] * self.nitems), file=fp)
            for i in range(1, self.nitems):
                if (self.cum_prob[i]-self.cum_prob[i-1]) * self.nitems > 5: 
                    print("{}  {}".format(
                        i, 
                        (self.cum_prob[i]-self.cum_prob[i-1]) * self.nitems
                        ), file=fp)
        print(file=fp)


class String:
    # friend class StringSet;
    def __init__(self, nitems: int):
    # private:
        self.nitems = nitems            # LINT      # number of items
        self.items = [None] * nitems    # Item*     # list of the items
      # self.rval           # FLOAT*    # random value (used to get random ordering of the items)
      # self.ritems         # Item*     # randomly chosen items
        self.prob = None    # FLOAT     # probability that this string is chosen
        self.conf = None    # FLOAT     # probability that this string is corrrupted

        # void shuffle(void);  # shuffles items in string

    # public:
    def display(self, fp, prob_comp: int = 1):
        print('{:6} {:6} '.format(prob_comp * self.prob, self.conf), file=fp)
        for i in range(self.nitems):
            print(' ' + self.items[i], end='', file=fp)
        print(file=fp)

    # TODO: [pylint] E0601:Using variable 'StringSet' before assignment
    # StringSet: StringSet
    # def display_(self, fp, lits: StringSet, prob_comp:int = 1):
    def display_(self, fp, lits, prob_comp: int = 1):
        # StringP lstr;
        print('{:6} {:6} '.format(prob_comp * self.prob, self.conf), file=fp)
        for i in range(self.nitems):
            print("  << ", end='', file=fp)
            lstr = lits.get_pat(self.items[i])
            for j in range(lstr.nitems):
                print("{} ".format(lstr.items[j]), end='', file=fp)
            print(">>", end='', file=fp)
        print(file=fp)

# typedef String *StringP;
StringP = String

class StringSet:
    # friend class StringSetIter;
    def __init__(self, nitems: int, par: PatternPar, tax: Taxonomy = None, 
        rept: float = 0.0, rept_lvl: float = 0.2):
    # private:
        self.items = None       # ItemSet*
        self.tax = None         # Taxonomy*
        self.npats = None       # LINT      # number of patterns
        self.pat = None         # StringP*  # array of patterns
        self.answer = None      # StringP
        self.cum_prob = None    # FLOAT*    # cumulative probabilities of patterns

    def specialize(self, i: int) -> StringP:
        "specializes pattern #i"
        pass

    # public:
    def display(self, fp, prob_comp:int = 1):
        pass

    def display_(self, fp, lit: StringSet):
        pass

    def get_pat(self, i:int) -> StringP:
        "returns pattern #i"
        pass


class StringSetIter:
    def __init__(self, str_set: StringSet):
    # private:
        self.rand = None        # UniformDist
        self.strset = str_set   # StringSet*
        self.last_pat = 0       # LINT  # if -ve, unget_pat() was called
    # public:

    def get_pat(self) -> StringP: 
        "returns a random pattern"
        pass
    
    def unget_pat(self):
        "the last pattern is put back in the sequence"
        pass

# ===============

class Transaction:
    def __init__(self, sz:int):
    # private:
        self.tlen = None    # LINT  # expected number of items in transaction
        self.nitems = None  # LINT  # number of items currently in transaction
        self.maxsize = None # LINT  # size of array items
        self.items = None   # LINT* # items in the transaction

        self.cid_len = None     # static const LINT # ASCII field-width of customer-id
        self.tid_len = None     # static const LINT # ASCII field-width of transaction-id
        self.item_len = None    # static const LINT # ASCII field-width of item-id

        self.tid = None # static LINT   # transaction-id

    def sort(self):
        pass

    def add_item(self, itm: int) -> bool:
        "returns TRUE if added, FALSE if already present"
        pass

    # public:
    def add(self, pat: String, corrupt:bool = True) -> bool:
        """
        adds pattern to transaction
        returns TRUE if added, FALSE if trans. full
        """
        pass

    def write(self, fp, cid: int = 0):
        pass
    
    def write_asc(self, fp, cid:int = 0):
        pass

    def size(self) -> int:
        return self.nitems

# typedef Transaction *TransactionP;
TransactionP = Transaction


class CustSeq: 
    def __init__(self, cid: Cid, seq_len: int, tot_items: int):
    # private:
        self.cid = None     # Cid   # customer-id
        self.slen = None    # LINT  # expected number of transactions in sequence
        self.tlen = None    # LINT  # avg. expected number of items in a transaction
        self.ntrans = None  # LINT  # number of transactions in sequence
        self.nitems = None  # LINT  # number of items in sequence
        self.maxsize = None # LINT  # size of array trans
        self.trans = None   # TransactionP* # transaction in the sequence

    # public:
    def add(self, pat: String, lits: StringSet) -> bool:
        "adds pattern to transaction"
        pass

    def write(self, fp):
        pass

    def write_asc(self, fp):
        pass
    
    def size(self) -> int:
        return self.nitems
