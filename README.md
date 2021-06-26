# Zerodha Hiring Challenge 2021

#### You can watch the Video of output here: https://youtu.be/XA8W0qyueRs (Demo Link)
It is the standalone python django web app with the features:

-> Downloads the equity bhavcopy zip from https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx every day at 18:00 IST.

-> Extracts the downloaded copy and parse the file in it(CSV file)

-> Data is stored in the Redis

![Capture](https://user-images.githubusercontent.com/46214838/117665474-7e8dee00-b1c0-11eb-9789-28f150dfcfb3.PNG)

-> Renders a simple VueJS frontend

-> Searching through the records is possible throgh the name field.

![Searching Zerodha](https://user-images.githubusercontent.com/46214838/117665052-13dcb280-b1c0-11eb-9681-df810304c463.gif)

-> Can download the search results into CSV File

<img src="https://user-images.githubusercontent.com/46214838/117703431-44841280-b1e7-11eb-80d3-b9b93d86a67e.gif" width = "650">


### Installation
    pip install -r requirements.txt
      
### Setup
    redis.from_url(os.environ.get("REDIS_URL")) // Reads data from environment variables
    Set Redis URL in Environment variables with name REDIS_URL
### Example
The Redis URL provided by the cloud hosting platform can be added into Environment Variable with name REDIS_URL. Example of the URL is shown:

    REDIS_URL : rediss://:p0026369516854253b1dc21fde8f4b6b6d9a54a331705c5ef69b57@ec2-52-204-217-245.compute-1.amazonaws.com:20973
