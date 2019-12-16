# tMDB-See-Through

### Usage

1. Install the requirements - just pip install it if you cannot find a module.
2. Open terminal and cd to this folder.
3. For Mac: `export FLASK_APP=server.py`; for Windows: `$env:FLASK_APP = "server.py"`
4. `flask run`
5. Check what the terminal displays and open it in the browser.

### API for Frontend

1. Check `server.py` to run Flask server.
2. GET `/movies` to get **all** information of movies in json. The keys are movie ids.
3. Similarly, GET `/actors` and `/directors`.
4. POST `/set_range` to set the range of years - only the movies inside the range will be layout.
5. POST or GET `/update` for 1 iteration of the layout. The positions of **all** nodes will be returned - only render the ones in the year range.

### Data Format

```json
{
    "movie": {
      "budget": 237000000,
      "tagline": "Enter the World of Pandora.",
      "runtime": 162.0,
      "popularity": 150.437577,
      "release_date": "2009-12-10",
      "vote_average": 7.2,
      "genres": "['Action', 'Adventure', 'Fantasy', 'Science Fiction']",
      "revenue": 2787965087,
      "vote_count": 11800,
      "title": "Avatar"
    },
    "actor/director": {
      "gender": 2,
      "name": "Harrison Ford"
    }
}
```