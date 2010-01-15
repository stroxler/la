
import unittest
from copy import deepcopy

import numpy as np
nan = np.nan
from numpy.testing import assert_, assert_equal

from la import larry
from test import (printfail, noreference, nocopy)


def dup23(x):
    """
    Stack a 2d array to make a 3d array. 
    
    Used in this module to compare reduction operations on 2d and 3d arrays.
    
    Example
    -------
    >>> xa = np.arange(12).reshape(3,4)
    >>> np.sum(xa, 0)
    array([12, 15, 18, 21])
    >>> np.sum(dup23(xa), 2)
    array([[12, 15, 18, 21],
           [12, 15, 18, 21]])
    >>> np.all(np.sum(dup23(xa), 2) == np.sum(xa, 0))
    True
    >>> np.all(larry(xa).mean(0).x == larry(dup23(xa)).mean(2).x)
    True
    
    For non reducing operations another swap of axes is required
    
    >>> np.all(np.cumsum(dup23(xa), 2).swapaxes(1,2) == np.cumsum(xa, 0))
    True
    
    """
    return np.rollaxis(np.dstack([x,x]), 2)

tol = 1e-8
nancode = -9999  

meth_unary1 = ['log', 'exp', 'sqrt', 'abs', 'sign']
# All reduce operations except lastrank
meth_reduce1 = ['sum', 'mean', 'var', 'std', 'max', 'min', 'median', 'any',
                'all']
meth_nonan = ['cumsum']


def assert_larry(opname, la, t, lab, msgstr):
    msg = printfail(la.label, lab, 'label'+msgstr)  
    assert_(la.label == lab, msg)        
    msg = printfail(t, la.x, 'x'+msgstr)
    t[np.isnan(t)] = nancode
    la.x[np.isnan(la.x)] = nancode        
    assert_((abs(t - la.x) < tol).all(), msg) 

x1 = np.array([[ 2.0, 2.0, 3.0, 1.0],
                [ 3.0, 2.0, 2.0, 1.0],
                [ 1.0, 1.0, 1.0, 1.0]])
la1 = larry(x1)
x3 = np.array([[ 2.0, 2.0, 3.0, 1.0],
                [ 3.0, 2.0, 2.0, nan],
                [ 1.0, nan, 1.0, 1.0]])
la3 = larry(x3)

x2 = np.array([[ 2.0, nan, 3.0, 1.0],
                [ 3.0, nan, 2.0, nan],
                [ 1.0, nan, 1.0, 1.0]])
la2 = larry(x2)

la3_3d = larry(np.dstack((x3,x1)))
la1_3d = larry(np.dstack((x1,2*x1)))

las = [(la1,'la1'), (la2,'la2'), (la1_3d, 'la1_3d'), (la3,'la3')]
lasnonan = [(la1,'la1'), (la1_3d, 'la1_3d')]

def test_methods_unary():
    # Simple unary elementwise operations
    for la, laname in las:
        for opname in meth_unary1:
            npop = getattr(np,opname)
            t = npop(la.x)   # Add +1 here to check whether tests fail
            p = getattr(la, opname)()
            
            yield assert_larry, opname, p, t, la.label, laname
            yield assert_, noreference(p, la), opname + ' - noreference'
            
def test_methods_reduce():
    # Simple unary elementwise operations
    for la, laname in las:
        for opname in meth_reduce1:
            if np.isnan(la.x).any(): 
                npmaop = getattr(np.ma,opname)
                npop = lambda *args: np.ma.filled(npmaop(np.ma.fix_invalid(args[0]),args[1]),np.nan)
            else:
                npop = getattr(np,opname)
                
            for axis in range(la.x.ndim):
                t = npop(la.x, axis)   #+1  to see whether tests fail
                p = getattr(la, opname)(axis)
                tlab = deepcopy(la.label)
                tlab.pop(axis)                
                yield assert_larry, opname, p, t, tlab, laname+' axis='+str(axis)

def test_methods_nonan():
    # Simple unary elementwise operations
    for la, laname in lasnonan:
        for opname in meth_nonan:
            npop = getattr(np,opname)
                
            for axis in range(la.x.ndim):
                t = npop(la.x, axis) 
                p = getattr(la, opname)(axis)
                tlab = deepcopy(la.label)
                yield assert_larry, opname, p, t, tlab, laname+' axis='+str(axis)

