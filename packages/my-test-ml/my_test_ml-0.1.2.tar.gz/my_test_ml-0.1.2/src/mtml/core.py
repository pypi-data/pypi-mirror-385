"""
Core functionality for mtml package
"""

describe_text = """
list

- get_pd()
- get_np()
- get_pipe()
- get_plt_sb()
- get_decision()
- get_imb()
- get_knn_nb_svm()
- get_lab1()
- get_reg()
- get_scipy()
- get_midterm()
- get_assign2()
- get_ml_clf()
- get_ml_reg()
"""

pd_text = """# --- Library Import ---

# Import the pandas library and assign it the alias 'pd'
import pandas as pd
# Import the numpy library for array creation, as it's used to build a DataFrame
import numpy as np


# --- Series Creation and Manipulation ---

# Create a pandas Series with custom index labels
series1 = pd.Series([1,2,3,4,5], index=['row1', 'row2', 'row3', 'row4', 'row5'])

# Get the values from the Series as a NumPy array
series1.values

# Get the index labels of the Series
series1.index

# Access an element using its index label as an attribute
series1.row3

# Access an element using its index label in brackets
series1['row2']

# Change the index labels of an existing Series
series1.index = ['a', 'b', 'c', 'd', 'e']


# --- DataFrame Creation ---

# Create a NumPy array
array1 = np.array([[1,5,9,13], [2,6,10,19], [3,7,11,5], [4,8,12,16]])

# Create a DataFrame from the NumPy array with custom row and column labels
df1 = pd.DataFrame(array1, index=['row1', 'row2', 'row3', 'row4'], columns=['col1', 'col2', 'col3', 'col4'])

# Create a dictionary where keys are column names and values are lists of column data
dic1 = {'col1': [1,2,3,4], 'col2': [5,6,7,8], 'col3': [9,10,11,12], 'col4': [13,14,16,16]}

# Create a DataFrame from the dictionary
df2 = pd.DataFrame(dic1, index=['row1', 'row2', 'row3', 'row4'])


# --- DataFrame Inspection ---

# Get the index (row labels) of the DataFrame
df2.index

# Get the column labels of the DataFrame
df2.columns

# Get the values of the DataFrame as a NumPy array
df2.values


# --- Data Selection and Slicing ---

# Select a row by its label using .loc
df2.loc['row1'][:]

# Select a single cell by its row and column labels using .loc
df2.loc['row1']['col2']

# Select a row by its integer position using .iloc
df2.iloc[0][:]

# Select a single cell by its row and column integer positions using .iloc
df2.iloc[0][1]


# --- DataFrame Modification ---

# Rename a specific column
# Note: The original PDF had a syntax error. The correct syntax uses a dictionary.
df2.rename(columns={'col4': 'column4'})

# Replace all occurrences of the value 1 with 10 throughout the DataFrame
df2.replace({1: 10})


# --- Sorting and Viewing ---

# Sort the DataFrame by column labels in descending order
df2.sort_index(axis=1, ascending=False)

# Sort the DataFrame by the values in a specific column ('col1') in descending order
df2.sort_values(by='col1', ascending=False)

# Display the first 2 rows of the DataFrame
df2.head(2)

# Display the last 2 rows of the DataFrame
df2.tail(2)


# --- Importing Data ---

# Read data from a CSV file into a new DataFrame called 'data1'
data1 = pd.read_csv('F:/00-Douglas College/1- Semester 1/3- Machine Learning in Data Science (3290)/Slides/ozone1.csv')

# Display the first 5 rows of the imported data to verify it loaded correctly
data1.head()"""


np_text = """# --- Library Import and Version ---

# Import the NumPy library and assign it the alias 'np'
import numpy as np

# Check the installed version of NumPy
np.__version__

# --- Array and Matrix Creation ---

# Correctly create a 2x2 NumPy array
a = np.array([[1,2],[3,4]])

# Create a 2x2 NumPy matrix
b = np.matrix([[1,2],[3,4]])

# Create a 2x2 array with a specific data type (8-bit integer)
a = np.array([[1,2],[3,4]], dtype='int8')

# Create a 1D array
b = np.array([1,2,3])

# Create a 3x3 array filled with the value 1
c = np.ones((3,3))

# Create another 1D array
d = np.array([5,6,7])

# Create a 3x1 array filled with the value 1
e = np.ones((3,1))

# Create a 2x2 array
g = np.array([[1,2],[3,4]])

# --- Multiplication Operations ---

# Perform matrix multiplication on array 'a' with itself
np.dot(a,a)

# Perform element-wise multiplication on array 'a' with itself
np.multiply(a,a)

# Calculate the product of all elements in array 'a'
np.prod(a)

# --- Broadcasting ---

# Add 5 to each element in array 'b'
b + 5

# Add 1D array 'd' to each row of 2D array 'c'
c + d

# Add 1D array 'f' to each row of 2D array 'e'
# Note: 'f' was not defined in the provided snippets, assuming it's similar to 'd' for this example.
f = np.array([5,6,7])
e + f

# --- Basic Math Operations ---

# Calculate the sum of all elements in array 'g'
np.sum(g)

# Calculate the cumulative sum along the columns (axis=0)
np.cumsum(g, axis=0)

# Calculate the cumulative sum along the rows (axis=1)
np.cumsum(g, axis=1)

# Subtract array 'a' from itself element-wise
np.subtract(a,a)

# Divide each element in the list by 3
np.divide([5,6,7],3)

# Perform floor division for each element in the list by 3
np.floor_divide([5,6,7],3)

# Generate a 2x3 array with random numbers from a uniform distribution between 1 and 5
np.random.uniform(1,5,(2,3))

# Generate a 2x1 array with random numbers from a standard normal distribution
np.random.standard_normal((2,1))

# --- Array Generation and Properties ---

# Create an array starting from 1 up to (but not including) 10, with a step of 3
np.arange(1,10,3)

# Create an array with 4 evenly spaced numbers from 1 to 10
np.linspace(1,10,4)

# Get the total number of elements in array 'a'
np.size(a)

# Get the dimensions (shape) of array 'a'
np.shape(a)

# --- Set and Statistical Operations ---

# Create a 1D array
a = np.array([1,7,2,3,1,2,4,3])

# Find the unique elements in array 'a'
np.unique(a)

# Create another 1D array
b = np.array([3,4,6,7,8,1,2])

# Find the union of elements in arrays 'a' and 'b'
np.union1d(a,b)

# Find the common elements (intersection) between arrays 'a' and 'b'
np.intersect1d(a,b)

# Calculate the mean (average) of array 'a'
np.mean(a)

# Find the median of array 'a'
np.median(a)

# Calculate the standard deviation of array 'a'
np.std(a)

# Calculate the variance of array 'a'
np.var(a)

# --- Polynomial Operations ---

# Define polynomial coefficients for x^2 + x + 2
coeff = np.array([1,1,2])

# Evaluate the polynomial at x=1
np.polyval(coeff, 1)

# Calculate the derivative of the polynomial
np.polyder(coeff)

# Calculate the integral of the polynomial
np.polyint(coeff)"""


