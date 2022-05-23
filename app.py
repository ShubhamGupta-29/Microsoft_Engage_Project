import streamlit as st
from PIL import Image
import json
from Classifier import KNearestNeighbours
from operator import itemgetter
from bs4 import BeautifulSoup
import requests,io
import PIL.Image
from urllib.request import urlopen

# Load data and movies list from corresponding JSON files
with open(r'data.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
with open(r'titles.json', 'r+', encoding='utf-8') as f:
    movie_titles = json.load(f)



  



img1 = Image.open('./engage_logo.jpg')
img1 = img1.resize((900,80),)
st.image(img1,use_column_width=False)
img2 = Image.open('./heading_poster.jpg')
img2 = img2.resize((900,150),)
st.image(img2,use_column_width=False)
st.text("")
st.text("")



def movie_poster_fetcher(imdb_link):
    ## Display Movie Poster
    url_data = requests.get(imdb_link).text
    s_data = BeautifulSoup(url_data, 'html.parser')
    imdb_dp = s_data.find("meta", property="og:image")
    movie_poster_link = imdb_dp.attrs['content']
    u = urlopen(movie_poster_link)
    raw_data = u.read()
    image = PIL.Image.open(io.BytesIO(raw_data))
    image = image.resize((220, 350), )
    st.image(image, use_column_width=False)


def get_movie_info(imdb_link):
    url_data = requests.get(imdb_link).text
    s_data = BeautifulSoup(url_data, 'html.parser')
    imdb_content = s_data.find("meta", property="og:description")
    movie_descr = imdb_content.attrs['content']
    movie_descr = str(movie_descr).split('.')
    movie_director = movie_descr[0]
    movie_cast = str(movie_descr[1]).replace('With', 'Cast: ').strip()
    movie_story = 'Story: ' + str(movie_descr[2]).strip()+'.'
    rating = s_data.find("div", class_="sc-7ab21ed2-3 dPVcnq")
    rating = str(rating).split('<div class="sc-7ab21ed2-3 dPVcnq')
    rating = str(rating[1]).split("</div>")
    rating = str(rating[0]).replace(''' "> ''', '').replace('">', '')


    # imdb_rating=s_data.find("div", class_="sc-7ab21ed2-1 jGRxWM")
    # imdb_rating = str(imdb_rating).split('<span class="sc-7ab21ed2-1 jGRxWM')
    # imdb_rating = str(imdb_rating[1]).split("</span>")
    # imdb_rating = str(imdb_rating[0]).replace(''' "> ''', '').replace('">', '')

    movie_rating = 'Total Rating count: '+ rating
    return movie_director,movie_cast,movie_story,movie_rating




def knn(test_point, k):
    # Create dummy target variable for the KNN Classifier
    target = [0 for item in movie_titles]
    # Instantiate object for the Classifier
    model = KNearestNeighbours(data, target, test_point, k=k)
    # Run the algorithm
    model.fit()
    # Distances to most distant movie
    max_dist = sorted(model.distances, key=itemgetter(0))[-1]
    # Print list of 10 recommendations < Change value of k for a different number >
    table = list()
    for i in model.indices:
        # Returns back movie title and imdb link
        table.append([movie_titles[i][0], movie_titles[i][2]])
    return table

if __name__ == '__main__':
    
    genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
              'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']

    movies = [title[0] for title in movie_titles]
    st.header('Movie Recommendation System')   
    
    apps = ['--Select--', 'Movie based', 'Genres based']   
    app_options = st.selectbox('Select application:', apps)
    
    if app_options == 'Movie based':
        
        movie_select = st.selectbox('Select movie:', ['--Select--'] + movies)
        if movie_select == '--Select--':
            st.write('Select a movie')
        else:
            n = st.number_input('Number of movies:', min_value=5, max_value=20, step=1)
            st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>* Fetching a Movie Posters or information will take a time."</h4>''',
                    unsafe_allow_html=True) 
            dec = st.radio("Want to Fetch Movie Poster?", ('No', 'Yes'))
            fec = st.radio("Want to Fetch Movie Information?", ('No', 'Yes'))
            st.text("")
            st.text("")

            genres = data[movies.index(movie_select)]
            test_point = genres
            table = knn(test_point, n)
            for movie, link in table:
                # Displays movie title with link to imdb
                st.markdown(f"[{movie}]({link})")
                
                if dec == 'Yes':
                 movie_poster_fetcher(link)
                if fec=='Yes': 
                 director,cast,story,total_rat = get_movie_info(link)
                 st.markdown(director)
                 st.markdown(cast)
                 st.markdown(story)
                 st.markdown(total_rat)

    elif app_options == apps[2]:
        options = st.multiselect('Select genres:', genres)
        if options:
            imdb_score = st.slider('IMDb score:', 1, 10, 8)
            n = st.number_input('Number of movies:', min_value=5, max_value=20, step=1)
            st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>* Fetching a Movie Poster and Information will take a time."</h4>''',
                    unsafe_allow_html=True) 
            dec = st.radio("Want to Fetch Movie Poster?", ('No', 'Yes'))
            fec = st.radio("Want to Fetch Movie Information?", ('No', 'Yes'))
            st.text("")
            st.text("")
            
            test_point = [1 if genre in options else 0 for genre in genres]
            test_point.append(imdb_score)
            table = knn(test_point, n)
            for movie, link in table:
                # Displays movie title with link to imdb
                st.markdown(f"[{movie}]({link})")
                
                if dec == 'Yes':
                 movie_poster_fetcher(link)
                if fec=='Yes': 
                 director,cast,story,total_rat = get_movie_info(link)
                 st.markdown(director)
                 st.markdown(cast)
                 st.markdown(story)
                 st.markdown(total_rat)
                # st.markdown('IMDB Rating: ' + irating + '⭐')

        else:
                st.write("This is a simple Movie Recommender application. "
                        "You can select the genres and change the IMDb score.")

    else:
        st.write('Select option')


    
    st.text("")
    st.text("")
    st.text("")  
    st.text("") 
    st.markdown('''<h5 style='text-align: left; color: #E8FF2B;'>Made by Shubham Gupta</h5>''',
                    unsafe_allow_html=True) 
    st.markdown('''<h6 style='text-align: left; color: #E8FF2B;'>shubham.gupta29062002@gmail.com</h6>''',
                    unsafe_allow_html=True) 
    st.markdown('''<h6 style='text-align: left; color: #E8FF2B;'>github.com/ShubhamGupta-29/Microsoft_Engage_Project</h6>''',
                    unsafe_allow_html=True) 


 
