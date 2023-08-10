
import pandas as pd

def parse_text(text):
    data = []
    columns = []
    lines = text.strip().split('\n')

    for line in lines:
        if line.startswith("Beta"):
            columns = line.split()
        elif not line.strip():
            break
        else:
            data.append(line.split()[:len(columns)])


    df = pd.DataFrame(data, columns=columns)
    df = df.astype({col: float for col in df.columns})
    return df
    
def polar_parser(file_path):
    with open(file_path, 'r') as file:
        data = file.readlines()
    data_str = ''.join(data)
    df = parse_text(data_str)
    df_selected = df[["AoA" , "CDtot" ]]
    df_selected['AoA'] = df_selected['AoA']*3.14/180
    return df_selected

if __name__ == "__main__":
    file_path = "C:/Users/Rayaan_Ghosh/Desktop/Airbus/OpenVSP/assignment-5_DegenGeom.polar"
    with open(file_path, 'r') as file:
        data = file.readlines()
    data_str = ''.join(data)
    df = parse_text(data_str)
    print("Data Frame:")