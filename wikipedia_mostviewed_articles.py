import requests
import sqlite3
import datetime
import markdown
import os
import streamlit as st
import pandas as pd
import time

# Wikipedia Api URL to use accross all functions
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
DB_FILE="wikipedia_articles.db"

# Generic Function to Call Wikipedia Api
def call_wikipedia_api(api_options,topic=""):
    response_data = None

    try:
        #calling api with parameters
        response = requests.get(WIKIPEDIA_API_URL, params=api_options)

        # Validating response status
        if response.status_code == 200:  
            # Parsing response into json object
            response_data = response.json()     
        else:
            topic_msg = f"- Pulling {topic} " if topic!="" else ""
            st.error(f"Wikipedia API call error {topic_msg}  - Error Code: {response.status_code}")

    except Exception as error:
        st.exception(f"Error Invoking Wikipedia Api with parameters: {api_options}")
    
    return response_data  

# Function to Fetch 'N' MostViewed Wikipedia Articles
def get_wikipedia_mostviewed_articles(articles_limit=10):    
    articles = None

    # Defining api parameters values for fetching wikipedia articles
    api_options = {
        "action": "query", #api action
        "format": "json", #response format
        "list": "mostviewed", #list selected
        "pvimlimit": articles_limit+2  #limiting result adding 2 (Because Main Page and Search are included in results)
    }

    #calling api with parameters
    json_data = call_wikipedia_api(api_options,"Most Viewed Articles")

    #validating response data
    if json_data: 
        try:
            #parsing json data to obtain articles
            articles = json_data["query"]["mostviewed"]

        except Exception as error:
            st.exception(json_data)

    return articles    

# Funtion to Fetch Last Editor by Article    
def get_last_editor(title):    
    last_editor = None

    # Defining api parameters values for fetching article revisions
    api_options = {
        "action": "query", #api action
        "format": "json", #response format,
        "prop": "revisions", #property to filter
        "titles": title, #article to filter
        "rvprop": "user", #revision property
        "rvdir": "newer", #revision directory        
        "rvlimit": 1  #revision limit
    }

    # Calling api with parameters
    print(f"Extracting Revisions for Article: {title}")
    json_data = call_wikipedia_api(api_options,"Last Article Editor")

     #validating response data
    if json_data:              
        # Parsing json data to obtain article editor based on revisions
        pages = json_data["query"]["pages"]
        for page_id in pages:
            revisions = pages[page_id]["revisions"]
            if revisions:
                # Getting last revision username
                last_editor = revisions[0]["user"]
                print(f"Last Editor Identified for Article: {title}")

    return last_editor

# Function to create SQLite database and table
def initiate_article_database():    
    try:
        # Deletes database if exists
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        # Creates database connection
        conn = sqlite3.connect(DB_FILE)    
        # Creates article database table
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS articles
                        (article_title TEXT, views_count INTEGER, last_editor TEXT, article_url TEXT, time_fetched TEXT, markdown TEXT)''')
        # Commit SQL sentence
        conn.commit()

    except Exception as error:
        st.exception(f"Error creating article database: {error}")
    finally:
        # Close connection if exists
        if conn:
            conn.close()

# Function to insert article data into SQLite database
def insert_article_into_db(article_title, views_count, last_editor, article_url, markdown_content):
    try:
        # Creates database connection
        conn = sqlite3.connect(DB_FILE)
        # Insert article into database table
        cursor = conn.cursor()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO articles VALUES (?, ? ,?, ?, ?, ?)",
                    (article_title, views_count, last_editor, article_url, current_time, markdown_content))
        # Commit SQL sentence
        conn.commit()

    except Exception as error:
        st.exception(f"Error inserting article into database: {error}")
    finally:
        # Close connection if exists
        if conn:
            conn.close()

def parse_insert_wikipedia_articles(json_data):

    if json_data:
        for article in json_data:
            # Build article URL
            article_path= article["title"].replace(" ","_")
            article_url = f"https://en.wikipedia.org/wiki/{article_path}"
            # Get article last editor
            article_title = article["title"].replace("Special:Search","Search")
            last_editor = get_last_editor(article_title)
            # Parse HMTL content into Markdown format
            print(f"Extracting markdown for Article: {article_title}")
            html_content = requests.get(article_url).text
            markdown_content = markdown.markdown(html_content)
            #Getting views
            views_count = article["count"] 
            # Insert article data into database
            insert_article_into_db(article_title, views_count, last_editor, article_url, markdown_content)
            print(f"Article successfully saved in DB: {article_title}")

    else:
        st.warning("No articles to process...")

def display_data():
    df = None

    try:
        # Creating database connection
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()    
        # Fetching all table rows using Pandas to map column names in charts
        df = pd.read_sql_query("SELECT ROW_NUMBER() OVER(ORDER BY views_count DESC) Rank, article_title as 'Article Title' , views_count as 'Views Count', format('%,d',views_count) as views_count_formatted, last_editor, time_fetched , article_url from articles where article_title not in ('Main Page','Search')", conn)                
    except Exception as error:
        st.exception(f"Error querying article database: {error}")
    finally:
        if conn:
            conn.close()

    # Setting up page title
    st.title('Top 20 most viewed articles in Wikipedia')
    
    # Barchart by views
    st.bar_chart(df, x="Article Title",y="Views Count",color="Views Count",use_container_width=True,)

    # Table with Data Detail
    st.dataframe(df, column_config={
        "rank": "Rank",
        "views_count_formatted": "Views Count",
        "last_editor": "Last Editor",
        "time_fetched": st.column_config.DatetimeColumn("Time Fetched",format="D MMM YYYY, h:mm a"),
        "article_url": st.column_config.LinkColumn("Article URL",display_text="Open Article"),
        "Views Count": None,        
        },
        hide_index=True,
        height=730,
        use_container_width=True,
    )    

# Main function
def main():
    with st.spinner('Please wait: Initiating Database'):
        # Starting database
        initiate_article_database()
    alert1 = st.success('Done: Database Initiated')

    with st.spinner('Please wait: Loading Wikipedia Mostviewed Articles'):
        #Fetching top 20 mostviewed wikipedia articles
        articles = get_wikipedia_mostviewed_articles(20)         
    alert2 = st.success('Done: Wikipedia 20 Mostviewed Articles Loaded')

    with st.spinner('Please wait: Checking Articles Revisions and Downloading HTML'):
        # Parse and store articles
        parse_insert_wikipedia_articles(articles)
    alert3 = st.success('Done: Wikipedia Mostviewed Articles Parsed and Stored in DB')

    with st.spinner('Please wait: Loading charts data'):
        # Show database results using streamlit
        display_data()    
   
    #Cleaning informational messages
    alert1.empty()
    alert2.empty()
    alert3.empty()
         
if __name__ == "__main__":
    main()