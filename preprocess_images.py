from icrawler.builtin import GoogleImageCrawler

def download_school_images(school_name, num_images, save_dir='images'):
    # Crée une instance du crawler Google
    google_crawler = GoogleImageCrawler(storage={'root_dir': save_dir})
    
    # Démarre le processus de téléchargement
    google_crawler.crawl(keyword=school_name, max_num=num_images)

# Exemple d'utilisation
#school_name = "Lycée Pierre Corneille Rouen Image"
#download_school_images(school_name, num_images=1)
import os 

import json 

f = open("assets/etablissements.geojson",encoding='utf-8')
data = json.load(f)
for i in range(len(data['features'])):
    nom = f"{data['features'][i]['properties']['appellation_officielle']} {data['features'][i]['properties']['libelle_commune']}"
    try:

        download_school_images(nom,1)
        print("------ DONE DOWNLOADING " + f"{data['features'][i]['properties']['appellation_officielle']} {data['features'][i]['properties']['libelle_commune']}")
        print(f"{i}/434")
        filename = [i for i in os.listdir("images") if "000001" in i][0]
        os.rename("images/" + filename,f"images/{data['features'][i]['properties']['numero_uai'] + os.path.splitext(filename)[1]}")
    except:
        print("------ FAILED TO DOWNLOAD")
    