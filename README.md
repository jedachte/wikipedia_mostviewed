# Wikipedia's MostViewed Articles Demo
Python Demo to Extract and Visualize Wikipedia's MostViewed Articles

This Python project mainly uses:
- Wikipedia API: to extract articles information
- SQLite: to store the data in a local file
- Streamlit: to display data in a web browser

**Project Installation**

Follow these steps to execute the project:
1. Clone project
2. Create and activate a virtual environment (optional but recommended to avoid conflicts with other Python projects running in your local)
3. Install requirements (pip install -r requirements.txt)
4. Execute Streamlit App (streamlit run wikipedia_mostviewed_articles.py)

**Project Structure**

The *wikipedia_mostviewed_articles* python file contains all the functions in the project:
- *call_wikipedia_api*: a generic function that returns API results in JSON format, requires an api_options parameter to indicate all args necessary along with an optional topic parameter for exception messages purposes.
- *get_wikipedia_mostviewed_articles*: returns a list of most viewed articles in JSON format, and uses an articles_limit parameter to indicate the number of top articles to retrieve. The Wikipedia API *mostviewed* method is used.
- *get_last_editor*: returns the last editor name based on the article title indicated as a parameter. The Wikipedia API *revisions* method is used along with newer directory property.
- *initiate_article_database*: creates database and table for storing the article data using SQLite library.
- *insert_article_into_db*: inserts records into the article table using SQLite library.
- *parse_insert_wikipedia_articles*: iterates over the most viewed article list pulling the last editor and the article content in markdown format, and finally inserting the data into the article table using the functions previously defined.
- *display_data*: uses Streamlit library to display a Pandas dataframe based on the article SQLite table, generating 2 visuals (a summary bar chart and a table with details). Dataframes allow easier graph formatting.
- *main*: orchestrates the calls to the main functions and informational messages.

The *requirements.txt* file includes the python modules on which this project relies. The dependencies can be installed with pip install -r requirements.txt

**How it looks like**

Running this streamlit project will result in the browser displaying general information. Some detailed information will be displayed in the terminal.

While Streamlit is loading data, information messages will appear as follows:
![image](https://github.com/jedachte/wikipedia_mostviewed/assets/62156163/c6a63f75-f5b2-46c4-98bd-63d05db2fcf2)

Once the data is downloaded and parsed two visualization will be displayed in 2 graphs:
![image](https://github.com/jedachte/wikipedia_mostviewed/assets/62156163/e7a793ad-e38d-4745-ba9e-886633fba83e)

**Wikipedia API**

The Wikipedia API (https://en.wikipedia.org/w/api.php) is an application programming interface (API) that allows developers to access and use Wikipedia data and functionality programmatically. Some of the common uses of the Wikipedia API include: 

Data query: Developers can query the API to obtain Wikipedia-specific information, such as articles, reviews, page metadata, link lists, categories, and more. 

Content Analysis: The API allows developers to access the content of Wikipedia articles to perform text analysis, information extraction, natural language processing (NLP), and other content-related tasks. 

Integration with applications: Developers can integrate Wikipedia data into their own applications or services, thus enriching the user experience with additional and contextual information. 

Tool development: The Wikipedia API is also used to develop tools and services that extend Wikipedia's functionality or provide new ways to interact with its content. 

Automation: The API makes it easy to automate tasks related to content management on Wikipedia, such as creating, editing and deleting pages, managing revisions and monitoring changes.

**Articles most viewed**

## **list=mostviewed (pvim)**

Lists the most viewed pages (based on last day's pageview count).

- <https://www.mediawiki.org/wiki/Special:MyLanguage/Extension:PageViewInfo>

**Specific parameters:**

Other general parameters are available.

**pvimmetric**

The metric to use for counting views. Depending on what backend is used, not all metrics might be supported. You can use the siteinfo API ([action=query&meta=siteinfo](https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bsiteinfo)) to check which ones are supported, under pageviewservice-supported-metrics / module name (siteviews, mostviewed, etc.)

For more information, please read [Extension:PageViewInfo - MediaWiki](https://www.mediawiki.org/wiki/Extension:PageViewInfo/en)

**API:Revisions**

Get revision information.

May be used in several ways:

1. Get data about a set of pages (last revision), by setting titles or pageids.
1. Get revisions for one given page, by using titles or pageids with start, end, or limit.
1. Get data about a set of revisions by setting their IDs with revids.
- <https://www.mediawiki.org/wiki/Special:MyLanguage/API:Revisions>
