# Part 10 - Starter

This part builds on your Part 9 solution. Now you will not get too detailed instructions anymore!

Your task is to introduce two new classes without introducing new features - a refactoring.
## Run the app

``` bash
python -m part10.app
```

## What to implement (ToDos)

Your ToDos start in `part10/app.py`, but you decide where to move the new classes to. Could be an
existing module, the `app` module itself, or a new module.

0.  First, **copy/redo** your implementation from Part 9.

    1. Create `file_utilities.py` and move the `Configuration` class
        as well as all file related functionality from `app.py` there
    2. Re-Introduce the configuration option for the `GREEN` 
        highlighting variant and pass it on to the ``ansi_highlight`` method.
    3. Move `save_config` into the `Configuration` class and rename it.

1.  In preparation for our next part (in 2026), we extract the search behavior into a 
    separate class. Basically, this is everything that's happening from lines
    231 to 257 in `app.py`. The part that we timed. Think of a class name, 
    and in which module to move it. You will have to pass the list of sonnets to that
    class to be able to search them.

    Then, you will add a method (again, choose a good name) that does the search and
    returns the list of `SearchResult`s that are printed at the end.

2.  Now that we have three settings, you see that a lot of code is duplicated.
    You want to find a way of moving that code into a new class. Find a good name
    and use it three times for each of the settings!