pipe_text = """# --- Library Imports ---

# General data science and machine learning libraries
from sklearn import datasets
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SelectKBest
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import accuracy_score
from pandas import read_csv


# --- Example 1: Basic Pipeline with Scaling, PCA, and a Classifier ---

# --- 1. Data Loading and Preparation ---

# Load the built-in Iris dataset
iris = datasets.load_iris()

# Separate the features (x) and the target variable (y)
x = iris.data
y = iris.target

# Split the data into training and testing sets, with 25% of the data reserved for testing
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25)


# --- 2. Pipeline Creation and Execution ---

# Define the sequence of steps for the pipeline:
# 1. 'pca': Reduce dimensionality to 2 principal components.
# 2. 'std': Standardize the features (scale to unit variance).
# 3. 'DC': Use a Decision Tree Classifier for the final prediction.
pipeline1 = Pipeline([
    ('pca', PCA(n_components=2)),
    ('std', StandardScaler()),
    ('DC', DecisionTreeClassifier())
], verbose=True)

# Train the entire pipeline on the training data.
# This will execute each step in sequence on the data.
pipeline1.fit(x_train, y_train)


# --- 3. Evaluation ---

# Make predictions on the test set using the trained pipeline and print the accuracy score.
print(f"Accuracy for Pipeline 1: {accuracy_score(y_test, pipeline1.predict(x_test))}")


# --- Example 2: Pipeline with FeatureUnion for Combined Feature Extraction ---

# --- 1. Data Loading and Preparation ---

# URL for the Pima Indians Diabetes dataset
url_data = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"

# Define column names for the dataset
varnames = ['var_preg', 'var_plas', 'var_pres', 'var_skin', 'var_test', 'var_mass', 'var_pedi', 'var_age', 'var_class']

# Read the CSV data from the URL into a pandas DataFrame
vardataframe = read_csv(url_data, names=varnames)

# Convert the DataFrame to a NumPy array
vararray = vardataframe.values

# Separate the features (varX) and the target variable (vary)
# Note: The PDF slice [:,0:7] was corrected to [:,0:8] to include all 8 feature columns.
varX = vararray[:, 0:8]
vary = vararray[:, 8]


# --- 2. Feature Union and Pipeline Creation ---

# Create a list to hold the feature extraction methods that will be combined
urlfeatures = []

# First feature extraction method: Select the 6 best features using statistical tests.
urlfeatures.append(('select_best', SelectKBest(k=6)))

# Second feature extraction method: Apply PCA to get the top 3 principal components.
urlfeatures.append(('pca', PCA(n_components=3)))

# Use FeatureUnion to combine the results of both feature extraction methods into a single feature set.
# The results of 'select_best' (6 features) and 'pca' (3 features) will be concatenated.
feature_union = FeatureUnion(urlfeatures)

# Create the final pipeline steps
pipeline2_steps = []

# Step 1: Apply the combined feature extraction (FeatureUnion).
pipeline2_steps.append(('feature_union', feature_union))

# Step 2: Apply a Logistic Regression model to the combined features.
pipeline2_steps.append(('logistic', LogisticRegression()))

# Create the final model by wrapping the steps in a Pipeline object
model = Pipeline(pipeline2_steps)


# --- 3. Evaluation using K-Fold Cross-Validation ---

# Initialize a 10-fold cross-validation splitter
varkfold = KFold(n_splits=10)

# Evaluate the entire pipeline model using 10-fold cross-validation and get the accuracy for each fold
dataresults = cross_val_score(model, varX, vary, cv=varkfold)

# Print the mean accuracy across all 10 folds
print(f"\nMean accuracy for Pipeline 2: {dataresults.mean()}")"""


plt_sb_text = """# --- Installation Commands (for Anaconda Prompt) ---

# Note: These are not Python code, but commands to be run in the Anaconda Powershell Prompt or terminal.
# conda install matplotlib
# conda install seaborn


# --- Library Imports ---

# Import necessary libraries for data handling, numerical operations, and plotting
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb


# --- Matplotlib Basic Plots ---

# Define data for plotting
years = [1960, 1970, 1980, 1990, 2000, 2010]
population = [21.91, 23.90, 24.80, 20.93, 22.30, 26.90]

# 1. Line Plot: Shows trends over continuous intervals.
print("--- Displaying Line Plot ---")
plt.plot(years, population)
plt.show()

# 2. Scatter Plot: Shows the relationship between two variables.
print("--- Displaying Scatter Plot ---")
plt.scatter(years, population)
plt.show()

# Scatter Plot with custom colors
# Note: The PDF uses different variables 'Years' and 'Population' here without defining them.
# The following are example values to make the code runnable.
Years_example = [1990, 2000, 2010, 2020, 2030]
Population_example = [26.7, 23.4, 27.5, 28.5, 24.9]
colors = ['violet', 'tomato', 'crimson', 'green', 'blue']
print("--- Displaying Scatter Plot with Custom Colors ---")
plt.scatter(Years_example, Population_example, c=colors)
plt.show()


# Define data for city populations
city_Name = ['London', 'Paris', 'Tokyo', 'Beijing', 'Rome'] # Corrected typo from 'Tokyu'
city_Pop = [65342, 89123, 54239, 23098, 12367]

# 3. Histogram: Represents the distribution of numerical data.
print("--- Displaying Histogram (Default Bins) ---")
plt.hist(city_Pop)
plt.show()

# Histogram with a specified number of bins
print("--- Displaying Histogram (1 Bin) ---")
plt.hist(city_Pop, bins=1)
plt.show()

# Histogram with bins determined automatically
print("--- Displaying Histogram (Auto Bins) ---")
plt.hist(city_Pop, bins='auto')
plt.show()

# 4. Pie Chart: Shows the proportion of different categories.
print("--- Displaying Pie Chart ---")
plt.pie(city_Pop, labels=city_Name)
plt.show()


# --- Plot Customization ---

# Customize a line plot by adding labels, titles, and custom tick marks.
print("--- Displaying Customized Line Plot ---")
# Set the figure size and resolution
plt.figure(figsize=(9, 7), dpi=80)
# Create the plot
plt.plot(years, population)
# Add labels and titles
plt.xlabel('Years')
plt.ylabel('Population') # Corrected typo from 'Popuation'
# Set custom ticks for x and y axes
plt.xticks([1960, 1970, 1980, 1990, 2000, 2010])
plt.yticks([20.93, 21.91, 22.30, 23.90, 24.80, 26.90], ['20M', '21M', '22M', '23M', '24M', '26M'])
plt.show()

# Customize a scatter plot
# The first plot shows the default x-axis (0, 1, 2, 3, 4)
print("--- Displaying Scatter Plot with Default Ticks ---")
plt.scatter(np.arange(5), city_Pop)
plt.show()

# The second plot adds a title and custom x-axis tick labels
print("--- Displaying Customized Scatter Plot ---")
plt.scatter(np.arange(5), city_Pop)
plt.title('Most Populated Cities')
plt.xticks([0, 1, 2, 3, 4], ['1960', '1970', '1980', '1990', '2000'])
plt.show()


# --- Multiple Plots ---

# Define data for two countries
years = [1960, 1970, 1980, 1990, 2000, 2010]
Canada_Pop = [21.91, 23.90, 24.80, 20.93, 22.30, 26.90]
USA_Pop = [32.91, 24.80, 23.60, 21.92, 32.30, 26.90]

# 1. Plot multiple lines on the same axes
print("--- Displaying Multiple Plots on Same Axes ---")
plt.plot(years, Canada_Pop, marker='s', mew=8, ls='-', label='Canada') # marker='s' for square
plt.plot(years, USA_Pop, ls='--', lw=1, label='USA')
# Add a legend to identify the lines
plt.legend(['Canada', 'USA'], loc='best')
# Add a grid for better readability
plt.grid()
plt.show()

# 2. Use subplots to create multiple plots in the same figure
print("--- Displaying Multiple Plots using Subplots ---")
# First subplot (1 row, 2 columns, plot 1)
plt.subplot(1, 2, 1)
plt.plot(years, Canada_Pop, marker='s', mew=8, ls='-') # marker='s' for square
plt.title('Population of Canada')

# Second subplot (1 row, 2 columns, plot 2)
plt.subplot(1, 2, 2)
plt.plot(years, USA_Pop, ls='--', lw=1)
plt.title('Population of United States')
plt.show()


# --- Seaborn Plots ---

# Load the dataset for Seaborn plots
# Note: You will need to replace the file path with the actual location of your 'ozone1.csv' file.
# data1 = pd.read_csv('path/to/your/ozone1.csv')
# The path from the document is used here as a placeholder.
try:
    data1 = pd.read_csv('F:/00-Douglas College/1- Semester 1/3- Machine Learning in Data Science (3290)/Slides/ozone1.csv', low_memory=False)

    # 1. Strip Plot: A scatter plot for categorical data.
    # 'jitter=True' adds a small amount of random noise to prevent points from overlapping.
    print("--- Displaying Seaborn Strip Plot ---")
    sb.stripplot(x='State Name', y='Site Num', data=data1, size=10, jitter=True)
    plt.show()

    # 2. Box Plot: Shows the distribution of data based on a five-number summary.
    print("--- Displaying Seaborn Box Plot ---")
    sb.boxplot(x='State Name', y='Site Num', data=data1)
    plt.show()

    # 3. Joint Plot: Combines a scatter plot with histograms on the axes.
    print("--- Displaying Seaborn Joint Plot ---")
    sb.jointplot(x='State Name', y='Site Num', data=data1, kind='scatter')
    plt.show()

except FileNotFoundError:
    print("\n" + "="*50)
    print("--- Seaborn Plotting Skipped ---")
    print("Could not find the 'ozone1.csv' file at the specified path.")
    print("Please update the file path in the code to run the Seaborn examples.")
    print("="*50 + "\n")"""