class est_calc(object):
    "Test calc functions of larry class"
    
    def setUp(self):
        self.assert_ = np.testing.assert_
        self.tol = tol
        self.nancode = nancode  

    def check_function(self, t, label, p, orig, view=False):
        "check a method of larry - comparison helper function"
        msg = printfail(t, p.x, 'x')  
        t[np.isnan(t)] = self.nancode
        p[p.isnan()] = self.nancode             
        self.assert_((abs(t - p.x) < self.tol).all(), msg)
        self.assert_(label == p.label, printfail(label, p.label, 'label'))
        if not view:
            self.assert_(noreference(p, orig), 'Reference found')   
        elif view == 'nocopy' :
            self.assert_(nocopy(p, orig), 'copy instead of reference found') 
        else:   #FIXME check view for different dimensional larries
            pass  

    def test_demedian_2(self):
        "larry.demedian_2"
        t = self.tmedian
        label = self.label
        p = self.lar.demedian(1)
        msg = printfail(t, p.x, 'x') 
        t[np.isnan(t)] = self.nancode
        p[p.isnan()] = self.nancode             
        self.assert_((abs(t - p.x) < self.tol).all(), msg)
        self.assert_(label == p.label, printfail(label, p.label, 'label'))
        self.assert_(noreference(p, self.lar), 'Reference found')

    def test_demedian_3(self):
        "larry.demedian_2"
        t = self.tmedian
        label = self.label3
        p = self.lar3.demedian(2)
        msg = printfail(t, p.x, 'x') 
        t[np.isnan(t)] = self.nancode
        p[p.isnan()] = self.nancode             
        self.assert_((abs(t - p.x) < self.tol).all(), msg)
        self.assert_(label == p.label, printfail(label, p.label, 'label'))
        self.assert_(noreference(p, self.lar3), 'Reference found')
    
    def test_movingsum_6(self):
        "larry.movingsum_6"
        t = self.tmovingsum 
        label = self.label
        p = self.lar.movingsum(2, norm=True)
        msg = printfail(t, p.x, 'x')  
        t[np.isnan(t)] = self.nancode
        p[p.isnan()] = self.nancode             
        self.assert_((abs(t - p.x) < self.tol).all(), msg)
        self.assert_(label == p.label, printfail(label, p.label, 'label'))
        self.assert_(noreference(p, self.lar), 'Reference found')   

    def est_movingsum_6_3(self):
        "larry.movingsum_6"
        t = self.tmovingsum
        label = self.label3
        p = self.lar3.movingsum(2, norm=True)
        msg = printfail(t, p.x, 'x')  
        t[np.isnan(t)] = self.nancode
        p[p.isnan()] = self.nancode             
        self.assert_((abs(t - p.x) < self.tol).all(), msg)
        self.assert_(label == p.label, printfail(label, p.label, 'label'))
        self.assert_(noreference(p, self.lar3), 'Reference found')  
        
    def test_movingsum_6_3(self):
        "duplicate larry.movingsum_6"
        t = self.tmovingsum
        label = self.label3
        p = self.lar3.movingsum(2, norm=True)
        self.check_function(t, label, p, self.lar3)

    def test_ranking_(self):
        "larry.ranking"  #not in deflarry_test
        t = self.tranking
        label = self.label
        p = self.lar.ranking(1)
        self.check_function(t, label, p, self.lar)

    def test_ranking_3(self):
        "larry.ranking 3d" 
        t = self.tranking
        label = self.label3
        p = self.lar3.ranking(2)
        self.check_function(t, label, p, self.lar3)

    def test_lag(self):
        "larry.ranking 3d" 
        t = self.tlag
        label = self.labellag
        p = self.lar.lag(1)
        self.check_function(t, label, p, self.lar)
                
    def test_lag_3(self):
        "larry.ranking 3d" 
        t = self.tlag
        label = self.label3lag
        p = self.lar3.lag(1)
        self.check_function(t, label, p, self.lar3)

    def test_pull(self):
        "larry.ranking 3d" 
        t = self.tpull
        label = self.labelpull
        p = self.lar.pull(1,1)
        self.check_function(t, label, p, self.lar, view='skip')
                
    def test_pull_3(self):
        "larry.ranking 3d" 
        t = self.tpull
        label = self.label3pull
        p = self.lar3.pull(1,2)
        self.check_function(t, label, p, self.lar3, view='skip')

    def test_squeeze(self):
        "larry.squeeze 3d" 
        t = self.lar.x
        label = self.lar.label
        x = self.lar.x[None,:]
        lar = larry(x)
        p = larry(x).squeeze()
        self.check_function(t, label, p, lar, view='skip') #should be nocopy
   
    def test_squeeze_3(self):
        "larry.squeeze 3d" 
        t = self.lar3.x
        label = self.lar3.label
        x = self.lar3.x[None,:]
        lar = larry(x)
        p = lar.squeeze()
        self.check_function(t, label, p, lar, view='skip') #should be nocopy

    def test_morph_3(self):
        "larry.morph 3d" 
        t = self.tmorph
        label = self.labelmorph
        label[1] = [0,3,2]
        p = self.lar.morph([0,3,2],axis=1)
        self.check_function(t, label, p, self.lar, view='copy')

    def test_morph_3(self):
        "larry.morph 3d" 
        t = self.tmorph
        label = self.label3
        label[2] = [0,3,2]
        p = self.lar3.morph([0,3,2],axis=2)
        self.check_function(t, label, p, self.lar3, view='copy')


