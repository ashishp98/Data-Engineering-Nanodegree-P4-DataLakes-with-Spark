import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.sql.types import StructType as R, StructField as Fld, DoubleType as Dbl, StringType as Str, IntegerType as Int, DateType as Dat, TimestampType


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config.get('DEFAULT', 'AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY']=config.get('DEFAULT', 'AWS_SECRET_ACCESS_KEY')

print(os.environ['AWS_ACCESS_KEY_ID'])
print(os.environ['AWS_SECRET_ACCESS_KEY'])


def create_spark_session():
    
    '''
    Description : This function Gets existing OR Creates new Spark Session
    '''

    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    
    '''
    Description : This function loads songs_data from S3 and process it using pyspark and then loads it back to S3
    
    Parameters :
        - spark : spark session
        - input_data : location of songs_data file stored in S3
        - output_data : S3 bucket path where the processed data needs to be stored
    '''

    song_data = input_data + 'song_data/*/*/*/*.json'
    
    songSchema = R([
        Fld("artist_id",Str()),
        Fld("artist_latitude",Dbl()),
        Fld("artist_location",Str()),
        Fld("artist_longitude",Dbl()),
        Fld("artist_name",Str()),
        Fld("duration",Dbl()),
        Fld("num_songs",Int()),
        Fld("title",Str()),
        Fld("year",Int()),
    ])
    
    df = spark.read.json(song_data, schema=songSchema)

    
    song_fields = ["title", "artist_id","year", "duration"]
    
    songs_table = df.select(song_fields).dropDuplicates().withColumn("song_id", monotonically_increasing_id())
    
    songs_table.write.partitionBy("year", "artist_id").parquet(output_data + 'songs/')

    
    artists_fields = ["artist_id", "artist_name as name", "artist_location as location", "artist_latitude as latitude", "artist_longitude as longitude"]

    artists_table = df.selectExpr(artists_fields).dropDuplicates()

    artists_table.write.parquet(output_data + 'artists/')


def process_log_data(spark, input_data, output_data):
    
    '''
    Description : This function loads logs_data from S3 and process it using pyspark and then loads it back to S3
    
    Parameters :
        - spark : spark session
        - input_data : location of songs_data file stored in S3
        - output_data : S3 bucket path where the processed data needs to be stored
    '''

    log_data = input_data + 'log_data/*/*/*.json'

    df = spark.read.json(log_data)
    
    df = df.filter(df.page == 'NextSong')

    
    users_fields = ["userdId as user_id", "firstName as first_name", "lastName as last_name", "gender", "level"]
    users_table = df.selectExpr(users_fields).dropDuplicates()

    users_table.write.parquet(output_data + 'users/')

    
    get_datetime = udf(date_convert, TimestampType())
    df = df.withColumn("start_time", get_datetime('ts'))

    
    time_table = df.select("ts", "start_time", "hour", "day", "week", "month", "year", "weekday").dropDuplicates() \
        .withColumn("hour", hour(col("start_time"))) \
        .withColumn("day", day(col("start_time"))) \
        .withColumn("week", week(col("start_time"))) \
        .withColumn("month", month(col("start_time"))) \
        .withColumn("year", year(col("start_time"))) \
        .withColumn("weekday", date_format(col("start_time"), 'E'))
       
    
    songs_table.write.partitionBy("year", "month").parquet(output_data + 'time/')

    
    songs_df = spark.read.parquet(output_data + 'songs/*/*/*')
    
    artists_df = spark.read.parquet(output_data + 'artists/*')
    
    
    songs_logs = df.join(songs_df, (df.song == songs_df.title))
    artists_songs_logs = songs_logs.join(artists_df, (songs_logs.artist == artists_df.name))
    
    songplays = artists_songs_logs.join(
        time_table,
        artists_songs_logs.ts == time_table.start_time, 'left'
    ).drop(artists_songs_logs.year)


    songplays_table = songplays.select(
        col('start_time').alias('start_time'),
        col('userId').alias('user_id'),
        col('level').alias('level'),
        col('song_id').alias('song_id'),
        col('artist_id').alias('artist_id'),
        col('sessionId').alias('session_id'),
        col('location').alias('location'),
        col('userAgent').alias('user_agent'),
        col('year').alias('year'),
        col('month').alias('month'),
    ).repartition("year", "month")
    

    songplays_table.write.partitionBy("year", "month").parquet(output_data + 'songplays/')


def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = "s3a://udacity-sparkify-dend/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
