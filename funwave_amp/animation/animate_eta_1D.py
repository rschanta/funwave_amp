import os
import numpy as np
import matplotlib
matplotlib.use("Agg")   # must be before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import funwave_amp as fpy

def animate_eta_1D(ds):
    '''
    Animates the surface profile of a 1D simulation, where Nglob == 1. 
    '''
    ## UNPACK ---------------------------------------------------------------------
    # Coordinates
    X = ds.X.values
    Z = -ds.Z.values[:,0]
    # Eta
    eta = ds.eta.values[:,0,:]
    # Common elements
    Xc_WK = ds.Xc_WK
    h = ds.DEP_WK
    ITER = ds.ITER
    ## [END] UNPACK ---------------------------------------------------------------
    
    
    
    ## BASIC PLOT FORMATTING ------------------------------------------------------
    fig, ax = plt.subplots(dpi=135)
    ax.set_title(f'tri_{ITER:05d}')
    ax.set_xlabel('x [m]'); ax.set_ylabel('z [m]')
    ax.set_xlim(0,X[-1]); ax.set_ylim(-1.1*h,h/2)
    ## [END] BASIC PLOT FORMATTING ------------------------------------------------
    
    
    
    ## Common Elements-------------------------------------------------------------
    # Wavemaker
    ax.axvline(Xc_WK,color='red',label='Xc_WK',zorder=-1,ls='--')
    # Bathymetry
    ax.plot(X,Z, color='black')
    ax.fill_between(X,Z,-1.1*h*np.ones_like(h),
                    color='darkgrey')
    # Water
    ax.fill_between(X,Z,np.zeros_like(Z),
                    color='aqua',zorder=-2)
    # Text box
    time_text = ax.text(
        0.02, 0.95, '', transform=ax.transAxes,
        bbox=dict(facecolor='white', edgecolor='black', 
                  boxstyle='square,pad=0.3', alpha=1.0)
    )
    ## [END] Common Elements-------------------------------------------------------
    
    
    # SPECIALIZED ELEMENTS --------------------------------------------------------
    if "Sponge_west_width" in ds.attrs:
        SWW = ds.Sponge_west_width
        i_SWW = np.argmin(np.abs(X-SWW)) + 1
        ax.fill_between(X[0:i_SWW], Z[0:i_SWW],np.zeros_like(Z[0:i_SWW]),
                        color='lightgreen',label='W. Sponge')
        
    if "Sponge_east_width" in ds.attrs:
        SEW = ds.Sponge_east_width
        SEWx = X[-1] - SEW
        i_SEW = np.argmin(np.abs(X-SEWx)) + 1
        ax.fill_between(X[i_SEW:-1], Z[i_SEW:-1],np.zeros_like(Z[i_SEW:-1]),
                        color='lime',label='E. Sponge')
    
    if 'BW_Width' in ds:
        i_no,boolean = np.nonzero(ds.BW_Width.values)
        BW_first,BW_last = i_no[0], i_no[-1]
        ax.fill_between(X[BW_first:BW_last], Z[BW_first:BW_last],np.zeros_like(Z[BW_first:BW_last]),
                        color='plum',label='Breakwater')
        
    if 'friction' in ds:
        i_no,boolean = np.nonzero(ds.friction.values)
        Fr_first,Fr_last = i_no[0], i_no[-1]
        ax.plot(X[Fr_first:Fr_last], Z[Fr_first:Fr_last], lw = 2,
                        color='orange',label='Friction',ls='--')
        
    if "Mglob_gage" in ds:
        Mglob_gage = ds.Mglob_gage.values
        for k, m in enumerate(Mglob_gage):
            if k == 0:
                ax.plot([X[m],X[m]],[-0.1*h,0.1*h],ls='--',color='grey',lw=1,label='Gages')
            else:
                ax.plot([X[m],X[m]],[-0.1*h,0.1*h],ls='--',color='grey',lw=1)
         
    # [END] SPECIALIZED ELEMENTS --------------------------------------------------
    
    
    
    # TIME UPDATING ELEMENTS ------------------------------------------------------
    # Eta
    line, = ax.plot(X, eta[0, :], color='blue')
    
    # nubrk
    if "nubrk" in ds:
        nubrk = ds.nubrk.values[:,0,:]
        mask = nubrk[0] != 0
        nubrk_line = ax.scatter(X[mask], nubrk[0, mask], 
                                color='red',zorder=10,label='Breaking')
    # [END] TIME UPDATING ELEMENTS ------------------------------------------------
    
    
    ## LEGEND
    ax.legend(loc='upper right',ncol=2,fontsize=6,fancybox=False)
    
    
    ## UPDATE ---------------------------------------------------------------------
    def update(frame):
        line.set_ydata(eta[frame, :])
        time_text.set_text(f'Time step: {frame}')
    
        if "nubrk" in ds:
            mask = nubrk[frame] != 0
            coords = np.column_stack((X[mask], eta[frame, mask]))
            nubrk_line.set_offsets(coords)
            nubrk_line.set_facecolors(['red'] * mask.sum())   # all red nonzeros
    
        if frame % 50 == 0:
            print(f"Frame {frame}/{eta.shape[0]-1}")
    
        # If nubrk exists, return nubrk_line too
        return (line, time_text, nubrk_line) if "nubrk" in ds else (line, time_text)
    ## [END] UPDATE ---------------------------------------------------------------
    
    
    # Acess necessary paths
    ani_dir = os.getenv("ani")
    save_path = os.path.join(ani_dir,f'tri_{ITER:05d}.mp4')
    # Animation
    ani = FuncAnimation(fig, update, frames=eta.shape[0], blit=True, interval=30)
    ani.save(save_path, writer="ffmpeg", fps=30)
    
    
    return