decision_text = """# --- Library Imports ---

# Import pandas for data manipulation and analysis
import pandas as pd

# Import the datasets module from scikit-learn to load sample data
from sklearn import datasets

# Import the model_selection module for splitting data
from sklearn.model_selection import train_test_split

# Import the Decision Tree classifier model
from sklearn.tree import DecisionTreeClassifier

# Import the metrics module to evaluate model performance
from sklearn import metrics

# Import the tree module for visualization
from sklearn import tree

# Import pyplot for plotting graphs
import matplotlib.pyplot as plt


# --- Data Loading and Exploration ---

# Load the built-in Iris dataset from scikit-learn
iris1 = datasets.load_iris()

# Check the dimensions (shape) of the feature data (150 samples, 4 features)
iris1.data.shape

# Get the names of the four features
iris1.feature_names

# Get the names of the three target classes (species of iris)
iris1.target_names

# Get a full description of the dataset
iris1.DESCR


# --- Data Preparation and Visualization ---

# Convert the Iris data into a pandas DataFrame
irisDF = pd.DataFrame(iris1.data, columns=iris1.feature_names)

# Add the target labels (the species) as a new column in the DataFrame
irisDF['target'] = iris1.target

# Create a scatter plot matrix to visualize the relationships between all features
# The points are colored by their target class
pd.plotting.scatter_matrix(irisDF, c=iris1.target, figsize=[11, 11], s=150)
plt.show()

# Separate the features (X) and the target variable (y)
x = iris1.data
y = iris1.target

# Print the feature values and the target class for a single sample (the 3rd one)
print(x[2], y[2])

# Create a scatter plot of the first two features (sepal length vs. sepal width), colored by target class
plt.scatter(x[:, 0], x[:, 1], c=y)
plt.show()

# Create a new feature set 'x1' containing only the last two features (petal length and petal width)
x1 = iris1.data[:, [2, 3]]


# --- Model Training Preparation ---

# Split the dataset into training (70%) and testing (30%) sets.
# 'stratify=y' ensures that the proportion of classes is the same in both train and test sets.
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)

# Check the shape of the training feature set
x_train.shape

# Check the shape of the testing feature set
x_test.shape


# --- Decision Tree Model: Training, Prediction, and Evaluation ---

# Initialize the Decision Tree classifier model
tree1 = DecisionTreeClassifier()

# Train (fit) the model using the training data
tree1.fit(x_train, y_train)

# Use the trained model to make predictions on the test data
pre1 = tree1.predict(x_test)

# Calculate the accuracy of the model by comparing the predictions (pre1) with the actual labels (y_test)
metrics.accuracy_score(y_test, pre1)

# Another way to calculate the accuracy of the model on the test set
tree1.score(x_test, y_test)


# --- Decision Tree Visualization ---

# Get the feature names for labeling the plot
f1 = iris1.feature_names

# Generate and display a plot of the trained decision tree
tree.plot_tree(tree1, feature_names=f1)
plt.show()"""


