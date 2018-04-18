from imblearn.over_sampling import SMOTE, ADASYN
from imblearn.under_sampling import EditedNearestNeighbours as ENN
from imblearn.under_sampling import RepeatedEditedNearestNeighbours as RENN
from imblearn.combine import SMOTEENN

def smote_sampling(X, Y):
    kind = 'regular'
    #smote = SMOTE(ratio=ratio, random_state=RND_SEED, kind=kind)
    smote = SMOTE()
    
    nsamples, nx, ny = X.shape
    X = X.reshape((nsamples, nx*ny))
    X,Y = smote.fit_sample(X, Y)
    
    nsamples, ny = X.shape
    X = X.reshape((nsamples, nx, ny/nx))
    Y = Y.reshape((nsamples, 1))

    return X, Y #X_resampled, Y_resampled

def adasyn_sampling(X, Y):
    kind = 'regular'
    #smote = SMOTE(ratio=ratio, random_state=RND_SEED, kind=kind)
       
    nsamples, nx, ny = X.shape
    X = X.reshape((nsamples, nx*ny))
    X,Y = ADASYN().fit_sample(X, Y)
    
    nsamples, ny = X.shape
    X = X.reshape((nsamples, nx, ny/nx))
    Y = Y.reshape((nsamples, 1))

    return X, Y #X_resampled, Y_resampled

def renn_sampling(X,Y):
    enn = ENN(return_indices=True)
    nsamples, nx, ny = X.shape
    print(X.shape)
    X = X.reshape((nsamples, nx*ny))

    X, Y, idx_resampled = enn.fit_sample(X,Y)
    
    nsamples, ny = X.shape
    print(X.shape)
    X = X.reshape((nsamples, nx, ny/nx))
    Y = Y.reshape((nsamples, 1))
    return X, Y

def smote_enn_sampling(X,Y):
    nsamples, nx, ny = X.shape
    X = X.reshape((nsamples, nx*ny))

    X, Y, idx_resampled = SMOTEENN().fit_sample(X,Y)
    
    nsamples, ny = X.shape
    X = X.reshape((nsamples, nx, ny/nx))
    Y = Y.reshape((nsamples, 1))
    return X, Y


def sampling(MODE, X,Y):
    if MODE=='SMOTE':
        return smote_sampling(X,Y)
    elif MODE=='ADASYN':
        return adasyn_sampling(X,Y)
    elif MODE=='ENN':
        return renn_sampling(X,Y)
    elif MODE=='RENN':
        return renn_sampling(X,Y)
    elif MODE=='SMOTEENN':
        return smote_enn_sampling(X,Y)
    else:
        return X,Y


