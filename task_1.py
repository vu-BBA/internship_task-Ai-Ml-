# Task 1: Exploring and Visualizing a Simple Dataset
# Objective:
# Learn how to load, inspect, and visualize a dataset to understand data trends and distributions.
# Dataset:
# Iris Dataset (CSV format, can be loaded via seaborn or downloaded)
# Instructions:
# Load the dataset using pandas.
# Print the shape, column names, and the first few rows using .head().
# Use .info() and .describe() for summary statistics.
# Visualize the dataset:
# Create a scatter plot to show relationships between features.
# create a histogram to show the distribution of a feature.
# Create a bar plot to compare average values across categories.
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
print(sns.__version__)
print(pd.__version__)
print(plt.matplotlib.__version__)
## Load the dataset
# df = sns.load_dataset('iris').head(15)  # load the iris dataset using seaborn
df = pd.read_csv('iris.csv') # load the iris dataset using pandas from a local CSV file
print(df.head(3))  # print the first few rows of the iris dataset to get an overview of the data
print(df.shape)  # print the shape of the dataset to understand the number of rows and columns
print(df.info())  # print summary information about the dataset, including data types and non-null counts
print(df.describe())  # print summary statistics for numerical columns in the dataset
######################### Visualization through seaborn and matplotlib using scatter plots #########################
m= {"setosa": "o", "versicolor": "s", "virginica": "D"}  # marker style for each species
sns.scatterplot(data=df, x="sepal_length", y="sepal_width", hue="species", edgecolor='black', style="species", markers=m)  # create a scatter plot to show the relationship between sepal length and sepal width, colored by species
plt.title("Scatter Plot of Sepal Length vs Sepal Width")  # set the title of the plot
plt.show()  # display the plot
####################### Visualization through seaborn and matplotlib using histogram plots #########################
sns.histplot(data=df, x="petal_width") 
plt.title("Histogram of Petal Width")  # set the title of the plot
plt.show()  # display the plot
########################### Visualization through seaborn and matplotlib using bar plots #########################
sns.barplot(data= df, x="petal_length", y="petal_width", hue="species")  # create a bar plot to show the average petal width for each species
plt.grid(True)  # add a grid to the plot for better readability
plt.show()  # display the plot