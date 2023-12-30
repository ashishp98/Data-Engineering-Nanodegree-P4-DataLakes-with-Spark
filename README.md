# Spark and Data Lake

In this project, the learnings of Spark and data lakes is applied to build an ETL pipeline for a data lake hosted on S3. To complete the project, I had to load data from S3, process the data into analytics tables using Spark, and load them back into S3. The Spark process is deployed on a cluster using AWS.

## Sparkify Dataset

Currently, Data is stored for songs available and user log activities that resides in S3, they are in the JSON format.

`Song data`: s3://udacity-dend/song_data
`Log data`: s3://udacity-dend/log_data

### Song dataset structure

```json
{
     "num_songs": 1, 
     "artist_id": "ARD842G1187B997376", 
     "artist_latitude": 43.64856, 
     "artist_longitude": -79.38533, 
     "artist_location": "Toronto, Ontario, Canada", 
     "artist_name": "Blue Rodeo", 
     "song_id": "SOHUOAP12A8AE488E9", 
     "title": "Floating", 
     "duration": 491.12771, 
     "year": 1987}
```

# Log dataset structure

```json
{
     "artist":"Des'ree",
     "auth":"Logged In",
     "firstName":"Kaylee",
     "gender":"F",
     "itemInSession":1,
     "lastName":"Summers",
     "length":246.30812,
     "level":"free",
     "location":"Phoenix-Mesa-Scottsdale, AZ",
     "method":"PUT",
     "page":"NextSong",
     "registration":1540344794796.0,
     "sessionId":139,
     "song":"You Gotta Be",
     "status":200,"ts":1541106106796,
     "userAgent":"\"Mozilla\/5.0 (Windows NT 6.1; WOW64) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/35.0.1916.153 Safari\/537.36\"",
     "userId":"8"
}
```

## How To Run

To run the project, follow the below steps:-
    
#### 1. Create a file dl.cfg in the root of this project with the following data:
``` sh
KEY=YOUR_AWS_ACCESS_KEY
SECRET=YOUR_AWS_SECRET_KEY
```
    
#### 2. Create an S3 Bucket named `udacity-sparkify-dend` where output results will be stored.

#### 3. Finally, run the command:
``` sh
python etl.py
```
