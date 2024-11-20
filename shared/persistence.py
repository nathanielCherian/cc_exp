import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import gudhi as gd
from gudhi.representations import PersistenceImage, Landscape, BettiCurve

def compute_persistence_diagram(X, Y):
    data = np.column_stack((X, Y))

    ac = gd.AlphaComplex(points = data)

    stree = ac.create_simplex_tree()
    pers = stree.compute_persistence()

    dgm_1 = stree.persistence_intervals_in_dimension(1)
    dgm_0 = stree.persistence_intervals_in_dimension(0)
    
    return dgm_0, dgm_1

def remove_inf(p):
    return p[np.all(np.isfinite(p), axis=1)]

def compute_bc(p, res=25):
    xmin, xmax = np.min(p), np.max(p)
    bc = BettiCurve(sample_range=[xmin, xmax], resolution=res).fit_transform([p])
    return bc

def compute_bc_new(p0, p1, res=25):
    return BettiCurve(sample_range=[0, np.max(p0)], resolution=12).fit_transform([p0, p1])

def display_persistence(X, Y):
    X = normalize_data(X)
    Y = normalize_data(Y)
    p0, p1 = compute_persistence_diagram(X, Y)
    p0 = remove_inf(p0)
    p1 = remove_inf(p1)
    gd.plot_persistence_barcode(p0)
    gd.plot_persistence_barcode(p1)

def normalize_data(vals):
    # Normalize time    
    val_min = vals.min()
    val_max = vals.max()
    vals_normalized = (vals - val_min) / (val_max - val_min)
    return vals_normalized

def barcode_pipeline(X, Y, together=False):
    X = normalize_data(X)
    Y = normalize_data(Y)
    p0, p1 = compute_persistence_diagram(X, Y)
    if p0.any():
        p0 = remove_inf(p0)
        b0 = compute_bc(p0)[0]
    else:
        b0 = np.array([0]*25)
    
    if p1.any():
        p1 = remove_inf(p1)
        b1 = compute_bc(p1)[0]
    else:
        b1 = np.array([0]*25)
    
    if together:
        vec = compute_bc_new(p0, p1)
        b0, b1 = vec[0], vec[1]
    return np.concatenate((b0, b1), axis=0)


def barcode_pipeline_ndim(data, normalize=True):
    if normalize:
      normalized_data = (data - data.min(axis=0)) / (data.max(axis=0) - data.min(axis=0))
    else:
      normalized_data = data

    #  prinstences(data)
    ac = gd.AlphaComplex(points = normalized_data)
    stree = ac.create_simplex_tree()
    pers = stree.compute_persistence()
    dgm_1 = stree.persistence_intervals_in_dimension(1)
    dgm_0 = stree.persistence_intervals_in_dimension(0)

    if dgm_0.any():
        dgm_0 = remove_inf(dgm_0)
        b0 = compute_bc(dgm_0)[0]
    else:
        b0 = np.array([0]*25)

    if dgm_1.any():
        dgm_1 = remove_inf(dgm_1)
        b1 = compute_bc(dgm_1)[0]
    else:
        b1 = np.array([0]*25)

    return np.concatenate((b0, b1), axis=0)
