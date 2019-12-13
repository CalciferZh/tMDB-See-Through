# tMDB-See-Through

### Usage

1. Check `server.py` to run Flask server.
2. GET `/movies` to get **all** information of movies in json. The keys are movie ids.
3. Similarly, GET `/actors` and `/directors`.
4. POST `/set_range` to set the range of years - only the movies inside the range will be layout.
5. POST or GET `/update` for 1 iteration of the layout. The positions of **all** nodes will be returned - only render the ones in the year range.

`$env:FLASK_APP = "server.py"`
`flask run`