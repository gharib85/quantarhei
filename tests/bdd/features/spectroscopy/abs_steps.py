# -*- coding: utf-8 -*-

from aloe import step
from aloe import world

from ..stepslib import upper_half_time_axis
from ..stepslib import temperature

import pkg_resources
import numpy

#from quantarhei import TimeAxis
from quantarhei import CorrelationFunction
from quantarhei import energy_units

from quantarhei import Molecule
from quantarhei import Aggregate
from quantarhei import AbsSpect

from quantarhei.qm.corfunctions import CorrelationFunctionMatrix

@step(r'reorganization energy (\d+(?:\.\d+)?) "([^"]*)"') 
def reorganization_energy(self, reorg, e_units):
    print("\nreorganization energy ", reorg, e_units)
    world.reorg = float(reorg)
    world.e_units = e_units

@step(r'correlation time (\d+(?:\.\d+)?) "([^"]*)"')
def correlation_time(self, ctime, t_units):
    print("correlation time ", ctime, t_units)
    world.ctime = float(ctime)
    world.t_units = t_units


@step(r'number of Matsubara frequencies (\d+(?:\.\d+)?)')
def matsubara(self, Nm):
    print("no. Matsubara frequencies ", Nm)
    world.mats = int(Nm)


@step(r'When I calculate the ([^"]*) correlation function')
def correlation_function_of_type(self, ctype):
    print("correlation function type ", ctype)
    world.ctype = ctype

    params = {"ftype":    world.ctype,
              "reorg":    world.reorg,
              "cortime":  world.ctime,
              "T":        world.temp,
              "matsubara":world.mats}
              
    # FIXME: also time_units, temperature_units
    with energy_units(world.e_units):
        cf = CorrelationFunction(world.ta,params) 
        
    i = 0
    data = numpy.zeros((world.ta.data.shape[0],3))
    for t in world.ta.data:
        data[i,0] = t
        data[i,1] = numpy.real(cf.data[i])
        data[i,2] = numpy.imag(cf.data[i])
        i += 1
    
    world.cf = cf

@step(r'I calculate absorption spectrum of a molecule')
def absorption_spectrum_molecule(self):

    dd = [0.0,0.0,1.0]
    cf = world.cf
 
    with energy_units("1/cm"):
        m = Molecule("Mol",[0.0, 10000])
    m.set_dipole(0,1,dd)
    
    m.set_egcf([0,1],cf)
    
    a1 = AbsSpect(world.ta,m)
    a1.calculate(rwa=m.elenergies[1])
    
    with energy_units("1/cm"):
        world.abs = numpy.zeros((len(a1.data),2))
        for kk in range(len(a1.data)):
            world.abs[kk,0] = a1.axis.data[kk] #frequency[kk]
            world.abs[kk,1] = a1.data[kk]

    
@step(r'I calculate absorption spectrum of a dimer aggregate')
def absorption_spectrum_dimer(self):
    
    dd1 = [0.0,10.0,0.0]
    dd2 = [0.0,10.0,10.0]
    
    cf = world.cf
    cm = CorrelationFunctionMatrix(world.ta,2,1)
    cm.set_correlation_function(1,cf,[(1,1),(0,0)])

    with energy_units("1/cm"):
        m1 = Molecule("Mol",[0.0, 12100])
        m1.set_dipole(0,1,dd1)
        m2 = Molecule("Mol",[0.0, 12000])
        m2.set_dipole(0,1,dd2)
        
    #m1.set_egcf([0,1],cf)
    #m2.set_egcf([0,1],cf)
    m1.set_egcf_mapping((0,1),cm,0)
    m2.set_egcf_mapping((0,1),cm,1)
    m1.position = [0.0,0.0,0.0]
    m2.position = [5.0,0.0,0.0] 
    
    AG = Aggregate("TestAggregate")
    AG.set_egcf_matrix(cm)

    AG.add_Molecule(m1)
    AG.add_Molecule(m2)

    AG.set_coupling_by_dipole_dipole(prefac=0.0147520827152)

    AG.build()

    a1 = AbsSpect(world.ta,AG)
    with energy_units("1/cm"):
        a1.calculate(rwa=12000)
    
    with energy_units("1/cm"):
        world.abs = numpy.zeros((len(a1.data),2))
        for kk in range(len(a1.data)):
            world.abs[kk,0] = a1.axis.data[kk] #frequency[kk]
            world.abs[kk,1] = a1.data[kk]    
    

    
@step(r'I calculate absorption spectrum of a trimer aggregate')
def absorption_spectrum_trimer(self):
    
    dd1 = [0.0,10.0,0.0]
    dd2 = [0.0,10.0,10.0]
    
    cf = world.cf
    cm = CorrelationFunctionMatrix(world.ta,3,1)
    cm.set_correlation_function(1,cf,[(1,1),(0,0),(2,2)])

    with energy_units("1/cm"):
        m1 = Molecule("Mol",[0.0, 12100])
        m1.set_dipole(0,1,dd1)
        m2 = Molecule("Mol",[0.0, 12000])
        m2.set_dipole(0,1,dd2)
        m3 = Molecule("Mol",[0.0, 12000])
        m3.set_dipole(0,1,dd2)  
        
    #m1.set_egcf([0,1],cf)
    #m2.set_egcf([0,1],cf)
    m1.set_egcf_mapping((0,1),cm,0)
    m2.set_egcf_mapping((0,1),cm,1)
    m3.set_egcf_mapping((0,1),cm,2)
    m1.position = [0.0,0.0,0.0]
    m2.position = [5.0,0.0,0.0] 
    m3.position = [0.0,5.0,0.0] 
    
    
    AG = Aggregate("TestAggregate")
    AG.set_egcf_matrix(cm)

    AG.add_Molecule(m1)
    AG.add_Molecule(m2)
    AG.add_Molecule(m3)

    AG.set_coupling_by_dipole_dipole(prefac=0.0147520827152)

    AG.build()

    a1 = AbsSpect(world.ta,AG)
    with energy_units("1/cm"):
        a1.calculate(rwa=12000)
    
    with energy_units("1/cm"):
        world.abs = numpy.zeros((len(a1.data),2))
        for kk in range(len(a1.data)):
            world.abs[kk,0] = a1.axis.data[kk] #frequency[kk]
            world.abs[kk,1] = a1.data[kk]  
            
            
    
def read_n_columns(file,n):
    """Reads n columns of data from a package file """
    data = pkg_resources.resource_string(__package__,file)    
    A = numpy.fromstring(data.decode('utf-8'),dtype=numpy.float32,sep=' ')
    N = A.shape[0]
    Nh = int(N/n)
    try:
        ret = A.reshape(Nh,n)
    except:
        raise Exception()
        
    return ret    


@step(r'I get absorption spectrum from the file ([^"]*) in 1/cm')
def compare_absorption_with_file(self, file):

    print("comparing absorption with file ", file)
    abs_data = read_n_columns(file,2)
    numpy.testing.assert_allclose(abs_data,world.abs,rtol=1.0e-6)