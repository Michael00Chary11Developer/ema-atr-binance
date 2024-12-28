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
# import pandas as pd

# data = {
#     "name": ["michael", "pourya", "parham"],
#     "family": ["Ch1", "Ch2", "Ch3"],
#     "age": [22, 21, 21],
# }

# data_frame = pd.DataFrame(data)
# print("########################")
# print(data_frame)
# print("########################")
# print(data_frame.iloc[0,2])

# import pandas as pd

# print(pd.options.display.max_columns)
# print(pd.options.display.max_rows)

# pd.options.display.max_rows = 9999

# data_frame = pd.read_csv('signals.csv')


# print(data_frame)

##################################################

# import pandas as pd

# data = {
#     "Duration": {
#         "0": 60,
#         "1": 60,
#         "2": 60,
#         "3": 45,
#         "4": 45,
#         "5": 60
#     },
#     "Pulse": {
#         "0": 110,
#         "1": 117,
#         "2": 103,
#         "3": 109,
#         "4": 117,
#         "5": 102
#     },
#     "Maxpulse": {
#         "0": 130,
#         "1": 145,
#         "2": 135,
#         "3": 175,
#         "4": 148,
#         "5": 127
#     },
#     "Calories": {
#         "0": 409,
#         "1": 479,
#         "2": 340,
#         "3": 282,
#         "4": 406,
#         "5": 300
#     }
# }

# data_frame = pd.DataFrame(data)
# print(data_frame)

###########################################

# import pandas as pd

# data_frame=pd.read_csv('signals.csv')

# print(data_frame.head())

# print(data_frame.tail())

# import pandas as pd

# data_frame=pd.read_csv('signals-test.csv')

# data_frame.dropna(inplace=True)

# print(data_frame)

###################################

# import pandas as pd

# data = {
#     'num1': [1, 2, 3, None],
#     'num2': [4, 5, 6, None],
#     'num3': [7, 8, 9, 10]
# }

# data_frame = pd.DataFrame(data)
# print('before dropna!!')
# print(data_frame)

# change_date_frame = data_frame.dropna(inplace=True)
# print('\ndrop-nan-data:')
# print(change_date_frame)

#######################################
# import pandas as pd

# data = {
# 'num1': [1, 2, 3, None],
# 'num2': [4, 5, 6, None],
# 'num3': [7, 8, 9, 10]
# }

# data_frame = pd.DataFrame(data)
# print('before dropna!!')
# print(data_frame)
# print("#################")
# print(id(data_frame))
# print("#################")


# data_frame.dropna(inplace=True)


# print('\ndrop-nan-data:')
# print(data_frame)
# print("#################")
# print(id(data_frame))
# print("#################")
#######################################

# import pandas as pd

# data = {
#     'num1': [1, 2, 3, 4],
#     'num2': [5, 6, 7, 8],
#     'num3': [9, 10, 11, 12],
# }

# data_frame = pd.DataFrame(data, index=[1, 2,3,4])

# print(data_frame)

#######################################

# import pandas as pd

# data = {
#     'num1': [1, 2, 3, None],
#     'num2': [4, 5, 6, None],
#     'num3': [7, 8, 9, 10]
# }

# data_frame = pd.DataFrame(data)
# data_frame.fillna(10, inplace=True)
# print(data_frame)

######################################

# import pandas as pd

# data_frame = pd.read_csv('data.csv')


# mean = data_frame['Calories'].mean()

# print('mean is:', mean)

# data_frame.fillna(x, inplace=True)

######################################

# import pandas as pd

# data_frame = pd.read_csv('data.csv')

# meadian = data_frame['Calories'].median()

# print("median is:", meadian)

######################################

# # # # # # import pandas as pd

# # # # # # data_frame = pd.read_csv('order-date.csv')

# # # # # # data_frame['Date'] = pd.to_datetime(data_frame['Date'],format='%Y/%m/%d',errors='coerce')

# # # # # # print(data_frame.to_string())

#####################################

# import pandas as pd

# df = pd.read_csv('data-2.csv')

# df['Date'] = pd.to_datetime(df['Date'])

# print(df.to_string())

# import pandas as pd

# data_frame=pd.read_csv("order-date.csv")

# data_frame.dropna(subset=['Date'],inplace=True)

# print(data_frame)

####################################

# import pandas as pd

# dataframe = pd.read_csv('data-2.csv')

# dataframe.loc[9, 'Duration'] = 45

# # for index in dataframe.index:
# #     if dataframe.loc(index, "Duration") > 120:
# #         dataframe.loc(index, 'Duration') = 120

# for x in dataframe.index:
#   if dataframe.loc[x, "Duration"] > 120:
#     dataframe.loc[x, "Duration"] = 120

####################################

# import pandas as pd

# dataframe=pd.read_csv('duplicated.csv')

# s=dataframe.duplicated()

# print(s)

####################################

# import pandas as pd

# data = {'A': [1, 2, 3, 4, 5, 6, 7, 8, 9.10, 11, 12, 13, 14]}

# data_frame = pd.DataFrame(data)

# print(data_frame.duplicated())
# print("#####################################")

# print(data_frame.to_string())
# print('#####################################')

# data_frame.drop_duplicates(inplace=True)

# print('#####################################')
# print(data_frame.to_string())
# print('#####################################')

# import pandas as pd

# data_frame = pd.read_csv('data-3.csv')

# print(data_frame.corr())

# import pandas as pd
# import matplotlib.pyplot as plt

# data = {
#     "age": [20, 25, 30, 35, 40, 45, 50],
#     "weight": [90, 85, 80, 75, 70, 65, 60]
# }

# index = [1, 2, 3, 4, 5, 6, 7]

# data_frame = pd.DataFrame(data, index=index)

# data_frame.plot()

# plt.show()

# import pandas as pd
# import matplotlib.pyplot as plt

# data_frame=pd.read_csv('signals-test.csv')

# data_frame.plot()

# plt.show()

##########################################

# import pandas as pd
# import matplotlib.pyplot as plt

# data_frame=pd.read_csv('data.csv')

# data_frame.plot()

# plt.show()

###########################################

# import pandas as pd
# import matplotlib.pyplot as plt

# data_frame=pd.read_csv('data-for-plot.csv')

# data_frame.plot()

# plt.show()

#####################################################

# import pandas as pd
# import matplotlib.pyplot as plt

# data_frame = pd.read_csv('data-for-plot.csv')

# data_frame.plot(kind='scatter',x = 'Duration', y = 'Calories')

# plt.show()

######################################################

# import pandas as pd
# import matplotlib.pyplot as plt

# data_frame = pd.read_csv('data-for-plot.csv')

# data_frame['Duration'].plot(kind='hist')

# plt.show()

#######################################################

# import pandas as pd

# data = pd.DataFrame({
#     'A': [1, 2, 3],
#     'B': [4, 5, 6],
#     'C': [7, 8, 9]
# })

# print(data)
# print(data.iloc[1])  
# print(data.iloc[1,2])
# print(data.iloc[0:2, 1:3])  

#######################################################