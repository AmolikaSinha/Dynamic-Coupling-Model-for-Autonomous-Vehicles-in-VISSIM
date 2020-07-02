"""
Author: Darko Frtunik
VERSION 0.2

PLEASE NOT THIS IS STILL A WIP

This program contains all code used for the data processing of VISSIM outputs
The purpose of this document is to give a map of all functions and data processing used to generate the results used
in various papers with a few notable exceptions listed below:
- Generation of .trax file

This document performs will perform the following tasks:
    - Checks throughput and counts number of autonomous vehicles
    - Takes the SSAM data and matches the Vehicle IDs up to manual vs automated
    - Processes the SSAM data and organizes the conflicts
    - Compiles and aggregates .att files and generates the seaborn heatmaps to visualize the data.
"""

# Test update to github

# Import Packages
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import os


def read_from_csv(file_name):
    """
    Function that will read a file based on its type and begin reading the file from the data header row.
    :param file_name: a string representing a file
    :return return_data
    This is the file read as a data-frame with the rows of useless data skipped. Ensure prior to use the rows of
    useless data are known exactly. pd.read_csv will automatically ignore lines that contain no input. So the
    header_row argument must be set 1 less than the row index (first line is: 0) of the header row.
    """
    if ".att" in file_name:
        header_row = 26
        col_sep = ";"
        output_df = pd.read_csv(file_name, sep=col_sep, header=header_row)
    elif ".fhz" in file_name:
        header_row = 5
        col_sep = ";"
        output_df = pd.read_csv(file_name, sep=col_sep, header=header_row)
    elif "_conflicts" in file_name:
        output_df = pd.read_csv(file_name)
    else:
        output_df = pd.read_csv(file_name)

    return output_df


def create_kde(data_frame, key_performance_parameter, conflicts_file_name, vehicle_types, p_style,
               collision_type='rear end'):
    """
    This function produces a KDE histogram plot of the Key performance parameter specified.
    NB: This function requires the seaborn library be imported as sns, and for pandas library to
    be available.
    :param data_frame: A dataFrame of the conflicts file which is desired to be analysed.
    :param key_performance_parameter: Key Performance parameter. PET, TTC, or DeltaS
    :param conflicts_file_name: a string name of the filename used to name the figure when saved
    :param vehicle_types: a string name used in setting the label of the graph
    :param p_style: String array used to define the colour and line-style of the KDE plot.
    :param collision_type: One of the accident types outputted from SSAM analysis. "rear end", "
    This function will create a KDE and save it to the source file as a .png with the filename taken from the
    conflicts file.
    """
    # Crop Data_Frame for conflict type
    kde_df = data_frame[data_frame['ConflictType'] == collision_type]

    # Create kde
    sns.kdeplot(kde_df[key_performance_parameter], color=p_style[0], linestyle=p_style[1],
                label=vehicle_types + ' ' + conflicts_file_name + ' ' + collision_type)

    # Set x-axis label
    plt.xlabel(key_performance_parameter + ' (s)')
    # Set legend
    plt.legend(loc='upper right')
    # plt.legend(loc='right', bbox_to_anchor=(1.25, 0.5))

    # Save image with filename from conflicts file
    plt.draw()


def create_heatmap(dataframe, value, heatmap_title, lower_better=True, format='.0f'):
    """
    Function to generate seaborn heatmaps out of a specified parameter
    :param dataframe:
    :param value:
    :param title: desired title of the graph
    :param ascending:
    :return:
    """
    # Format data into 5x4 matrix for use
    idx = [2, 3, 4, 5, 6]
    cols = [2, 5, 10, 15]
    df = pd.DataFrame(np.reshape(dataframe[value].values, (5, 4)), index=idx, columns=cols)

    if lower_better:
        colour_scheme = "RdBu_r"
    else:
        colour_scheme = "RdBu"

    img = sns.heatmap(df, cbar=False, cmap=colour_scheme, annot=True, fmt=format)
    plt.xlabel('b')
    plt.ylabel('a')
    plt.title(heatmap_title)


# Begin main function
# Change working directory to separate folder
# Get a dataframe which is the simulation ID of the filename associated with the .trj, .fhz
# This will be used for labelling graphs
os.chdir("C:\\Users\\darko\\Dropbox\\Uni\\UNSW\\Thesis\\CollisionDataProcessor\\Simulation_Library\\")
sim_ID_list = pd.read_csv("C:\\Users\\darko\\Dropbox\\Uni\\UNSW\\Thesis\\"
                          "CollisionDataProcessor\\Simulation_Library\\VISSIM_Scenario_Library.csv")
