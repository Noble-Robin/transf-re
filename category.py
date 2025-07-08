import requests
import urllib3
import pandas as pd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MOODLE_URL = 'https://moodle.caplogy.com'
TOKEN = 'a75ad55504b5cb4ce99d6881e47c9bdf'
FORMAT = 'json'

def create_category(name, parent=0):
    params = {
        'wstoken': TOKEN,
        'wsfunction': 'core_course_create_categories',
        'moodlewsrestformat': FORMAT,
        'categories[0][name]': name,
        'categories[0][parent]': parent
    }
    r = requests.post(f'{MOODLE_URL}/webservice/rest/server.php', params=params, verify=False)
    try:
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and len(data) > 0 and 'id' in data[0]:
            return data[0]['id']
        else:
            print("Erreur Moodle :", data)
            return None
    except requests.exceptions.HTTPError as e:
        print("Erreur HTTP :", r.text)
        raise e

def main():
    df = pd.read_excel('cours.xlsx')
    df.fillna('', inplace=True)

    cat_ids = {}

    for _, row in df.iterrows():
        main_cat = row['Catégorie principale'].strip()
        sub_cat = row['Sous-catégorie'].strip()
        parent_cat = row['Parent'].strip()

        if main_cat not in cat_ids:
            main_id = create_category(main_cat)
            if not main_id:
                continue
            cat_ids[main_cat] = main_id

        if not sub_cat:
            continue
        
        if parent_cat:
            parent_key = f"{main_cat}>{parent_cat}"
        else:
            parent_key = main_cat

        if parent_key not in cat_ids:
            print(f"Catégorie parente manquante : {parent_key}")
            continue

        full_key = f"{main_cat}>{sub_cat}"
        if full_key not in cat_ids:
            new_id = create_category(sub_cat, cat_ids[parent_key])
            if new_id:
                cat_ids[full_key] = new_id

if __name__ == '__main__':
    main()