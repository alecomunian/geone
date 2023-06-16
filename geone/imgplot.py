#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python module:  'imgplot.py'
author:         Julien Straubhaar
date:           dec-2017

Definition of functions for plotting images (geone.Img class).
"""

from geone import img
from geone.img import Img
from geone import customcolors as ccol
from geone.customcolors import add_colorbar

import numpy as np
import matplotlib.pyplot as plt

from matplotlib import rcParams as mpl_rcParams
import matplotlib.colors as mcolors

# ----------------------------------------------------------------------------
def drawImage2D(
        im, ix=None, iy=None, iz=None, iv=None,
        plot_empty_grid=False,
        cmap=ccol.cmap_def,
        alpha=None,
        excludedVal=None,
        categ=False, categVal=None,
        categCol=None, categColCycle=False, categColbad=ccol.cbad_def,
        vmin=None, vmax=None,
        contourf=False,
        contour=False,
        contour_clabel=False,
        levels=None,
        contourf_kwargs={},
        contour_kwargs={'linestyles':'solid', 'colors':'gray'},
        contour_clabel_kwargs={'inline':1},
        interpolation='none',
        aspect='equal',
        frame=True, xaxis=True, yaxis=True,
        title=None,
        xlabel=None, xticks=None, xticklabels=None, xticklabels_max_decimal=None,
        ylabel=None, yticks=None, yticklabels=None, yticklabels_max_decimal=None,
        clabel=None, cticks=None, cticklabels=None, cticklabels_max_decimal=None,
        colorbar_extend='neither',
        colorbar_aspect=20, colorbar_pad_fraction=1.0,
        showColorbar=True,
        removeColorbar=False,
        showColorbarOnly=0,
        #animated=False,
        **kwargs):
    """
    Draws an 2D image (can be a slice of a 3D image):

    :param im:  (img.Img class) image
    :param ix:  (int or None) index along x-axis of the yz-slice to be drawn
    :param iy:  (int or None) index along y-axis of the xz-slice to be drawn
    :param iz:  (int or None) index along z-axis of the xy-slice to be drawn
                    only one of the parameters ix, iy, iz should be specified,
                    or none of them (in this case, iz is set to 0)
    :param iv:  (int or None) index of the variable to be drawn,
                    if None (default):
                         - if im.nv > 0: iv is set to 0, i.e. variable of index
                            0 will be plotted
                         - otherwise (im.nv=0): an "empty grid is plotted, i.e.
                            a fake variable with nan over the entire grid is
                            considered
    :param plot_empty_grid:
                (bool) if True, an "empty grid is plotted, i.e. a fake variable
                    with nan over the entire grid is considered ('iv' is ignored)

    :param cmap:    colormap (can be a string: in this case the color map
                        matplotlib.pyplot.get_cmap(cmap) is used)

    :param alpha:   (float or None) values of alpha channel for transparency
                        (if None, value 1.0 is used (no transparency))

    :param excludedVal: (int/float or sequence or None) values to be
                            excluded from the plot.
                            Note: not used if categ is True and categVal is
                            not None
    :param categ:       (bool) indicates if the variable of the image to plot
                            has to be treated as categorical (True) or as
                            continuous (False)
    :param categVal:    (int/float or sequence or None)
                            -- used only if categ is True --
                            explicit list of the category values to be
                            displayed (if None, the list of all unique values
                            are automatically computed)
    :param categCol:    (sequence or None)
                            -- used only if categ is True --
                            colors (given by string or rgb-tuple) used for the
                            category values that will be displayed:
                                If categVal is not None: categCol must have
                                    the same length as categVal,
                                else: first entries of categCol are used if its
                                    length is greater or equal to the number
                                    of displayed category values, otherwise:
                                    the entries of categCol are used cyclically
                                    if categColCycle is True and otherwise,
                                    colors taken from the colormap cmap are used
    :param categColCycle:
                        (bool)
                            -- used only if categ is True --
                            indicates if the entries of categCol can be used
                            cyclically or not (when the number of displayed
                            category values exceeds the length of categCol)
    :param categColbad:  color for bad categorical value
                            -- used only if categ is True --

    :param vmin, vmax:      (float) min and max values to be plotted
                                -- used only if categ is False --
    :param contourf:        (bool) indicates if plot with plt.contourf, i.e.
                                contour map with filled area between levels,
                                instead of standard plot (plt.imshow)
    :param contour:         (bool) indicates if contour levels are added to the
                                plot (plt.contour)
                            (dict) keyword arguments passed to plt.contour
    :param contour_clabel:  (bool) indicates if labels are added to contour
                                (ignored if 'contour' is False)
    :param levels:          (int or array-like or None) keyword argument 'levels'
                                passed to plt.contourf (used if 'contourf' is
                                True) and/or plt.contour (used if 'contour' is
                                True), can be: None (default), number of levels,
                                or sequence of level values
    :param contourf_kwargs: (dict) keyword arguments passed to plt.contourf
                                (the argument 'levels' (see above) is used as
                                keyword argument for plt.contourf, i.e. it
                                prevails over the key 'levels' in
                                'contourf_kwargs' (if given))
    :param contour_kwargs:  (dict) keyword arguments passed to plt.contour
                                (the argument 'levels' (see above) is used as
                                keyword argument for plt.contourf, i.e. it
                                prevails over the key 'levels' in
                                'contourf_kwargs' (if given))
    :param contour_clabel_kwargs:
                            (dict) keyword arguments passed to plt.clabel
                                relying on the contour plot
    :param interpolation:   (string) 'interpolation' parameters to be passed
                                to plt.imshow()
    :param aspect:          (string or scalar) 'aspect' parameters to be passed
                                to plt.imshow()
    :param frame:           (bool) indicates if a frame is drawn around the
                                image
    :param xaxis, yaxis:    (bool) indicates if x-axis (resp. y-axis) is
                                visible
    :param title:       (string or None) title of the figure
    :param xlabel, ylabel, clabel:
                        (string or None) label for x-axis, y-axis, colorbar
                            respectively
    :param xticks, yticks, cticks:
                        (sequence or None) sequence where to place ticks along
                            x-axis, y-axis, colorbar respectively,
                            None by default
    :param xticklabels, yticklabels, cticklabels:
                        (sequence or None) sequence of labels for ticks along
                            x-axis, y-axis, colorbar respectively,
                            None by default
    :param xticklabels_max_decimal, yticklabels_decimal, cticklabels_max_decimal:
                        (int or None) maximal number of decimals (fractional part)
                            for ticks labels along x-axis, y-axis, colorbar
                            respectively,
                            (not used if xticklabels, yticklabels, cticklabels
                            are respectively given)
                            None by default
    :param colorbar_extend: (string)
                                -- used only if categ is False --
                                keyword argument 'extend' to be passed
                                to plt.colorbar() /
                                geone.customcolors.add_colorbar(), can be:
                                    'neither' | 'both' | 'min' | 'max'
    :param colorbar_aspect: (float or int) keyword argument 'aspect' to be
                                passed to geone.customcolors.add_colorbar(),
    :param colorbar_pad_fraction:
                            (float or int) keyword argument 'pad_fraction' to
                                be passed to
                                geone.customcolors.add_colorbar(),
                                (not used if showColorbar is False)
    :param showColorbar:    (bool) indicates if the colorbar (vertical) is drawn
    :param removeColorbar:  (bool) if True (and if showColorbar is True), then
                                the colorbar is removed (not used if showColorbar
                                is False)
                                (Note: it can be useful to draw and then remove
                                the colorbar for size of the plotted image...)
    :param showColorbarOnly:(int) indicates if only the colorbar (vertical) is
                                drawn; possible values:
                                - 0    : not applied
                                - not 0: only the colorbar is shown (even if
                                         showColorbar is False or if
                                         removeColorbar is True):
                                         - 1: the plotted image is "cleared"
                                         - 2: an image of same color as the
                                              background is drawn onto the
                                              plotted image
    # :param animated:        (bool) passed to imshow for for matplotlib animation...
    #                             default: False

    :param kwargs: additional keyword arguments:
        Each keyword argument with the key "xxx_<name>" will be passed as
        keyword argument with the key "<name>" to a function related to "xxx".
        Possibilities for "xxx_" and related function
            - "title_"         fun: ax.set_title()
            - "xlabel_"        fun: ax.set_xlabel()
            - "xticks_"        fun: ax.set_xticks()
            - "xticklabels_"   fun: ax.set_xticklabels()
            - "ylabel_"        fun: ax.set_ylabel()
            - "yticks_"        fun: ax.set_yticks()
            - "yticklabels_"   fun: ax.set_yticklabels()
            - "clabel_"        fun: cbar.set_label()
            - "cticks_"        fun: cbar.set_ticks()
            - "cticklabels_"   fun: cbar.ax.set_yticklabels()
        Examples:
            - title_fontsize, <x|y|c>label_fontsize
            - title_fontweight, <x|y|c>label_fontweight
                Possible values: numeric value in 0-1000 or one
                of ‘ultralight’, ‘light’, ‘normal’, ‘regular’,
                ‘book’, ‘medium’, ‘roman’, ‘semibold’,
                ‘demibold’, ‘demi’, ‘bold’, ‘heavy’,
                ‘extra bold’, ‘black’
        Notes:
            - default value for font size is matplotlib.rcParams['font.size']
            - default value for font weight is matplotlib.rcParams['font.weight']

    :return:    imout: "list of matplotlib object"
                #   (ax, cbar) axis and colorbar of the plot
    """

    fname = 'drawImage2D'

    # Initialization for output
    imout = []
    #ax, cbar = None, None

    if plot_empty_grid:
        iv = None
    else:
        # Check / set iv
        if iv is None:
            if im.nv > 0:
                iv = 0
        else:
            if iv < 0:
                iv = im.nv + iv

            if iv < 0 or iv >= im.nv:
                print(f'ERROR ({fname}): invalid iv index!')
                return imout
                #return (ax, cbar)

    # Check slice direction and indices
    n = int(ix is not None) + int(iy is not None) + int(iz is not None)

    if n == 0:
        sliceDir = 'z'
        iz = 0

    elif n==1:
        if ix is not None:
            if ix < 0:
                ix = im.nx + ix

            if ix < 0 or ix >= im.nx:
                print(f'ERROR ({fname}): invalid ix index!')
                return imout
                #return (ax, cbar)

            sliceDir = 'x'

        elif iy is not None:
            if iy < 0:
                iy = im.ny + iy

            if iy < 0 or iy >= im.ny:
                print(f'ERROR ({fname}): invalid iy index!')
                return imout
                #return (ax, cbar)

            sliceDir = 'y'

        else: # iz is not None
            if iz < 0:
                iz = im.nz + iz

            if iz < 0 or iz >= im.nz:
                print(f'ERROR ({fname}): invalid iz index!')
                return imout
                #return (ax, cbar)

            sliceDir = 'z'

    else: # n > 1
        print(f'ERROR ({fname}): slice specified in more than one direction!')
        return imout
        #return (ax, cbar)

    # Extract what to be plotted
    if sliceDir == 'x':
        dim0 = im.ny
        min0 = im.oy
        max0 = im.ymax()

        dim1 = im.nz
        min1 = im.oz
        max1 = im.zmax()
        if iv is None: # empty image
            zz = np.nan * np.ones((im.nz, im.ny))
        else:
            zz = np.array(im.val[iv, :, :, ix].reshape(dim1, dim0)) # np.array() to get a copy
                # reshape to force 2-dimensional array

    elif sliceDir == 'y':
        dim0 = im.nx
        min0 = im.ox
        max0 = im.xmax()

        dim1 = im.nz
        min1 = im.oz
        max1 = im.zmax()
        if iv is None: # empty image
            zz = np.nan * np.ones((im.nz, im.nx))
        else:
            zz = np.array(im.val[iv, :, iy, :].reshape(dim1, dim0)) # np.array() to get a copy

    else: # sliceDir == 'z'
        dim0 = im.nx
        min0 = im.ox
        max0 = im.xmax()

        dim1 = im.ny
        min1 = im.oy
        max1 = im.ymax()
        if iv is None: # empty image
            zz = np.nan * np.ones((im.ny, im.nx))
        else:
            zz = np.array(im.val[iv, iz, :, :].reshape(dim1, dim0)) # np.array() to get a copy

    # Get the color map
    if isinstance(cmap, str):
        try:
            cmap = plt.get_cmap(cmap)
        except:
            print(f'ERROR ({fname}): invalid cmap string!')
            return imout
            #return (ax, cbar)

    if categ:
        # --- Treat categorical variable ---
        if categCol is not None\
                and type(categCol) is not list\
                and type(categCol) is not tuple:
            print(f"ERROR ({fname}): 'categCol' must be a list or a tuple (if not None)!")
            return imout
            #return (ax, cbar)

        # Get array 'dval' of displayed values
        if categVal is not None:
            dval = np.array(categVal).reshape(-1) # force to be an 1d array

            if len(np.unique(dval)) != len(dval):
                print(f"ERROR ({fname}): 'categVal' contains duplicated entries!")
                return imout
                #return (ax, cbar)

            # Check 'categCol' (if not None)
            if categCol is not None and len(categCol) != len(dval):
                print(f"ERROR ({fname}): length of 'categVal' and 'categCol' differs!")
                return imout
                #return (ax, cbar)

        else:
            # Possibly exclude values from zz
            if excludedVal is not None:
                for val in np.array(excludedVal).reshape(-1):
                    np.putmask(zz, zz == val, np.nan)

            # Get the unique value in zz
            dval = np.array([v for v in np.unique(zz).reshape(-1) if ~np.isnan(v)])

        if not len(dval): # len(dval) == 0
            print("Warning: no value to be drawn!")

        # Replace dval[i] by i in zz and other values by np.nan
        zz2 = np.array(zz) # copy array
        zz[...] = np.nan # initialize
        for i, v in enumerate(dval):
            zz[zz2 == v] = i

        del zz2

        # Set 'colorList': the list of colors to use
        colorList = None
        if categCol is not None:
            if len(categCol) >= len(dval):
                colorList = [categCol[i] for i in range(len(dval))]
                # colorList = [mcolors.ColorConverter().to_rgba(categCol[i]) for i in range(len(dval))]

            elif categColCycle:
                print("Warning: 'categCol' is used cyclically (too few entries)")
                colorList = [categCol[i%len(categCol)] for i in range(len(dval))]

            else:
                print("Warning: 'categCol' not used (too few entries)")

        if colorList is None:
            # Use colors from cmap
            colorList = [cmap(x) for x in np.arange(len(dval)) * 1.0/(len(dval)-1)]

        # Set the colormap: 'cmap'
        if len(dval) == 1:
            cmap = ccol.custom_cmap([colorList[0], colorList[0]], ncol=2,
                                    cbad=categColbad, alpha=alpha)

        else: # len(dval) == len(colorList) > 1
            # cmap = mcolors.ListedColormap(colorList)
            cmap = ccol.custom_cmap(colorList, ncol=len(colorList),
                                    cbad=categColbad, alpha=alpha)

        # Set the min and max of the colorbar
        vmin, vmax = -0.5, len(dval) - 0.5

        # Set colorbar ticks and ticklabels if not given
        if cticks is None:
            cticks = range(len(dval))

        if cticklabels is None:
            #cticklabels = ['{:.3g}'.format(v) for v in cticks]
            cticklabels = ['{:.3g}'.format(v) for v in dval]

        # Reset cextend if needed
        colorbar_extend = 'neither'

    else: # categ == False
        # --- Treat continuous variable ---
        # Possibly exclude values from zz
        if excludedVal is not None:
            for val in np.array(excludedVal).reshape(-1): # force to be an 1d array
                np.putmask(zz, zz == val, np.nan)

    # Generate "sub-dictionaries" from kwargs
    #   For each item 'xxx_<name>':<value> from kwargs (whose the key begins
    #   with "xxx_"): the item '<name>':<value> is added to the dictionary
    #   xxx_kwargs
    #   "xxx_" is replaced by the strings below (in sub_prefix list)
    # These sub-dictionaries are passed (unpacked) as keyword arguments to
    # functions that draw labels, ticklabels, ...
    title_kwargs = {}

    xlabel_kwargs = {}
    xticks_kwargs = {}
    xticklabels_kwargs = {}

    ylabel_kwargs = {}
    yticks_kwargs = {}
    yticklabels_kwargs = {}

    clabel_kwargs = {}
    cticks_kwargs = {}
    cticklabels_kwargs = {}

    sub_prefix = ['title_',
                  'xlabel_', 'xticks_', 'xticklabels_',
                  'ylabel_', 'yticks_', 'yticklabels_',
                  'clabel_', 'cticks_', 'cticklabels_']
    sub_kwargs = [title_kwargs,
                  xlabel_kwargs, xticks_kwargs, xticklabels_kwargs,
                  ylabel_kwargs, yticks_kwargs, yticklabels_kwargs,
                  clabel_kwargs, cticks_kwargs, cticklabels_kwargs] # list of dictionaries

    for k, v in kwargs.items():
        for i in range(len(sub_kwargs)):
            n = len(sub_prefix[i])
            if k[0:n] == sub_prefix[i]:
                sub_kwargs[i][k[n:]] = v # add item k[n:]:v to dictionary sub_kwargs[i]

    if showColorbarOnly:
        # Overwrite some parameters if needed
        frame = False
        xaxis = False
        yaxis = False
        title = None
        showColorbar = True
        removeColorbar = False

    # Get current axis (for plotting)
    ax = plt.gca()

    # image plot
    im_plot = ax.imshow(zz, cmap=cmap, alpha=alpha, vmin=vmin, vmax=vmax,
                        origin='lower', extent=[min0, max0, min1, max1],
                        interpolation=interpolation, aspect=aspect) #, animated=animated)
    imout.append(im_plot)

    if contourf:
        # imshow is still used above to account for 'aspect'
        # Set key word argument 'levels' from the argument 'levels'
        contourf_kwargs['levels']=levels
        im_contf = ax.contourf(zz, cmap=cmap, alpha=alpha, vmin=vmin, vmax=vmax,
                              origin='lower', extent=[min0, max0, min1, max1],
                              **contourf_kwargs)
        imout.append(im_contf)

    if contour:
        # Set key word argument 'levels' from the argument 'levels'
        contour_kwargs['levels']=levels
        im_cont = ax.contour(zz,
                              origin='lower', extent=[min0, max0, min1, max1],
                              **contour_kwargs)
        imout.append(im_cont)
        if contour_clabel:
            ax.clabel(im_cont, **contour_clabel_kwargs)

    # title
    if title is not None:
        ax.set_title(title, **title_kwargs)

    # xlabel, xticks and xticklabels
    if xlabel is not None:
        ax.set_xlabel(xlabel, **xlabel_kwargs)

    if xticks is not None:
        ax.set_xticks(xticks, **xticks_kwargs)

    if xticklabels is not None:
        ax.set_xticklabels(xticklabels, **xticklabels_kwargs)
    elif xticklabels_max_decimal is not None:
        s = 10**xticklabels_max_decimal
        labels = [np.round(t*s)/s for t in ax.get_xticks()]
        ax.set_xticklabels(labels, **xticklabels_kwargs)
    elif len(xticklabels_kwargs):
        ax.set_xticklabels(ax.get_xticks(), **xticklabels_kwargs)
    # else... default xticklabels....

    # ylabel, yticks and yticklabels
    if ylabel is not None:
        ax.set_ylabel(ylabel, **ylabel_kwargs)

    if yticks is not None:
        ax.set_yticks(yticks, **yticks_kwargs)

    if yticklabels is not None:
        ax.set_yticklabels(yticklabels, **yticklabels_kwargs)
    elif yticklabels_max_decimal is not None:
        s = 10**yticklabels_max_decimal
        labels = [np.round(t*s)/s for t in ax.get_yticks()]
        ax.set_yticklabels(labels, **yticklabels_kwargs)
    elif len(yticklabels_kwargs):
        ax.set_yticklabels(ax.get_yticks(), **yticklabels_kwargs)
    # else... default yticklabels....

    # Display or hide: frame, xaxis, yaxis
    if not frame:
        ax.set_frame_on(False)

    if not xaxis:
        ax.get_xaxis().set_visible(False)

    if not yaxis:
        ax.get_yaxis().set_visible(False)

    # Colorbar
    if showColorbar:
        cbar_kwargs = {'aspect':colorbar_aspect, 'pad_fraction':colorbar_pad_fraction}
        if not contourf:
            cbar_kwargs['extend']=colorbar_extend
        cbar = add_colorbar(im_plot, **cbar_kwargs)

        if clabel is not None:
            cbar.set_label(clabel, **clabel_kwargs)

        if cticks is not None:
            cbar.set_ticks(cticks, **cticks_kwargs)

        if cticklabels is not None:
            cbar.ax.set_yticklabels(cticklabels, **cticklabels_kwargs)
        elif cticklabels_max_decimal is not None:
            s = 10**cticklabels_max_decimal
            labels = [np.round(t*s)/s for t in cbar.get_ticks()]
            cbar.ax.set_yticklabels(labels, **cticklabels_kwargs)
        elif len(cticklabels_kwargs):
            cbar.ax.set_yticklabels(cbar.get_ticks(), **cticklabels_kwargs)
        # else... default cticklabels....

        if removeColorbar:
            # cbar.ax.get_xaxis().set_visible(False)
            # cbar.ax.get_yaxis().set_visible(False)
            # cbar.ax.clear()
            cbar.ax.set_visible(False)

    if showColorbarOnly:
        if showColorbarOnly == 1:
            ax.clear() # change the size of the colorbar...
        else:
            # Trick: redraw the image in background color...
            zz[...] = 0
            # bg_color = mpl_rcParams['figure.facecolor'] # background color
            bg_color = ax.get_facecolor() # background color
            # bg_color = plt.gcf().get_facecolor()  # background color
            ncmap = ccol.custom_cmap([bg_color,bg_color], ncol=2)
            ax.imshow(zz, cmap=ncmap)
            ax.set_frame_on(True)
            for pos in ('bottom', 'top', 'right', 'left'):
                ax.spines[pos].set_color(bg_color)
                ax.spines[pos].set_linewidth(10)

    return imout
    #return (ax, cbar)
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
def get_colors_from_values(
        val,
        cmap=ccol.cmap_def,
        alpha=None,
        excludedVal=None,
        categ=False, categVal=None,
        categCol=None, categColCycle=False, categColbad=ccol.cbad_def,
        vmin=None, vmax=None,
        cmin=None, cmax=None):
    """
    Get the colors for given values, according to color settings (as in function
    drawImage2D).

    :param val:     (float or array of floats) values
    :param cmap, alpha, excludedVal, categ, categVal, categCol, categColCycle,
        categColbad, vmin, vmax:
                    settings as in function drawIamge2D.
    :param cmin, cmax: alternative keyword for vmin, vmax (for compatibility with
                    color settings in the functions of the module imgplot3d)

    :return col:    (array) color for each values in val according to given
                        settings
    """

    fname = 'get_colors_from_values'

    # Check vmin, cmin and vmax, cmax
    if vmin is not None and cmin is not None:
        print(f'ERROR ({fname}): use vmin or cmin (not both)')
        return None

    if vmax is not None and cmax is not None:
        print(f'ERROR ({fname}): use vmax or cmax (not both)')
        return None

    if vmin is None:
        vmin = cmin

    if vmax is None:
        vmax = cmax

    # Copy val in a 1d array
    zz = np.copy(np.atleast_1d(val)).reshape(-1)

    # --- Code adapted from function drawImage2D - start ----
    # Get the color map
    if isinstance(cmap, str):
        try:
            cmap = plt.get_cmap(cmap)
        except:
            print(f'ERROR ({fname}): invalid cmap string!')
            return None
            # return imout
            # #return (ax, cbar)

    if categ:
        # --- Treat categorical variable ---
        if categCol is not None\
                and type(categCol) is not list\
                and type(categCol) is not tuple:
            print(f"ERROR ({fname}): 'categCol' must be a list or a tuple (if not None)!")
            return None
            # return imout
            # #return (ax, cbar)

        # Get array 'dval' of displayed values
        if categVal is not None:
            dval = np.array(categVal).reshape(-1) # force to be an 1d array

            if len(np.unique(dval)) != len(dval):
                print(f"ERROR ({fname}): 'categVal' contains duplicated entries!")
                return None
                # return imout
                # #return (ax, cbar)

            # Check 'categCol' (if not None)
            if categCol is not None and len(categCol) != len(dval):
                print(f"ERROR ({fname}): length of 'categVal' and 'categCol' differs!")
                return None
                # return imout
                # #return (ax, cbar)

        else:
            # Possibly exclude values from zz
            if excludedVal is not None:
                for val in np.array(excludedVal).reshape(-1):
                    np.putmask(zz, zz == val, np.nan)

            # Get the unique value in zz
            dval = np.array([v for v in np.unique(zz).reshape(-1) if ~np.isnan(v)])

        if not len(dval): # len(dval) == 0
            print("Warning: no value to be drawn!")

        # Replace dval[i] by i in zz and other values by np.nan
        zz2 = np.array(zz) # copy array
        zz[...] = np.nan # initialize
        for i, v in enumerate(dval):
            zz[zz2 == v] = i

        del zz2

        # Set 'colorList': the list of colors to use
        colorList = None
        if categCol is not None:
            if len(categCol) >= len(dval):
                colorList = [categCol[i] for i in range(len(dval))]
                # colorList = [mcolors.ColorConverter().to_rgba(categCol[i]) for i in range(len(dval))]

            elif categColCycle:
                print("Warning: 'categCol' is used cyclically (too few entries)")
                colorList = [categCol[i%len(categCol)] for i in range(len(dval))]

            else:
                print("Warning: 'categCol' not used (too few entries)")

        if colorList is None:
            # Use colors from cmap
            colorList = [cmap(x) for x in np.arange(len(dval)) * 1.0/(len(dval)-1)]

        # Set the colormap: 'cmap'
        if len(dval) == 1:
            cmap = ccol.custom_cmap([colorList[0], colorList[0]], ncol=2,
                                    cbad=categColbad, alpha=alpha)

        else: # len(dval) == len(colorList) > 1
            # cmap = mcolors.ListedColormap(colorList)
            cmap = ccol.custom_cmap(colorList, ncol=len(colorList),
                                    cbad=categColbad, alpha=alpha)

        # Set the min and max of the colorbar
        vmin, vmax = -0.5, len(dval) - 0.5

    else: # categ == False
        # --- Treat continuous variable ---
        # Possibly exclude values from zz
        if excludedVal is not None:
            for v in np.array(excludedVal).reshape(-1): # force to be an 1d array
                np.putmask(zz, zz == v, np.nan)

        if np.all(np.isnan(zz)):
            vmin, vmax= 0.0, 1.0 # any values
        else:
            if vmin is None:
                vmin = np.nanmin(zz)

            if vmax is None:
                vmax = np.nanmax(zz)

    col = cmap((zz-vmin)/(vmax-vmin))

    return col
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
def drawImage2Drgb(im, nancol=(1.0, 0.0, 0.0)):
    """
    Draw a 2D image with 3 or 4 variables interpreted as RGB or RGBA code.

    :param im:      (img.Img class) image with 3 or 4 variables
    :param nancol:  (3-tuple or 4-tuple) RGB or RGBA color code (or string)
                        used for missing value (nan) in input image
    """

    fname = 'drawImage2Drgb'

    # Check image parameters
    if im.nz != 1:
        print(f"ERROR ({fname}): 'im.nz' must be 1")
        return None

    if im.nv != 3 and im.nv != 4:
        print(f"ERROR ({fname}): 'im.nv' must be 3 or 4")
        return None

    vv = im.val.reshape(im.nv, -1).T

    if vv.shape[1] == 3:
        nancolf = mcolors.to_rgb(nancol)
    else: # vv.shape[1] == 4
        nancolf = mcolors.to_rgba(nancol)

    ind_isnan = np.any(np.isnan(vv), axis=1)
    vv[ind_isnan, :] = nancolf

    plt.imshow(vv.reshape(im.ny, im.nx, -1), origin='lower')
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
def drawGeobodyMap2D(im, iv=0):
    """
    Draws a geobody map 2D, with adapted color bar.

    :param im:  (img.Img class) image with variables being geobody label
                    (value 0: not in considered medium, value n > 0: n-th geobody
                    (connected component))
    :param iv:  (int) index of the variable to be drawn
    """
    categ = True
    ngeo = int(im.val[iv].max())
    categVal = [i for i in range(1, ngeo+1)]
    categCol = None
    if ngeo <= 10:
        categCol = plt.get_cmap('tab10').colors[:ngeo]
        cticks = np.arange(ngeo)
        cticklabels = 1 + cticks
    elif ngeo <= 20:
        categCol = plt.get_cmap('tab20').colors[:ngeo]
        cticks = np.arange(ngeo)
        cticklabels = 1 + cticks
    elif ngeo <= 40:
        categCol = plt.get_cmap('tab20b').colors + plt.get_cmap('tab20c').colors[:ngeo-20]
        cticks = np.arange(0,ngeo,5)
        cticklabels = 1 + cticks
    else:
        categ = False
        cticks = None
        cticklabels = None
    drawImage2D(im, iv=iv, excludedVal=0, categ=categ, categVal=categVal, categCol=categCol,
                cticks=cticks, cticklabels=cticklabels)
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
def writeImage2Dppm(im, filename,
                    ix=None, iy=None, iz=None, iv=0,
                    cmap=ccol.cmap_def,
                    excludedVal=None,
                    categ=False, categVal=None, categCol=None,
                    vmin=None, vmax=None,
                    interpolation='none'):
    """
    Writes an image from 'im' in ppm format in the file 'filename',
    using colors as in function drawImage2D (other arguments are defined as in
    this function).
    """

    fname = 'writeImage2Dppm'

    # Check iv
    if iv < 0:
        iv = im.nv + iv

    if iv < 0 or iv >= im.nv:
        print(f'ERROR ({fname}): invalid iv index!')
        return None

    # Check slice direction and indices
    n = int(ix is not None) + int(iy is not None) + int(iz is not None)

    if n == 0:
        sliceDir = 'z'
        iz = 0

    elif n==1:
        if ix is not None:
            if ix < 0:
                ix = im.nx + ix

            if ix < 0 or ix >= im.nx:
                print(f'ERROR ({fname}): invalid ix index!')
                return None

            sliceDir = 'x'

        elif iy is not None:
            if iy < 0:
                iy = im.ny + iy

            if iy < 0 or iy >= im.ny:
                print(f'ERROR ({fname}): invalid iy index!')
                return None

            sliceDir = 'y'

        else: # iz is not None
            if iz < 0:
                iz = im.nz + iz

            if iz < 0 or iz >= im.nz:
                print(f'ERROR ({fname}): invalid iz index!')
                return None

            sliceDir = 'z'

    else: # n > 1
        print(f'ERROR ({fname}): slice specified in more than one direction!')
        return None

    # Extract what to be plotted
    if sliceDir == 'x':
        dim0 = im.ny
        min0 = im.oy
        max0 = im.ymax()

        dim1 = im.nz
        min1 = im.oz
        max1 = im.zmax()
        zz = np.array(im.val[iv, :, :, ix].reshape(dim1, dim0)) # np.array() to get a copy
            # reshape to force 2-dimensional array

    elif sliceDir == 'y':
        dim0 = im.nx
        min0 = im.ox
        max0 = im.xmax()

        dim1 = im.nz
        min1 = im.oz
        max1 = im.zmax()
        zz = np.array(im.val[iv, :, iy, :].reshape(dim1, dim0)) # np.array() to get a copy

    else: # sliceDir == 'z'
        dim0 = im.nx
        min0 = im.ox
        max0 = im.xmax()

        dim1 = im.ny
        min1 = im.oy
        max1 = im.ymax()
        zz = np.array(im.val[iv, iz, :, :].reshape(dim1, dim0)) # np.array() to get a copy

    if categ:
        # --- Treat categorical variable ---
        if categCol is not None\
                and type(categCol) is not list\
                and type(categCol) is not tuple:
            print(f"ERROR ({fname}): 'categCol' must be a list or a tuple (if not None)!")
            return None

        # Get array 'dval' of displayed values
        if categVal is not None:
            dval = np.array(categVal).reshape(-1) # force to be an 1d array

            if len(np.unique(dval)) != len(dval):
                print(f"ERROR ({fname}): 'categVal' contains duplicated entries!")
                return None

            # Check 'categCol' (if not None)
            if categCol is not None and len(categCol) != len(dval):
                print(f"ERROR ({fname}): length of 'categVal' and 'categCol' differs!")
                return None

        else:
            # Possibly exclude values from zz
            if excludedVal is not None:
                for val in np.array(excludedVal).reshape(-1):
                    np.putmask(zz, zz == val, np.nan)

            # Get the unique value in zz
            dval = np.array([v for v in np.unique(zz).reshape(-1) if ~np.isnan(v)])

        if not len(dval): # len(dval) == 0
            print(f'ERROR ({fname}): no value to be drawn!')

        # Replace dval[i] by i in zz and other values by np.nan
        zz2 = np.array(zz) # copy array
        zz[...] = np.nan # initialize
        for i, v in enumerate(dval):
            zz[zz2 == v] = i

        del zz2

        # Set 'colorList': the list of colors to use
        colorList = None
        if categCol is not None:
            if len(categCol) >= len(dval):
                colorList = [categCol[i] for i in range(len(dval))]

            else:
                print("Warning: 'categCol' not used (too few entries)")

        if colorList is None:
            # Use colors from cmap
            colorList = [cmap(0)]
            if len(dval) > 1:
                t = 1./(len(dval)-1)
                for i in range(1,len(dval)):
                    colorList.append(cmap(i*t))

        # Set the colormap: 'cmap'
        if len(dval) == 1:
            cmap = ccol.custom_cmap([colorList[0], colorList[0]], ncol=2,
                                    cbad=ccol.cbad_def)

        else: # len(dval) == len(colorList) > 1
            # cmap = mcolors.ListedColormap(colorList)
            cmap = ccol.custom_cmap(colorList, ncol=len(colorList),
                                    cbad=ccol.cbad_def)

        # Set the min and max of the colorbar
        vmin, vmax = -0.5, len(dval) - 0.5

        # Set colorbar ticks and ticklabels if not given
        if cticks is None:
            cticks = range(len(dval))

        if cticklabels is None:
            cticklabels = ['{:.3g}'.format(v) for v in dval]

        # Reset cextend if needed
        colorbar_extend = 'neither'

    else: # categ == False
        # --- Treat continuous variable ---
        # Possibly exclude values from zz
        if excludedVal is not None:
            for val in np.array(excludedVal).reshape(-1): # force to be an 1d array
                np.putmask(zz, zz == val, np.nan)

    # Get dimension of zz, flip zz vertically, then reshape as a list of value
    ny = zz.shape[0]
    nx = zz.shape[1]
    zz = zz[list(reversed(range(zz.shape[0]))),:].reshape(-1)

    # Set vmin and vmax (if needed)
    if vmin is None:
        vmin = np.nanmin(zz)

    if vmax is None:
        vmax = np.nanmax(zz)

    # Get indices of bad, under, over value
    ind_bad = np.isnan(zz)
    ind_under = np.all((~ind_bad, zz < vmin),0)
    ind_over = np.all((~ind_bad, zz > vmax),0)

    # Normalize value according to colorbar
    zz = np.maximum(np.minimum((zz-vmin)/(vmax-vmin), 1.0), 0.0)

    # Get rgba code at each pixel
    rgba_arr = np.asarray([cmap(v) for v in zz])

    if cmap._rgba_bad is not None:
        rgba_arr[ind_bad] = cmap._rgba_bad

    if cmap._rgba_under is not None:
        rgba_arr[ind_under] = cmap._rgba_under

    if cmap._rgba_over is not None:
        rgba_arr[ind_over] = cmap._rgba_over

    # Convert rgb from 0-1 to integer in 0-255 (ignored a chanel)
    zz = np.round(rgba_arr[:,0:3]*255)

    # Write file (ppm)
    shead = ("P3\n"
             "# CREATED BY PYTHON3-CODE\n"
             "{0} {1}\n"
             "255\n").format(nx, ny) # header of ppm file
    # Open the file in write binary mode
    with open(filename,'wb') as ff:
        ff.write(shead.encode()) # write header
        # Write rgb values
        np.savetxt(ff, zz.reshape(-1), fmt='%d')
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    print("Module 'geone.imgplot' example:")
    import matplotlib.pyplot as plt

    # Set image with 50 variables
    # ---------------------------
    # Set domain and number of cell in each direction
    xmin, xmax = -2, 2
    ymin, ymax = -1, 2
    nx, ny = 200, 150

    # Set the cell size
    sx, sy = (xmax-xmin)/nx, (ymax-ymin)/ny

    # Set the meshgrid
    x, y = xmin + 0.5 * sx + sx * np.arange(nx), ymin + 0.5 * sy + sy * np.arange(ny)
    # # equivalently:
    # x, y = np.arange(xmin+sx/2, xmax, sx), np.arange(ymin+sy/2, ymax ,sy)
    # x, y = np.linspace(xmin+sx/2, xmax-sx/2, nx), np.linspace(ymin+sy/2, ymax-sy/2, ny)
    xx,yy = np.meshgrid(x, y)

    # function values
    zz = xx**2 + yy**2 - 2

    # Set some values to nan
    zz[np.where(zz < -1.7)] = np.nan

    # set image, where each variable consists in
    # the function values 'zz' + a gaussian noise
    nv = 50
    im = Img(nx=nx, ny=ny, nz=1, nv=nv,
             sx=sx, sy=sy, sz=1.0,
             ox=xmin, oy=ymin, oz=0.0)

    for i in range(nv):
        im.set_var(ind=i, val=zz.reshape(-1)+np.random.normal(size=im.nxy()))

    # Compute the mean and standard deviation
    # ---------------------------------------
    imMean = img.imageContStat(im,op='mean')
    imStd = img.imageContStat(im,op='std',ddof=1)

    # Draw images
    # -----------
    # Set min and max value to be displayed
    vmin, vmax = -1.0, 3.0

    fig, ax = plt.subplots(2,2,figsize=(12,10))
    plt.subplot(2,2,1)
    drawImage2D(im, iv=0, vmin=vmin, vmax=vmax, title='1-st real',
                colorbar_extend='both')

    plt.subplot(2,2,2)
    drawImage2D(im, iv=1, vmin=vmin, vmax=vmax, title='2-nd real',
                colorbar_extend='both')

    plt.subplot(2,2,3)
    drawImage2D(imMean, vmin=vmin, vmax=vmax,
                title='Mean over {} real'.format(nv),
                colorbar_extend='both')

    plt.subplot(2,2,4)
    drawImage2D(imStd, title='Std over {} real'.format(nv))

    # plt.tight_layout()

    # fig.show()
    plt.show()

    # Copy im and categorize
    # ----------------------
    imCat = img.copyImg(im)
    bins = np.array([-np.inf, -1., 0., 1., np.inf])
    # set category j to a value v of image im as follows:
    #   bins[j-1] <= v < bins[j], for j=1,...,bins.size-1
    # and j=np.nan if v is np.nan

    defInd = np.array(~np.isnan(im.val)).reshape(-1) # defined indices

    imCat.val[...] = np.nan # initialization

    for j in range(1, bins.size):
        # Set category j
        imCat.val[np.all((defInd,
                          np.asarray(im.val >= bins[j-1]).reshape(-1),
                          np.asarray(im.val < bins[j]).reshape(-1)),
                         0).reshape(imCat.val.shape)] = j

    categ = list(range(1, bins.size))
    imCatProp = img.imageCategProp(imCat,categ)

    # Draw images
    # -----------
    # Set background color to "white"
    mpl_rcParams['figure.facecolor'] = 'white'

    fig, ax = plt.subplots(2,3,figsize=(18,10))
    plt.subplot(2,3,1)
    drawImage2D(imCat, iv=0, categ=True, title='1-st real')

    plt.subplot(2,3,2)
    # drawImage2D(imCat, iv=1, categ=True, title='2-nd real')
    drawImage2D(imCat, iv=1, categ=True, title='2-nd real',
                title_fontsize=18, title_fontweight='bold',
                xlabel="x-axis", xlabel_fontsize=8,
                xticks=[-2,0,2], xticklabels_fontsize=8,
                clabel="facies",clabel_fontsize=16,clabel_rotation=90,
                cticklabels=['A','B','C','D'],cticklabels_fontsize=8)

    plt.subplot(2,3,3)
    drawImage2D(imCatProp, iv=0, vmin=0, vmax=0.7, colorbar_extend='max',
                title='Prop. of "{}" over {} real'.format(categ[0], nv))

    plt.subplot(2,3,4)
    drawImage2D(imCatProp, iv=1, vmin=0, vmax=0.7, colorbar_extend='max',
                title='Prop. of "{}" over {} real'.format(categ[1], nv))

    plt.subplot(2,3,5)
    drawImage2D(imCatProp, iv=2, vmin=0, vmax=0.7, colorbar_extend='max',
                title='Prop. of "{}" over {} real'.format(categ[2], nv))

    plt.subplot(2,3,6)
    drawImage2D(imCatProp, iv=3, vmin=0, vmax=0.7, colorbar_extend='max',
                title='Prop. of "{}" over {} real'.format(categ[3], nv),
                cticks=np.arange(0,.8,.1), cticklabels=['{:4.2f}'.format(i) for i in np.arange(0,.8,.1)],
                cticklabels_fontweight='bold')

    plt.suptitle('Categorized images...')
    # plt.tight_layout()

    # fig.show()
    plt.show()

    a = input("Press enter to continue...")
