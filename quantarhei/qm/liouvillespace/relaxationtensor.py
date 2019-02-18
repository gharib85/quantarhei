# -*- coding: utf-8 -*-

import numpy

from .superoperator import SuperOperator
#from ...core.managers import BasisManaged
#from ...utils.types import BasisManagedComplexArray

from ...core.managers import BasisManaged
from ...utils.types import BasisManagedComplexArray

class RelaxationTensor(SuperOperator):

    #data = BasisManagedComplexArray("data")
    Km = BasisManagedComplexArray("Km")
    Lm = BasisManagedComplexArray("Lm")
    Ld = BasisManagedComplexArray("Ld")
    
    def __init__(self):
        
        self._initialize_basis()
            
        self._data_initialized = False
        self.name = ""
        self.as_operators = False
        
    def _initialize_basis(self):

        # Set the currently used basis
        cb = self.manager.get_current_basis()
        self.set_current_basis(cb)
        # unless it is the basis outside any context
        if cb != 0:
            self.manager.register_with_basis(cb, self)        


    def apply(self, oper, copy=True):
        """Applies the relaxation tensor on a superoperator
        
        """
        
        if self.as_operators:
            
            print("Applying Relaxation tensor")
            if copy:
                import copy
                oper_ven = copy.copy(oper)
            else:
                oper_ven = oper
            
            rho1 = oper.data
            # apply tensor to data
            Km = self._Km
            Ld = self._Ld
            Lm = self._Lm
            Kd = numpy.zeros(Km.shape, dtype=numpy.float64)
            Nm = Km.shape[0]
            ven = numpy.zeros(oper.data.shape, dtype=numpy.complex128)
            for mm in range(Nm):
                Kd[mm, :, :] = numpy.transpose(Km[mm, :, :])
            
                ven += (
                numpy.dot(Km[mm,:,:],numpy.dot(rho1, Ld[mm,:,:]))
                +numpy.dot(Lm[mm,:,:],numpy.dot(rho1, Kd[mm,:,:]))
                -numpy.dot(numpy.dot(Kd[mm,:,:],Lm[mm,:,:]), rho1)
                -numpy.dot(rho1, numpy.dot(Ld[mm,:,:],Km[mm,:,:])))
                
            oper_ven.data = ven
                
            return oper_ven
            
        else:
            
            return super().apply(oper, copy=copy)


    def secularize(self):
        """Secularizes the relaxation tensor


        """
        if self.as_operators:
            self.convert_2_tensor()
            #raise Exception("Cannot be secularized in the operator form")
            
        if True:
            if self.data.ndim == 4:
                N = self.data.shape[0]
                for ii in range(N):
                    for jj in range(N):
                        for kk in range(N):
                            for ll in range(N):
                                if not (((ii == jj) and (kk == ll)) 
                                    or ((ii == kk) and (jj == ll))) :
                                        self.data[ii,jj,kk,ll] = 0
            else:  
                N = self.data.shape[1]
                for ii in range(N):
                    for jj in range(N):
                        for kk in range(N):
                            for ll in range(N):
                                if not (((ii == jj) and (kk == ll)) 
                                    or ((ii == kk) and (jj == ll))) :
                                        self.data[:,ii,jj,kk,ll] = 0                                        

                               
    def transform(self, SS, inv=None):
        """Transformation of the tensor by a given matrix
        
        
        This function transforms the Operator into a different basis, using
        a given transformation matrix.
        
        Parameters
        ----------
         
        SS : matrix, numpy.ndarray
            transformation matrix
            
        inv : matrix, numpy.ndarray
            inverse of the transformation matrix
            
        """        

        if not self._data_initialized:
            
            if (self.manager.warn_about_basis_change):
                print("\nQr >>> Operators of relaxation"+
                      " tensor '%s' changes basis" %self.name)
        
            if inv is None:
                S1 = numpy.linalg.inv(SS)
            else:
                S1 = inv

            for m in range(self.Lm.shape[0]):
                self._Lm[m,:,:] = numpy.dot(S1,numpy.dot(self._Lm[m,:,:], SS))  
                self._Ld[m,:,:] = numpy.dot(S1,numpy.dot(self._Ld[m,:,:], SS))
                self._Km[m,:,:] = numpy.dot(S1,numpy.dot(self._Km[m,:,:], SS))
            
            return
        
        
        if (self.manager.warn_about_basis_change):
                print("\nQr >>> Relaxation tensor '%s' changes basis"
                      %self.name)
           
        if inv is None:
            S1 = numpy.linalg.inv(SS)
        else:
            S1 = inv
        dim = SS.shape[0]
        
        if self._data.ndim == 4:
            for c in range(dim):
                for d in range(dim):
                    self._data[:,:,c,d] = \
                    numpy.dot(S1,numpy.dot(self._data[:,:,c,d],SS))
                    
            for a in range(dim):
                for b in range(dim):
                    self._data[a,b,:,:] = \
                    numpy.dot(S1,numpy.dot(self._data[a,b,:,:],SS))
        else:

            for tt in range(self._data.shape[0]):
                for c in range(dim):
                    for d in range(dim):
                        self._data[tt,:,:,c,d] = \
                            numpy.dot(S1,numpy.dot(self._data[tt,:,:,c,d],SS))
                    
                for a in range(dim):
                    for b in range(dim):
                        self._data[tt,a,b,:,:] = \
                            numpy.dot(S1,numpy.dot(self._data[tt,a,b,:,:],SS))            


    def convert_2_tensor(self):
        """Converts from operator to tensor form
        
        """
        pass


    def updateStructure(self):
        """ Recalculates dephasing and depopulation rates
        
        """
        
        if self._data.ndim == 4:
            # depopulation rates 
            for nn in range(self.dim):
                #for ii in range(0,self.data.shape[1]):
                #    if ii != nn:
                #        self.data[nn,nn,nn,nn] -= self.data[ii,ii,nn,nn]
                self._data[nn,nn,nn,nn] -= (numpy.trace(self._data[:,:,nn,nn])
                                            - self._data[nn,nn,nn,nn])
                
            # dephasing rates 
            for nn in range(self.dim):    
                for mm in range(nn+1,self.dim):
                    self._data[nn,mm,nn,mm] = -(self._data[nn,nn,nn,nn]
                                              +self._data[mm,mm,mm,mm])/2.0
                    self._data[mm,nn,mm,nn] = self._data[nn,mm,nn,mm] 

        else:
            # depopulation rates 
            for nn in range(self.dim):
                #for ii in range(0,self.data.shape[1]):
                #    if ii != nn:
                #        self.data[nn,nn,nn,nn] -= self.data[ii,ii,nn,nn]
                self._data[:,nn,nn,nn,nn] -= (numpy.trace(self._data[:,:,:,nn,nn],
                                                          axis1=1,axis2=2)
                                            - self._data[:,nn,nn,nn,nn])
                
            # dephasing rates 
            for nn in range(self.dim):    
                for mm in range(nn+1,self.dim):
                    self._data[:,nn,mm,nn,mm] = -(self._data[:,nn,nn,nn,nn]
                                              +self._data[:,mm,mm,mm,mm])/2.0
                    self._data[:,mm,nn,mm,nn] = self._data[:,nn,mm,nn,mm] 
            
    
    def __mult__(self, scalar):
        """Multiplication of the Tensor by a scalar
        
        """
        import numbers
        
        if not isinstance(scalar, numbers.Number):
            raise Exception("Only multiplication by numbers is implemented")
            
        if self.as_operators:
            raise Exception("Multiplication in operator form not implemented")
            
        self._data = self._data*scalar
        return self
        
    def __rmult__(self, scalar):
        return self.__mult__(scalar)
    
    
    def __add__(self, other):
        self._data += other._data
        return self

    def __iadd__(self, other):
        return self.__add__(other)
    
    
        
        
        
        