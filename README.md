# AdsDataToTikz
Parses Keysight ADS data window exported data to a tikz plot via matplotlib

This script uses python 3.6, matplotlib and tikzplotlib to read and parse an ADS data file.
To get such a file select the plot in the Data Window and select 

```File->Export->Write selected item to tab-delimited ASCII```

You get a `*.txt` file with the data points. Specify this in the script and you get a nice tikz file you can include into your LaTeX code. Further there are some modifications done to the tikz code to ease integration. A typical LaTeX code to include the tikz figure looks like this:

```
\begin{figure}[htpb]
	\centering
	\def\tkzwidth{0.7\textwidth}
	\def\tkzheight{7.5cm}
	\def\tkzxlabel{Time in \si{\second}}
	\def\tkzylabel{Output Voltage in \si{\volt}}
	\input{generated_figure.tex}
	\caption{Super awesome caption}
	\label{fig:best_figure_ever}
\end{figure}
```
