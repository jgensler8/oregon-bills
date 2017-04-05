# Oregon Bills

## Purpose

Find links between bills in the Oregon House and Senate. Useful in finding out which to get involved with based on your interest.

## Data Pipeline

### Data Acquisition

* Selenium (ASP async data loading)
* Beautiful Soup (pulling out `<a>`'s `ref`s)
* PyPDF2

### Cleaning

* simple regex

### Analysis

* sklean (LDA)
* networkx
* matplotlib