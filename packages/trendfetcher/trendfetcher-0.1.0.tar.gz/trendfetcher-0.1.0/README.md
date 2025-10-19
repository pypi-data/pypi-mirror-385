This is a wrapper of pytrends. Fetch Google Trends data.

Parameters
----------

timeframe : str, default 'today 3-m'

    Time range for data retrieval. Supported formats:
    
    - 'now 1-H' : past 1 hour
    
    - 'now 4-H' : past 4 hours

    - 'now 7-d' : past 7 days
    
    - 'today 1-m' : past 1 month
    
    - 'today 3-m' : past 3 months
    
    - 'today 12-m' : past 12 months
    
    - 'today 5-y' : past 5 years
    
    - 'all' : full available history
