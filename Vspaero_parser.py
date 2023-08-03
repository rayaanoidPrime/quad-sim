import pandas as pd

def parse_text(text):
    data = {}
    lines = text.strip().split('\n')

    for line in lines:
        if "=" in line:
            key, value = line.split("=")
            key = key.strip()
            value = value.strip()
            data[key] = value
        elif line.startswith("NumberOfRotors"):
            break


    df_data = {key: [value] for key, value in data.items()}
    df = pd.DataFrame(df_data)
    
 

    return df

def vsp_parser(file_path):
    with open(file_path, 'r') as file:
        data = file.readlines()
    data_str = ''.join(data)
    df = parse_text(data_str)
    df = df.astype({col: float for col in df.columns if col != 'Preconditioner'  and col != 'Karman-Tsien Correction' and col != 'Symmetry' and col != 'AoA'})
    df['AoA'] = df["AoA"].apply(lambda x: [float(val)*3.14/180 for val in x.split(",")])
    return df


if __name__ == '__main__':
    file_path = "C:/Users/Rayaan_Ghosh/Desktop/Airbus/OpenVSP/assignment-5_DegenGeom.vspaero"
    with open(file_path, 'r') as file:
        data = file.readlines()
    data_str = ''.join(data)
    df = parse_text(data_str)
    df = df.astype({col: float for col in df.columns if col != 'Preconditioner'  and col != 'Karman-Tsien Correction' and col != 'Symmetry' and col != 'AoA'})
    df['AoA'] = df["AoA"].apply(lambda x: [float(val) for val in x.split(",")])
    print("Data Frame:")
    print(df)