import numpy as np 
from  optipoly import Pol
import pandas as pd
import random 
from copy import deepcopy
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from sklearn.neighbors import KNeighborsClassifier


def generate_pol(nx, deg, nModes, intercept=True):

    # create a random matrix of integer powers for nx variables with 
    # maximum deg and a number of different lines equal 
    # to nModes

    def generate_line_power(nx, deg_max, intercept=intercept):
        
        # generate a single line of powers with prescribed 
        # upper bound on the sum of the terms. 
        # this function is called multiple times inside 
        # the enclosing function.

        if not intercept:
            again = True
            while again: 
                p = np.zeros(nx)
                for i in range(nx):
                    sum_deg = p.sum()
                    p[i] = np.random.randint(0,deg_max-sum_deg+1)
                if np.sum(p) > 0:
                    again = False
                    return p
        else:
            p = np.zeros(nx)
            for i in range(nx):
                sum_deg = p.sum()
                p[i] = np.random.randint(0,deg_max-sum_deg+1)
            return p


    powers = np.array([generate_line_power(nx, deg, intercept) 
                             for _ in range(nModes)])
    
    # Remove identical lines 
    powers = np.unique(powers, axis=0)
    powers = powers[:, np.random.permutation(powers.shape[1])]
    powers = powers.astype('int32')
    c = np.random.randn(len(powers))

    return powers, c

