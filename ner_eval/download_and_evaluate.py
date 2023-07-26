import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

#============================================ set parameters here =========================================

# links for gold-standard files and model prediction file to be downloaded from
# gold_url = 'https://github.com/clamsproject/aapb-annotations/tree/main/newshour-namedentity/golds/aapb-collaboration-21'
# test_url = 'https://github.com/clamsproject/aapb-collaboration/tree/master/21'
gold_url = 'https://github.com/clamsproject/clams-aapb-annotations/tree/main/golds/ner/2022-jun-namedentity'
test_url = 'https://github.com/JinnyViboonlarp/ner-evaluation/tree/main/testfiles'

# local folders to save the files from gold_url and test_url respectively
gold_folder = 'goldfiles'
test_folder =  'testfiles'

# path to save NER evaluation result
resultpath = 'results.txt'

#============================================ set parameters end here ====================================

def download(url=None, folder_name=None):
    # code adapt from Angela Lam's

    # Extract the repository name from the URL, name would be the phrase after the last "/"
    repo_name = urlparse(url).path.split('/')[-1]

    # Create a new directory to store the downloaded files on local computer
    if folder_name == None:
        folder_name = repo_name
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    # Check if the directory is empty
    if not (len(os.listdir(folder_name)) == 0):
        raise Exception("The folder '" + folder_name + "' already exists and is not empty")

    # Send a GET request to the repository URL and extract the HTML content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links to .mmif, .txt, .md and .ann files in the HTML content
    links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith(('.mmif', '.txt', '.md', '.ann'))]

    # Download each file in the links list into the created folder
    for link in links:
        raw_url = urljoin('https://raw.githubusercontent.com/', link.replace('/blob/', '/'))
        file_name = os.path.basename(link)
        file_path = os.path.join(folder_name, file_name)
        with open(file_path, 'wb') as file:
            response = requests.get(raw_url)
            file.write(response.content)

if __name__ == "__main__":
    print('a')
    #download(gold_url, gold_folder)
    download(test_url, test_folder)
    print('a')
    #os.system("python evaluate.py " + gold_folder + "/ " + test_folder + "/ " + resultpath)
    #
    # edit the text file to add in the url paths to the github repos
    with open(resultpath, 'r') as fh_in:
        s = fh_in.read()
    s = ("link containing gold-standard files: " + gold_url + "\n" +\
         "link containing model prediction files: " + test_url + "\n\n" + s)
    with open(resultpath, 'w') as fh_out:
        fh_out.write(s)



