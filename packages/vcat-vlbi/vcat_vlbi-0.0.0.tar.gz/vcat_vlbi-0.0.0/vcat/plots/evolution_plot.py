from os import write
import matplotlib as mpl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.collections import LineCollection
import matplotlib.colors as colors
import matplotlib.markers as markers
from astropy.io import fits
from astropy.modeling import models, fitting
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable
from astropy.time import Time
from matplotlib.lines import Line2D
import sys
import pexpect
from datetime import datetime
import colormaps as cmaps
import matplotlib.ticker as ticker
from vcat.helpers import get_sigma_levs, getComponentInfo, convert_image_to_polar, wrap_evpas, closest_index, get_date, get_freq, write_mod_file
import vcat.fit_functions as ff
from vcat.kinematics import Component
from vcat.config import logger, font
from scipy.interpolate import interp1d


#optimized draw on Agg backend
mpl.rcParams['path.simplify'] = True
mpl.rcParams['path.simplify_threshold'] = 1.0
mpl.rcParams['agg.path.chunksize'] = 1000

#define some matplotlib figure parameters
mpl.rcParams['font.family'] = font
mpl.rcParams['axes.linewidth'] = 1.0

font_size_axis_title=13
font_size_axis_tick=12


class EvolutionPlot(object):
    def __init__(self,xlabel="",ylabel="",font_size_axis_title=10,pol_plot=False,fig="",ax=""):

        super().__init__()
        if pol_plot:

            if fig=="" or ax=="":
                self.fig, self.ax = plt.subplots(subplot_kw={'projection': 'polar'})
            else:
                self.fig=fig
                self.ax=ax

            #Set 0° to top
            self.ax.set_theta_zero_location("N")
            self.ax.set_theta_direction(1)

            #create ticks
            tick_angles_deg = np.arange(0,360,30)
            tick_labels = []
            for ang in tick_angles_deg:
                if ang<180:
                    tick_labels.append(f"{ang // 2}°")
                elif ang==180:
                    tick_labels.append("+90°/-90°")
                else:
                    tick_labels.append(f"{(ang-360)//2}°")

            self.ax.set_xticks(np.deg2rad(tick_angles_deg))
            self.ax.set_xticklabels(tick_labels)
        else:
            if fig == "" or ax == "":
                self.fig, self.ax = plt.subplots(1, 1)
            else:
                self.fig=fig
                self.ax=ax
            self.ax.set_xlabel(xlabel, fontsize=font_size_axis_title)
            self.ax.set_ylabel(ylabel, fontsize=font_size_axis_title)
        self.fig.subplots_adjust(left=0.13,top=0.96,right=0.93,bottom=0.2)

    def plotEvolution(self,mjds,value,c="black",marker=".",label="",linestyle="none"):
        self.ax.plot(mjds, value, c=c, marker=marker,label=label,linestyle=linestyle)

    def plotEvolutionWithEVPA(self,mjds,value,evpas,value_err=[],err_alpha=0.2,err_zorder=-3,evpas_err=[],evpa_err_increment=100,
                              evpa_width=2,evpa_err_color="lightgrey",evpa_err_alpha=1,zorder=1,evpa_err_zorder=-1,
                              c="black",marker=".",label="",
                              linestyle="none",evpa_len=200,evpa_color=""):
        self.ax.plot(mjds, value, c=c, marker=marker,label=label,linestyle=linestyle,zorder=zorder)

        for i in range(len(mjds)):
            mjd=mjds[i]
            val=value[i]
            evpa=evpas[i]

            # make a markerstyle class instance and modify its transform prop
            t = markers.MarkerStyle(marker="|")
            t._transform = t.get_transform().rotate_deg(evpa)
            if evpa_color=="":
                evpa_color=c
            self.ax.scatter(mjd, val, marker=t, s=evpa_len,c=evpa_color,zorder=zorder)


            if len(evpas_err) == len(evpas):
                for i in np.linspace(-evpas_err[i], +evpas_err[i], evpa_err_increment):
                    t = markers.MarkerStyle(marker="|")
                    t._transform = t.get_transform().rotate_deg(evpa + i)
                    self.ax.scatter(mjd, val, marker=t, s=evpa_len, linewidths=evpa_width,
                               c=evpa_err_color, alpha=evpa_err_alpha, zorder=evpa_err_zorder)

        if len(value_err) == len(value):
            sort_ind=np.argsort(mjds)
            mjds=mjds[sort_ind]
            value=value[sort_ind]
            value_err=value_err[sort_ind]
            self.ax.fill_between(mjds, np.array(value) + np.array(value_err),
                                 np.array(value) - np.array(value_err), color=c, alpha=err_alpha,zorder=err_zorder)


    def plotEVPAevolution(self,mjds,evpas,c="black",marker=".",label="",linestyle="-"):


        plot_evpas=2*np.array(wrap_evpas(evpas))/180*np.pi #we will plot two times EVPA

        #interpolate EVPA for the line plot
        evpa_interp=interp1d(mjds,plot_evpas,kind="linear")
        mjd_interp=np.linspace(min(mjds),max(mjds),10000)
        self.ax.plot(evpa_interp(mjd_interp),mjd_interp,color=c,linestyle=linestyle)

        #scatter plot the actual values
        self.ax.scatter(plot_evpas,mjds,color=c,marker=marker,label=label)
        mjd_range=max(mjds)-min(mjds)
        self.ax.set_rmin(min(mjds)-0.05*mjd_range)
        self.ax.set_rmax(max(mjds)+0.05*mjd_range)