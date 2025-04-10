# Overview

This module focuses on extracting author information and contains the following scripts:

## Pipeline
- `pipeline.py` : Combines all functions from `extract.py`, `transform.py` and `load.py` below. This performs the pipeline in a single script, which is ran using a single command:
```
python pipeline.py
```


## Extract
- `extract.py` : Extracts user information for a given url specified in the code and returns a dictionary with values:
```
{
    'author_name':author_name,
    'author_page':author_url,
    'average_rating':average_rating,
    'rating_count':rating_count,
    'review_count':review_count
}
```

## Transform
- `transform.py` : Transforms the information provided by the extract script, and ensures it is consistent and cleaned, such that these requirements are met:

    
    - Authors have exactly the expected number of fields, with no missing values.

    - Book titles are confirmed to be individual works and not collections (e.g., “box set”).

    - All ratings, review, and follower counts are valid integers

    - Numbers with commas (e.g. “12,345,678”) are cleaned and parsed properly.

    - Average ratings must be between 0.0 and 5.0.

    - All years are 4-digit integers representing valid publication dates.

## Load
- `load.py` : Loads the transformed data into the database, specifically in this order of tables:
    - book
    - author
    - book_measurement
    - author_measurement


# Pre-requisites

1. `pip install -r requirements.txt`

2. Specify an author as a parameter for get_user_info() (SUBJECT TO CHANGE)

## Tests

The all functions in `extract.py`, `transform.py` and `load.py` are tested in their respective test scripts and can be tested locally with:

```
pytest test_<insert_script_here>
```