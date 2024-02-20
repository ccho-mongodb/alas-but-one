import csv

FIELD_NAMES = ['word', 'repo', 'locations', 'num_occurrences', 'misspelled', 'ignore']

def format_locations(token_locations):

    formatted_locations = str()
    try:
        if len(token_locations) == 1:
            formatted_locations = ("%s:%d" % (token_locations[0].filename, token_locations[0].line)).rstrip()
        else:
            loc_and_line = [ "%s:%d" % (x.filename, x.line) for x in token_locations ]
            formatted_locations = "\n".join(loc_and_line)

    except Exception as e:
        print(e)

    return formatted_locations


def run(tokens, dest_file='out.csv'):

    with open(dest_file, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames = FIELD_NAMES )
        writer.writeheader()

        for token in tokens:
            locations = format_locations(token.locations)

            writer.writerow({
                'word': token.text,
                'repo': token.repo,
                'locations': locations,
                'num_occurrences': len(token.locations),
                'misspelled': token.misspelled,
                'ignore': token.ignore })
