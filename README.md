# Alas, But One

This app identifies atomic typo candidates in text files by surfacing words
that occur a user-definable maximum number of times. Words that seem out of
place can be quickly checked in the location in which they appear.

This app is designed for use in MongoDB documentation repositories.

# Installation

1. Clone this repo (or optionally, fork the repository and clone the fork).

2. Navigate to the repo directory root:

   ```
   cd alas-but-one
   ```

3. Install the required packages by running the following command:

   ```
   pip3 install -r requirements.txt
   ```

# Setup

1. Configure your directory settings and which repos the app runs on in the ``config.json`` file.

   Update the ``config.json`` file to set the ``repo_base_full_path`` to the
   absolute path to the base directory that contains your docs repositories.

   The script concatenates the ``repo_base_full_path`` with the ``relative_path``
   values for each repository entry in the configuration file.

   The script is currently configured to run the app on all the listed.
   Comment out or remove the repository documents from the ``docs`` JSON object
   if you do not want to run it for those repos or have not cloned them.

2. If you need to enable or disable the ignore list, make the following edits to the ``alas.py`` file:

   Comment out both the ``MONGODB_URI`` line and
   ``ignore_list`` stage. For example:

   ```python
   # MONGODB_URI = os.environ['ABO_MONGO_URI']
   ...
   # ignore_list(token_dict, cfg, MONGODB_URI, IGNORE_DB_NAME, IGNORE_COLL_NAME)
   ```

   To use the shared ignored list, make sure both those lines are uncommented.
   Set the value of your environment variable ``ABO_MONGO_URI`` to the
   MongoDB cluster designated for sharing ignore lists. Ask your team if you
   need the credentials.

# Run

Run the following command to start the app:

```bash
python3 alas.py
```

This outputs files for each repo checked, named after the "docs" dictionary
key. You can import these into Google Sheets for convenient viewing and editing.

The output list includes the following information:

- word: the atomic typo candidate
- repo: the name of the docs repository the word was located
- locations: the file paths in which the word was found (needs update to exclude full path) including the line number
- num_occurrences: the number of times the word occurred in that repo
- misspelled: whether the word passed the spell check
- ignore: whether the word is on the ignore list

# How to Use the Ignore List

The ignore list is represented as the ``ignore`` column value in the csv
output file generated by ``alas.py``.

When you generate the output list with the ignore list enabled, any words
matching an entry in the ignore list for that repo contain a value of
"Y" in the ``ignore`` column in the output file. All other words contain
a value of "N".

Run the ``save_ignore_list.py`` script on the csv to persist any
changes to the ignore list. To add a word to the ignore list, set the
``ignore`` column value to "Y" in the csv. To remove a word from the ignore
list, set the ``ignore`` column value to "N" in the csv.

If you are using a Google Sheet, export the sheet to a csv when you are ready
to save changes to the ignore list. Ensure the headers are exactly the same as
the original csv file. Then, run the following script to perform the updates:

```bash
save_ignore_list.py <csv filename>
```


# Customization

TODO