sim_ID_list.columns = sim_ID_list.columns.str.replace(' ', '')

# Change Working Directory
os.chdir("C:\\Users\\darko\\Dropbox\\Uni\\UNSW\\Thesis\\CollisionDataProcessor\\Data\\")
sub_folder_file_list = os.listdir()  # creates list of the files in the subfolder

# Extract list of each file type that will be used to create the plots
throughput_files = [fname for fname in sub_folder_file_list if '.fhz' in fname]
conflicts_fnames = [fname for fname in sub_folder_file_list if '_conflicts' in fname]
att_fnames = [fname for fname in sub_folder_file_list if '.att' in fname]

# Get the Simulation code which each filename represents, used in conjunction with the simulation library.
tpcodes = [f.split('_')[0] for f in throughput_files]
conflict_codes = [f.split('_')[0] for f in conflicts_fnames]
attcodes = [at.split('_')[0] for at in att_fnames]
attcodes = [at.split(' ')[3] + '_' + at.split(' ')[5] for at in attcodes]
attcodes = [sim_ID_list.loc[sim_ID_list['SimID'] == code]['Code'].to_string(index=False).replace(' ', '')
            for code in attcodes]
plot_legend = [sim_ID_list.loc[sim_ID_list['Code'] == code]['SimID'].to_string(index=False).replace(' ', '')
               for code in tpcodes]

plot_colour = [None]*len(plot_legend)
for i, entry in enumerate(plot_legend):
    if 'a2' in entry:
        plot_colour[i] = 'b'
    elif 'a3' in entry:
        plot_colour[i] = 'r'
    elif 'a4' in entry:
        plot_colour[i] = 'g'
    elif 'a5' in entry:
        plot_colour[i] = 'c'
    elif 'a6' in entry:
        plot_colour[i] = 'm'

plot_style = [None]*len(plot_legend)
for i, entry in enumerate(plot_legend):
    if 'b2' in entry:
        plot_style[i] = ':'
    elif 'b5' in entry:
        plot_style[i] = '-'
    elif 'b10' in entry:
        plot_style[i] = '--'
    elif 'b15' in entry:
        plot_style[i] = '-.'

# Combine dictionaries of codes into a dataframe which will store each filename as rows under the simulation ID code
# in addition to its simID for use with plot legend. This dataframe used for iteration and creating the graphs one
# file row at a time.
all_files = pd.DataFrame((dict(zip(tpcodes, throughput_files)), dict(zip(conflict_codes, conflicts_fnames)),
                          dict(zip(attcodes, att_fnames)), dict(zip(tpcodes, plot_legend)),
                          dict(zip(tpcodes, plot_colour)), dict(zip(tpcodes, plot_style))))

# Set output filepath for saving figures
file_save_path = r'C:\Users\darko\Dropbox\Uni\UNSW\Thesis\CollisionDataProcessor\Results\\'