imb_text = """# --- Library Imports and Data Loading ---

# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import NearMiss

# Load the credit card fraud dataset from a CSV file
data1 = pd.read_csv('C:/Users/Paris/Desktop/creditcard.csv')

# Display a summary of the DataFrame, including data types and non-null values
print(data1.info())


# --- Initial Data Preparation and Splitting ---

# Drop the 'Time' and 'Amount' columns as they are not needed for this model
data1 = data1.drop(['Time', 'Amount'], axis=1)

# Check the distribution of the target variable 'Class' (0 for non-fraud, 1 for fraud)
data1['Class'].value_counts()

# Separate the feature variables (X) from the target variable (y)
x = data1.drop(['Class'], axis=1).values
y = data1['Class'].values # Corrected from PDF for consistency

# Split the data into training (70%) and testing (30%) sets
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=0)

# Print the dimensions of the resulting datasets to confirm the split
print("Number transactions X_train dataset: ", X_train.shape)
print("Number transactions y_train dataset: ", y_train.shape)
print("Number transactions X_test dataset: ", X_test.shape)
print("Number transactions y_test dataset: ", y_test.shape)


# --- Model Training on Original (Imbalanced) Data ---

# Initialize a Logistic Regression model
lr = LogisticRegression()

# Train the model on the original imbalanced training data
# .ravel() is used to flatten the y_train array to the 1D format expected by the fit method
lr.fit(X_train, y_train.ravel())

# Make predictions on the test set
predictions = lr.predict(X_test)

# Print the classification report to evaluate the model's performance
print("--- Results on Imbalanced Data ---")
print(classification_report(y_test, predictions))

# Display the count of minority (1) and majority (0) classes before resampling
print("\nBefore OverSampling, counts of label '1': {}".format(sum(y_train == 1)))
print("Before OverSampling, counts of label '0': {} \n".format(sum(y_train == 0)))


# --- Handling Imbalance with SMOTE (Oversampling) ---

# Initialize the SMOTE (Synthetic Minority Over-sampling Technique) algorithm
sm = SMOTE(random_state=2)

# Apply SMOTE to the training data to generate synthetic samples for the minority class
X_train_res, y_train_res = sm.fit_resample(X_train, y_train.ravel())

# Print the shape and class distribution of the newly resampled training data
print('After OverSampling, the shape of train_X: {}'.format(X_train_res.shape))
print('After OverSampling, the shape of train_y: {} \n'.format(y_train_res.shape))
print("After OverSampling, counts of label '1': {}".format(sum(y_train_res == 1)))
print("After OverSampling, counts of label '0': {}".format(sum(y_train_res == 0)))

# Initialize a new Logistic Regression model
lr1 = LogisticRegression()

# Train the new model on the balanced (oversampled) training data
lr1.fit(X_train_res, y_train_res.ravel())

# Make predictions on the original test set
predictions = lr1.predict(X_test)

# Print the classification report for the model trained on SMOTE data
print("\n--- Results after SMOTE Oversampling ---")
print(classification_report(y_test, predictions))


# --- Handling Imbalance with NearMiss (Undersampling) ---

# Display the class counts before applying undersampling
print("\nBefore Undersampling, counts of label '1': {}".format(sum(y_train == 1)))
print("Before Undersampling, counts of label '0': {} \n".format(sum(y_train == 0)))

# Initialize the NearMiss undersampling algorithm
nr = NearMiss()

# Apply NearMiss to the training data to reduce the number of majority class samples
X_train_miss, y_train_miss = nr.fit_resample(X_train, y_train.ravel())

# Print the shape and class distribution of the newly undersampled training data
print('After Undersampling, the shape of train_X: {}'.format(X_train_miss.shape))
print('After Undersampling, the shape of train_y: {} \n'.format(y_train_miss.shape))
print("After Undersampling, counts of label '1': {}".format(sum(y_train_miss == 1)))
print("After Undersampling, counts of label '0': {}".format(sum(y_train_miss == 0)))

# Initialize a third Logistic Regression model
lr2 = LogisticRegression()

# Train the model on the balanced (undersampled) training data
lr2.fit(X_train_miss, y_train_miss.ravel())

# Make predictions on the original test set
predictions = lr2.predict(X_test)

# Print the classification report for the model trained on NearMiss data
print("\n--- Results after NearMiss Undersampling ---")
print(classification_report(y_test, predictions))"""


knn_nb_svm_text = """# --- Common Imports and Data Preparation ---

# Import necessary libraries
import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, classification_report

# Load the Iris dataset, a classic dataset in machine learning
iris1 = datasets.load_iris()

# --- Inspect the Dataset ---

# Check the dimensions of the data (samples, features)
print("--- Iris Dataset Shape ---")
print(iris1.data.shape) # Expected output: (150, 4)

# Display the names of the features (columns)
print("\n--- Iris Feature Names ---")
print(iris1.feature_names)

# Display the names of the target classes (types of iris flowers)
print("\n--- Iris Target Names ---")
print(iris1.target_names)
print("\n" + "="*50 + "\n")


# --- Data Splitting ---

# Assign feature data to 'x' and target data to 'y'
x = iris1.data
y = iris1.target

# Split the dataset into training and testing sets
# 70% for training, 30% for testing
# stratify=y ensures that the proportion of classes is the same in train and test sets
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)

# --- K-Nearest Neighbors (KNN) Classifier ---

# Model 1: n_neighbors=6, metric='minkowski', p=2 (Euclidean distance)
print("--- KNN Model 1 (k=6, Euclidean) ---")
knn1 = KNeighborsClassifier(n_neighbors=6, metric='minkowski', p=2)
knn1.fit(x_train, y_train)
y_predict_knn1 = knn1.predict(x_test)
print(f"Score: {knn1.score(x_test, y_test)}\n") # Expected score: ~0.955

# Model 2: n_neighbors=20, metric='minkowski', p=2 (Euclidean distance)
print("--- KNN Model 2 (k=20, Euclidean) ---")
knn2 = KNeighborsClassifier(n_neighbors=20, metric='minkowski', p=2)
knn2.fit(x_train, y_train)
y_predict_knn2 = knn2.predict(x_test)
print(f"Score: {knn2.score(x_test, y_test)}\n") # Expected score: ~0.933

# Model 3: n_neighbors=6, metric='minkowski', p=1 (Manhattan distance)
print("--- KNN Model 3 (k=6, Manhattan) ---")
knn3 = KNeighborsClassifier(n_neighbors=6, metric='minkowski', p=1)
knn3.fit(x_train, y_train)
y_predict_knn3 = knn3.predict(x_test)
print(f"Score: {knn3.score(x_test, y_test)}\n") # Expected score: ~0.888
print("\n" + "="*50 + "\n")


# --- Gaussian Naïve Bayes Classifier ---
print("--- Gaussian Naïve Bayes Model ---")
gnb1 = GaussianNB()
# Fit the model and predict on the test data in one line
y_pred_gnb = gnb1.fit(x_train, y_train).predict(x_test)

# Evaluate the model's accuracy
print(f"Score: {gnb1.score(x_test, y_test)}\n") # Expected score: ~0.911

# Display the confusion matrix to see where the model made errors
print("--- Confusion Matrix ---")
print(confusion_matrix(y_test, y_pred_gnb))
print("\n")

# Display a detailed classification report (precision, recall, f1-score)
print("--- Classification Report ---")
print(classification_report(y_test, y_pred_gnb))
print("\n" + "="*50 + "\n")


# --- Support Vector Machine (SVM) Classifier ---

# Model 1: Linear Kernel with 'ovo' (one-vs-one) decision function
print("--- SVM Model 1 (Linear Kernel, ovo) ---")
svc1 = SVC(kernel='linear', random_state=0, decision_function_shape='ovo')
svc1.fit(x_train, y_train)
preds1 = svc1.predict(x_test)
print(f"Predictions: {preds1}")
print(f"Score: {svc1.score(x_test, y_test)}\n") # Expected score: 1.0

# Model 2: Linear Kernel with 'ovr' (one-vs-rest) decision function
print("--- SVM Model 2 (Linear Kernel, ovr) ---")
svc2 = SVC(kernel='linear', random_state=0, decision_function_shape='ovr')
svc2.fit(x_train, y_train)
preds2 = svc2.predict(x_test)
print(f"Score: {svc2.score(x_test, y_test)}\n") # Expected score: 1.0

# Model 3: RBF Kernel with high gamma (gamma=0.7)
# High gamma can lead to overfitting
print("--- SVM Model 3 (RBF Kernel, gamma=0.7) ---")
svc3 = SVC(kernel='rbf', gamma=0.7, C=1.0)
svc3.fit(x_train, y_train)
preds3 = svc3.predict(x_test)
print(f"Score: {svc3.score(x_test, y_test)}\n") # Expected score: ~0.977

# Model 4: RBF Kernel with lower gamma (gamma=0.2)
# Lower gamma creates a smoother decision boundary
print("--- SVM Model 4 (RBF Kernel, gamma=0.2) ---")
svc4 = SVC(kernel='rbf', gamma=0.2, C=1.0)
svc4.fit(x_train, y_train)
preds4 = svc4.predict(x_test)
print(f"Score: {svc4.score(x_test, y_test)}\n") # Expected score: 1.0

# Model 5: RBF Kernel with lower gamma (0.2) and smaller C (0.2)
# A smaller C value creates a wider margin, allowing for more misclassifications
print("--- SVM Model 5 (RBF Kernel, gamma=0.2, C=0.2) ---")
svc5 = SVC(kernel='rbf', gamma=0.2, C=0.2)
svc5.fit(x_train, y_train)
preds5 = svc5.predict(x_test)
print(f"Score: {svc5.score(x_test, y_test)}\n") # Expected score: ~0.933"""


