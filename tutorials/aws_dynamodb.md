# DynamoDB

Let's take a closer look at the [NetflixMovieCatalog][NetflixMovieCatalog] service. 
Currently, the service provides movies catalog content from a JSON files located in the source code. 
Obviously, this is not a good approach since we want the content to be dynamically stored and retrieved from a strong database engine. 

In this tutorial you'll configure the [NetflixMovieCatalog][NetflixMovieCatalog] app to retrieve content from a DynamoDb table.

## Create a table

1. Open the DynamoDB console at [https://console.aws.amazon.com/dynamodb/](https://console.aws.amazon.com/dynamodb/)
2. In the navigation pane on the left side of the console, choose **Dashboard**.
3. On the right side of the console, choose **Create Table**.
4. Enter the table details as follows:
    1. For the table name, enter a unique table name.
    2. For the partition key, enter `id`, type **Number**.
    3. Enter `title` as the sort key, type **String**.
    4. Choose **Customize settings**.
    5. On **Read/write capacity settings** choose **Provisioned** mode with autoscale capacity with a minimum capacity of **1** and maximum of **10**.
5. Choose **Create** to create the table.

## Write data using Python and `boto3`

Try the below script to write an item to your DynamoDB table:

```python
import boto3

client = boto3.client('dynamodb')
item = {
    "adult": {'BOOL': False},
    "backdrop_path": {'S': "/tdkCqOQ87ns39bWtzjJYsGTloH9.jpg"},
    "genre_ids": {'NS': ["28", "80", "9648", "53"]},
    "id": {'N': "996154"},
    "original_language": {'S': "en"},
    "original_title": {'S': "Black Lotus"},
    "overview": {'S': "An ex-special forces operative wages a one man war through the streets of Amsterdam to rescue his friend's daughter from the local crime syndicate."},
    "popularity": {'N': "1070.023"},
    "poster_path": {'S': "/y3AeW200hqGLxoPyHMDHpzudylz.jpg"},
    "release_date": {'S': "2023-04-12"},
    "title": {'S': "Black Lotus"},
    "video": {'BOOL': False},
    "vote_average": {'N': "6.559"},
    "vote_count": {'N': "85"}
}

response = client.put_item(
    TableName='<your-table>',   # Change <your-table> accordingly
    Item=item
)
print(response)
```

## Write and query data using AWS cli

```bash
aws dynamodb put-item \
    --table-name <table-name> \
    --item '{ "adult": {"BOOL": false}, "backdrop_path": {"S": "/jnE1GA7cGEfv5DJBoU2t4bZHaP4.jpg"}, "genre_ids": {"NS": ["28", "878"]}, "id": {"N": "1094844"}, "original_language": {"S": "en"}, "original_title": {"S": "Ape vs. Mecha Ape"}, "overview": {"S": "Recognizing the destructive power of its captive giant Ape, the military makes its own battle-ready A.I., Mecha Ape. But its first practical test goes horribly wrong, leaving the military no choice but to release the imprisoned giant ape to stop the colossal robot before it destroys downtown Chicago."}, "popularity": {"N": "877.18"}, "poster_path": {"S": "/dJaIw8OgACelojyV6YuVsOhtTLO.jpg"}, "release_date": {"S": "2023-03-24"}, "title": {"S": "Ape vs. Mecha Ape"}, "video": {"BOOL": false}, "vote_average": {"N": "5.689"}, "vote_count": {"N": "190"} }'
```

Query the data by:

```bash
aws dynamodb get-item --consistent-read --table-name <table-name> --key '{ "id": {"N": "1094844"}, "title": {"S": "Ape vs. Mecha Ape"}}'
```

## Create and query a global secondary index

Let's say you need to query items according to `vote_count` and `vote_average`.
Since those fields aren't part the primary key, there is a need to create a secondary index, otherwise,  
queries will be inefficient and slow, and the cost of scanning the database will be significantly higher.

1. In the navigation pane on the left side of the console, choose **Tables**.
2. Choose your table from the table list.
3. Choose the **Indexes** tab for your table.
4. Choose **Create** index.
5. For the **Partition key**, enter `vote_count`.
6. For the **Sort key**, enter `vote_average`.
6. For **Index** name, enter `vote-index`.
7. Leave the other settings on their default values and choose **Create** index.

Once done, use `boto3` or `awscli` to query all movies with `vote_count > 100` and `vote_average > 6`.


# Exercises

### :pencil2: NetflixMovieCatalog with DynamoDB table

In this exercise you'll make the [NetflixMovieCatalog][NetflixMovieCatalog] app to retrieve and serve movies data from a DynamoDB table (instead a JSON file as it's configured now). 

1. In the NetflixMovieCatalog repo, under `data/` you'll find the JSON used by the server in responses data. 
   Create a Python script to emit all data into your Dynamo table. Note that there are two JSON files: `data_tv.json` and `data_movies.json`, you should think how to store the data in DynamoDB (either in a separate tables, or in the same table while differentiating tv and movies data). 
2. As the NetflixMovieCatalog queries movies by `genre_ids`, and a single movie can belong to multiple genres, there is no efficient way to retrieve the data (the `genre_ids` field is a set of numbers, thus cannot be part of a primary key). 
   The solution is to create **another** DynamoDB table as follows: 

   - Partition Key: genre_id (Number)
   - Sort Key: movie_id (Number)
   
   Each item corresponds to one of the genres of a given movie. This allows efficient querying by genre ID:

   ```python
   import boto3
   dynamodb = boto3.resource('dynamodb')
   table = dynamodb.Table('MoviesByGenre')
   
   response = table.query(
       KeyConditionExpression=boto3.dynamodb.conditions.Key('genre_id').eq(27)
   )
   
   for item in response['Items']:
       print(item)
   ```

   
2. Modify the code of `app.py` to query data from DynamoDB instead the JSON files. 
3. Deploy the NetflixMovieCatalog app as a new Docker image version. 


### :pencil2: Point-in-time recovery for DynamoDB

Restore your table to how it was looking like a few minutes ago.   

https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/PointInTimeRecovery.Tutorial.html#restoretabletopointintime_console


[NetflixMovieCatalog]: https://github.com/exit-zero-academy/NetflixMovieCatalog.git