# This loop sorts through the files which have been placed in the folder and produces a number of visualisations
for i in range(len(all_files.columns)):
    # Find Throughput for the simulation
    # Import dataframe of throughput csv
    # For some reason .fhz produces an extra useless columm so this must be dropped, if this is not present
    # the error will be ignored. Replacement of spaces is necessary as the .fhz files tend to be messy with spaces
    throughput = read_from_csv(all_files.iloc[0][i]).drop(columns="Unnamed: 7", errors='ignore')
    throughput.columns = throughput.columns.str.replace(' ', '')

    # Matchup VehicleIDs with their types from the .fhz
    # Creates a dictionary of Vehicle IDs whose value is their type
    VehID_Lookup = pd.Series(throughput.VehType.values, index=throughput.VehNo).to_dict()

    # SSAM Conflicts register import as DataFrame, drop useless column as per throughput
    conflicts = read_from_csv(all_files.iloc[1][i]).drop(columns="Unnamed: 44", errors='ignore')

    # Creates two new columns in conflicts DataFrame which inserts the vehicle type
    conflicts['FirstVType'] = conflicts['FirstVID'].map(VehID_Lookup)
    conflicts['SecondVType'] = conflicts['SecondVID'].map(VehID_Lookup)

    # Separate conflicts into the types of vehicles involved in the collisions, save as separate DataFrames
    av_mv_conflicts = conflicts[(conflicts['FirstVType'] == 101) | (conflicts['SecondVType'] == 101)]
    mv_mv_conflicts = conflicts[(conflicts['FirstVType'] == 100) & (conflicts['SecondVType'] == 100)]

    # Extract all unique conflict types from the conflicts file, useful for loops, left for now may revisit in future
    # collision_types = conflicts.ConflictType.unique()
    # collision_types = collision_types[np.logical_not(pd.isnull(collision_types))]

    # Create x4 KDE plots for each combination of rear-end collisions
    # Rear-End AV-MV TTC
    plt.figure(1, figsize=(10, 10))
    create_kde(av_mv_conflicts, 'TTC', all_files.iloc[3][i], 'AV_MV', [all_files.iloc[4][i], all_files.iloc[5][i]])
    plt.savefig(file_save_path + "AV_MV_Conflicts" + '_' + 'Rear-End' + '_' + 'TTC' + '.png', transparent=True)

    # Rear-End AV-MV PET
    plt.figure(2, figsize=(10, 10))
    create_kde(av_mv_conflicts, 'PET', all_files.iloc[3][i], 'AV_MV', [all_files.iloc[4][i], all_files.iloc[5][i]])
    plt.savefig(file_save_path + "AV_MV_Conflicts" + '_' + 'Rear-End' + '_' + 'PET' + '.png', transparent=True)

    # Rear-end MV-MV TTC
    plt.figure(3, figsize=(10, 10))
    create_kde(mv_mv_conflicts, 'TTC', all_files.iloc[3][i], 'MV_MV', [all_files.iloc[4][i], all_files.iloc[5][i]])
    plt.savefig(file_save_path + "MV_MV_Conflicts" + '_' + 'Rear-End' + '_' + 'TTC' + '.png', transparent=True)

    # Rear-end MV-MV PET
    plt.figure(4, figsize=(10, 10))
    create_kde(mv_mv_conflicts, 'PET', all_files.iloc[3][i], 'MV_MV', [all_files.iloc[4][i], all_files.iloc[5][i]])
    plt.savefig(file_save_path + "MV_MV_Conflicts" + '_' + 'Rear-End' + '_' + 'PET' + '.png', transparent=True)

    # Rear-end Total? unsure if needed
    # plt.figure(3)

    # Filter PET = 0 for collisions
    av_mv_collisions = av_mv_conflicts[av_mv_conflicts['PET'] == 0]
    mv_mv_collisions = av_mv_conflicts[av_mv_conflicts['PET'] == 0]

    # Plot KDE with DeltaS for the filtered collision data and plot

    # Rear-End AV-MV TTC, with PET = 0
    plt.figure(5, figsize=(10, 10))
    create_kde(av_mv_collisions, 'TTC', all_files.iloc[3][i], 'AV_MV', [all_files.iloc[4][i], all_files.iloc[5][i]])
    plt.savefig(file_save_path + "AV_MV_Collisions" + '_' + 'Rear-End' + '_' + 'TTC' + '.png', transparent=True)

    # Rear-End Collisions AV-MV DeltaS, with PET = 0
    plt.figure(6, figsize=(10, 10))
    create_kde(av_mv_collisions, 'DeltaS', all_files.iloc[3][i], 'AV_MV', [all_files.iloc[4][i], all_files.iloc[5][i]])
    plt.savefig(file_save_path + "AV_MV_Collisions" + '_' + 'Rear-End' + '_' + 'PET' + '.png', transparent=True)

    # Rear-End MV-MV TTC, with PET = 0
    plt.figure(7, figsize=(10, 10))
    create_kde(mv_mv_collisions, 'TTC', all_files.iloc[3][i], 'MV_MV', [all_files.iloc[4][i], all_files.iloc[5][i]])
    plt.savefig(file_save_path + "AV_MV_Collisions" + '_' + 'Rear-End' + '_' + 'TTC' + '.png', transparent=True)

    # Rear-End Collisions MV-MV DeltaS, with PET = 0
    plt.figure(8, figsize=(10, 10))
    create_kde(mv_mv_collisions, 'DeltaS', all_files.iloc[3][i], 'MV_MV', [all_files.iloc[4][i], all_files.iloc[5][i]])
    plt.savefig(file_save_path + "AV_MV_Collisions" + '_' + 'Rear-End' + '_' + 'DeltaS' + '.png', transparent=True)

    # Import the attributes file as a Data_Frame
    att = read_from_csv(all_files.iloc[2][i])

    # Update att with key statistics from throughput and collision Data_Frames use in generating heat maps
    att['Throughput'] = len(throughput.index)
    att['TotalCAV'] = len(throughput[throughput["VehType"] == 101].index)
    att['Total_Manual'] = att['Throughput'] - att['TotalCAV']
    att['TotalConflicts_MV-MV'] = len(mv_mv_collisions.index)
    att['TotalConflicts_AV-MV'] = len(av_mv_collisions.index)
    att['TotalConflictRate'] = (att['TotalConflicts_AV-MV'] + att['TotalConflicts_MV-MV'])/att['Throughput']
    att['MV-MV_TotalRate'] = att['TotalConflicts_MV-MV']/att['Total_Manual']
    att['AV-MV_TotalRate'] = att['TotalConflicts_AV-MV']/att['TotalCAV']
    att['MV-AV_TotalRate'] = att['TotalConflicts_AV-MV']/att['Total_Manual']
    att['Total_Collisions_AV-MV'] = len(av_mv_collisions.index)
    att['Total_Collisions_MV-MV'] = len(mv_mv_collisions.index)
    att['Total_Collisions'] = att['Total_Collisions_MV-MV'] + att['Total_Collisions_AV-MV']
    att['Total_Collision_Rate'] = (att['Total_Collisions_MV-MV'] + att['Total_Collisions_AV-MV'])/att['Throughput']

    # Concatenates the attribute files into a dataframe for use in heatmap generators
    if i == 0:
        att_compiled = att
    else:
        att_compiled = att_compiled.append(att)