lab1_text = """# --- Library Imports ---

# Import necessary libraries for data manipulation, analysis, and visualization
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb

# Import scikit-learn modules for datasets, modeling, and evaluation
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score


# --- Data Loading and Initial Exploration ---

# Load the built-in wine dataset
wine1 = load_wine()

# Check the shape of the dataset (number of samples, number of features)
print(wine1.data.shape)

# Display the names of the features (columns)
print(wine1.feature_names)

# Display the names of the target classes
print(wine1.target_names)

# Create a pandas DataFrame from the dataset for easier analysis
wineDF = pd.DataFrame(wine1.data, columns=wine1.feature_names)

# Add the target labels as a new column to the DataFrame
wineDF['target'] = wine1.target


# --- Data Visualization and Correlation Analysis ---

# Create a scatter plot matrix to visualize pairwise relationships between all features
# Points are colored by their target class
pd.plotting.scatter_matrix(wineDF, c=wine1.target, figsize=[11, 11], s=150)
plt.show()

# Calculate the correlation matrix for all features and the target
cor1 = wineDF.corr()

# Display the correlation matrix
print(cor1)

# Generate a heatmap to visually represent the correlation matrix
sb.heatmap(cor1)
plt.show()


# --- Data Preparation for Modeling ---

# Separate the features (x) and the target variable (y)
x = wine1.data
y = wine1.target

# Split the data into training (70%) and testing (30%) sets
# 'stratify=y' ensures the class proportions are maintained in both sets
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)


# --- Model 1: Decision Tree Classifier ---

# Initialize the Decision Tree classifier model
tree1 = DecisionTreeClassifier()

# Train (fit) the model using the training data
tree1.fit(x_train, y_train)

# Use the trained model to make predictions on the test data
pre1 = tree1.predict(x_test)

# Calculate and print the accuracy of the model
print(f"Decision Tree Accuracy: {accuracy_score(y_test, pre1)}")

# Print the detailed classification report (precision, recall, f1-score)
print("\nDecision Tree Classification Report:")
print(classification_report(y_test, pre1))

# Print the confusion matrix
print("\nDecision Tree Confusion Matrix:")
print(confusion_matrix(y_test, pre1))

# Visualize the structure of the trained decision tree
plt.figure(figsize=(20,10)) # Set figure size for better readability
plot_tree(tree1, feature_names=wine1.feature_names, class_names=wine1.target_names, filled=True)
plt.show()


# --- Model 2: K-Nearest Neighbors (KNN) Classifier ---

# --- KNN with k=6 ---
# Initialize the KNN classifier with 6 neighbors
knn1 = KNeighborsClassifier(n_neighbors=6, metric='minkowski', p=2)
knn1.fit(x_train, y_train)
print(f"\nKNN (k=6) Accuracy: {knn1.score(x_test, y_test)}")

# --- KNN with k=8 ---
# Initialize the KNN classifier with 8 neighbors
knn2 = KNeighborsClassifier(n_neighbors=8, metric='minkowski', p=2)
knn2.fit(x_train, y_train)
print(f"KNN (k=8) Accuracy: {knn2.score(x_test, y_test)}")

# --- KNN with k=10 ---
# Initialize the KNN classifier with 10 neighbors
knn3 = KNeighborsClassifier(n_neighbors=10, metric='minkowski', p=2)
knn3.fit(x_train, y_train)
y_predict3 = knn3.predict(x_test)
print(f"KNN (k=10) Accuracy: {knn3.score(x_test, y_test)}")

# Print the confusion matrix for the KNN model with k=10
print("\nKNN (k=10) Confusion Matrix:")
print(confusion_matrix(y_test, y_predict3))"""


reg_text = """# --- Library Imports ---

# Import necessary libraries for data handling, plotting, and machine learning
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.datasets import load_wine
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import confusion_matrix, classification_report, mean_squared_error
from sklearn.preprocessing import normalize


# --- Linear Regression Example ---

# --- 1. Data Creation and Visualization ---

# Create sample data using NumPy arrays for a simple linear relationship
x1 = np.arange(1, 10)
y1 = np.array([23, 34, 44, 56, 65, 67, 70, 76, 79]) # Note: y1 is redefined in the PDF later, using the values from the plot for consistency.

# Create a scatter plot to visualize the initial data points
plt.scatter(x1, y1)
plt.show()

# --- 2. Data Preparation ---

# Reshape the 1D arrays into 2D column vectors, as required by scikit-learn
x1 = x1.reshape(-1, 1)
y1 = y1.reshape(-1, 1) # Note: The PDF shows different values for y1 here. This code reflects the reshape action.

# --- 3. Model Training and Prediction ---

# Initialize the Linear Regression model
reg1 = LinearRegression()

# Train (fit) the model using the prepared data
reg1.fit(x1, y1)

# Use the trained model to make predictions on the original x-values
y_pred = reg1.predict(x1)

# --- 4. Evaluation and Visualization ---

# Plot the original data points (blue) and the model's predictions (orange)
plt.scatter(x1, y1)
plt.scatter(x1, y_pred)
plt.show()

# Calculate the Mean Squared Error (MSE) to evaluate the model's performance
mse1 = mean_squared_error(y1, y_pred)
print(f"Mean Squared Error: {mse1}")


# --- K-Fold Cross-Validation for Linear Regression ---

# Perform 4-fold cross-validation using the default scoring metric (R-squared)
cv_score_r2 = cross_val_score(reg1, x1, y1, cv=4)
print(f"\nCross-Validation R2 Scores: {cv_score_r2}")
print(f"Mean R2 Score: {np.mean(cv_score_r2)}")

# Perform 4-fold cross-validation using negative mean squared error as the scoring metric
cv_score_neg_mse = cross_val_score(reg1, x1, y1, cv=4, scoring='neg_mean_squared_error')
print(f"\nCross-Validation Negative MSE Scores: {cv_score_neg_mse}")
print(f"Mean Negative MSE: {np.mean(cv_score_neg_mse)}")

# Perform 4-fold cross-validation using negative root mean squared error
cv_score_neg_rmse = cross_val_score(reg1, x1, y1, cv=4, scoring='neg_root_mean_squared_error')
print(f"\nCross-Validation Negative RMSE Scores: {cv_score_neg_rmse}")
print(f"Mean Negative RMSE: {np.mean(cv_score_neg_rmse)}")


# --- Logistic Regression Example ---

# --- 1. Data Loading and Preparation ---

# Load the built-in Wine dataset
data1 = load_wine()

# Create a pandas DataFrame from the wine data for easier manipulation
wineDF = pd.DataFrame(data1.data, columns=data1.feature_names)
wineDF['target'] = data1.target

# Separate the features (x) and the target variable (y)
x = data1.data
y = data1.target

# Split the data into training (70%) and testing (30%) sets
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

# --- 2. Model Training and Prediction ---

# Initialize the Logistic Regression model
reg2 = LogisticRegression(max_iter=2500) # Increased max_iter to address convergence warning in PDF

# Train the model on the training data
reg2.fit(x_train, y_train)

# Make predictions on the test data
pre2 = reg2.predict(x_test)

# --- 3. Evaluation ---

# Generate the confusion matrix to evaluate the classification accuracy
cm = confusion_matrix(y_test, pre2)
print("\n--- Logistic Regression Results ---")
print("Confusion Matrix:")
print(cm)

# Normalize the confusion matrix by row (using L1 norm) to see proportions
cm1 = normalize(cm, norm='l1', axis=1)

# Create a DataFrame from the normalized matrix for better readability
cm1Df = pd.DataFrame(cm1, columns=data1.target_names, index=data1.target_names)
print("\nNormalized Confusion Matrix:")
print(cm1Df)"""


