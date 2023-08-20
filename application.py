from flask import Flask, render_template, request
import requests
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
import pymongo
import logging
import os
logging.basicConfig(filename="scapper.log", level=logging.INFO)

application=Flask(__name__)
app=application

@app.route('/', methods=['GET'])
def homepage():
    return render_template('index.html')

@app.route('/review', methods=['GET', 'POST'])
def index():
    if request.method=='GET':
        return render_template('index.html')
    else:
        try:
            # query to search in windows
            query = request.form['content'].replace(" ", "")

            save_directory = "images/"

            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            # fake user agent to avoid getting blocked by Google
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

            # fetch the search result page
            response = requests.get(f"https://www.google.com/search?q={query}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")

            soup = BeautifulSoup(response.content, "html.parser")

            image_tags = soup.find_all('img')

            del image_tags[0]

            img_data = []
            for index, image_tag in enumerate(image_tags):
                image_url = image_tag['src']

                image_data = requests.get(image_url).content
                my_dict = {"Index": index, "Image": image_data}
                img_data.append(my_dict)

                with open(os.path.join(save_directory, f"{query}_{index}.jpg"), "wb") as f:
                    f.write(image_data)

            client = pymongo.MongoClient("mongodb+srv://sowmya:Soumyajeevan33@cluster0.nrip8qz.mongodb.net/?retryWrites=true&w=majority")
            db = client['image_scrap']
            review_col = db['image_scrap_data']
            review_col.insert_many(img_data)

            return "image loaded"



            

        except Exception as e:
            logging.info(e)
            return "Something went wrong"




if __name__=="__main__":
    app.run(debug=True, host='0.0.0.0')