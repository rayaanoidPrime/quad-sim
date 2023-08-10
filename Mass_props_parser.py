import pandas as pd

def parse_text(text):
    lines = text.strip().split('\n')
    data = []
    ignore = True
    columns = []
    
    for line in lines:
        if line.startswith('Name'):
            ignore = False
            columns = line.split()
            continue

        if not ignore:
            if not line.strip():
                break
            data.append(line.split())

    df = pd.DataFrame(data, columns=columns)
    df = df.astype({col: float for col in df.columns if col != 'Name'})
    return df.iloc[:-1] , df.iloc[-1]

def mass_props_parser(filepath):
    file_path = filepath
    with open(file_path, 'r') as file:
        data = file.readlines()
    data_str = ''.join(data)
    wing_mass_props_df , tot_mass_props_df = parse_text(data_str)
    new_row = {
    'Name': 'WingGeom',
    'Mass': 0,
    'cgX': 0.400698,
    'cgY': 0,
    'cgZ': 0,
    'Ixx': 0,
    'Iyy': 0,
    'Izz': 0,
    'Ixy': 0,
    'Ixz': 0,
    'Iyz': 0,
    'Volume': 0
    }
    wing_mass_props_df = wing_mass_props_df._append(new_row, ignore_index=True)
    return wing_mass_props_df,tot_mass_props_df


if __name__ == "__main__":
    file_path = "C:/Users/Rayaan_Ghosh/Desktop/Airbus/OpenVSP/assignment-5_MassProps.txt"
    with open(file_path, 'r') as file:
        data = file.readlines()
    data_str = ''.join(data)
    wing_mass_props_df , tot_mass_props_df = parse_text(data_str)
    new_row = {
    'Name': 'WingGeom',
    'Mass': 0,
    'cgX': 0.400698,
    'cgY': 0,
    'cgZ': 0,
    'Ixx': 0,
    'Iyy': 0,
    'Izz': 0,
    'Ixy': 0,
    'Ixz': 0,
    'Iyz': 0,
    'Volume': 0
    }
    wing_mass_props_df = wing_mass_props_df.append(new_row, ignore_index=True)
    print(wing_mass_props_df)
    print(tot_mass_props_df)