scipy_text = """# Import necessary libraries
# pandas for data manipulation and analysis
import pandas as pd
# numpy for numerical operations
import numpy as np
# matplotlib.pyplot for plotting graphs
import matplotlib.pyplot as plt
# seaborn for statistical data visualization
import seaborn as sb
# scipy.stats for statistical functions
from scipy.stats import pearsonr, spearmanr, chi2_contingency

# --- DATASET 1: Weather Data ---

# Load the first dataset from a CSV file into a pandas DataFrame
# Note: You will need to replace the file path with the actual location of your 'Weather1.csv' file.
# data1 = pd.read_csv('path/to/your/Weather1.csv')
# The path from the document is used here as a placeholder.
data1 = pd.read_csv('F:/00-Douglas College/1- Semester 1/3- Machine Learning in Data Science (3290)/Slides/Weather1.csv')

# Display the entire DataFrame to inspect the data
print("--- Weather Dataset Head ---")
print(data1)
print("\n" + "="*50 + "\n")


# --- Feature Analysis: Humidity ---

# Access and print the 'Humidity' column (feature) of the DataFrame
print("--- Humidity Column ---")
print(data1.Humidity)
print("\n" + "="*50 + "\n")

# Calculate and print the mean (average) of the 'Humidity' column
humidity_mean = np.mean(data1.Humidity)
print(f"Mean of Humidity: {humidity_mean}")

# Calculate and print the standard deviation of the 'Humidity' column
humidity_std = np.std(data1.Humidity)
print(f"Standard Deviation of Humidity: {humidity_std}")
print("\n" + "="*50 + "\n")

# Count the occurrences of each unique value in the 'Humidity' column and print it
print("--- Value Counts for Humidity ---")
print(data1.Humidity.value_counts())
print("\n" + "="*50 + "\n")


# --- Data Visualization ---

# Generate a pairplot to visualize relationships between all numerical variables in the DataFrame
# Histograms are shown on the diagonal, and scatter plots for pairs of variables are shown on the off-diagonal
print("--- Generating Pairplot of Weather Data ---")
sb.pairplot(data1)
# Display the generated plot
plt.show()


# --- Correlation Analysis ---

# Calculate the Pearson correlation coefficient and the p-value between 'Temperature' and 'Humidity'
# This measures the linear relationship between the two variables.
cor1_pearson = pearsonr(data1.Temperature, data1.Humidity)
print(f"--- Pearson Correlation (Temperature vs Humidity) ---\n{cor1_pearson}\n")

# Calculate the Spearman rank-order correlation coefficient and the p-value between 'WindBearing' and 'WindSpeed'
# This measures the monotonic relationship between two variables.
sp1_spearman = spearmanr(data1.WindBearing, data1.WindSpeed)
print(f"--- Spearman Correlation (WindBearing vs WindSpeed) ---\n{sp1_spearman}\n")

# Compute the pairwise correlation of all columns in the DataFrame using the Pearson method by default
correlation_matrix = data1.corr()
print("--- Full Correlation Matrix (Pearson) ---")
print(correlation_matrix)
print("\n" + "="*50 + "\n")

# Visualize the correlation matrix using a heatmap
# This provides a color-coded overview of the relationships between variables
print("--- Generating Heatmap of Correlation Matrix ---")
sb.heatmap(correlation_matrix)
# Display the generated plot
plt.show()


# --- DATASET 2: Smartphone Data & Chi-Square Test ---

# Load the second dataset from a CSV file into a new DataFrame
# Note: You will need to replace the file path with the actual location of your 'smartphone.csv' file.
# data2 = pd.read_csv('path/to/your/smartphone.csv')
# The path from the document is used here as a placeholder.
data2 = pd.read_csv('F:/00-Douglas College/1- Semester 1/3- Machine Learning in Data Science (3290)/Slides/smartphone.csv')

# Display the first 5 rows of the new DataFrame to inspect it
print("--- Smartphone Dataset Head ---")
print(data2.head())
print("\n" + "="*50 + "\n")

# Create a contingency table (crosstab) of two categorical variables: 'Brand' and 'Ram'
# This table shows the frequency distribution of the variables.
contingency_table = pd.crosstab(data2.Brand, data2.Ram)
print("--- Contingency Table (Brand vs Ram) ---")
print(contingency_table)
print("\n" + "="*50 + "\n")

# Perform the Chi-Square test of independence on the contingency table
# This test determines if there is a significant association between the two categorical variables.
chi2, p_value, dof, expected = chi2_contingency(contingency_table.values)

# Print the results of the Chi-Square test
print("--- Chi-Square Test Results ---")
print(f"Chi-Square Statistic: {chi2}")
print(f"P-value: {p_value}")
print(f"Degrees of Freedom: {dof}")
print("\n--- Expected Frequencies ---")
print(expected)
print("\n" + "="*50 + "\n")"""


