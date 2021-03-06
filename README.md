# mini_project
This is a demonstration on how to build and run a web application using python, flask, docker, clusters, and Cassandra. The application uses information from the Tfl API to return train line information, such as the name of the train line, which mode it is, the date modified and created. This will also return the information of the given line passed through the URL.

Furthermore, the app allows the extracting of mario kart stats. The method created allows the ability to obtain the characters speed, based on the character name passed through the URL.


# Tfl API
Te get the information of the train lines, go to the Tfl API ([here](https://api.tfl.gov.uk/)) and download it into a json file to use later.


# Setting up
To begin, open the google cloud shell and create a directory where the app will live (e.g. mkdir ......).

Set the region and zone for the new cluster. 

```
gcloud config set compute/zone europe-west2-b
export PROJECT_ID="$(gcloud config get-value project -q)"
```
# Cassandra Node
The next step will be to set up a Cassandra node in a container. First pull the most up to date Cassandra Docker image.

```
docker pull cassandra:latest
```

The run a Cassandra instance inside docker.

```
docker run --name cassandra-test -d cassandra:latest
```

Check that it is running correctly before progressing by issuing:

```
docker ps
```

Now that the instance is running, it is time to insert some data into it. In this case it is Mario Kart statistics.

```
wget -O characters.csv https://tinyurl.com/yy2e462k
```

You can have a peak at the data by running the following commands:

```
head characters.csv
tail characters.csv
```

Next, copy the data into the container:

```
docker cp characters.csv cassandra-test:/home/characters.csv
```

It is now possible to interact with Cassandra through its command line shell (cqlsh). To do this run:

```
docker exec -it cassandra-test cqlsh
```

Now we are in the Cassandra Terminal. Next create a keyspace for the data to be inserted into:

```
CREATE KEYSPACE characters WITH REPLICATION =
{'class' : 'SimpleStrategy', 'replication_factor' : 1};
```

Now create the table inside the keyspace just made, with stating the columns and the type of data it is:

```
CREATE TABLE characters.stats (Character text PRIMARY KEY, Class text,
Speed decimal, Speed_Water decimal, Speed_Air decimal,
Speed_Ground decimal, Acceleration decimal, Weight decimal,
Handling decimal, Handling_Water decimal, Handling_Air decimal,
Handling_Ground decimal, Traction decimal, Mini_Turbo decimal);
```

Now copy the data from the csv database.

```
COPY characters.stats(Character,Class,Speed,Speed_Water,
Speed_Air,Speed_Ground,Acceleration,Weight,Handling,Handling_Water,
Handling_Air,Handling_Ground,Traction,Mini_Turbo)
FROM '/home/characters.csv'
WITH DELIMITER=',' AND HEADER=TRUE;
```
From here the data can now be queries. For example run:

```
select * from characters.stats;
```

Experiment with other queries and see what happens.

# Cassandra in Kubernetes
It is time to create a Kubernetes cluster. Issue the following command to create 3 node clusters named 'cassandra'. Note that ```n1-standard-2``` machines will be used, as they have two virtual CPUs and more memory.

```
gcloud container clusters create cassandra --num-nodes=3 --machine-type "n1-standard-2"
```

Next step is to run a specified Kubernetes service. This will be done using three files which are a Headless service, the Cassandra itself, and the replication Controller. Run the following commands:

```
wget -O cassandra-peer-service.yml http://tinyurl.com/yyxnephy
wget -O cassandra-service.yml http://tinyurl.com/y65czz8e
wget -O cassandra-replication-controller.yml http://tinyurl.com/y2crfsl8
```

As soon as they are downloaded you can now run the three components:

```
kubectl create -f cassandra-peer-service.yml
kubectl create -f cassandra-service.yml
kubectl create -f cassandra-replication-controller.yml
```

To check that the container is running fine, run:

```
kubectl get pods -l name=cassandra
```
If it is, then you can scale up the number of nodes through the replication-controller:

```
kubectl scale rc cassandra --replicas=3
```

Issue ```kubectl get pods``` to check that they are all running.

Then select on of the container and check if the cassandra ring has been formed:
```
kubectl exec -it cassandra-7m4pf -- nodetool status
```
Note that "7m4pf" should be replaced with the unique tag of your chose container.

When the ring is formed, use the same container to copy the from the previous stage:
```
kubectl cp characters.csv cassandra-7m4pf:/characters.csv
```
run cqlsh in the container:
```
kubectl exec -it cassandra-7m4pf cqlsh
```
and create your keyspace:
```
CREATE KEYSPACE characters WITH REPLICATION =
{'class' : 'SimpleStrategy', 'replication_factor' : 2};
```

Now create the table for the mario stats and ingest the CSV through copy, as previously done:
```
CREATE TABLE characters.stats (Character text PRIMARY KEY, Class text,
Speed decimal, Speed_Water decimal, Speed_Air decimal,
Speed_Ground decimal, Acceleration decimal, Weight decimal,
Handling decimal, Handling_Water decimal, Handling_Air decimal,
Handling_Ground decimal, Traction decimal, Mini_Turbo decimal);

COPY characters.stats(Character,Class,Speed,Speed_Water,
Speed_Air,Speed_Ground,Acceleration,Weight,Handling,Handling_Water,
Handling_Air,Handling_Ground,Traction,Mini_Turbo) FROM 'characters.csv'
WITH DELIMITER=',' AND HEADER=TRUE;
```

# Connecting Flask to Cassandra
The last task is to pull the data from the Cassandra database into a flask web client.

First create requirements.txt, which will contain the requirements of Flask, json, the python cassandra-driver, ans son.
```
pip
Flask
requests
jsonify
plotly
cassandra-driver
```

Then create a Dockerfile with the following content:
```
FROM python:3.7-alpine
WORKDIR /tflapp
COPY . /tflapp 
RUN pip install -U -r requirements.txt
EXPOSE 8080
CMD ["python", "tflapp.py"]
```

Then fill in the code (tflapp.py, located in the repository).


Note that on line 4 is the cluster object (connection to the database) specified as 'cassandra'.

On line 9 is where the json file containing data from the Tfl API is loaded.

Also, note that there are three GET methods relating to the Tfl API. The first method will retrieve the names of all the train lines. The second GET method will return the type of mode the train line sed on the name parsed through the URL. The third, returns the name of the train lines that run on the given mode type.

Additionally there is a POST method to add a train line into the database, a PUT method to update existing information on the database, and a DELETE method that deletes a train line from the database completely.

Finally, there is one more GET method which gets the speed of a mario kart racer from the Cassandra database previously created, and returns it along with the name of the character. Queries are carried out through the session object and is the same string you would enter in cqlsh.

To continue, it is now time to build our image:
```
docker build -t gcr.io/${PROJECT_ID}/mar-app:v1 .
```

Then push it into the Google Repository:
```
docker push gcr.io/${PROJECT_ID}/mar-app:v1
```

Next, run it as a service, and expose the deployment:
```
kubectl run mar-app --image=gcr.io/${PROJECT_ID}/mar-app:v1 --port 8080

kubectl expose deployment mar-app --type=LoadBalancer --port 80 --target-port 8080
```

Once you have received your external IP by running 'kubectl get services', try out the service methods with train lines, mode types, and mario kart racers of your choice.

