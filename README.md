# WebScraping

Main repository for scraping statistics from the [odbojka.si](https://ozs-web.dataproject.com/MainHome.aspx) webpage.

## Dependencies

The only prerequisite is to have installed the following tools:
- Python 3.8 <=
- pipenv

Then other dependencies can be installed using:

    pipenv install
   
## Run

After the dependencies are installed, then the scraping script can be run using:

    pipenv run python main.py
    
## Working principle

The script utilises Selenium that simulated user clicks on the webpage. It traverses the webpage for Volleyball stats and stores it to a local directory on the system where script is run. 