midterm_text = """# --- Library Imports ---

import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.feature_selection import SelectKBest
from sklearn.metrics import confusion_matrix, classification_report


# --- Task 1: Data Loading and Descriptive Analysis ---

# Load the breast cancer dataset from scikit-learn
cancer1 = load_breast_cancer()

# 1. Print the dimensions of the feature data and target data
print("Data shape:", cancer1.data.shape)
print("Target shape:", cancer1.target.shape)

# 2. Print the names of the features (columns)
print("Feature names:", cancer1.feature_names)

# 3. Print the target values (0 or 1 for cancer diagnosis)
print("Target values:", cancer1.target)

# 4. Convert the dataset into a pandas DataFrame for easier manipulation
df = pd.DataFrame(cancer1.data, columns=cancer1.feature_names)
df['target'] = cancer1.target

# 5. Split the data into training (75%) and testing (25%) sets
x = cancer1.data
y = cancer1.target
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42, stratify=y)

# 6. Calculate the correlation matrix for all attributes in the DataFrame
cor1 = df.corr()

# 7. Plot a heatmap to visualize the correlation matrix
sb.heatmap(cor1)
plt.show()

# 8. Plot 'mean radius' vs. 'mean perimeter' and 'mean radius' vs. 'worst symmetry'
# First plot: mean radius vs mean perimeter (shows a strong linear relationship)
plt.plot(df["mean radius"], df["mean perimeter"], ls='-')
plt.grid()
plt.legend(['mean radius vs mean perimeter'])
plt.show()

# Second plot: mean radius vs worst symmetry (shows a weaker, more scattered relationship)
plt.plot(df["mean radius"], df["worst symmetry"], ls='--')
plt.grid()
plt.legend(['mean radius vs worst symmetry'])
plt.show()


# --- Task 2: Classification ---

# 1 & 2. Implement and evaluate the Decision Tree Classifier
tree1 = DecisionTreeClassifier()
tree1.fit(x_train, y_train)
pred_tree1 = tree1.predict(x_test)
print(f"Decision Tree Accuracy: {tree1.score(x_test, y_test)}")

# 3. Show the confusion matrix and classification report for the Decision Tree
print("\nDecision Tree Confusion Matrix:")
print(confusion_matrix(y_test, pred_tree1))
print("\nDecision Tree Classification Report:")
print(classification_report(y_test, pred_tree1))

# 4. Draw the trained decision tree
plt.figure(figsize=(20, 10)) # Added for better readability
plot_tree(tree1, feature_names=cancer1.feature_names, class_names=cancer1.target_names, filled=True)
plt.show()

# 5, 6, & 7. Implement and evaluate KNN for k=2 and k=10
# KNN with k=2
knn1 = KNeighborsClassifier(n_neighbors=2, metric='minkowski', p=2)
knn1.fit(x_train, y_train)
pred_knn1 = knn1.predict(x_test)
print(f"\nKNN (k=2) Accuracy: {knn1.score(x_test, y_test)}")
print("\nKNN (k=2) Confusion Matrix:")
print(confusion_matrix(y_test, pred_knn1))
print("\nKNN (k=2) Classification Report:")
print(classification_report(y_test, pred_knn1))

# KNN with k=10
knn2 = KNeighborsClassifier(n_neighbors=10, metric='minkowski', p=2)
knn2.fit(x_train, y_train)
pred_knn2 = knn2.predict(x_test)
print(f"\nKNN (k=10) Accuracy: {knn2.score(x_test, y_test)}")
print("\nKNN (k=10) Confusion Matrix:")
print(confusion_matrix(y_test, pred_knn2))
print("\nKNN (k=10) Classification Report:")
print(classification_report(y_test, pred_knn2))


# --- Task 3: Modeling and Feature Importance ---

# 1, 2, & 3. Implement and evaluate Random Forest for max_depth=4 and max_depth=6
# Random Forest with max_depth=4
rf1 = RandomForestClassifier(max_depth=4)
rf1.fit(x_train, y_train)
pred_rf1 = rf1.predict(x_test)
print(f"\nRandom Forest (depth=4) Accuracy: {rf1.score(x_test, y_test)}")
print("\nRandom Forest (depth=4) Confusion Matrix:")
print(confusion_matrix(y_test, pred_rf1))
print("\nRandom Forest (depth=4) Classification Report:")
print(classification_report(y_test, pred_rf1))

# Random Forest with max_depth=6
rf2 = RandomForestClassifier(max_depth=6)
rf2.fit(x_train, y_train)
pred_rf2 = rf2.predict(x_test)
print(f"\nRandom Forest (depth=6) Accuracy: {rf2.score(x_test, y_test)}")
print("\nRandom Forest (depth=6) Confusion Matrix:")
print(confusion_matrix(y_test, pred_rf2))
print("\nRandom Forest (depth=6) Classification Report:")
print(classification_report(y_test, pred_rf2))


# 4, 5, & 6. Implement and evaluate AdaBoost Classifier
ada1 = AdaBoostClassifier(n_estimators=50, learning_rate=0.2)
ada1.fit(x_train, y_train)
pred_ada1 = ada1.predict(x_test)
print(f"\nAdaBoost Accuracy: {ada1.score(x_test, y_test)}")
print("\nAdaBoost Confusion Matrix:")
print(confusion_matrix(y_test, pred_ada1))
print("\nAdaBoost Classification Report:")
print(classification_report(y_test, pred_ada1))


# 7 & 8. Calculate and show feature importances
print("\nFeature importances from Random Forest (depth=4):", rf1.feature_importances_)
print("\nFeature importances from Random Forest (depth=6):", rf2.feature_importances_)
print("\nFeature importances from AdaBoost:", ada1.feature_importances_)


# 9. Plot the feature importances in horizontal bar charts
# For Random Forest (depth=4)
plt.barh(cancer1.feature_names, sorted(rf1.feature_importances_))
plt.title("Feature importances of Random Forest Classifier with max depth of 4")
plt.show()

# For Random Forest (depth=6)
plt.barh(cancer1.feature_names, sorted(rf2.feature_importances_))
plt.title("Feature importances of Random Forest Classifier with max depth of 6")
plt.show()

# For AdaBoost
plt.barh(cancer1.feature_names, sorted(ada1.feature_importances_))
plt.title("Feature importances of AdaBoost Classifier")
plt.show()


# 10. Select the three and six most important features using SelectKBest
# Select three most important features
selector1 = SelectKBest(k=3)
selector1.fit(x_train, y_train)
x_train_selected3 = selector1.transform(x_train)
x_test_selected3 = selector1.transform(x_test)
selected3_feature_names = cancer1.feature_names[selector1.get_support()]
print(f"\nShape with 3 best features: {x_train_selected3.shape}")
print(f"Top 3 feature names: {selected3_feature_names}")


# Select six most important features
selector2 = SelectKBest(k=6)
selector2.fit(x_train, y_train)
x_train_selected6 = selector2.transform(x_train)
x_test_selected6 = selector2.transform(x_test)
selected6_feature_names = cancer1.feature_names[selector2.get_support()]
print(f"\nShape with 6 best features: {x_train_selected6.shape}")
print(f"Top 6 feature names: {selected6_feature_names}")"""


