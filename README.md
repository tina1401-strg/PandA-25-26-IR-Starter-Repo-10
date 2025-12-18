# Part 10 - Starter

This part builds on your Part 9 solution. You will no longer receive very detailed instructions.

Your task is to introduce two new classes without introducing new features—this is a refactoring exercise.

## Run the app

``` bash
python -m part10.app
```

## What to implement (ToDos)

Your ToDos start in `part10/app.py`, but you decide where to move the new classes. They may live in an existing module, 
the `app` module itself, or a new module.

0.  First, **copy/redo** your implementation from Part 9.

    1. Create `file_utilities.py` and move the `Configuration` class
        as well as all file-related functionality from `app.py` there
    2. Re-Introduce the configuration option for the `GREEN` 
        highlighting variant and pass it on to the ``ansi_highlight`` method.
    3. Move `save_config` into the `Configuration` class and rename it.

1. In preparation for the next part (in 2026), we will extract the search behavior into a separate class—most likely with a single method. Concretely, this includes everything that happens between lines 231 and 257 in ``app.py``: the part that we timed.

Think of a good name for this class and decide in which module it should live. You will need to pass the list of sonnets to this class so it can use them during the search.

Also choose a good name for the method. The method will most likely need two parameters: the user’s ``query`` (a string) and the current ``search_mode`` (also a string), so the class knows how to combine results for multiple words. It should return the list of ``SearchResult``s that are printed at the end of ``app.py``.

2. Now that we have three settings, you can see that much of the code that handles user input is duplicated. Try to find a way to move this code into a new class as well. Like the previous class, this one will most likely consist of a single method containing the duplicated logic. Use three instances of this class to represent the individual settings.
