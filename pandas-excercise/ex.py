## 1 ##
# import pandas as pd

# df = pd.read_csv('signals.csv')

# print(df.to_string())
## 1 ##
# import pandas as pd

# dtfrm = {
#     'name': ["michael", "saghar"],
#     'family': ["chary", "amini"],
# }

# df = pd.DataFrame(dtfrm)
# print(id(df))
# print(df)
# print(pd.__version__)

# import pandas as pd

# num = ['1', '2', '3', '4', '5', '6']

# may_var = pd.Series(num)

# print(may_var)

##########################

# import pandas as pd

# days = {"day-1": 1, "day-2": 2, "day-3": 3, "day-4": 4}
# my_var = pd.Series(days)

# print(my_var)

# import pandas as pd

# calories = {"day1": 420, "day2": 380, "day3": 390}

# myvar = pd.Series(calories, index=["day1", "day2"])

# print(myvar)

# import pandas as pd

# data = {
#     'name': ['michael', 'saghar'],
#     'family': ['chary', 'amini'],
#     'age':[22,22]
# }

# data_frame = pd.DataFrame(data,index=['p1','p2'])
# print(data_frame)

# import pandas as pd

# data = {
#     "year": [2002, 2024],
#     "duration": [5, 10]
# }
# # loc -> label-based indexing

# data_frame = pd.DataFrame(data, index=['row_1', 'row_2'])
# # print(data_frame.describe())
# # print(data_frame)
# print(data_frame.loc['row_1'])
# print(data_frame.loc["row_2","year"])

# import pandas as pd

# data_frame = pd.read_csv('signals.csv')

# print(data_frame)

# import pandas as pd

# pd.options.display.max_rows = 9999

# dataframe=pd.read_csv

##############################
import pandas as pd

data = {
    "name": ["michael", "pourya", "parham"],
    "family": ["Ch1", "Ch2", "Ch3"],
    "age": [22, 21, 21],
}

data_frame = pd.DataFrame(data)
print("########################")
print(data_frame)
print("########################")
print(data_frame.iloc[0,2])