assign2_text = """# --- Library Imports ---

# Import necessary libraries for data handling, modeling, and evaluation
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# --- Data Loading and Exploration ---

# Load the heart disease dataset from a local CSV file
df = pd.read_csv('C:/Users/Xiangru/Downloads/heart2 1.csv')

# Display a summary of the DataFrame, including data types and non-null counts
df.info()

# Generate descriptive statistics for the numerical columns
df.describe()

# Display the first few rows of the dataset to inspect the data
df.head()

# Check the distribution of the target variable to see class balance
df['target'].value_counts()


# --- Data Partitioning ---

# Separate the features (X) from the target labels (y)
x = df.drop(columns=['target'])
y = df['target']

# Split the data into training (80%) and testing (20%) sets
# random_state=42 is used for reproducibility
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)


# --- Model 1: Support Vector Machine (SVM) ---

# --- Linear SVM ---
# Initialize and train a linear SVM with C=1.0 for a balance between fitting and generalization
C = 1.0
svc1 = SVC(kernel='linear', C=C).fit(x_train, y_train)
# Make predictions on the test set
y_pred_svc1 = svc1.predict(x_test)
# Evaluate the model
print('Accuracy of Linear SVM: {:.2f}'.format(accuracy_score(y_test, y_pred_svc1)))
print(confusion_matrix(y_test, y_pred_svc1))
print(classification_report(y_test, y_pred_svc1))

# --- RBF Kernel SVM ---
# Initialize and train an RBF kernel SVM. gamma=0.02 is chosen for moderate influence
rbf_svc = SVC(kernel='rbf', gamma=0.02, C=C).fit(x_train, y_train)
# Make predictions on the test set
y_pred_rbf = rbf_svc.predict(x_test)
# Evaluate the model
print('Accuracy of RBF: {:.2f}'.format(accuracy_score(y_test, y_pred_rbf)))
print(confusion_matrix(y_test, y_pred_rbf))
print(classification_report(y_test, y_pred_rbf))

# --- Polynomial Kernel SVM ---
# Initialize and train a Polynomial kernel SVM with degree=7 for a flexible decision boundary
poly_svc = SVC(kernel='poly', degree=7, C=C).fit(x_train, y_train)
# Make predictions on the test set
y_pred_poly = poly_svc.predict(x_test)
# Evaluate the model
print('Accuracy of Polynomial: {:.2f}'.format(accuracy_score(y_test, y_pred_poly)))
print(confusion_matrix(y_test, y_pred_poly))
print(classification_report(y_test, y_pred_poly))


# --- Model 2: Naïve Bayes ---

# Initialize the Gaussian Naïve Bayes model
gnb1 = GaussianNB()
# Train the model and make predictions on the test set
predNB = gnb1.fit(x_train, y_train).predict(x_test)
# Evaluate the model's performance
print(gnb1.score(x_test, y_test))
print(confusion_matrix(y_test, predNB))
print(classification_report(y_test, predNB))


# --- Model 3: K-Nearest Neighbors (KNN) ---

# Initialize the KNN model with 4 neighbors and Euclidean distance (p=2)
knn1 = KNeighborsClassifier(n_neighbors=4, metric='minkowski', p=2)
# Train the model on the training data
knn1.fit(x_train, y_train)
# Make predictions on the test set
y_predict = knn1.predict(x_test)
# Evaluate the model's performance
print(knn1.score(x_test, y_test))
print(confusion_matrix(y_test, y_predict))
print(classification_report(y_test, y_predict))"""


ml_clf_text = """# --- Imports ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb

from sklearn.datasets import load_iris, load_wine, load_breast_cancer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, mean_squared_error


# --- Data Loading and Preparation ---
data = load_iris()
x = data.data
y = data.target

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)


# --- Imbalanced Data Handling (Optional) ---
# SMOTE (Over-sampling): sampling_strategy='auto'/'minority', k_neighbors=5
smote = SMOTE(random_state=42)
x_train_smote, y_train_smote = smote.fit_resample(x_train, y_train)

# NearMiss (Under-sampling): version=1/2/3, n_neighbors=3
nearmiss = NearMiss(version=1)
x_train_nm, y_train_nm = nearmiss.fit_resample(x_train, y_train)


# --- Model Instantiation ---
# KNN: n_neighbors=6/20, metric='minkowski', p=1(Manhattan)/2(Euclidean)
knn1 = KNeighborsClassifier(n_neighbors=6, metric='minkowski', p=2)

# Gaussian Naive Bayes: no hyperparameters
gnb1 = GaussianNB()

# SVM: kernel='linear'/'rbf'/'poly', gamma=0.2/0.7, C=0.2/1.0, decision_function_shape='ovo'/'ovr', degree=7(for poly)
svc1 = SVC(kernel='linear', random_state=0, decision_function_shape='ovr')

# Decision Tree: max_depth, criterion='gini'/'entropy'
tree1 = DecisionTreeClassifier()

# Logistic Regression: max_iter=2500, C, solver
logreg1 = LogisticRegression(max_iter=2500)


# --- Fit ---
knn1.fit(x_train, y_train)

# Option 2: With SMOTE
# knn1.fit(x_train_smote, y_train_smote)

# Option 3: With NearMiss
# knn1.fit(x_train_nm, y_train_nm)


# --- Predict ---
y_pred_knn1 = knn1.predict(x_test)


# --- Evaluation: Accuracy ---
print(f"KNN: {knn1.score(x_test, y_test)}")

# --- Evaluation: K-Fold Cross Validation ---
# cv=4/5/10, scoring='accuracy'/'precision'/'recall'/'f1'/'neg_mean_squared_error'
cv_scores = cross_val_score(knn1, x_train, y_train, cv=4)
print(f"Cross-Validation Scores: {cv_scores}")
print(f"Mean CV Score: {np.mean(cv_scores)}")


# --- Evaluation: Confusion Matrix ---
print(confusion_matrix(y_test, y_pred_knn1))


# --- Evaluation: Classification Report ---
print(classification_report(y_test, y_pred_knn1))"""


ml_reg_text = """# --- Imports ---
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score


# --- Data Creation and Preparation ---
x1 = np.arange(1, 10)
y1 = np.array([23, 34, 44, 56, 65, 67, 70, 76, 79])

# Reshape for sklearn
x1 = x1.reshape(-1, 1)
y1 = y1.reshape(-1, 1)


# --- Model Instantiation ---
# Linear Regression: fit_intercept=True/False, normalize=False
reg1 = LinearRegression()


# --- Fit ---
reg1.fit(x1, y1)


# --- Predict ---
y_pred = reg1.predict(x1)


# --- Evaluation: MSE and R2 ---
print(f"Mean Squared Error: {mean_squared_error(y1, y_pred)}")
print(f"R2 Score: {r2_score(y1, y_pred)}")


# --- Evaluation: K-Fold Cross Validation ---
# cv=4/5/10, scoring='r2'/'neg_mean_squared_error'/'neg_root_mean_squared_error'/'neg_mean_absolute_error'
cv_score_r2 = cross_val_score(reg1, x1, y1, cv=4, scoring='r2')
print(f"Cross-Validation R2 Scores: {cv_score_r2}")
print(f"Mean R2 Score: {np.mean(cv_score_r2)}")

cv_score_neg_mse = cross_val_score(reg1, x1, y1, cv=4, scoring='neg_mean_squared_error')
print(f"Cross-Validation Negative MSE Scores: {cv_score_neg_mse}")
print(f"Mean Negative MSE: {np.mean(cv_score_neg_mse)}")

cv_score_neg_rmse = cross_val_score(reg1, x1, y1, cv=4, scoring='neg_root_mean_squared_error')
print(f"Cross-Validation Negative RMSE Scores: {cv_score_neg_rmse}")
print(f"Mean Negative RMSE: {np.mean(cv_score_neg_rmse)}")"""


# - pd
# - np
# - pipe
# - plt_sb
# - decision
# - imb
# - knn_nb_svm
# - lab1
# - reg
# - scipy
# - midterm
# - assign2
# - ml_clf
# - ml_reg

def describe():
    return describe_text

def get_pd():
    return pd_text

def get_np():
    return np_text

def get_pipe():
    return pipe_text

def get_plt_sb():
    return plt_sb_text

def get_decision():
    return decision_text

def get_imb():
    return imb_text

def get_knn_nb_svm():
    return knn_nb_svm_text

def get_lab1():
    return lab1_text

def get_reg():
    return reg_text

def get_scipy():
    return scipy_text

def get_midterm():
    return midterm_text

def get_assign2():
    return assign2_text

def get_ml_clf():
    return ml_clf_text

def get_ml_reg():
    return ml_reg_text