class Problem:

    """
    The class that defines the problem to be solved. 

    nx: Number of features 
    rho: the side of the hypercube where the features lie 
    degrees: the list of degrees of polynomial over the sub-domain
    nModes_max: maximum number of monomial inside each subdomain
    deg_boundary: the degree of the polynomial defining the boundary 
    nModes_boundary_max: Maximum number of monomial defining the boundaries 
    """

    def __init__(self, nx, rho, degrees, nModes_max=5, 
                 deg_boundary=1, nModes_boundary_max=3):

        nSubModels = len(degrees)

        xmax = np.array([rho] * nx)
        xmin = -xmax
        xmiddle = 0.5 * (xmin+xmax)

        # if any, generate the boundary polynomial 
        if deg_boundary > 0:
            self.pboundary = Pol(*generate_pol(nx=nx, deg=deg_boundary, 
                                               nModes=nModes_boundary_max))
            solmin, _ = self.pboundary.solve(x0=xmiddle, xmax=xmax, xmin=xmin, 
                                 Ntrials=15, ngrid=10000, iter_max=100, 
                                 eps=0.001, psi=lambda v:v)
            solmax, _ = self.pboundary.solve(x0=xmiddle, xmax=xmax, xmin=xmin, 
                                 Ntrials=15, ngrid=10000, iter_max=100, 
                                 eps=0.001, psi=lambda v:-v)
            
            zmin =  solmin.f + 0.1 * abs(solmax.f-solmin.f)
            zmax =  solmax.f - 0.1 * abs(solmax.f-solmin.f)

        else:
            
            self.pboundary = None
            zmin = xmin[0]
            zmax = xmax[0]


        # Compute the right end of the subdomain in z 
        zdiv = np.array([zmin + (i+1) * (zmax-zmin)/nSubModels 
                            for i in range(nSubModels)])

        # The map that compute the index of the subdomain for z 
        def qz(z):
            try: 
                if z > zdiv.max():
                    out = nSubModels-1
                else:
                    out = np.where(zdiv>z)[0][0]
            except:
                out = None
                print(z, zdiv, zmin, zmax)
            
            return out
        
        # Generate the subdomains' polynomials
        pols = [Pol(*generate_pol(nx=nx, deg=degrees[i], 
                    nModes=np.random.randint(1,nModes_max+1), 
                    intercept=True)) 
                for i in range(nSubModels)
            ]
        
        self.nx = nx
        self.xmax = xmax
        self.xmin = xmin
        self.zmin = zmin 
        self.zmax = zmax 
        self.zdiv = zdiv 
        self.qz = qz 
        self.pols = pols
        self.nSubModels = nSubModels
        self.deg_boundary = deg_boundary

    def generate_data(self, nSamples=10000, stratified=False, cv=None, plot=False):

        """
        Generate the benchmark data. 

        INPUTS: 

            nSamples: number of samples 
            stratified: if True, group the data in chunck of piecewise constant subdomains 
            cv: the number of subdomains for each original label. 

        RETURNS: 

            X: Features matrix 
            y: label vector 
            idz: the subdomain indices 
        """

        # Generate X
        R = np.random.rand(nSamples, self.nx)
        X = self.xmin + R * (self.xmax - self.xmin)

        # Compute the corresponding z        
        if self.deg_boundary > 0:
            z = self.pboundary.eval(X).reshape(-1,1)
        else:
            z = X[:,0].reshape(-1,1)

        # Compute the corresponding indices of subdomains
        idz = np.apply_along_axis(self.qz, axis=1, arr=z)
        
        # Compute the resulting label y 
        y = np.zeros(len(X))
        for i in range(self.nSubModels):
            y[idz==i] = self.pols[i].eval(X[idz==i,:])

        # if requrested, stratify the data 
        if stratified and cv is not None:
            X, y, idz = self.stratify_data(X, y, idz, cv=cv)

        if plot:

            fig = make_subplots(x_title='Sample Index', rows=2, cols=1)
            ind = [i for i in range(len(idz))]
            fig.add_trace(go.Scatter(x=ind, y=idz, name='Context indicator'), row=1, col=1)
            fig.add_trace(go.Scatter(x=ind, y=y, name='y-value'), row=2, col=1)
            fig.update_layout(
                width=600,
                height=600,
                title=f'Example of dataset generated by pwBench, nx={self.nx}, {cv=}'
            )
        else:
            fig=None
        
        return X, y, idz, fig
    
    def stratify_data(self, X, y, idz, cv=5):

        """
        Takes the triplet (X, y, idz) issued from random generation 
        and create stratified version by manipulating and ordering 
        the indices. 
        """

        # Create a pandas dataframe to easy the manipulation 
        # start by ordering by subdomain index 
        colX = [f'x{i}' for i in range(self.nx)]
        df = pd.DataFrame(X, columns=colX)
        df['y'] = y
        df['idz'] = idz
        df = df.sort_values(by='idz').reset_index()

    
        ndiv = [int(len(df[df.idz==i])/cv) for i in range(self.nSubModels)]
        panel = []
        for i in range(self.nSubModels):
            dfi = df[df.idz == i].reset_index()
            for j in range(cv):
                panel.append(deepcopy(dfi).iloc[j*ndiv[i]:(j+1)*ndiv[i]])

        random.shuffle(panel)
        df = pd.concat(panel)
            
        X = df[colX].values
        y = df['y'].values.flatten()
        idz = df['idz'].values

        return X, y, idz

    def compute_residual(self, df):

        colX = [c for c in df.columns if c not in ['y', 'idz']]
        df['res'] = [None] * len(df)

        for iz in list(df['idz'].unique()):

            pol = self.pols[iz]
            X_iz = df.loc[df.idz == iz, colX].values
            y_iz = df.loc[df.idz == iz, 'y'].values
            df.loc[df.idz == iz, 'res'] = abs(pol.eval(X_iz)-y_iz)

        return df.res.values

    def create_working_dataframe(self, X, i_anomaly=1, rel_bias=0.1, test_size=0.5):
        '''
        Create a dataframe containing a nominal part [(1-test_size) of the dataframe] 
        followed by a detuned part that is defined by the chosen context indicator 
        i_anomaly, and the amount of relative change in the associated polynomial 
        relationship in that specific context. 

        INPUT ARGUMENTS 

        X           : the features matrix 
        i_anomaly   : the index of context under which the anomaly is introduced. 
        rel_bias    : maximum value of the standard deviation introduced on the parameters for 
                    the specific context.
        test_size   : Define the part of the nominal and detuned part of the dataframe 


        RETURNS 

        df          : The dataframe with columns (x1,...x_n, y, idz)
        res         : The residual profile as computed under perfect knowledge of the relationship
        '''

        # Compute the regions' indicator
        g = self.pboundary.eval(X)
        idz = [self.qz(z) for z in g]

        # Create the nominal dataframe 
        colX = [f'x{i+1}' for i in range(X.shape[1])]
        df = pd.DataFrame(X, columns=colX)
        df['idz'] = idz
        df['y'] = np.zeros(len(df))

        y = np.zeros(len(g))
        for iz in list(df['idz'].unique()):
            X_iz = X[idz==iz,:]
            y[idz==iz] = self.pols[iz].eval(X_iz)
        df['y'] = y
        
        # Generate random error accross the coefficients of the 
        # polynomial dedicated to the context specified by 
        # i_anomaly.
        ncoef = len(self.pols[i_anomaly].coefs)
        eps = rel_bias * np.random.randn(ncoef)
        new_coefs =  (1+eps) * np.array(self.pols[i_anomaly].coefs)

        # Create the associated detuned polynomial 
        pol_detuned = Pol(powers=self.pols[i_anomaly].powers, 
                coefs=new_coefs)
        
        # Update the y column in the dataframe
        nTrain = int((1-test_size) * len(df))
        mask = (np.arange(len(df)) >= nTrain) & (df['idz'].eq(i_anomaly))
        X_iz = df.loc[mask, colX].values
        df.loc[mask, 'y'] = pol_detuned.eval(X_iz)

        res = self.compute_residual(df)

        return df, res
    
