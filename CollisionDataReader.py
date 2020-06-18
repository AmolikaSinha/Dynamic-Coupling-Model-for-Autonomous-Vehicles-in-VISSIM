"""
Author: Darko Frtunik
VERSION 0.1

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


def create_kde(dataframe, collisiontype, kpp, conflictsfilename, vehicletypes):
    """
    This function produces a KDE histogram plot of the Key performance parameter specified.

    NB: This function requires the seaborn library be imported as sns

    :param DataFrame: A dataFrame of the conflicts file which is desired to be analysed.
    :param CollisionType: One of the accident types outputted from SSAM analysis. "rear end", "
    :param kpp: Key Performance parameter. PET, TTC, or DeltaS
    :param conflictsfilename: a string name of the filename used to name the figure when saved
    :param vehicletypes: a string name used in setting the label of the graph
    This function will create a KDE and save it to the source file as a .png with the filename taken from the
    conflicts file.
    """

    # Crop Dataframe for conflict type
    kde_df = dataframe[dataframe['ConflictType'] == ctype]

    # Create kde
    sns.kdeplot(kde_df[kpp], cut=0)

    # Set x-axis label
    plt.xlabel(kpp + ' (s)')
    # Set legend
    plt.legend([vehicletypes + ' ' + conflictsfilename + ' ' + collisiontype], loc='upper center',
               bbox_to_anchor=(0.5, 1.1))

    # Save image with filename from conflicts file
    plt.savefig(vehicletypes + conflictsfilename + '_' + collisiontype + '_' + kpp + '.png', transparent=True)


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

tpcodes = [tf.split('.')[0] for tf in throughput_files]

attcodes = [at.split('_')[0] for at in att_fnames]
attcodes = [at.split(' ')[3] + '_' + at.split(' ')[5] for at in attcodes]

# Create a dictionary containing the files and their respective codes for easy matchup



# Initialize DataFrame to store Throughput Values


for tpf, cff, i in throughput_files, conflicts_fnames, range(len(throughput_files)):
    # Find Throughput for the simulation
    # Import dataframe of throughput csv
    # For some reason .fhz produces an extra useless columm so this must be dropped, if this is not present
    # the error will be ignored. Replacement of spaces is necessary as the .fhz files tend to be messy with spaces
    throughput = read_from_csv(tpf).drop(columns="Unnamed: 7", errors='ignore')
    throughput.columns = throughput.columns.str.replace(' ', '')

    # Obtain summary statistics from the throughput DataFrame
    total_veh = len(throughput.index)
    cav_total = len(throughput[throughput["VehType"] == 101].index)
    man_total = total_veh - cav_total

    # Matchup VehicleIDs with their types from the .fhz
    # Creates a dictionary of Vehicle IDs whose value is their type
    VehID_Lookup = pd.Series(throughput.VehType.values, index=throughput.VehNo).to_dict()

    # SSAM Conflicts register import as DataFrame, drop useless column as per throughput
    conflicts = read_from_csv(cff).drop(columns="Unnamed: 44", errors='ignore')

    # Matches the conflicts file to its respective SIMID code for simpler visualization of data
    cf_name = conflicts['trjFile'][0][0:conflicts['trjFile'][0].index('_')]
    cf_ID = sim_ID_list["SimID"][sim_ID_list["Code"] == cf_name].to_string(index=False)

    # Creates two new columns in conflicts DataFrame which inserts the vehicle type
    conflicts['FirstvType'] = conflicts['FirstVID'].map(VehID_Lookup)
    conflicts['SecondvType'] = conflicts['SecondVID'].map(VehID_Lookup)

    # Extract all unique conflict types from the conflicts file
    collision_types = conflicts.ConflictType.unique()
    collision_types = collision_types[np.logical_not(pd.isnull(collision_types))]

    # Separate conflicts into the types of vehicles involved in the collisions, save as separate DataFrames
    av_mv_collisions = conflicts[(conflicts['FirstvType'] == 101) | (conflicts['SecondvType'] == 101)]
    mv_mv_collisions = conflicts[(conflicts['FirstvType'] == 100) & (conflicts['SecondvType'] == 100)]

    # Set up list of desired performance parameters
    performance_param = ['TTC', 'PET']

    # Filter by collision type and produce KDEs for
    # KDE for PET and TTC
    # AV-MV Collisions
    for ctype in collision_types:
        for p in performance_param:
            create_kde(av_mv_collisions, ctype, p, cf_ID, "AV-MV")

    for ctype in collision_types:
        for p in performance_param:
            create_kde(mv_mv_collisions, ctype, p, cf_ID, "MV-MV")

    # Filter PET = 0


    # Plot KDE with DeltaS

    # Add throughput values to value


crash_rates = pd.DataFrame([])

# Add data to the conflict rates dataframe ready for export
av_mv_total = len(av_mv_collisions.index)
mv_mv_total = len(mv_mv_collisions.index)
crash_rates[0] = (mv_mv_total+av_mv_total)/total_veh
crash_rates[1] = av_mv_total/man_total
crash_rates[2] = mv_mv_total/man_total
crash_rates[3] = av_mv_total/cav_total
crash_rates[4] = mv_mv_total/cav_total