class Test_calc_la2(est_calc):
    "Test calc functions of larry class"
    # This runs all methods with `test_` of the super class as tests
    # check by introducing a failure in original data self.x2
    
    def setUp(self):
        self.assert_ = np.testing.assert_
        self.tol = tol
        self.nancode = nancode        
        self.x2 = np.array([[ 2.0, 2.0, nan, 1.0],
                            [ nan, nan, nan, 1.0],
                            [ 1.0, 1.0, nan, 1.0]])
        self.lar = larry(self.x2)
        self.lar3 = larry(dup23(self.x2))
        self.tmedian = np.array([[ 0.0, 0.0, nan,-1.0],
                          [ nan, nan, nan, 0.0],
                          [ 0.0, 0.0, nan, 0.0]])                    
        self.label = [[0, 1, 2], [0, 1, 2, 3]]
        self.label3 = [[0,1], [0, 1, 2], [0, 1, 2, 3]]
        self.labelmedian = self.label
        self.label3median = self.label3
        
        self.tmovingsum = np.array([[ nan, 4.0, 4.0, 2.0],
                                    [ nan, nan, nan, 2.0],
                                    [ nan, 2.0, 2.0, 2.0]]) 
        
        self.tranking = np.array([[ 0.5,  0.5,  nan, -1. ],
                                 [ nan,  nan,  nan,  0. ],
                                 [ 0. ,  0. ,  nan,  0. ]])
        
        self.tlag = np.array([[  2.,   2.,  nan],
                              [ nan,  nan,  nan],
                              [  1.,   1.,  nan]])
        self.labellag = [[0, 1, 2], [1, 2, 3]]
        self.label3lag = [[0,1], [0, 1, 2], [1, 2, 3]]
        
        self.tpull = np.array([  2.,  nan,   1.])
        self.labelpull = [[0, 1, 2]]
        self.label3pull = [[0,1], [0, 1, 2]]
        
        self.tmorph = np.array([[  2.,   1.,  nan],
                               [ nan,   1.,  nan],
                               [  1.,   1.,  nan]])
               
class est_groups_moving(object):
    "Test calc functions of larry class"
    
    def setUp(self):
        self.assert_ = np.testing.assert_
        self.tol = tol
        self.nancode = nancode

    def check_function(self, t, label, p, orig, view=False):
        "check a method of larry - comparison helper function"
        msg = printfail(t, p.x, 'x')  
        t[np.isnan(t)] = self.nancode
        p[p.isnan()] = self.nancode             
        self.assert_((abs(t - p.x) < self.tol).all(), msg)
        self.assert_(label == p.label, printfail(label, p.label, 'label'))
        if not view:
            self.assert_(noreference(p, orig), 'Reference found')   
        elif view == 'nocopy' :
            self.assert_(nocopy(p, orig), 'copy instead of reference found') 
        else:   #FIXME check view for different dimensional larries
            pass  

    def test_grouprank(self):
        "larry.grouprank"  #not in deflarry_test
        t = self.trank1
        label = self.label
        p = self.lar.group_ranking(self.sectors)
        self.check_function(t, label, p, self.lar)
        
    def test_groupmean(self):
        "larry.grouprank"  #not in deflarry_test
        t = self.tmean1
        label = self.label
        p = self.lar.group_mean(self.sectors)
        self.check_function(t, label, p, self.lar)

    def test_groupmedian(self):
        "larry.grouprank"  #not in deflarry_test
        t = self.tmedian1
        label = self.label
        p = self.lar.group_median(self.sectors)
        self.check_function(t, label, p, self.lar)

    def test_groupmean3(self):
        "larry.groupmean 3d"  #not in deflarry_test
        t = self.tmean3
        label = self.label3
        p = self.lar3.group_mean(self.sectors)
        self.check_function(t, label, p, self.lar3)

    def test_groupmedian3(self):
        "larry.groupmedian 3d"  #not in deflarry_test
        t = self.tmedian3
        label = self.label3
        p = self.lar3.group_median(self.sectors)
        self.check_function(t, label, p, self.lar3)
        
    def test_movingsum31(self):
        "larry.movingsum 3d 1"
        t = self.tmovingsum3
        label = self.label3
        p = self.lar3.movingsum(2, axis=1, norm=False)
        self.check_function(t, label, p, self.lar3) 
        
    def test_movingsum32(self):
        "larry.groupmedian 3d 2"
        #requires numpy 1.4 for nan equality testing 
        lar3r = self.lar3.movingsum(2, axis=0, norm=True)
        lar2r = self.lar.movingsum(2, axis=0, norm=True)
        assert_equal(self.label3, lar3r.label)
        assert_equal(lar3r.x[:,:,0], lar2r.x)
        assert_equal(lar3r.x[:,:,1], lar2r.x)
        
    def test_movingsum33(self):
        "larry.groupmedian 3d 3"
        #requires numpy 1.4 for nan equality testing 
        lar3r = self.lar3.movingsum(2, axis=2, norm=True)
        assert_equal(self.label3, lar3r.label)
        assert_(not np.isfinite(lar3r.x[:,:,0]).any())
        assert_equal(lar3r.x[:,:,1], 2*self.lar3.x[:,:,1])

