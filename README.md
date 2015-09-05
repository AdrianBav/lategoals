# Soccer match data processing tool

The soccer match data processing tool is a data analysis web app that I worked on as part of a small team. The back-end is built in Python. The cache and reply files represent part of my involvement in the project. The two files are accompanied by their respective unit test files.

## Data Cache

The data source cache (**sbo_data_source_cache.py**), is a mechanism that keeps track of any events created, updated or deleted.

## Data Replay

The data source reply (**sbo_data_source_replay.py**), allows simulated data to be captured and subsequently played back from a local source of static replay files.

## Unit Tests

The data cache and replay functionality can be indipendently tested via unit testing. The **test_sbo_data_source_cache.py** and **test_sbo_data_source_replay.py** files apply a series of tests to their respective modules.
