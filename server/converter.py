import pandas as pd

def convert_to_db(file_path):
    if file_path:
        file_type = file_path.split('.')[-1]
        if file_type == "xlsx" or file_type == "xls":
            df = pd.read_excel(file_path, names=['number', 'fullname', 'address', 'checked'], header=None)
            out_file = df.values.tolist()
        else:
            print('not valid file type')
    return out_file
