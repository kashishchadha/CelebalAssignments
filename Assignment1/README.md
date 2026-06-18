# Myntra Product Dataset Analysis and Preprocessing

This project performs exploratory data analysis (EDA) and preprocessing on a Myntra product dataset. The objective is to understand product trends, clean inconsistent data, create useful derived features, and extract business-oriented insights from the dataset.

## Project Overview

The dataset contains information about products listed on Myntra, including pricing, discounts, ratings, seller information, categories, and customer engagement metrics.

The notebook focuses on:

- Understanding dataset structure and quality
- Identifying missing and duplicate records
- Cleaning price-related fields
- Handling incomplete values
- Creating additional analytical features
- Exploring product popularity and pricing behavior
- Visualizing category-level and product-level trends
- Generating actionable business insights

## Dataset Information

**Dataset:** Myntra Shopping Dataset

**Source:**  
https://www.kaggle.com/datasets/anvitkumar/shopping-dataset

**File Used:** `Combined_dataset.csv`

### Dataset Characteristics

- Approximately 1000 product records
- Multiple product categories
- Pricing and discount information
- Product ratings and review counts
- Seller details and metadata

## Data Preparation Steps

The following preprocessing operations were performed:

1. Removed currency symbols and converted price columns into numerical format.
2. Examined missing values across all features.
3. Filled or removed incomplete records where appropriate.
4. Eliminated duplicate entries.
5. Filtered products with insufficient rating information.
6. Standardized column formats for analysis.

## Feature Engineering

Several new attributes were generated to support deeper analysis:

### Price Difference
Measures the difference between original price and discounted price.

### Popularity Score
Combines product ratings and rating counts to estimate customer engagement.

### Total Purchase Value
Represents the overall monetary impact of products using available sales-related attributes.

## Exploratory Analysis

The notebook investigates:

### Product Pricing
- Distribution of selling prices
- Comparison of discounted and original prices
- Discount behavior across categories

### Product Ratings
- Rating distributions
- Highly rated products
- Relationship between ratings and popularity

### Category Analysis
- Category-wise product counts
- Average category pricing
- Category performance comparisons

### Customer Engagement
- Rating count trends
- Popularity patterns
- Products receiving the highest attention

## Visualizations Included

The project uses various visualization techniques such as:

- Histograms
- Box plots
- Scatter plots
- Bar charts
- Category comparison charts

## Key Findings

- Product prices vary significantly across categories.
- Discounts play an important role in customer attraction.
- Higher-rated products generally receive greater engagement.
- Certain categories dominate the dataset in terms of product volume.
- Popularity metrics help identify products with stronger market presence.

## Project Structure

```text
shopping-analysis/
│
├── data/
│   ├── Combined_dataset.csv
│   └── Combined_dataset_cleaned.csv
│
├── notebook/
│   └── analysis.ipynb
│
└── README.md
```

## Requirements

```bash
pip install pandas numpy matplotlib seaborn notebook
```

## Running the Notebook

```bash
cd notebook
jupyter notebook analysis.ipynb
```

## Conclusion

This project demonstrates a complete workflow for cleaning, exploring, and analyzing e-commerce product data. The resulting insights can assist in understanding pricing strategies, customer preferences, and category performance within an online retail environment.