class Test_group_moving(est_groups_moving):
    "Test calc functions of larry class"
    # This runs all methods with `test_` of the super class as tests
    # check by introducing a failure in original data self.x2
    
    def setUp(self):
        self.assert_ = np.testing.assert_
        self.tol = tol
        self.nancode = nancode

        self.label3 = [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5],
                       [0,1]]
        self.x = np.array([[0.0, 3.0, nan, nan, 0.0, nan],
                           [1.0, 1.0, 1.0, nan, nan, nan],
                           [2.0, 2.0, 0.0, nan, 1.0, nan],
                           [3.0, 0.0, 2.0, nan, nan, nan],
                           [4.0, 4.0, 3.0, 0.0, 2.0, nan],
                           [5.0, 5.0, 4.0, 4.0, nan, nan]])
        sectors = ['a', 'b', 'a', 'b', 'a', 'c']
        self.lar = larry(self.x)
        self.sectors = larry(np.array(sectors, dtype=object))
        self.lar3 = larry(np.dstack([self.lar.x, self.lar.x]))
        
        self.label = [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]]
        
        self.trank1 = np.array([[-1.0, 0.0,  nan, nan, -1.0, nan],
                               [-1.0, 1.0, -1.0, nan,  nan, nan],
                               [ 0.0,-1.0, -1.0, nan,  0.0, nan],
                               [ 1.0,-1.0,  1.0, nan,  nan, nan],
                               [ 1.0, 1.0,  1.0, 0.0,  1.0, nan],
                               [ 0.0, 0.0,  0.0, 0.0,  nan, nan]])
        
        self.tmean1 = np.array([[ 2.0, 3.0,  1.5, 0.0,  1.0, nan],
                               [ 2.0, 0.5,  1.5, nan,  nan, nan],
                               [ 2.0, 3.0,  1.5, 0.0,  1.0, nan],
                               [ 2.0, 0.5,  1.5, nan,  nan, nan],
                               [ 2.0, 3.0,  1.5, 0.0,  1.0, nan],
                               [ 5.0, 5.0,  4.0, 4.0,  nan, nan]])
        
        self.tmean3 = np.dstack([self.tmean1, self.tmean1])
        
        self.tmedian1 = np.array([[ 2.0, 3.0,  1.5, 0.0,  1.0, nan],
                               [ 2.0, 0.5,  1.5, nan,  nan, nan],
                               [ 2.0, 3.0,  1.5, 0.0,  1.0, nan],
                               [ 2.0, 0.5,  1.5, nan,  nan, nan],
                               [ 2.0, 3.0,  1.5, 0.0,  1.0, nan],
                               [ 5.0, 5.0,  4.0, 4.0,  nan, nan]])
        
        self.tmedian3 = np.dstack([self.tmedian1, self.tmedian1])
        self.tmovingsum1 = np.array([[ nan,   3.,   3.,  nan,   0.,   0.],
                               [ nan,   2.,   2.,   1.,  nan,  nan],
                               [ nan,   4.,   2.,   0.,   1.,   1.],
                               [ nan,   3.,   2.,   2.,  nan,  nan],
                               [ nan,   8.,   7.,   3.,   2.,   2.],
                               [ nan,  10.,   9.,   8.,   4.,  nan]])
        self.tmovingsum3 = np.dstack([self.tmovingsum1, 
                                      self.tmovingsum1])
             