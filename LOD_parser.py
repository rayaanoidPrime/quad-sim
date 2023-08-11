import pandas as pd
import io
import numpy as np



def list_to_dataframe(data_list):
    # Extract column headers from the first element of the list
    column_headers = data_list[0].split()

    # Initialize an empty list to store data rows
    data_rows = []

    # Iterate over the remaining elements of the list and split them into individual values
    for item in data_list[1:]:
        row_data = item.split()
        data_rows.append(row_data)

    # Create the pandas DataFrame
    df = pd.DataFrame(data_rows, columns=column_headers)

    return df

# Function to extract the data after encountering the line starting with 'Comp'
def extract_data_after_comp(data,ignore_headers):
    tables = []
    current_table = []

    # Flag to indicate if we have encountered the line starting with 'Comp'
    found_comp = False
    

    # Function to check if a line starts with any of the ignore_headers
    def starts_with_ignore_headers(line):
        return any(line.startswith(header) for header in ignore_headers)

    # Iterate through the lines of the input data
    for line in data:
        if not found_comp:
            if line.startswith('Comp'):
                found_comp = True
            else:
                continue

        # Check if the line is empty, indicating the end of the current table
        if not line.strip():
            # Add the current table to the tables list and reset for the next table
            tables.append(current_table)
            current_table = []
            found_comp = False
        else:
            # Check if the line starts with any of the ignore_headers
            if not starts_with_ignore_headers(line):
                current_table.append(line)

    # Append the last table in the data (if any)
    if current_table:
        tables.append(current_table)

    # Convert the tables to Pandas dataframes
    dfs = pd.DataFrame()
    for table in tables:
        df = list_to_dataframe(table)
        dfs = pd.concat([dfs , df])

    return dfs

def lod_parser(file_path):
    with open(file_path, 'r') as file:
        data = file.readlines()

    # List of headers to ignore
    ignore_headers = {
        '# Name',
        'Sref_',
        'Cref_',
        'Bref_',
        'Xcg_',
        'Ycg_',
        'Zcg_',
        'Mach_',
        'AoA_',
        'Beta_',
        'Rho_',
        'Vinf_',
        'Roll__Rate',
        'Pitch_Rate',
        'Yaw___Rate',
        "0"
    }
    # Extract the data after encountering 'Comp' and the lines until an empty line is found
    dataframes = extract_data_after_comp(data , ignore_headers)
    # Print the dataframes 
    # for idx, df in enumerate(dataframes):
    #     print(f"Dataframe for section {idx}:\n{df}\n\n")
    df_sorted = dataframes.sort_values(by='Comp')
    df_sorted['Key'] = range(len(df_sorted))
    df_sorted.set_index('Key', inplace=True)
    df_sorted = df_sorted.astype({col: float for col in df_sorted.columns if col != 'Name'  and col != 'Comp' and col != 'Component-Name'})
    df_sorted['Comp'] = df_sorted['Comp'].astype(int)
    df_sorted['AoA'] = df_sorted['AoA']*3.14/180
    return df_sorted


def get_cm_df(input_df):
    output_data = {'Comp': [], 'Component-Name': [], 'Slope': [], 'Y-Intercept': []}
    
    # Group the DataFrame by component and process each group
    grouped = input_df.groupby('Comp')
    for comp, group in grouped:
        aoa = group['AoA']
        cmy = group['Cmy']
        
        # Calculate the slope and y-intercept using np.polyfit
        slope, intercept = np.polyfit(aoa, cmy, 1)
        
        # Add the data to the output dictionary
        output_data['Comp'].append(comp)
        output_data['Component-Name'].append(group['Component-Name'].iloc[0])
        output_data['Slope'].append(slope)
        output_data['Y-Intercept'].append(intercept)
    
    # Create a new DataFrame from the output dictionary
    output_df = pd.DataFrame(output_data)
    return output_df


def get_coeffs(df_sorted ):
    df = df_sorted

    # Step 1: Group by 'Comp'
    groups = df.groupby('Comp')

    # Step 2 and 3: Calculate Cmac and x_ac and dCl_dalpha and CL_0 for each group
    for comp, group in groups:
        # CL_1 = group['CL'].iloc[0]
        # CL_2 = group['CL'].iloc[1]
     
        # Cmy_1 = group['Cmy'].iloc[0]
        # Cmy_2 = group['Cmy'].iloc[1]
   
        # AoA_1 = group['AoA'].iloc[0]
        # AoA_2 = group['AoA'].iloc[1]
       
        aoa = group['AoA']
        cl = group['CL']
        
        # Calculate the slope and y-intercept using np.polyfit
        dCl_dalpha, CL_0 = np.polyfit(aoa, cl, 1)
        # Cmac = (CL_1 * Cmy_2 - CL_2 * Cmy_1) / (CL_1 - CL_2)
        # x_ac = wing_mass_props_df.iloc[comp-1]['cgX']
        
        # df.loc[df['Comp'] == comp, 'Cmac'] = Cmac
        # df.loc[df['Comp'] == comp, 'x_ac'] = x_ac
        df.loc[df['Comp'] == comp , 'dCl_dalpha'] = dCl_dalpha
        df.loc[df['Comp'] == comp, 'CL_0'] = CL_0

    # Step 4: Create the new dataframe with the desired columns
    result_df = df.drop_duplicates('Comp').reset_index(drop=True)
    result_df = result_df[['Comp', 'Component-Name', 'AoA', 'CL', 'CDi','dCl_dalpha','CL_0' ]]
    return result_df



if __name__ == "__main__":
    # Read the data from the file
    file_path = "C:/Users/Rayaan_Ghosh/Desktop/Airbus/OpenVSP/4th_config_2.0-20230809T165813Z-001/4th_config_2.0/4thconfig_DegenGeom.lod"
    with open(file_path, 'r') as file:
        data = file.readlines()

    # List of headers to ignore
    ignore_headers = {
        '# Name',
        'Sref_',
        'Cref_',
        'Bref_',
        'Xcg_',
        'Ycg_',
        'Zcg_',
        'Mach_',
        'AoA_',
        'Beta_',
        'Rho_',
        'Vinf_',
        'Roll__Rate',
        'Pitch_Rate',
        'Yaw___Rate',
        "0"
    }
    # Extract the data after encountering 'Comp' and the lines until an empty line is found
    dataframes = extract_data_after_comp(data , ignore_headers)
    # Print the dataframes 
    # for idx, df in enumerate(dataframes):
    #     print(f"Dataframe for section {idx}:\n{df}\n\n")
    df_sorted = dataframes.sort_values(by='Comp')
    df_sorted['Key'] = range(len(df_sorted))
    df_sorted.set_index('Key', inplace=True)
    df_sorted = df_sorted.astype({col: float for col in df_sorted.columns if col != 'Name'  and col != 'Comp' and col != 'Component-Name'})
    df_sorted['Comp'] = df_sorted['Comp'].astype(int)
    df_sorted['AoA'] = df_sorted['AoA']*3.14/180
    cm_df = get_cm_df(df_sorted)
    print(cm_df)
