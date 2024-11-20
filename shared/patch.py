# import pickle
import numpy as np
import sklearn
import gudhi as gd
from gudhi.representations import PersistenceImage, Landscape, BettiCurve
from joblib import Parallel, delayed
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
from sklearn import tree
from gudhi.representations import PersistenceImage
def return_PI(pers_diag, resolution, imrange):
    return PersistenceImage(resolution=resolution, im_range=imrange).fit_transform(pers_diag)

def return_sampled_data(X, y, num_samples):

    X_sample = np.zeros((1, X.shape[1]))
    y_sample = []

    for label in np.unique(y):
        X_sample = np.vstack([X_sample, X[np.random.choice(np.where(y == label)[0], num_samples, replace=False)]])
        y_sample.extend([label for i in range(num_samples)])

    y_sample = np.array(y_sample)
    X_sample = X_sample[1:, :]
    
    return X_sample, y_sample

def compute_persistence_batch(X, Y, block_size, label_vals, num_jobs, pkt_max):    #n_jobs: To specify the size for joblib
    unique_labels = label_vals.unique()
    pers_dgms_0 = {}
    pers_dgms_1 = {}
    
    for label in unique_labels:
        X_label = X[np.where(label_vals == label)[0]]
        Y_label = Y[np.where(label_vals == label)[0]]

        Y_label = Y_label * (block_size/pkt_max)

        res_pers_diags = Parallel(n_jobs=num_jobs, verbose=1)(delayed(compute_persistence_diagram)(X_label[iter][X_label[iter] < block_size], Y_label[iter][X_label[iter] < block_size]) for iter in range(X_label.shape[0]))

        pers_dgms_0[label] = [res_pers_diags[iter][0] for iter in range(len(res_pers_diags))]
        pers_dgms_1[label] = [res_pers_diags[iter][1] for iter in range(len(res_pers_diags))]
    
    for label in pers_dgms_0:
        for idx, dgm in enumerate(pers_dgms_0[label]):
            dgm = dgm[dgm[:, 1] != np.inf]
            pers_dgms_0[label][idx] = dgm

        for idx, dgm in enumerate(pers_dgms_1[label]):
            dgm = dgm[dgm[:,1] != np.inf]
            pers_dgms_1[label][idx] = dgm
    
    return pers_dgms_0, pers_dgms_1


def compute_persistence_diagram(X, Y):
    data = np.column_stack((X, Y))

    ac = gd.AlphaComplex(points = data)

    stree = ac.create_simplex_tree()
    pers = stree.compute_persistence()

    dgm_1 = stree.persistence_intervals_in_dimension(1)
    dgm_0 = stree.persistence_intervals_in_dimension(0)
    
    return dgm_0, dgm_1

def return_bc(pers_diag, xmin, xmax, res):
    return BettiCurve(sample_range=[xmin, xmax], resolution=res).fit_transform(pers_diag)

def compute_betti_curve_batch(xmin, xmax, resolution, pers_diag_0, pers_diag_1, num_jobs):
    l_0 = np.zeros((1, resolution))
    l_1 = np.zeros((1, resolution))

    y_label = []
    
    for label in pers_diag_0.keys():
        res_bc = Parallel(n_jobs=num_jobs, verbose=1)(delayed(return_bc)([pers_diag], xmin, xmax, resolution) for pers_diag in pers_diag_0[label])

        res_bc = np.array(res_bc).reshape(-1, resolution)
        l_0 = np.vstack((l_0, res_bc))

        res_bc = Parallel(n_jobs=num_jobs, verbose=1)(delayed(return_bc)([pers_diag], xmin, xmax, resolution) for pers_diag in pers_diag_1[label])

        res_bc = np.array(res_bc).reshape(-1, resolution)
        l_1 = np.vstack((l_1, res_bc))

        y_label.extend([label for i in range(len(pers_diag_0[label]))])

    l_0 = l_0[1:]
    l_1 = l_1[1:]
    y_label = np.array(y_label)
    
    X_result = np.hstack((l_0, l_1))
    
    return X_result, y_label


