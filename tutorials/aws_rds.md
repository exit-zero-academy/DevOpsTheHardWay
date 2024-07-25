# Relational Database Service (RDS)

## SQL vs NoSql

SQL and NoSQL are two different types of database management systems, each have its own strengths and weaknesses.

Let's explore the key differences between them:

- **Data Model**:

   SQL databases use a **structured data model** where data is organized into **tables** with **predefined** schemas.
   Each table contains rows and columns, and **relationships** between tables are established through **keys**.

   Let's consider a simple relational database scenario with three tables: Students, Courses, and Enrollments. These tables will demonstrate how relationships are established through keys.
    
    ```mermaid
    erDiagram
        USERS ||--|{ TWEETS : post
        USERS ||--|{ FOLLOWS : follow
        USERS {
            string username PK
            string fullName
            string email
            date birthdate
        }
        
        FOLLOWS {
            string fromUser
            string toUser
        }
        
        TWEETS {
            key tweetId PK
            string username
            string text
            date createdAt
        }
    ```   

   On the other side, NoSQL databases use a more flexible data model that allows for storing **unstructured** or semi-structured data.
   They can include various data structures like key-value pairs, documents, columns, and graphs.

    Example given:

    ```json
    {
        "_id": ObjectId("5f4dbdbb8cc835a3b4cf979e"),
        "name": "Alice",
        "age": 25,
        "address": {
            "street": "123 Main St",
            "city": "Los Angeles",
            "zipcode": "90001"
        }
    }
    ```

- **Scalability**

    In general, SQL databases can scale **vertically**, meaning you can increase the load on a server by migrating to a larger server that adds more CPU, RAM or SSD capability.
    
    ![][aws_vertical.png]
    
    **Horizontal** scaling of involves adding more nodes to the database cluster to distribute the load and increase the overall capacity of the system, it's very hard to achieve horizontal scaling in relational databases. 
    
    ![][horizontal.png]
    
    NoSQL databases are designed for horizontal scalability, allowing them to distribute data across multiple servers or nodes.
    This makes them well-suited for handling large amounts of data and high traffic.

