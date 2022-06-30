#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python module:  'pgs.py'
author:         Julien Straubhaar
date:           may-2022

Module for plurig-Gaussian simulations in 1D, 2D and 3D.
"""

import numpy as np
from geone import covModel as gcm
from geone import multiGaussian

# ----------------------------------------------------------------------------
def pluriGaussianSim_unconditional(cov_model_T1, cov_model_T2, flag_value,
                                   dimension, spacing=None, origin=None,
                                   x=None, v=None,
                                   algo_T1='fft', params_T1={},
                                   algo_T2='fft', params_T2={},
                                   nreal=1,
                                   full_output=True,
                                   verbose=4):
    """
    Simulation of a pluri-Gaussian Z, unconditional, defined as
        Z(x) = flag_value(T1(x), T2(x))
    where
        T1, T2 are two multi-Gaussian random fields (latent fields)
        flag_value is a function of two variables defining the final value (given as a "flag")
    Z and T1, T2 are field in 1D, 2D or 3D.

    :param cov_model_T1, cov_model_T2:
                        (CovModel1D or CovModel2D or CovModel3D class or None) covariance model for T1, T2
                            in 1D or 2D or 3D (same dimension for T1 and T2), see definition of
                            the class in module geone.covModel
                            if None: 'algo_T1' ('algo_T2') must be 'deterministic', and the field given by
                            param_T1['mean'] (param_T2['mean']) is considered
    :param flag_value:  (func) function of two variables:
                            flag_value(x, y): return the "flag value" at x, y (x, y: array like)
    :param dimension:   number of cells along each axis,
                        for simulation in
                            - 1D: (int, or sequence of 1 int): nx
                            - 2D: (sequence of 2 ints): (nx, ny)
                            - 3D: (sequence of 3 ints): (nx, ny, nz)
    :param spacing:     spacing between two adjacent cells along each axis,
                        for simulation in
                            - 1D: (float, or sequence of 1 float): sx
                            - 2D: (sequence of 2 floats): (sx, sy)
                            - 3D: (sequence of 3 floats): (sx, sy, sz)
                            (if None, set to 1.0 along each axis)
    :param origin:      origin of the simulation grid (corner of first grid cell),
                        for simulation in
                            - 1D: (float, or sequence of 1 float): ox
                            - 2D: (sequence of 2 floats): (ox, oy)
                            - 3D: (sequence of 3 floats): (ox, oy, oz)
                            (if None, set to 0.0 along each axis)
    :param algo_T1, algo_T2:
                        (str) defines the algorithm used for generating multi-Gaussian field T1, T2:
                            - 'fft' or 'FFT' (default): based on circulant embedding and FFT,
                                function called for <d>D (d = 1, 2, or 3):
                                    'geone.grf.grf<d>D'
                            - 'classic' or 'CLASSIC': classic algorithm, based on
                                the resolution of kriging system considered points
                                in a search ellipsoid,
                                function called for <d>D (d = 1, 2, or 3):
                                    'geone.geoscalassicinterface.simulate<d>D'
                            - 'deterministic': use a deterministic field
    :param params_T1, params_T2:
                        (dict) keyword arguments (additional parameters) to be passed to
                            the function corresponding to what is specified by the argument 'algo_T1', 'algo_T2'
                            (see the corresponding function for its keyword arguments),
                            in particular the key 'mean' can be specified (set to value 0 if None)
                            if 'algo_T1', 'algo_T2' is 'deterministic', a deterministic field is used
                            (given by the key 'mean' in 'params_T1', 'params_T2')
    :param nreal:       (int) number of realizations
    :param full_output: (bool) controls what is retrieved as output (see below)
    :param verbose:     (int) verbose mode, integer >=0, higher implies more display:

    :return:        if full_output is True:
                        (Z, T1, T2)
                    else:
                        Z
                    where
                        Z:  (nd-array) array of shape:
                                - for 1D: (nreal, nx), where nx = dimension
                                - for 2D: (nreal, ny, nx), where nx, ny = dimension
                                - for 3D: (nreal, nz, ny, nx), where nx, ny, nz = dimension
                                Z[k] is the k-th realization
                        T1:  (nd-array) array of shape:
                                - for 1D: (nreal, nx), where nx = dimension
                                - for 2D: (nreal, ny, nx), where nx, ny = dimension
                                - for 3D: (nreal, nz, ny, nx), where nx, ny, nz = dimension
                                T1[k] is the k-th realization
                        T2:  (nd-array) array of shape:
                                - for 1D: (nreal, nx), where nx = dimension
                                - for 2D: (nreal, ny, nx), where nx, ny = dimension
                                - for 3D: (nreal, nz, ny, nx), where nx, ny, nz = dimension
                                T2[k] is the k-th realization
    """
    if full_output:
        out = None, None, None
    else:
        out = None

    if not callable(flag_value):
        if verbose > 0:
            print("ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): 'flag_value' invalid, should be a function (callable) of two arguments")
        return out

    if algo_T1 not in ('fft', 'FFT', 'classic', 'CLASSIC', 'deterministic', 'DETERMINISTIC'):
        if verbose > 0:
            print("ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): 'algo_T1' invalid, should be 'fft' (default) or 'classic' or 'deterministic'")
        return out

    if algo_T2 not in ('fft', 'FFT', 'classic', 'CLASSIC', 'deterministic', 'DETERMINISTIC'):
        if verbose > 0:
            print("ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): 'algo_T2' invalid, should be 'fft' (default) or 'classic' or 'deterministic'")
        return out

    # Ignore covariance model if 'algo' is deterministic for T1, T2
    if algo_T1 in ('deterministic', 'DETERMINISTIC'):
        cov_model_T1 = None

    if algo_T2 in ('deterministic', 'DETERMINISTIC'):
        cov_model_T2 = None

    # Set space dimension (of grid) according to covariance model for T1
    d = 0
    if cov_model_T1 is None:
        if algo_T1 not in ('deterministic', 'DETERMINISTIC'):
            if verbose > 0:
                print("ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): 'cov_model_T1' is None, then 'algo_T1' must be 'deterministic'")
            return out
    elif isinstance(cov_model_T1, gcm.CovModel1D):
        d = 1
    elif isinstance(cov_model_T1, gcm.CovModel2D):
        d = 2
    elif isinstance(cov_model_T1, gcm.CovModel3D):
        d = 3
    else:
        if verbose > 0:
            print("ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): 'cov_model_T1' invalid, should be a class: <geone.covModel.CovModel1D>, <geone.covModel.CovModel2D>, or <geone.covModel.CovModel3D>")
        return out

    if cov_model_T2 is None:
        if algo_T2 not in ('deterministic', 'DETERMINISTIC'):
            if verbose > 0:
                print("ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): 'cov_model_T2' is None, then 'algo_T2' must be 'deterministic'")
            return out
        # if d == 0:
        #     if verbose > 0:
        #         print("ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): 'cov_model_T1' and 'cov_model_T2' are None, at least one covariance model is required")
        #     return out
    elif (d == 1 and not isinstance(cov_model_T2, gcm.CovModel1D)) or (d == 2 and not isinstance(cov_model_T2, gcm.CovModel2D)) or (d == 3 and not isinstance(cov_model_T2, gcm.CovModel3D)):
        if verbose > 0:
            print("ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): 'cov_model_T1' and 'cov_model_T2' not compatible (dimension differs)")
        return out

    if d == 0:
        # Set space dimension (of grid) according to 'dimension'
        if hasattr(dimension, '__len__'):
            d = len(dimension)
        else:
            d = 1

    # Check argument 'dimension'
    if hasattr(dimension, '__len__') and len(dimension) != d:
        if verbose > 0:
            print("ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): 'dimension' of incompatible length")
        return out

    if d == 1:
        grid_size = dimension
    else:
        grid_size = np.prod(dimension)

    # Check (or set) argument 'spacing'
    if spacing is None:
        if d == 1:
            spacing = 1.0
        else:
            spacing = tuple(np.ones(d))
    else:
        if hasattr(spacing, '__len__') and len(spacing) != d:
            if verbose > 0:
                print("ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): 'spacing' of incompatible length")
            return out

    # Check (or set) argument 'origin'
    if origin is None:
        if d == 1:
            origin = 0.0
        else:
            origin = tuple(np.zeros(d))
    else:
        if hasattr(origin, '__len__') and len(origin) != d:
            if verbose > 0:
                print("ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): 'origin' of incompatible length")
            return out

#    if not cov_model_T1.is_stationary(): # prevent calculation if covariance model is not stationary
#         if verbose > 0:
#             print("ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): 'cov_model_T1' is not stationary")

#    if not cov_model_T2.is_stationary(): # prevent calculation if covariance model is not stationary
#         if verbose > 0:
#             print("ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): 'cov_model_T2' is not stationary")

    # Set default parameter 'verbose' for params_T1, params_T2
    if 'verbose' not in params_T1.keys():
        params_T1['verbose'] = 0
    if 'verbose' not in params_T2.keys():
        params_T2['verbose'] = 0

    # Generate T1
    if cov_model_T1 is not None:
        sim_T1 = multiGaussian.multiGaussianRun(cov_model_T1, dimension, spacing, origin,
                                                mode='simulation', algo=algo_T1, output_mode='array',
                                                **params_T1, nreal=nreal)
    else:
        sim_T1 = np.array([params_T1['mean'].reshape(1,*dimension[::-1]) for ireal in range(nreal_T)])
    # -> sim_T1: nd-array of shape
    #      (nreal_T, dimension) (for T1 in 1D)
    #      (nreal_T, dimension[1], dimension[0]) (for T1 in 2D)
    #      (nreal_T, dimension[2], dimension[1], dimension[0]) (for T1 in 3D)
    if sim_T1 is None:
        if verbose > 0:
            print('ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): simulation of T1 failed')
        return out
    #
    # Generate T2
    if cov_model_T2 is not None:
        sim_T2 = multiGaussian.multiGaussianRun(cov_model_T2, dimension, spacing, origin,
                                                mode='simulation', algo=algo_T2, output_mode='array',
                                                **params_T2, nreal=nreal)
    else:
        sim_T2 = np.array([params_T2['mean'].reshape(1,*dimension[::-1]) for ireal in range(nreal_T)])
    # -> sim_T2: nd-array of shape
    #      (nreal_T, dimension) (for T2 in 1D)
    #      (nreal_T, dimension[1], dimension[0]) (for T2 in 2D)
    #      (nreal_T, dimension[2], dimension[1], dimension[0]) (for T2 in 3D)
    if sim_T2 is None:
        if verbose > 0:
            print('ERROR (PLURIGAUSSIANSIM_UNCONDITIONAL): simulation of T2 failed')
        return out

    # Generate Z
    if verbose > 2:
        print('PLURIGAUSSIANSIM_UNCONDITIONAL: retrieving Z...')
    Z = flag_value(sim_T1, sim_T2)
    # Z = np.asarray(Z).reshape(len(Z), *np.atleast_1d(dimension)[::-1])

    if full_output:
        return Z, sim_T1, sim_T2
    else:
        return Z
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
def pluriGaussianSim(cov_model_T1, cov_model_T2, flag_value,
                     dimension, spacing=None, origin=None,
                     x=None, v=None,
                     algo_T1='fft', params_T1={},
                     algo_T2='fft', params_T2={},
                     accept_init=0.25, accept_pow=2.0,
                     mh_iter_min=100, mh_iter_max=200,
                     ntry_max=1,
                     retrieve_real_anyway=False,
                     nreal=1,
                     full_output=True,
                     verbose=4):
    """
    Simulation of a pluri-Gaussian Z defined as
        Z(x) = flag_value(T1(x), T2(x))
    where
        T1, T2 are two multi-Gaussian random fields (latent fields)
        flag_value is a function of two variables defining the final value (given as a "flag")
    Z and T1, T2 are field in 1D, 2D or 3D.

    :param cov_model_T1, cov_model_T2:
                        (CovModel1D or CovModel2D or CovModel3D class or None) covariance model for T1, T2
                            in 1D or 2D or 3D (same dimension for T1 and T2), see definition of
                            the class in module geone.covModel
                            if None: 'algo_T1' ('algo_T2') must be 'deterministic', and the field given by
                            param_T1['mean'] (param_T2['mean']) is considered
    :param flag_value:  (func) function of two variables:
                            flag_value(x, y): return the "flag value" at x, y (x, y: array like)
    :param dimension:   number of cells along each axis,
                        for simulation in
                            - 1D: (int, or sequence of 1 int): nx
                            - 2D: (sequence of 2 ints): (nx, ny)
                            - 3D: (sequence of 3 ints): (nx, ny, nz)
    :param spacing:     spacing between two adjacent cells along each axis,
                        for simulation in
                            - 1D: (float, or sequence of 1 float): sx
                            - 2D: (sequence of 2 floats): (sx, sy)
                            - 3D: (sequence of 3 floats): (sx, sy, sz)
                            (if None, set to 1.0 along each axis)
    :param origin:      origin of the simulation grid (corner of first grid cell),
                        for simulation in
                            - 1D: (float, or sequence of 1 float): ox
                            - 2D: (sequence of 2 floats): (ox, oy)
                            - 3D: (sequence of 3 floats): (ox, oy, oz)
                            (if None, set to 0.0 along each axis)
    :param x:           coordinate of data points,
                        for simulation in
                            - 1D: (1-dimensional array or float)
                            - 2D: (2-dimensional array of dim n x 2, or
                                   1-dimensional array of dim 2)
                            - 3D: (2-dimensional array of dim n x 3, or
                                   1-dimensional array of dim 3)
                            (None if no data)
    :param v:           value at data points,
                        for simulation in
                            - 1D: (1-dimensional array or float)
                            - 2D: (1-dimensional array of length n)
                            - 3D: (1-dimensional array of length n)
                            (None if no data)
    :param algo_T1, algo_T2:
                        (str) defines the algorithm used for generating multi-Gaussian field T1, T2:
                            - 'fft' or 'FFT' (default): based on circulant embedding and FFT,
                                function called for <d>D (d = 1, 2, or 3):
                                    'geone.grf.grf<d>D'
                            - 'classic' or 'CLASSIC': classic algorithm, based on
                                the resolution of kriging system considered points
                                in a search ellipsoid,
                                function called for <d>D (d = 1, 2, or 3):
                                    'geone.geoscalassicinterface.simulate<d>D'
                            - 'deterministic': use a deterministic field
    :param params_T1, params_T2:
                        (dict) keyword arguments (additional parameters) to be passed to
                            the function corresponding to what is specified by the argument 'algo_T1', 'algo_T2'
                            (see the corresponding function for its keyword arguments),
                            in particular the key 'mean' can be specified (set to value 0 if None)
                            if 'algo_T1', 'algo_T2' is 'deterministic', a deterministic field is used
                            (given by the key 'mean' in 'params_T1', 'params_T2')
    :param accept_init: (float) initial acceptation probability
                            (see 'mh_iter_min', 'mh_iter_max' below)
    :param accept_pow:  (float) power for computing acceptation probability
                             (see 'mh_iter_min', 'mh_iter_max' below)
    :param mh_iter_min, mh_iter_max:
                        (int) number of iterations (min and max) for Metropolis-Hasting algorithm
                            (conditional case only)
                            when updating T1 and T2 at conditioning location at iteration 'nit'
                            (in 0, ..., mh_iter_max-1):
                                if nit < mh_iter_min: for any k:
                                    - simulate new candidate at x[k]: (T1(x[k,0]), T2(x[k,1]))
                                    - if flag_value(T1(x[k,0]), T2(x[k,1])) == v[k] (conditioning ok):
                                        accept the new candidate
                                    - else (conditioning not ok):
                                        accept the new candidate with probability
                                        p = accept_init * (1 - 1/mh_iter_min)**accept_pow
                                if nit >= mh_iter_min:
                                    - if conditioning ok at every x[k]: stop, exit the loop,
                                    - else: for any k:
                                        - if conditioning ok at x[k]: skip
                                        - else:
                                            simulate new candidate at x[k]: (T1(x[k,0]), T2(x[k,1]))
                                            - if flag_value(T1(x[k,0]), T2(x[k,1])) == v[k] (conditioning ok):
                                                accept the new candidate
                                            - else:
                                                reject the new candidate
    :param ntry_max:    (int) number of tries per realization before giving up if
                            something goes wrong
    :param retrieve_real_anyway:
                        (bool) if after ntry_max tries any conditioning data is not honoured, then
                        the realization is:
                            - retrieved if retrieve_real_anyway is True
                            - not retrieved (missing realization) if retrieve_real_anyway is False
    :param nreal:       (int) number of realizations
    :param full_output: (bool) controls what is retrieved as output (see below)
    :param verbose:     (int) verbose mode, integer >=0, higher implies more display

    :return:        if full_output is True:
                        (Z, T1, T2, n_cond_ok)
                    else:
                        Z
                    where
                        Z:  (nd-array) array of shape:
                                - for 1D: (nreal, nx), where nx = dimension
                                - for 2D: (nreal, ny, nx), where nx, ny = dimension
                                - for 3D: (nreal, nz, ny, nx), where nx, ny, nz = dimension
                                Z[k] is the k-th realization
                        T1:  (nd-array) array of shape:
                                - for 1D: (nreal, nx), where nx = dimension
                                - for 2D: (nreal, ny, nx), where nx, ny = dimension
                                - for 3D: (nreal, nz, ny, nx), where nx, ny, nz = dimension
                                T1[k] is the k-th realization
                        T2:  (nd-array) array of shape:
                                - for 1D: (nreal, nx), where nx = dimension
                                - for 2D: (nreal, ny, nx), where nx, ny = dimension
                                - for 3D: (nreal, nz, ny, nx), where nx, ny, nz = dimension
                                T2[k] is the k-th realization
                        n_cond_ok:
                            (list of length nreal):
                                    n_cond_ok[k]: 1d-array containing number of conditioning location
                                        honoured at each iteration of the Metropolis-Hasting algorithm
                                        for the k-th realization,
                                        in particular len(n_cond_ok[k]) is the number of iteration done,
                                        n_cond_ok[k][-1] is the number of conditioning location honoured
                                        at the end
    """
    if full_output:
        out = None, None, None, None
    else:
        out = None

    if not callable(flag_value):
        if verbose > 0:
            print("ERROR (PLURIGAUSSIANSIM): 'flag_value' invalid, should be a function (callable) of two arguments")
        return out

    if algo_T1 not in ('fft', 'FFT', 'classic', 'CLASSIC', 'deterministic', 'DETERMINISTIC'):
        if verbose > 0:
            print("ERROR (PLURIGAUSSIANSIM): 'algo_T1' invalid, should be 'fft' (default) or 'classic' or 'deterministic'")
        return out

    if algo_T2 not in ('fft', 'FFT', 'classic', 'CLASSIC', 'deterministic', 'DETERMINISTIC'):
        if verbose > 0:
            print("ERROR (PLURIGAUSSIANSIM): 'algo_T2' invalid, should be 'fft' (default) or 'classic' or 'deterministic'")
        return out

    # Ignore covariance model if 'algo' is deterministic for T1, T2
    if algo_T1 in ('deterministic', 'DETERMINISTIC'):
        cov_model_T1 = None

    if algo_T2 in ('deterministic', 'DETERMINISTIC'):
        cov_model_T2 = None

    # Set space dimension (of grid) according to covariance model for T1
    d = 0
    if cov_model_T1 is None:
        if algo_T1 not in ('deterministic', 'DETERMINISTIC'):
            if verbose > 0:
                print("ERROR (PLURIGAUSSIANSIM): 'cov_model_T1' is None, then 'algo_T1' must be 'deterministic'")
            return out
    elif isinstance(cov_model_T1, gcm.CovModel1D):
        d = 1
    elif isinstance(cov_model_T1, gcm.CovModel2D):
        d = 2
    elif isinstance(cov_model_T1, gcm.CovModel3D):
        d = 3
    else:
        if verbose > 0:
            print("ERROR (PLURIGAUSSIANSIM): 'cov_model_T1' invalid, should be a class: <geone.covModel.CovModel1D>, <geone.covModel.CovModel2D>, or <geone.covModel.CovModel3D>")
        return out

    if cov_model_T2 is None:
        if algo_T2 not in ('deterministic', 'DETERMINISTIC'):
            if verbose > 0:
                print("ERROR (PLURIGAUSSIANSIM): 'cov_model_T2' is None, then 'algo_T2' must be 'deterministic'")
            return out
        # if d == 0:
        #     if verbose > 0:
        #         print("ERROR (PLURIGAUSSIANSIM): 'cov_model_T1' and 'cov_model_T2' are None, at least one covariance model is required")
        #     return out
    elif (d == 1 and not isinstance(cov_model_T2, gcm.CovModel1D)) or (d == 2 and not isinstance(cov_model_T2, gcm.CovModel2D)) or (d == 3 and not isinstance(cov_model_T2, gcm.CovModel3D)):
        if verbose > 0:
            print("ERROR (PLURIGAUSSIANSIM): 'cov_model_T1' and 'cov_model_T2' not compatible (dimension differs)")
        return out

    if d == 0:
        # Set space dimension (of grid) according to 'dimension'
        if hasattr(dimension, '__len__'):
            d = len(dimension)
        else:
            d = 1

    # Check argument 'dimension'
    if hasattr(dimension, '__len__') and len(dimension) != d:
        if verbose > 0:
            print("ERROR (PLURIGAUSSIANSIM): 'dimension' of incompatible length")
        return out

    if d == 1:
        grid_size = dimension
    else:
        grid_size = np.prod(dimension)

    # Check (or set) argument 'spacing'
    if spacing is None:
        if d == 1:
            spacing = 1.0
        else:
            spacing = tuple(np.ones(d))
    else:
        if hasattr(spacing, '__len__') and len(spacing) != d:
            if verbose > 0:
                print("ERROR (PLURIGAUSSIANSIM): 'spacing' of incompatible length")
            return out

    # Check (or set) argument 'origin'
    if origin is None:
        if d == 1:
            origin = 0.0
        else:
            origin = tuple(np.zeros(d))
    else:
        if hasattr(origin, '__len__') and len(origin) != d:
            if verbose > 0:
                print("ERROR (PLURIGAUSSIANSIM): 'origin' of incompatible length")
            return out

#    if not cov_model_T1.is_stationary(): # prevent calculation if covariance model is not stationary
#         if verbose > 0:
#             print("ERROR (PLURIGAUSSIANSIM): 'cov_model_T1' is not stationary")

#    if not cov_model_T2.is_stationary(): # prevent calculation if covariance model is not stationary
#         if verbose > 0:
#             print("ERROR (PLURIGAUSSIANSIM): 'cov_model_T2' is not stationary")

    # Compute meshgrid over simulation domain if needed (see below)
    if ('mean' in params_T1.keys() and callable(params_T1['mean'])) or ('var' in params_T1.keys() and callable(params_T1['var'])) \
    or ('mean' in params_T2.keys() and callable(params_T2['mean'])) or ('var' in params_T2.keys() and callable(params_T2['var'])):
        if d == 1:
            xi = origin + spacing*(0.5+np.arange(dimension)) # x-coordinate of cell center
        elif d == 2:
            xi = origin[0] + spacing[0]*(0.5+np.arange(dimension[0])) # x-coordinate of cell center
            yi = origin[1] + spacing[1]*(0.5+np.arange(dimension[1])) # y-coordinate of cell center
            yyi, xxi = np.meshgrid(yi, xi, indexing='ij')
        elif d == 3:
            xi = origin[0] + spacing[0]*(0.5+np.arange(dimension[0])) # x-coordinate of cell center
            yi = origin[1] + spacing[1]*(0.5+np.arange(dimension[1])) # y-coordinate of cell center
            zi = origin[2] + spacing[2]*(0.5+np.arange(dimension[2])) # z-coordinate of cell center
            zzi, yyi, xxi = np.meshgrid(zi, yi, xi, indexing='ij')

    # Set mean_T1 (as array) from params_T1
    if 'mean' not in params_T1.keys():
        mean_T1 = np.array([0.0])
    else:
        mean_T1 = params_T1['mean']
        if mean_T1 is None:
            mean_T1 = np.array([0.0])
        elif callable(mean_T1):
            if d == 1:
                mean_T1 = mean_T1(xi).reshape(-1) # replace function 'mean_T1' by its evaluation on the grid
            elif d == 2:
                mean_T1 = mean_T1(xxi, yyi).reshape(-1) # replace function 'mean_T1' by its evaluation on the grid
            elif d == 3:
                mean_T1 = mean_T1(xxi, yyi, zzi).reshape(-1) # replace function 'mean_T1' by its evaluation on the grid
        else:
            mean_T1 = np.asarray(mean_T1).reshape(-1)
            if mean_T1.size not in (1, grid_size):
                if verbose > 0:
                    print("ERROR (PLURIGAUSSIANSIM): 'mean' parameter for T1 (in 'params_T1') has incompatible size")
                return out

    # Set var_T1 (as array) from params_T1, if given
    var_T1 = None
    if 'var' in params_T1.keys():
        var_T1 = params_T1['var']
        if var_T1 is not None:
            if callable(var_T1):
                if d == 1:
                    var_T1 = var_T1(xi).reshape(-1) # replace function 'var_T1' by its evaluation on the grid
                elif d == 2:
                    var_T1 = var_T1(xxi, yyi).reshape(-1) # replace function 'var_T1' by its evaluation on the grid
                elif d == 3:
                    var_T1 = var_T1(xxi, yyi, zzi).reshape(-1) # replace function 'var_T1' by its evaluation on the grid
            else:
                var_T1 = np.asarray(var_T1).reshape(-1)
                if var_T1.size not in (1, grid_size):
                    if verbose > 0:
                        print("ERROR (PLURIGAUSSIANSIM): 'var' parameter for T1 (in 'params_T1') has incompatible size")
                    return out

    # Set mean_T2 (as array) from params_T2
    if 'mean' not in params_T2.keys():
        mean_T2 = np.array([0.0])
    else:
        mean_T2 = params_T2['mean']
        if mean_T2 is None:
            mean_T2 = np.array([0.0])
        elif callable(mean_T2):
            if d == 1:
                mean_T2 = mean_T2(xi).reshape(-1) # replace function 'mean_T2' by its evaluation on the grid
            elif d == 2:
                mean_T2 = mean_T2(xxi, yyi).reshape(-1) # replace function 'mean_T2' by its evaluation on the grid
            elif d == 3:
                mean_T2 = mean_T2(xxi, yyi, zzi).reshape(-1) # replace function 'mean_T2' by its evaluation on the grid
        else:
            mean_T2 = np.asarray(mean_T2).reshape(-1)
            if mean_T2.size not in (1, grid_size):
                if verbose > 0:
                    print("ERROR (PLURIGAUSSIANSIM): 'mean' parameter for T2 (in 'params_T2') has incompatible size")
                return out

    # Set var_T2 (as array) from params_T2, if given
    var_T2 = None
    if 'var' in params_T2.keys():
        var_T2 = params_T2['var']
        if var_T2 is not None:
            if callable(var_T2):
                if d == 1:
                    var_T2 = var_T2(xi).reshape(-1) # replace function 'var_T2' by its evaluation on the grid
                elif d == 2:
                    var_T2 = var_T2(xxi, yyi).reshape(-1) # replace function 'var_T2' by its evaluation on the grid
                elif d == 3:
                    var_T2 = var_T2(xxi, yyi, zzi).reshape(-1) # replace function 'var_T2' by its evaluation on the grid
            else:
                var_T2 = np.asarray(var_T2).reshape(-1)
                if var_T2.size not in (1, grid_size):
                    if verbose > 0:
                        print("ERROR (PLURIGAUSSIANSIM): 'var' parameter for T2 (in 'params_T2') has incompatible size")
                    return out

    # Note: format of data (x, v) not checked !

    if x is None:
        if v is not None:
            if verbose > 0:
                print("ERROR (PLURIGAUSSIANSIM): 'x' is not given (None) but 'v' is given (not None)")
            return out
    #
    else:
        # Preparation for conditional case
        if v is None:
            if verbose > 0:
                print("ERROR (PLURIGAUSSIANSIM): 'x' is given (not None) but 'v' is not given (None)")
            return out
        #
        x = np.asarray(x, dtype='float').reshape(-1, d) # cast in d-dimensional array if needed
        v = np.asarray(v, dtype='float').reshape(-1) # cast in 1-dimensional array if needed
        if len(v) != x.shape[0]:
            if verbose > 0:
                print("ERROR (PLURIGAUSSIANSIM): length of 'v' is not valid")
            return out
        #
        # Compute
        #    indc: node index of conditioning node (nearest node),
        #          rounded to lower index if between two grid node and index is positive
        indc_f = (x-origin)/spacing
        indc = indc_f.astype(int)
        indc = indc - 1 * np.all((indc == indc_f, indc > 0), axis=0)
        if d == 1:
            indc = 1 * indc[:, 0] # multiply by 1.0 makes a copy of the array !
        elif d == 2:
            indc = indc[:, 0] + dimension[0] * indc[:, 1]
        elif d == 3:
            indc = indc[:, 0] + dimension[0] * (indc[:, 1] + dimension[1] * indc[:, 2])
        indc_unique, indc_inv = np.unique(indc, return_inverse=True)
        if len(indc_unique) != len(x):
            if np.any([len(np.unique(v[indc_inv==j])) > 1 for j in range(len(indc_unique))]):
                if verbose > 0:
                    print('ERROR (PLURIGAUSSIANSIM): more than one conditioning point fall in a same grid cell and have different conditioning values')
                return out
            else:
                if verbose > 1:
                    print('WARNING (PLURIGAUSSIANSIM): more than one conditioning point fall in a same grid cell with same conditioning value (consistent)')
                x = np.array([x[indc_inv==j][0] for j in range(len(indc_unique))])
                v = np.array([v[indc_inv==j][0] for j in range(len(indc_unique))])
        #
        # Number of conditioning points
        npt = x.shape[0]
        #
        # Get index in mean_T1 for each conditioning point
        x_mean_T1_grid_ind = None
        if mean_T1.size == 1:
            x_mean_T1_grid_ind = np.zeros(npt, dtype='int')
        else:
            indc_f = (x-origin)/spacing
            indc = indc_f.astype(int)
            indc = indc - 1 * np.all((indc == indc_f, indc > 0), axis=0)
            if d == 1:
                x_mean_T1_grid_ind = 1 * indc[:, 0] # multiply by 1.0 makes a copy of the array !
            elif d == 2:
                x_mean_T1_grid_ind = indc[:, 0] + dimension[0] * indc[:, 1]
            elif d == 3:
                x_mean_T1_grid_ind = indc[:, 0] + dimension[0] * (indc[:, 1] + dimension[1] * indc[:, 2])
        #
        # Get index in var_T1 (if not None) for each conditioning point
        if var_T1 is not None:
            if var_T1.size == 1:
                x_var_T1_grid_ind = np.zeros(npt, dtype='int')
            else:
                if x_mean_T1_grid_ind is not None:
                    x_var_T1_grid_ind = x_mean_T1_grid_ind
                else:
                    indc_f = (x-origin)/spacing
                    indc = indc_f.astype(int)
                    indc = indc - 1 * np.all((indc == indc_f, indc > 0), axis=0)
                    if d == 1:
                        x_var_T1_grid_ind = 1 * indc[:, 0] # multiply by 1.0 makes a copy of the array !
                    elif d == 2:
                        x_var_T1_grid_ind = indc[:, 0] + dimension[0] * indc[:, 1]
                    elif d == 3:
                        x_var_T1_grid_ind = indc[:, 0] + dimension[0] * (indc[:, 1] + dimension[1] * indc[:, 2])
        #
        # Get index in mean_T2 for each conditioning point
        x_mean_T2_grid_ind = None
        if mean_T2.size == 1:
            x_mean_T2_grid_ind = np.zeros(npt, dtype='int')
        else:
            indc_f = (x-origin)/spacing
            indc = indc_f.astype(int)
            indc = indc - 1 * np.all((indc == indc_f, indc > 0), axis=0)
            if d == 1:
                x_mean_T2_grid_ind = 1 * indc[:, 0] # multiply by 1.0 makes a copy of the array !
            elif d == 2:
                x_mean_T2_grid_ind = indc[:, 0] + dimension[0] * indc[:, 1]
            elif d == 3:
                x_mean_T2_grid_ind = indc[:, 0] + dimension[0] * (indc[:, 1] + dimension[1] * indc[:, 2])
        #
        # Get index in var_T2 (if not None) for each conditioning point
        if var_T2 is not None:
            if var_T2.size == 1:
                x_var_T2_grid_ind = np.zeros(npt, dtype='int')
            else:
                if x_mean_T2_grid_ind is not None:
                    x_var_T2_grid_ind = x_mean_T2_grid_ind
                else:
                    indc_f = (x-origin)/spacing
                    indc = indc_f.astype(int)
                    indc = indc - 1 * np.all((indc == indc_f, indc > 0), axis=0)
                    if d == 1:
                        x_var_T2_grid_ind = 1 * indc[:, 0] # multiply by 1.0 makes a copy of the array !
                    elif d == 2:
                        x_var_T2_grid_ind = indc[:, 0] + dimension[0] * indc[:, 1]
                    elif d == 3:
                        x_var_T2_grid_ind = indc[:, 0] + dimension[0] * (indc[:, 1] + dimension[1] * indc[:, 2])
        #
        # Get covariance function for T1, T2 and Y, and their evaluation at 0
        if cov_model_T1 is not None:
            cov_func_T1 = cov_model_T1.func() # covariance function
            cov0_T1 = cov_func_T1(np.zeros(d))
        if cov_model_T2 is not None:
            cov_func_T2 = cov_model_T2.func() # covariance function
            cov0_T2 = cov_func_T2(np.zeros(d))
        #
        if cov_model_T1 is not None:
            # Set kriging matrix for T1 (mat_T1) of order npt, "over every conditioining point"
            mat_T1 = np.ones((npt, npt))
            for i in range(npt-1):
                # lag between x[i] and x[j], j=i+1, ..., npt-1
                h = x[(i+1):] - x[i]
                cov_h_T1 = cov_func_T1(h)
                mat_T1[i, (i+1):npt] = cov_h_T1
                mat_T1[(i+1):npt, i] = cov_h_T1
                mat_T1[i, i] = cov0_T1
            #
            mat_T1[-1,-1] = cov0_T1
            #
            if var_T1 is not None:
                varUpdate = np.sqrt(var_T1[x_var_T1_grid_ind]/cov0_T1)
                mat_T1 = varUpdate*(mat_T1.T*varUpdate).T
        #
        if cov_model_T2 is not None:
            # Set kriging matrix for T2 (mat_T2) of order npt, "over every conditioining point"
            mat_T2 = np.ones((npt, npt))
            for i in range(npt-1):
                # lag between x[i] and x[j], j=i+1, ..., npt-1
                h = x[(i+1):] - x[i]
                cov_h_T2 = cov_func_T2(h)
                mat_T2[i, (i+1):npt] = cov_h_T2
                mat_T2[(i+1):npt, i] = cov_h_T2
                mat_T2[i, i] = cov0_T2
            #
            mat_T2[-1,-1] = cov0_T2
            #
            if var_T2 is not None:
                varUpdate = np.sqrt(var_T2[x_var_T2_grid_ind]/cov0_T2)
                mat_T2 = varUpdate*(mat_T2.T*varUpdate).T

    # Set (again if given) default parameter 'mean' and 'var' for T1, T2
    if cov_model_T1 is not None:
        params_T1['mean'] = mean_T1
        params_T1['var'] = var_T1
    else:
        if mean_T1.size == grid_size:
            params_T1['mean'] = mean_T1.reshape(*dimension[::-1])
        else:
            params_T1['mean'] = mean_T1 * np.ones(dimension[::-1])
    if cov_model_T2 is not None:
        params_T2['mean'] = mean_T2
        params_T2['var'] = var_T2
    else:
        if mean_T2.size == grid_size:
            params_T2['mean'] = mean_T2.reshape(*dimension[::-1])
        else:
            params_T2['mean'] = mean_T2 * np.ones(dimension[::-1])

    # Set default parameter 'verbose' for params_T1, params_T2
    if 'verbose' not in params_T1.keys():
        params_T1['verbose'] = 0
    if 'verbose' not in params_T2.keys():
        params_T2['verbose'] = 0

    # Initialization for output
    Z = []
    if full_output:
        T1 = []
        T2 = []
        n_cond_ok = []

    for ireal in range(nreal):
        # Generate ireal-th realization
        if verbose > 2:
            print('PLURIGAUSSIANSIM: simulation {} of {}...'.format(ireal+1, nreal))
        for ntry in range(ntry_max):
            sim_ok = True
            nhd_ok = [] # to be appended for full output...
            if verbose > 3 and ntry > 0:
                print('   ... new trial ({} of {}) for simulation {} of {}...'.format(ntry+1, ntry_max, ireal+1, nreal))
            if x is None:
                # Unconditional case
                # ------------------
                # Generate T1 (one real)
                if cov_model_T1 is not None:
                    sim_T1 = multiGaussian.multiGaussianRun(cov_model_T1, dimension, spacing, origin,
                                                            mode='simulation', algo=algo_T1, output_mode='array',
                                                            **params_T1, nreal=1)
                else:
                    sim_T1 = params_T1['mean'].reshape(1,*dimension[::-1])
                # -> sim_T1: nd-array of shape
                #      (1, dimension) (for T1 in 1D)
                #      (1, dimension[1], dimension[0]) (for T1 in 2D)
                #      (1, dimension[2], dimension[1], dimension[0]) (for T1 in 3D)
                if sim_T1 is None:
                    sim_ok = False
                    if verbose > 3:
                        print('   ... simulation of T1 failed')
                    continue
                #
                # Generate T2 (one real)
                if cov_model_T2 is not None:
                    sim_T2 = multiGaussian.multiGaussianRun(cov_model_T2, dimension, spacing, origin,
                                                            mode='simulation', algo=algo_T2, output_mode='array',
                                                            **params_T2, nreal=1)
                else:
                    sim_T2 = params_T2['mean'].reshape(1,*dimension[::-1])
                # -> sim_T2: nd-array of shape
                #      (1, dimension) (for T2 in 1D)
                #      (1, dimension[1], dimension[0]) (for T2 in 2D)
                #      (1, dimension[2], dimension[1], dimension[0]) (for T2 in 3D)
                if sim_T2 is None:
                    sim_ok = False
                    if verbose > 3:
                        print('   ... simulation of T2 failed')
                    continue
            #
            else:
                # Conditional case
                # ----------------
                v_T = np.zeros((npt, 2))
                # Initialize: unconditional simulation of T1 at x (values in v_T[:,0])
                ind = np.random.permutation(npt)
                for j, k in enumerate(ind):
                    if cov_model_T1 is not None:
                        # Simulate value at x[k] (= x[ind[j]]), conditionally to the previous ones
                        # Solve the kriging system (for T1)
                        try:
                            w = np.linalg.solve(
                                    mat_T1[ind[:j], :][:, ind[:j]], # kriging matrix
                                    mat_T1[ind[:j], ind[j]], # second member
                                )
                        except:
                            sim_ok = False
                            break

                        # Mean (kriged) value at x[k]
                        mu_T1_k = mean_T1[x_mean_T1_grid_ind[k]] + (v_T[ind[:j], 0] - mean_T1[x_mean_T1_grid_ind[ind[:j]]]).dot(w)
                        # Standard deviation (of kriging) at x[k]
                        std_T1_k = np.sqrt(np.maximum(0, cov0_T1 - np.dot(w, mat_T1[ind[:j], ind[j]])))
                        # Draw value in N(mu_T1_k, std_T1_k^2)
                        v_T[k, 0] = np.random.normal(loc=mu_T1_k, scale=std_T1_k)
                    else:
                        v_T[k, 0] = mean_T1[x_mean_T1_grid_ind[k]]

                if not sim_ok:
                    sim_ok = False
                    if verbose > 3:
                        print('    ... unable to solve kriging system (for T1, initialization)')
                    continue

                # Initialize: unconditional simulation of T2 at x (values in v_T[:,1])
                ind = np.random.permutation(npt)
                for j, k in enumerate(ind):
                    if cov_model_T2 is not None:
                        # Simulate value at x[k] (= x[ind[j]]), conditionally to the previous ones
                        # Solve the kriging system (for T2)
                        try:
                            w = np.linalg.solve(
                                    mat_T2[ind[:j], :][:, ind[:j]], # kriging matrix
                                    mat_T2[ind[:j], ind[j]], # second member
                                )
                        except:
                            sim_ok = False
                            break

                        # Mean (kriged) value at x[k]
                        mu_T2_k = mean_T2[x_mean_T2_grid_ind[k]] + (v_T[ind[:j], 1] - mean_T2[x_mean_T2_grid_ind[ind[:j]]]).dot(w)
                        # Standard deviation (of kriging) at x[k]
                        std_T2_k = np.sqrt(np.maximum(0, cov0_T2 - np.dot(w, mat_T2[ind[:j], ind[j]])))
                        # Draw value in N(mu_T2_k, std_T2_k^2)
                        v_T[k, 1] = np.random.normal(loc=mu_T2_k, scale=std_T2_k)
                    else:
                        v_T[k, 1] = mean_T2[x_mean_T2_grid_ind[k]]

                if not sim_ok:
                    sim_ok = False
                    if verbose > 3:
                        print('    ... unable to solve kriging system (for T2, initialization)')
                    continue

                # Update simulated values v_T at x using Metropolis-Hasting (MH) algorithm
                v_T_k_new = np.zeros(2)
                stop_mh = False
                for nit in range(mh_iter_max):
                    #hd_ok = np.array([flag_value(v_T[k, 0], v_T[k, 1]) == v[k] for k in range(npt)])
                    hd_ok = flag_value(v_T[:, 0], v_T[:, 1]) == v
                    nhd_ok.append(np.sum(hd_ok))
                    if nit >= mh_iter_min:
                        if nhd_ok[-1] == npt:
                            stop_mh = True
                            break
                    else:
                        # Set acceptation probability for bad case
                        p_accept = accept_init * np.power(1.0 - nit/mh_iter_min, accept_pow)
                    if verbose > 4:
                        print('   ... sim {} of {}: MH iter {} of {},  {}...'.format(ireal+1, nreal, nit+1, mh_iter_min, mh_iter_max))
                    ind = np.random.permutation(npt)
                    for k in ind:
                        if nit >= mh_iter_min and hd_ok[k]:
                           #print('skip')
                           continue
                        #
                        # Sequence of indexes without k
                        indmat = np.hstack((np.arange(k), np.arange(k+1, npt)))
                        # Simulate possible new value v_T_new at x[k], conditionally to all the ohter ones
                        #
                        if cov_model_T1 is not None:
                            # Solve the kriging system for T1
                            try:
                                w = np.linalg.solve(
                                        mat_T1[indmat, :][:, indmat], # kriging matrix
                                        mat_T1[indmat, k], # second member
                                    )
                            except:
                                sim_ok = False
                                if verbose > 3:
                                    print('   ... unable to solve kriging system (for T1)')
                                break
                            #
                            # Mean (kriged) value at x[k]
                            mu_T1_k = mean_T1[x_mean_T1_grid_ind[k]] + (v_T[indmat, 0] - mean_T1[x_mean_T1_grid_ind[indmat]]).dot(w)
                            # Standard deviation (of kriging) at x[k]
                            std_T1_k = np.sqrt(np.maximum(0, cov0_T1 - np.dot(w, mat_T1[indmat, k])))
                            # Draw value in N(mu, std^2)
                            v_T_k_new[0] = np.random.normal(loc=mu_T1_k, scale=std_T1_k)
                        else:
                            v_T_k_new[0] = mean_T1[x_mean_T1_grid_ind[k]]
                        #
                        # Solve the kriging system for T2
                        if cov_model_T2 is not None:
                            try:
                                w = np.linalg.solve(
                                        mat_T2[indmat, :][:, indmat], # kriging matrix
                                        mat_T2[indmat, k], # second member
                                    )
                            except:
                                sim_ok = False
                                if verbose > 3:
                                    print('   ... unable to solve kriging system (for T2)')
                                break
                            #
                            # Mean (kriged) value at x[k]
                            mu_T2_k = mean_T2[x_mean_T2_grid_ind[k]] + (v_T[indmat, 1] - mean_T2[x_mean_T2_grid_ind[indmat]]).dot(w)
                            # Standard deviation (of kriging) at x[k]
                            std_T2_k = np.sqrt(np.maximum(0, cov0_T2 - np.dot(w, mat_T2[indmat, k])))
                            # Draw value in N(mu, std^2)
                            v_T_k_new[1] = np.random.normal(loc=mu_T2_k, scale=std_T2_k)
                        else:
                            v_T_k_new[1] = mean_T2[x_mean_T2_grid_ind[k]]
                        #
                        # Accept or not the new candidate
                        if flag_value(v_T_k_new[0], v_T_k_new[1]) == v[k]:
                            # Accept the new candidate
                            v_T[k] = v_T_k_new
                        elif nit < mh_iter_min and np.random.random() < p_accept:
                            # Accept the new candidate
                            v_T[k] = v_T_k_new

                    if not sim_ok:
                        break

                if not sim_ok:
                    continue

                if not stop_mh:
                    hd_ok = flag_value(v_T[:, 0], v_T[:, 1]) == v
                    nhd_ok.append(np.sum(hd_ok))
                if nhd_ok[-1] != npt:
                    # sim_ok kept to True
                    if verbose > 3:
                        print('   ... conditioning failed')
                    if ntry < ntry_max - 1 or not retrieve_real_anyway:
                        continue

                # Generate T1 conditional to (x, v_T[:, 0]) (one real)
                if cov_model_T1 is not None:
                    sim_T1 = multiGaussian.multiGaussianRun(cov_model_T1, dimension, spacing, origin, x=x, v=v_T[:, 0],
                                                           mode='simulation', algo=algo_T1, output_mode='array',
                                                           **params_T1, nreal=1)
                else:
                    sim_T1 = params_T1['mean'].reshape(1,*dimension[::-1])
                # -> sim_T1: nd-array of shape
                #      (1, dimension) (for T1 in 1D)
                #      (1, dimension[1], dimension[0]) (for T1 in 2D)
                #      (1, dimension[2], dimension[1], dimension[0]) (for T1 in 3D)
                if sim_T1 is None:
                    sim_ok = False
                    if verbose > 3:
                        print('   ... conditional simulation of T1 failed')
                    continue
                #
                # Generate T2 conditional to (x, v_T[:, 1]) (one real)
                if cov_model_T2 is not None:
                    sim_T2 = multiGaussian.multiGaussianRun(cov_model_T2, dimension, spacing, origin, x=x, v=v_T[:, 1],
                                                           mode='simulation', algo=algo_T2, output_mode='array',
                                                           **params_T2, nreal=1)
                else:
                    sim_T2 = params_T2['mean'].reshape(1,*dimension[::-1])
                # -> sim_T2: nd-array of shape
                #      (1, dimension) (for T2 in 1D)
                #      (1, dimension[1], dimension[0]) (for T2 in 2D)
                #      (1, dimension[2], dimension[1], dimension[0]) (for T2 in 3D)
                if sim_T2 is None:
                    sim_ok = False
                    if verbose > 3:
                        print('   ... conditional simulation of T2 failed')
                    continue

            # Generate Z (one real)
            if sim_ok:
                if x is not None:
                    if nhd_ok[-1] != npt:
                        if not retrieve_real_anyway:
                            break
                        else:
                            if verbose > 1:
                                print('WARNING (PLURIGAUSSIANSIM): realization does not honoured all data, but retrieved anyway')
                Z_real = flag_value(sim_T1[0], sim_T2[0])
                Z.append(Z_real)
                if full_output:
                    T1.append(sim_T1[0])
                    T2.append(sim_T2[0])
                    n_cond_ok.append(np.asarray(nhd_ok))
                break

    # Get Z
    if verbose > 1 and len(Z) < nreal:
        print('WARNING (PLURIGAUSSIANSIM): some realization failed (missing)')
    Z = np.asarray(Z).reshape(len(Z), *np.atleast_1d(dimension)[::-1])

    if full_output:
        T1 = np.asarray(T1).reshape(len(T1), *np.atleast_1d(dimension)[::-1])
        T2 = np.asarray(T2).reshape(len(T2), *np.atleast_1d(dimension)[::-1])
        return Z, T1, T2, n_cond_ok
    else:
        return Z
# ----------------------------------------------------------------------------