def plot_regions(X, idz, col1, col2, k=5, grid_res=100, padding=0.05, title=None):
    """
    Visualize 2D regions defined by integer labels `idz` over columns i and j of X.

    Parameters
    ----------
    X : (n_samples, n_features) array-like
    idz : (n_samples,) array-like of ints (labels)
    i, j : int
        Column indices to visualize.
    k : int
        k for k-NN (k=1 gives Voronoi-like cells per sample).
    grid_res : int
        Resolution of the grid per axis (total grid points = grid_res^2).
    padding : float
        Fractional padding added around data bounds for the plot.
    title : str or None
        Figure title.
    """
    X = np.asarray(X)
    y = np.asarray(idz)

    # Extract the two dimensions
    X2 = X[:, [col1, col2]]

    # Build k-NN classifier on these two features
    clf = KNeighborsClassifier(n_neighbors=k)
    clf.fit(X2, y)

    # Grid covering the data range (with small padding)
    xmin, xmax = X2[:, 0].min(), X2[:, 0].max()
    ymin, ymax = X2[:, 1].min(), X2[:, 1].max()
    xr = xmax - xmin
    yr = ymax - ymin
    xmin -= padding * xr
    xmax += padding * xr
    ymin -= padding * yr
    ymax += padding * yr

    xs = np.linspace(xmin, xmax, grid_res)
    ys = np.linspace(ymin, ymax, grid_res)
    xx, yy = np.meshgrid(xs, ys)
    grid = np.c_[xx.ravel(), yy.ravel()]

    # Predict labels on grid
    y_pred = clf.predict(grid)

    # For discrete coloring: remap labels to 0..L-1 for a clean colorscale
    labels = np.unique(y)
    label_to_idx = {lab: idx for idx, lab in enumerate(labels)}
    z = np.vectorize(label_to_idx.get)(y_pred).reshape(xx.shape)

    # Build a discrete colorscale that matches a qualitative palette
    base_colors = px.colors.qualitative.Plotly
    # Ensure we have enough colors
    while len(base_colors) < len(labels):
        base_colors += base_colors
    colors = base_colors[:len(labels)]
    colorscale = [[k/(len(labels)-1 if len(labels)>1 else 1), c] for k, c in enumerate(colors)]

    fig = go.Figure()

    # Background region map
    fig.add_trace(go.Heatmap(
        x=xs, y=ys, z=z,
        colorscale=colorscale,
        zsmooth='best',  
        showscale=True,
        colorbar=dict(
            title="Label",
            #tickmode="array",
            tickvals=list(range(len(labels))),
            #ticktext=[str(l) for l in labels]
        ),
        hoverinfo="skip"  # hover on points, not on every pixel
    ))

    # Overlay the training points, one trace per label (for a legend)
    for lab, color in zip(labels, colors):
        mask = (y == lab)
        fig.add_trace(go.Scatter(
            x=X2[mask, 0], y=X2[mask, 1],
            mode="markers",
            name='',
            marker=dict(size=6, line=dict(width=0.5, color="black"), color=color),
            hovertemplate=f"Label={lab}<br><extra></extra>",
        ))

    fig.update_layout(
        title="Region of contexts",
        width=600,
        height=500,
        xaxis_title=f"X[:, {col1}]",
        yaxis_title=f"X[:, {col2}]",
        xaxis=dict(constrain="domain"),
        yaxis=dict(scaleanchor="x", scaleratio=1),  # equal aspect ratio
        #legend_title="Samples"
    )

    return fig
    