- **Data consistency, data availability and partition tolerance (CAP)**:

    SQL databases prioritize **consistency** and **partition tolerance**. They adhere to [ACID (Atomicity, Consistency, Isolation, Durability)](https://en.wikipedia.org/wiki/ACID) properties.
    This ensures that data remains accurate and reliable but can sometimes affect availability during failures.
    
    NoSQL databases often prioritize **availability** and **partition tolerance**.  
    This might result in eventual consistency, where data might be slightly outdated but the system remains available.
    
    There is no distributed database in the world (and there will never be such one) that can both be 100% consistent, highly available, and durable (can recover from disk failure).
    This statement was proved in 1998 and referred to as the [CAP theorem](https://en.wikipedia.org/wiki/CAP_theorem).

    ![][aws_cap.png]    

    In real life, both SQL and NoSql databases achieve very good levels of consistency, high availability and durability. 


## Amazon RDS

Amazon Relational Database Service (Amazon RDS) is a web service that makes it easier to set up, operate, and scale a relational database in the AWS Cloud.

You can use the database products you are already familiar with: MariaDB, Microsoft SQL Server, MySQL, Oracle, and PostgreSQL.

![][aws_rds.png]

## Provision Postgres using RDS

1. Open the Amazon RDS console at [https://console\.aws\.amazon\.com/rds/](https://console.aws.amazon.com/rds/)\.

2. In the navigation pane, choose **Databases**\.

3. Choose **Create database** and make sure that **Standard create** is chosen\.

4. In **Configuration**, choose **PostgreSQL**\.

5. For **DB instance size**, choose **Free Tier**\.

6. For **DB instance identifier**, enter a name for the DB instance.

7. For **Master username**, leave the default name \(**postgres**\)\.

8. Enter your master password, and then enter the same password **Confirm password**\.

9. Choose a DB instance according to your needs (**the smallest**).
10. Under **Connectivity**, **Public access** choose **Yes**.
11. Choose **Create database**\.


## Create tables, insert and retrieve data

1. First, install the `psql` cli tool, which is the client for Postgres used from bash terminal

   ```shell
   sudo apt-get update
   sudo apt-get install postgresql-client
   ```

   Start Postgres shell by `psql postgres://<db-username>:<db-password>@<db-endpoint>:5432`

2. Create a database in Postgres (drop previous is exists)
   ```shell
   DROP DATABASE IF EXISTS twitter_demo;
   CREATE DATABASE twitter_demo;
   ```
3. Switch to `twitter_demo` db by `\c twitter_demo`.
4. Create tables:
   ```text
   CREATE TABLE users (
   full_name VARCHAR(100),
   username VARCHAR(100) PRIMARY KEY
   );
   
   CREATE TABLE follows (
   from_user VARCHAR(100),
   to_user VARCHAR(100)
   );
   
   CREATE TABLE tweets (
   id SERIAL,
   username VARCHAR(100),
   text VARCHAR(500),
   created_at DATE NOT NULL DEFAULT CURRENT_DATE
   );
   ```

5. Insert data
   ```text
   INSERT INTO users (full_name, username) VALUES ('Boris Hadjur', '_DreamLead');
   INSERT INTO users (full_name, username) VALUES ('Gunnar Svalander', 'GunnarSvalander');
   INSERT INTO users (full_name, username) VALUES ('GE Software', 'GEsoftware');
   INSERT INTO users (full_name, username) VALUES ('Adrian Burch', 'adrianburch');
   INSERT INTO users (full_name, username) VALUES ('Andy Ryder', 'AndyRyder5');
   INSERT INTO users (full_name, username) VALUES ('Brett Englebert', 'Brett_Englebert');
   INSERT INTO users (full_name, username) VALUES ('Nimbus Data Systems', 'NimbusData');
   INSERT INTO users (full_name, username) VALUES ('SSWUG.ORG', 'SSWUGorg');
   
   
   INSERT INTO follows (from_user, to_user) VALUES ('_DreamLead', 'Scootmedia');
   INSERT INTO follows (from_user, to_user) VALUES ('_DreamLead', 'MetiersInternet');
   INSERT INTO follows (from_user, to_user) VALUES ('GunnarSvalander', 'klout');
   INSERT INTO follows (from_user, to_user) VALUES ('GunnarSvalander', 'zillow');
   INSERT INTO follows (from_user, to_user) VALUES ('GEsoftware', 'DayJobDoc');
   INSERT INTO follows (from_user, to_user) VALUES ('GEsoftware', 'byosko');
   INSERT INTO follows (from_user, to_user) VALUES ('adrianburch', 'CindyCrawford');
   INSERT INTO follows (from_user, to_user) VALUES ('adrianburch', 'Arjantim');
   INSERT INTO follows (from_user, to_user) VALUES ('AndyRyder', 'MichaelDell');
   INSERT INTO follows (from_user, to_user) VALUES ('AndyRyder', 'Yahoo');
   INSERT INTO follows (from_user, to_user) VALUES ('Brett_Englebert', 'RealSkipBayless');
   INSERT INTO follows (from_user, to_user) VALUES ('Brett_Englebert', 'stephenasmith');
   INSERT INTO follows (from_user, to_user) VALUES ('NimbusData', 'dellock6');
   INSERT INTO follows (from_user, to_user) VALUES ('NimbusData', 'rohitkilam');
   INSERT INTO follows (from_user, to_user) VALUES ('SSWUGorg', 'drsql');
   INSERT INTO follows (from_user, to_user) VALUES ('SSWUGorg', 'steam_games');
   
   
   INSERT INTO tweets (text, created_at, username) VALUES ('What do you think about #emailing #campaigns #traffic in #USA? Is it a good market nowadays? do you have #databases?',	'Tue, 12 Feb 2013 08:43:09 +0000', '_DreamdLead');
   INSERT INTO tweets (text, created_at, username) VALUES ('Bill Gates Talks Databases, Free Software on Reddit http://t.co/ShX4hZlA #billgates #databases', 'Tue, 12 Feb 2013 07:31:06 +0000', 'MetiersInternet');
   INSERT INTO tweets (text, created_at, username) VALUES ('RT @KirkDBorne: Readings in #Databases: excellent reading list, many categories: http://t.co/S6RBUNxq via @rxin Fascinating.',	'Tue, 12 Feb 2013 07:30:24 +0000', 'GEsoftware');
   INSERT INTO tweets (text, created_at, username) VALUES ('RT @tisakovich: @NimbusData at the @Barclays Big Data conference in San Francisco today, talking #virtualization, #databases, and #flash memory.',	'Tue, 12 Feb 2013 06:58:22 +0000', 'adrianburch');
   INSERT INTO tweets (text, created_at, username) VALUES ('http://t.co/D3KOJIvF article about Madden 2013 using AI to prodict the super bowl #databases #bus311',	'Tue, 12 Feb 2013 05:29:41 +0000', 'MetiersInternet');
   INSERT INTO tweets (text, created_at, username) VALUES ('http://t.co/rBhBXjma an article about privacy settings and facebook #databases #bus311', 'Tue, 12 Feb 2013 05:24:17 +0000'	,'AndyRyder5');
   INSERT INTO tweets (text, created_at, username) VALUES ('#BUS311 University of Minnesotas NCFPD is creating #databases to prevent food fraud. http://t.co/0LsAbKqJ', 'Tue, 12 Feb 2013 01:49:19 +0000', 'Brett_Englebert');
   INSERT INTO tweets (text, created_at, username) VALUES ('#BUS311 companies might be protecting their production #databases, but what about their backup files? http://t.co/okJjV3Bm', 'Tue, 12 Feb 2013 01:31:52 +0000', 'Scootmedia');
   INSERT INTO tweets (text, created_at, username) VALUES ('@NimbusData CEO @tisakovich @BarclaysOnline Big Data conference in San Francisco today, talking #virtualization, #databases,& #flash memory', 'Mon, 11 Feb 2013 23:15:05 +0000', 'NimbusData');
   INSERT INTO tweets (text, created_at, username) VALUES ('Dont forget to sign up for our FREE expo this Friday: #Databases, #BI, and #Sharepoint: What You Need to Know! http://t.co/Ijrqrz29',	'Mon, 11 Feb 2013 22:15:37 +0000', 'SSWUGorg');
   ```

6. Retrieve some data
    * Joint table of all users, and all followings for each user:
      ```shell
      SELECT * FROM users JOIN follows ON users.username=follows.from_user;
      ```
    * The tweets of all users that are followed by the user *_DreamLead*:
      ```text     
      SELECT to_user, text, created_at
      FROM users u
      JOIN follows f
      ON u.username=f.from_user
      JOIN tweets t
      ON f.to_user=t.username
      WHERE u.username='_DreamLead';
      ```
    * Use aggregation
      ```text
      SELECT to_user, COUNT(*) as tweets_count
      FROM users u
      JOIN follows f
      ON u.username=f.from_user
      JOIN tweets t
      ON f.to_user=t.username
      WHERE u.username='_DreamLead'
      GROUP BY to_user;
      ```

## Monitoring and alerting for an RDS database

1. Open the CloudWatch console at [https://console\.aws\.amazon\.com/cloudwatch/](https://console.aws.amazon.com/cloudwatch/)\.

2. In the navigation pane, choose **Alarms**, **All alarms**\.

3. Choose **Create alarm**\.

4. On the **Specify metric and conditions** page, choose **Select metric**\.

5. In the search box, enter the name of your RDS database and press Enter\.

6. Choose **RDS**, **Per\-Database Metrics**\.

7. In the search box, enter **IOPS** and press Enter, then select **ReadIOPS** and **WriteIOPS** metrics. The graph will show both read and write i/o operations metric for your db.

8. We would like to base the alarm on the total sum of read + write i/o. From **Add math**, choose **All functions**, **SUM**\.

9. Choose the **Graphed metrics** tab, and edit the details for **Expression1** to **TotalIOPS**\.

10. Change the **Period** to **1 minute**\.

11. Clear selection from all metrics except for **TotalIOPS**\.

12. Choose **Select metric**\.

13. On the **Specify metric and conditions** page, enter a number of IOPS in **Define the threshold value**\.
    For this tutorial, enter **100**. You can adjust this value for your workload requirements\.

14. Choose **Next**, and the **Configure actions** page appears\.

15. Keep **In alarm** selected, choose **Create new topic**, and enter the topic name and a valid email address\.

16. Choose **Create topic**, and then choose **Next**\.

17. On the **Add name and description** page, enter the **Alarm name** and **Alarm description**, and then choose **Next**\.

18. Preview the alarm that you're about to create on the **Preview and create** page, and then choose **Create alarm**\.

### Testing your alarm

It is very important to test all the alarms you set, in production environment if possible.

19. Connect to an Amazon Linux EC2 instance in the same region of your DB instance.
20. Install PostgreSQL tooling package by
```
sudo yum install postgresql-server postgresql-contrib
```
21. Perform a load test of your server and watch the alarm in action
    To initialize test tables, execute first:
```shell
PGPASSWORD=<password> pgbench -i -U postgres -h <db-url> <internal-db-name>
```

Then run the full test by:

```shell
PGPASSWORD=<password> pgbench -P 10 -t 10000 -j 10 -c 10 -U postgres -h <db-url> <internal-db-name>
```

While `<password>` is you db password. `<db-url>` is you RDS database url and `<internal-db-name>` is an existed table.

For more information on the `pgbench` command, read [here](https://www.postgresql.org/docs/current/pgbench.html).

# Exercises 

### :pencil2: Test failover for your DB instance 

**Note:** 
In order to test the faliover mechanism, a **Multi-AZ DB instance** should be provisioned.

We would like to understand how long the failover process takes for your particular use case and to ensure that the application that accesses your DB instance can automatically connect to the new DB instance after failover occurs.

Reboot a DB instance to simulate a failover

1. Open the Amazon RDS console at [https://console\.aws\.amazon\.com/rds/](https://console.aws.amazon.com/rds/)\.

1. In the navigation pane, choose **Databases**, and then choose the DB instance that you want to reboot\.

1. For **Actions**, choose **Reboot**\.

   The **Reboot DB Instance** page appears\.

1. Choose **Reboot with failover?** to force a failover from one AZ to another\.

1. Choose **Reboot** to reboot your DB instance\.


### :pencil2: Exporting data from PostgreSQL to Amazon S3

https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/postgresql-s3-export.html





[aws_vertical.png]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/aws_vertical.png.png
[horizontal.png]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/horizontal.png.png
[aws_cap.png]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/aws_cap.png.png
[aws_rds.png]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/aws_rds.png.png

