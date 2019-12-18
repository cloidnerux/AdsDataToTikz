# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 09:57:38 2019

@author: joachim
"""

import matplotlib.pyplot as plt
import numpy as np
import csv
from io import StringIO
import re
import matplotlib.colors as mcolors
import matplotlib as mpl
import os

import tikzplotlib

#The input file name 
file_path = r'input_file.txt'

# ADS adds the variable name and sweep info in rectengular brackets at the end
# This removes this
def TruncateName(s):
    if(s.find('[') == -1):
        return s
    ind = s.rindex('[')
    return s[:ind]

# Map a value from the old range to a new one
def map_range(val, old_min, old_max, new_min, new_max):
    return (val - old_min) / (old_max-old_min) * (new_max-new_min) + new_min

	
# Plot a parameter sweep or multiple values
# s is the text of the file to parse
# fileName is the file name and apth of the resulting tikz file
# The Tikz file is generated with MatplotlibToTikz
def PlotSteps(s, fileName):
    units = {-5:r'$\times 10^{-15}$', -4:r'$\times 10^{-12}$', -3:r'$\times 10^{9}$', -2:r'$\times 10^{-6}$', -1:r'$\times 10^{-3}$', 0:r'$\times 10^{0}$', 1:r'$\times 10^{3}$', 2:r'$\times 10^{6}$', 3:r'$\times 10^{9}$', 4:r'$\times 10^{12}$'}
    with StringIO(s) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        plot_count = 1
        steps = np.zeros(0)
        first_row = True
        l_ = []
        last_newline = False
        name_sweep = ''
        name_x = ''
        name_y = ''
        for row in csv_reader:
            if(len(row) == 0):
                if(not last_newline):
                    plot_count += 1
                    first_row = True
                last_newline == True
            else:
                last_newline = False
                if(first_row):
                    first_row = False
                    name_sweep = row[0]
                    name_x = row[1]
                    name_y = TruncateName(row[2])
                else:
                    if(steps.shape[0] == 0):
                        steps = np.append(steps, [float(row[0])])
                    elif(steps[-1] != float(row[0])):
                        steps = np.append(steps, [float(row[0])])
                    l_.append(row)
        c_rgb = mcolors.to_rgb('r')
        c_hsv= mcolors.rgb_to_hsv(c_rgb)
        sat = c_hsv[1]
        fig = plt.figure()
        ax = fig.gca()
        mpl.style.use('default')
        
        data = np.array(l_, float)
        ind = 0
        
        x_data = data[:,1]
        x_log = np.log10(np.abs(x_data[np.any(x_data)]))
        x_log = np.floor(x_log/3)
        base = np.max(x_log)
        y_data = data[:,2]
        y_log = np.log10(np.abs(y_data[np.any(y_data)]))
        y_log = np.floor(y_log/3)
        base_y = np.max(y_log)
        x_min = np.min(x_data)/np.power(10, base*3)
        x_max = np.max(x_data)/np.power(10, base*3)
        for s in steps:
            subdata = data[np.where(data[:,0] == s), :]
            c_hsv[1] = map_range(sat * (ind / steps.shape[0]), 0, 1, 1, 0.2)
            ind += 1
            if(steps.shape[0] < 5):
                plt.plot(subdata[0,:,1]/np.power(10, base*3), subdata[0,:,2]/np.power(10, base_y*3), label=name_sweep + ' ' + "{:.1f}".format(s), color = mcolors.hsv_to_rgb(c_hsv))
            else:
                plt.plot(subdata[0,:,1]/np.power(10, base*3), subdata[0,:,2]/np.power(10, base_y*3), color = mcolors.hsv_to_rgb(c_hsv))
        plt.xlabel(name_x + ' ' + units[base])
        plt.ylabel(name_y + ' ' + units[base_y])
        plt.xlim((x_min, x_max))
        if(steps.shape[0] < 5):
            plt.legend()
        else:
            plt.legend([name_sweep + ' from ' + "{:.1f}".format(steps[0]) + " to {:.1f}".format(steps[-1])])
        plt.grid(True, ls='--')
        ax.tick_params(direction='in')
        plt.tight_layout()
        tikzplotlib.save(fileName)
        PatchGeneratedTikzFile(fileName)
        plt.show()
        return(data)
            
# This "patches" a generated tikz file
# To ease the integration of the generated tikz files into a latex document
# This functions adds some variables to control x and y labels as well as the widht and height
# Typical latex code to use the plots
# \begin{figure}[htpb]
#	\centering
#	\def\tkzwidth{0.7\textwidth}
#	\def\tkzheight{7.5cm}
#	\def\tkzxlabel{Time in \si{\second}}
#	\def\tkzylabel{Output Voltage in \si{\volt}}
#	\input{figures/generated_figure.tex}
#	\caption{Your caption}
#	\label{fig:generated_figure}
# \end{figure}
def PatchGeneratedTikzFile(fileName):
    lines = []
    with open(fileName, 'r') as file:
        lines = file.readlines()
    ind = 0
    for l in lines:
        if(l.find(r'\begin{') != -1):
            ind += 1
            break;
        ind += 1
    ind2 = 0
    xname = ''
    for l in lines:
        if(l.find(r'xlabel={') != -1):
            xname = l[l.find('{')+1:l.rindex('}')]
            lines[ind2] = r'xlabel={\xlabel},' + '\n'
            break
        ind2 += 1
    yname = ''
    ind2 = 0
    for l in lines:
        if(l.find(r'ylabel={') != -1):
            yname = l[l.find('{')+1:l.rindex('}')]
            lines[ind2] = r'ylabel={\ylabel},' + '\n'
            break
        ind2 += 1
    patch = [r'\pgfplotsset{width=\tkzwidth,', 
		r'height=\tkzheight', 
	r'}' + '\n']
    patch_x = [r'\ifdefined\tkzxlabel',
               r'\def\xlabel{\tkzxlabel}',
               r'\else',
               r'\def\xlabel{' + xname + r'}',
               r'\fi' + '\n']
    patch_y = [r'\ifdefined\tkzylabel',
               r'\def\ylabel{\tkzylabel}',
               r'\else',
               r'\def\ylabel{' + yname + r'}',
               r'\fi' + '\n']
    for l in patch:
        lines.insert(ind, l + '\n')
        ind+=1
    for l in patch_x:
        lines.insert(ind, l + '\n')
        ind+=1
    for l in patch_y:
        lines.insert(ind, l + '\n')
        ind+=1
    with open(fileName, 'w') as file:
        file.write("".join(lines))
        

#Read the given file and generate the plots
#Will skip invalid data		
count = 1
with open(file_path, 'r') as file:
    first = True
    name = ''
    s = ''
    fname = os.path.basename(file_path)
    fname = os.path.splitext(fname)[0]
    match_number = re.compile('-?\ *[0-9]+\.?[0-9]*(?:[Ee]\ *-?\ *[0-9]+)?')
    end_of_block = False
    for x in file:
        if(x == '\n'):
            s += x
            continue
        if(first or end_of_block):
            name = TruncateName(x)
            first = False
            if(end_of_block):
                s = x;
            end_of_block = False
        if(match_number.match(x.split('\t')[0]) is None):
            #we found a name line
            if(x.find('<invalid>') != -1):
                continue
                #not a valid plot
                #print(x + ' not valid')
            elif(TruncateName(x) != name):
                #found a new plot
                #PlotSteps(s)
                #print(s)
                print(name.split('\t')[2])
                PlotSteps(s, fname + str(count) + '.tex')
                if(x != '\n'):
                    s = x
                    name = TruncateName(x)
                    end_of_block = False
                else:
                    end_of_block = True
                count += 1
            else:
                s += x
        else:
            s += x
    print(name.split('\t')[2])
    PlotSteps(s, fname + str(count) + '.tex')
    
print('Total count: ' + str(count))

    