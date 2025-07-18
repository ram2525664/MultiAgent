import requests
import json

def movieDetailes(movieName):

    response = requests.get(f"http://www.omdbapi.com/?t={movieName}&apikey=47a5a28d")
    #print(response)

    try:
        if response.status_code == 200:
            data = response.json()
            #print(data)

            jsonData = json.dumps(data, indent=2, sort_keys=True)
            #print(jsonData)

            if data['Response'] == 'True':
                return f'''
                Actrors:  {data['Actors']}\n
                Awards:  {data['Awards']}\n
                BoxOffice Collection:  {data['BoxOffice']}\n
                Director:  {data['Director']}\n
                Country:  {data['Country']}\n
                Genre:  {data['Genre']}\n
                Language:  {data['Language']}\n
                Rated:  {data['Rated']}\n
                Rotten Tomatoes Rating:  {data['Ratings'][1]['Value']}\n
                IMDB:  {data['Ratings'][0]['Value']}\n
                Released Date:  {data['Released']}\n
                Runtime:  {data['Runtime']}\n
                Writer:  {data['Writer']}\n
                Plot:  {data['Plot']}''', data['Actors'], data['Awards'], data['BoxOffice'], data['Director'], data['Country'], data['Genre'], data['Language'], data['Rated'], data['Ratings'][1]['Value'], data['Ratings'][0]['Value'], data['Released'], data['Runtime'], data['Writer'], data['Plot'], data['Title'], data['Poster']
            
            elif data['Response'] == 'False':
                return data['Error']
        
    except:
        return "Something went wrong"
    

#details, title, poster  = movieDetailes("Thor")
#print(title)
#print(poster)
#print(details)
#print(movieDetailes("Thor"))