import traceback
import requests
from datetime import datetime, timedelta
from models.token import Token
from models.token_location import TokenLocation

def get_changed_files_github(days, base_dir, repo_owner, repo_name, token):
    start_dt = datetime.now() - timedelta(days=days)
    fileset = set()

    try:
        api_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits'
        params = {
                'since': start_dt.isoformat(),
                }

        headers = {
                'Authorization': f'bearer {token}',
                }

        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()

        sha_arr = []
        for commit in data:
            commit_sha = commit['sha']
            sha_arr.append(commit_sha)

            contents_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{commit_sha}'
            response_contents = requests.get(contents_url, headers=headers)
            response_contents.raise_for_status()

            contents_data = response_contents.json()

            fileset.update([base_dir + "/" + file['filename'] for file in contents_data['files']])

        return fileset
    except Exception as e:
        traceback.print_exc()
        return fileset 

def run(token_dict, num_days, base_dir, repo_org, repo_name, token):

    # assemble base directory
    changed_files = get_changed_files_github(num_days, base_dir, repo_org, repo_name, token)

    for word, token in token_dict.items():
        locations = [ t.filename for t in token.locations]
        if (any(loc in changed_files for loc in locations)):
            token.in_date_range = True

