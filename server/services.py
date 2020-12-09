import pandas as pd

def read_from_excel(file_path):
    data = []
    if file_path:
        file_type = file_path.split('.')[-1]
        if file_type == "xlsx" or file_type == "xls":
            df = pd.read_excel(file_path, names=['number', 'fullname', 'address', 'checked'], header=None)
            data= data + df.values.tolist()
        else:
            print('not valid file type')
    return data


def allowed_file(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



#td = read_from_excel('test.xlsx')
#for t in td[1:10]:
#    print(t)
