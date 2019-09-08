# direct-youtube
For example, you'll send a request to serverip/?s=<youtube link or search term>, then it will redirect to the best found audio stream of the link or first result of the search term, and store the link in a database until it expires. When the same YouTube URL or search term is requested again it will use what's found in the database, or delete and get a new one if expired.
  
To install and set it up use this guide: https://linoxide.com/linux-how-to/install-flask-python-ubuntu/