# ATT Heatmap diagrams
att_compiled.index = all_files.iloc[3].values

plt.figure(9)
create_heatmap(att_compiled, 'TRAVTMTOT(ALL)', 'Total System Travel Time ' + all_files.iloc[3][0].split('_')[0] +
               ' Penetration')
plt.savefig(file_save_path + 'Total_System_Travel_Time_' + all_files.iloc[3][0].split('_')[0] +
            '_Penetration.png', transparent=True)

plt.figure(10)
create_heatmap(att_compiled, 'SPEEDAVG(ALL)', 'Network Average Speed ' + all_files.iloc[3][0].split('_')[0] +
               ' Penetration', lower_better=False, format='.2f')
plt.savefig(file_save_path + 'Network_Average_Speed_' + all_files.iloc[3][0].split('_')[0] +
            '_Penetration.png', transparent=True)

plt.figure(11)
create_heatmap(att_compiled, 'Throughput', 'Throughput ' + all_files.iloc[3][0].split('_')[0] +
               ' Penetration')
plt.savefig(file_save_path + 'Throughput_' + all_files.iloc[3][0].split('_')[0] +
            '_Penetration.png', transparent=True)

plt.figure(12)
create_heatmap(att_compiled, 'DELAYAVG(ALL)', 'Average Delay ' + all_files.iloc[3][0].split('_')[0] +
               ' Penetration', format='.2f')
plt.savefig(file_save_path + 'Average_Delay_' + all_files.iloc[3][0].split('_')[0] +
            '_Penetration.png', transparent=True)

plt.figure(13)
create_heatmap(att_compiled, 'TotalConflictRate', 'Total Rate of Conflict ' + all_files.iloc[3][0].split('_')[0] +
               ' Penetration', format='.4f')
plt.savefig(file_save_path + 'Total_Rate_of_Conflict_' + all_files.iloc[3][0].split('_')[0] +
            '_Penetration.png', transparent=True)

plt.figure(14)
create_heatmap(att_compiled, 'MV-MV_TotalRate', 'Total Rate of Conflict MV-MV ' +
               all_files.iloc[3][0].split('_')[0] + ' Penetration', format='.4f')
plt.savefig(file_save_path + 'Total_Rate_of_Conflict_MV-MV_' + all_files.iloc[3][0].split('_')[0] +
            '_Penetration.png', transparent=True)

plt.figure(15)
create_heatmap(att_compiled, 'AV-MV_TotalRate', 'Total Rate of Conflict AV-MV ' +
               all_files.iloc[3][0].split('_')[0] + ' Penetration', format='.4f')
plt.savefig(file_save_path + 'Total_Rate_of_Conflict_AV-MV_' + all_files.iloc[3][0].split('_')[0] +
            '_Penetration.png', transparent=True)

plt.figure(16)
create_heatmap(att_compiled, 'Total_Collision_Rate', 'Total Rate of Collisions ' +
               all_files.iloc[3][0].split('_')[0] + ' Penetration', format='.4f')
plt.savefig(file_save_path + 'Total_Rate_of_Collisions_' + all_files.iloc[3][0].split('_')[0] +
            '_Penetration.png', transparent=True)
