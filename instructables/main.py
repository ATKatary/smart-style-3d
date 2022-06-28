import os
import csv
import shutil
import pathlib
import argparse
from utils import *
from requests_html import HTMLSession, AsyncHTMLSession

### Global Constants ###
current_dir = pathlib.Path(__file__).parent.resolve()
instructables_url = "https://www.instructables.com"
get_session  = lambda x : HTMLSession() if x == 'sync' else AsyncHTMLSession()
database_url = "https://www.kaggle.com/datasets/kingburrito666/instructables-diy-all-projects?datasetId=533694&select=projects_circuits.csv"

def read_dataset(database_dir):
    """
    Reads the files in the database directory and returns a mapping of categories and projects per category

    Inputs
        :database_dir: <str> path to the directory containing the database files

    Outputs
        :returns: <dict> category -> projects per category 
    """
    n = 0
    database = {}
    for filename in os.listdir(database_dir):
        projects = {}
        project_path = f"{database_dir}/{filename}"
        category = os.path.splitext(filename)[0].strip()

        with open(project_path, "r") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                if len(row) < 2: continue
                if row[1].startswith('/id/'): projects[row[0]] = row[1]

        n += len(projects)
        print(f"Found {len(projects)} projects in {category}")
        database[category] = projects
        
    print(f"Found a total of {n} projects in database directory")
    return database

def parse_data(database, parent_url, dir, category = None, overwrite = False, store_content = False, store_images = False, max_iters = -1):
    """
    Parses the database and saves the parsed information 

    Inputs
        :database: <dict> category -> projects
        :parent_url: <str> of the paetn website
        :dir: <str> path to directory to save to
        :category: <str> | None if provided we only parse that category, default is None
        :overwrite: <bool> indicating whether to overwrite existing parsed files, default is False 
        :store_content: <bool> indicating whether to store the content of the projects parsed
        :store_images: <bool> indicating whether to store the images parsed
        :max_iters: <int> maximum number of projects to parse
    """
    # number of files parsed so far
    i = 0
    projects = {}
    session = get_session('sync')
    if category is not None: database = {category: database[category]}

    for category, projects in database.items():
        category_dir = f"{dir}/{category}"
        # _check_overwrite(category_dir, overwrite)

        for name, link in projects.items():
            project_dir = f"{category_dir}/{category}_{i}"; i += 1
            # _check_overwrite(project_dir, overwrite)

            if os.path.exists(f"{project_dir}/website.html"): 
                content = scrape(session, f"{parent_url}{link}")
                with open(f"{project_dir}/website.html", 'wb') as dump: dump.write(content.encode('utf-8')); dump.close()
            else:
                content = soup(open(f"{project_dir}/website.html", 'r').read())

            info = extract_info(content)
            images = info['images']
            materials = info['materials']
            instructions = info['instructions']
            
            if store_content: save_json(info, f"{project_dir}/info.json")
            if store_images: 
                image_dir = f"{project_dir}/images"
                _check_overwrite(image_dir, overwrite)
                download_images(images, image_dir)
        
            if max_iters != -1 and max_iters < i: print(f"Parsed {i} projects!"); return 

    session.close()

##### Helper Functions #####
def _check_overwrite(dir, overwrite = False): 
    """
    Checks whether to overwrite a directory if it exists, else creates

    Inputs
        :dir: <str> path of directory to check
        :overwrite> <bool> indicating whether to overwrite directory if it exists, default is False
    """
    if os.path.exists(dir):
        if not overwrite: 
            overwrite = input(f"Directory {dir} exists! Do you want to overwrite? (y/n): ")
            overwrite = True if overwrite == "y" else False

        if overwrite: 
            shutil.rmtree(dir)
            os.mkdir(dir)
    
    else: os.mkdir(dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--max_iters', type=int, default=-1)
    parser.add_argument('--overwrite', type=bool, default=False)
    parser.add_argument('--store_images', type=bool, default=True)
    parser.add_argument('--store_content', type=bool, default=True)
    parser.add_argument('--dir', type=str, default=f'{current_dir}/scraped_data')
    parser.add_argument('--category', type=str, default='projects_circuits')
    parser.add_argument('--database_dir', type=str, default=f'{current_dir}/dataset')
    
    args = parser.parse_args()
    # _check_overwrite(args.dir)
    database = read_dataset(args.database_dir)
    parse_data(database, instructables_url, args.dir, category=args.category, overwrite=args.overwrite, store_content=args.store_content, store_images=args.store_images, max_iters=args.max_iters)