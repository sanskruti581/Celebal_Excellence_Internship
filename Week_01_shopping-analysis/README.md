# Assignment 01: Basic Data Exploration and Cleaning using Pandas

## Objective

The objective of this assignment is to perform basic data exploration and data cleaning using Python and Pandas. The analysis helps in understanding the dataset structure, identifying missing values, cleaning the data, and preparing it for further analysis.

## Dataset

The project uses the `Combined_dataset.csv` file containing shopping product information.

## Tasks Performed

### Data Loading

* Imported required libraries such as Pandas and NumPy.
* Loaded the dataset into a Pandas DataFrame.

### Data Exploration

* Checked the shape of the dataset.
* Displayed column names.
* Examined data types of all columns.
* Viewed sample records using head() and tail().
* Generated summary statistics using describe().
* Used info() to understand the dataset structure.

### Missing Value Analysis

* Identified missing values in each column.
* Calculated the percentage of missing values.

### Data Cleaning

* Filled missing numerical values using the median.
* Filled missing categorical values with "Unknown".
* Checked the dataset after cleaning to ensure missing values were handled properly.
* Removed duplicate records.

### Basic Analysis

* Calculated unique values for selected columns.
* Explored dataset characteristics using Pandas operations.

## Technologies Used

* Python
* Pandas
* NumPy
* Jupyter Notebook

## Project Structure

shopping-analysis/

├── data/

│   └── Combined_dataset.csv

├── notebook/

│   └── Analysis.ipynb

└── README.md

## Conclusion

This assignment demonstrates the use of Pandas for data exploration and preprocessing. The cleaned dataset can be used for further analysis, visualization, and machine learning tasks.

