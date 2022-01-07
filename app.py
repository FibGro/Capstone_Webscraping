from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests
import numpy as np

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
movie = soup.find_all('div', class_ = 'lister-item mode-advanced')
row_length = len(movie)

temp = [] #initiating a list 

#insert the scrapping process here

for i in range (0, row_length):

    #title of the released movie
    title = movie[i].h3.a.text
    
    #imdb_rating 
    rating = movie[i].strong.text
    
    #Create if function to collect movie with metascore. However, if it's not available return to '0'
    m_score = movie[i].find('span', class_ = 'metascore').text if movie[i].find('span', class_ = 'metascore') else '0'
    m_score = m_score.strip()    
    
    #votes
    vote = movie[i].find('span', attrs = {'name':'nv'})['data-value']

    temp.append((title,rating, m_score, vote))
    

#change into dataframe
df = pd.DataFrame(temp, columns = ('movie_name','imdb_rating','metascore','votes'))

#insert data wrangling here
df[['votes','metascore']] = df[['votes','metascore']].astype('int')
df['imdb_rating']=df['imdb_rating'].astype('float')
df['metascore']=df['metascore'].replace(0,np.nan)
top_seven_movie=df.head(7)

#end of data wranggling 

@app.route("/")
def index(): 
	
	# generate plot
    
	fig, axes = plt.subplots(nrows = 1, ncols = 3, figsize = (12,3))
	
	axes[0].bar(top_seven_movie['movie_name'],top_seven_movie['imdb_rating'])
	axes[0].set_ylabel('Rating')
	axes[0].set_title("IMDb Rating")
	axes[0].tick_params('x',labelrotation=70)
	axes[0].set_xticklabels(top_seven_movie['movie_name'], fontsize=7)

	axes[1].bar(top_seven_movie['movie_name'],top_seven_movie['metascore'], color ='r')
	axes[1].set_ylabel('Metascore')
	axes[1].set_title("Metascore")
	axes[1].tick_params('x',labelrotation=70)
	axes[1].set_xticklabels(top_seven_movie['movie_name'], fontsize=7)

	axes[2].bar(top_seven_movie['movie_name'],top_seven_movie['votes'],color='y')
	axes[2].set_ylabel('Votes')
	axes[2].set_title("Votes")
	axes[2].tick_params('x',labelrotation=70)
	axes[2].set_xticklabels(top_seven_movie['movie_name'], fontsize=7)

	plt.tight_layout()
	plt.show()

	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	#Scatter plot (my own project)
	#Save all movie with available metascore data on variable moveie_meta
	df['metascore']=df['metascore'].replace(np.nan, 0)
	movie_meta=df[df['metascore'] != 0]

	fig, axes = plt.subplots(nrows = 1, ncols = 3, figsize = (12,3))

	axes[0].scatter(movie_meta['imdb_rating'], movie_meta['metascore'], color='y') 
	axes[0].set_title('IMDb Rating vs Metascore')
	axes[0].set_ylabel('Metascore')
	axes[0].set_xlabel('Rating')

	axes[1].scatter(movie_meta['imdb_rating'], movie_meta['votes'], color='r') 
	axes[1].set_title('IMDb Rating vs Votes')
	axes[1].set_ylabel('Votes')
	axes[1].set_xlabel('Rating')

	axes[2].scatter(movie_meta['metascore'], movie_meta['votes']) 
	axes[2].set_title('Votes vs Metascore')
	axes[2].set_ylabel('Votes')
	axes[2].set_xlabel('Metascore')

	plt.tight_layout()
	plt.show()
	
	card_data = f'{movie_meta["imdb_rating"].mean().round(2), movie_meta["metascore"].mean().round(2), movie_meta["votes"].mean().round(2)}' #be careful with the " and ' 

	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data=card_data, 
		plot_result=plot_result,
		result=result
		)


if __name__ == "__main__": 
    app.run(debug=True)