def get_timestamps_and_sizes(x):
    timestamps,sizes = zip(*x)
    timestamp_series = pd.Series(timestamps).apply(np.array)
    timestamp_series = timestamp_series - timestamp_series.apply(np.min)
    
    return timestamp_series, pd.Series(sizes).apply(np.array)

def get_labels(labels):
    return pd.Series(labels)

def get_persistence_representation(x, y, vector_type='betti'):
    timestamps, sizes = get_timestamps_and_sizes(x)
    y_lab = get_labels(y)
    
    pers_train_0, pers_train_1 = compute_persistence_batch(timestamps.values, sizes.values, 15, y_lab, -1, 1500)
    if vector_type == 'betti':
        x_betti, y_betti = compute_betti_curve_batch(0, 12, 25, pers_train_0, pers_train_1, -1)
    elif vector_type == 'image':
        x_betti, y_betti = compute_persistence_image_batch(pers_train_0, pers_train_1, [6, 1])
    
    return x_betti, y_betti


def compute_persistence_image_batch(pers_diagram_0, pers_diagram_1, resolution, num_jobs=-1, filename=None): #, labels,
    pers_diag_0 = []
    pers_diag_1 = []
    y = []
    num = 0
    for label in pers_diagram_0.keys():
        pers_diag_0.extend(pers_diagram_0[label])
        pers_diag_1.extend(pers_diagram_1[label])
        y.extend([label for i in range(len(pers_diagram_1[label]))])
        num += 1
    
    res_pi_0 = Parallel(n_jobs=num_jobs, verbose=1)(delayed(return_PI)([pers_diag], resolution, [0,4,0,4]) for pers_diag in pers_diag_0)
    res_pi_0 = np.array(res_pi_0).reshape(-1, resolution[0]*resolution[1])
    res_pi_1 = Parallel(n_jobs=num_jobs, verbose=1)(delayed(return_PI)([pers_diag], resolution, [0,6,0,6]) for pers_diag in pers_diag_1)
    res_pi_1 = np.array(res_pi_1).reshape(-1, resolution[0]*resolution[1])
    print(res_pi_0.shape)
    X = np.hstack([res_pi_0, res_pi_1])
    if filename is not None:
        str_filename = f'{filename}_PI.npy'
        np.save(str_filename, X)
        return str_filename
    
    return X, y


def main(x_train, y_train, x_test, y_test, do_confusion='', display_labels=['Email', 'VS', 'FTP', 'Web', 'VC'], clf_type='GB', vector_type='betti'):
    # Convert x and y into our required formats
    X_train_betti, y_train_betti = get_persistence_representation(x_train, y_train, vector_type)
    return X_train_betti, y_train_betti
    
    clf = None
    if clf_type == 'RF':
        clf = RandomForestClassifier(max_depth=10, n_estimators=100, random_state=42)
    elif clf_type == 'DT':
        clf = tree.DecisionTreeClassifier(max_depth=8, random_state=42, min_samples_leaf=8, min_samples_split=20)
    elif clf_type == 'GB':
        clf = GradientBoostingClassifier(max_depth=4, n_estimators=200, learning_rate=0.02, random_state=42)
    

    clf.fit(X_train_betti, y_train_betti)

    X_test_betti, y_test_betti = get_persistence_representation(x_test, y_test, vector_type)

    training_acc = clf.score(X_train_betti, y_train_betti)
    testing_acc = clf.score(X_test_betti, y_test_betti)
    if len(do_confusion) > 0:
        y_pred = clf.predict(X_test_betti)
        str_labels = [str(lab) for lab in y_pred]
        balance_counter = Counter(str_labels)
        print('balanced_counter', balance_counter.items())


        confusion_matrix = sklearn.metrics.confusion_matrix(y_test_betti[:len(y_pred)], y_pred, normalize='true')
        print(confusion_matrix)

        if len(balance_counter) == len(display_labels):

            disp = ConfusionMatrixDisplay(confusion_matrix=confusion_matrix, display_labels=display_labels)


            disp.plot()
            plt.savefig(do_confusion + '.pdf', bbox_inches='tight')

    print(f'Training Accuracy: {clf.score(X_train_betti, y_train_betti)}')
    print(f'Test Accuracy: {clf.score(X_test_betti, y_test_betti)}')

    return (training_acc, testing_acc, 0)