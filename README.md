# Efento-cloud-webhook-integration

**This tutorial will show you how to setup a simple http server with a database and configure Efento webhook to send the data to it. In this tutorial we are using Python, Flask and PostgreSQL database, but the same idea can be easily implemented in other programming languages / with different databases. Should you have any issues or questions, feel free to drop us a line at help.efento.io**

# Before you start

Before you start you will need to install and configure the following components: 


-   [PyCharm](https://www.jetbrains.com/pycharm/download/) or any Python 3 IDE,
-   [PostgreSQL database](https://www.postgresql.org/),
-   [Efento sensors](https://getefento.com/technology/efento-bluetooth-low-energy-wireless-sensors/) added to [Efento Cloud](https://cloud.efento.io/)

# PostgreSQL database 

## Setting up the database

After downloading and installing PostgreSQL you will need to create the first database. This in one of the steps during the PostgreSQL installation. By default, the database will be created with the following credentials:

_DATABASE_HOST = ‘localhost’;_  
_DATABASE_USER = ‘postgres’;_  
_DATABASE_PASSWORD = ‘Your password’;_  
_DATABASE_NAME = ‘postgres’;_

If you want to, you can change the names / credentials. Write them down, as they will be needed in the next steps. If you want to check database credentials, open pgAdmin in the PostgreSQL folder. **Next open Object -> Properties -> General**

![](https://getefento.com/wp-content/uploads/2021/05/Database-credentials.png)

## Creating a table

To save the measurements coming from Efento Gateway in your database, you need to create a table. In this example, we are creating a very simple table to store all the data from the sensors, no matter what the sensor type. The table will have 7 columns, all of them of “text” type. **Please note that this architecture of the database is only for the demonstration purposes. Database structure should be selected according to your project requirements.**  

You can create the table manually, using pgAdmin’s interface or using a SQL query. In pgAdmin select your database, open Tools menu: **Tools -> Query Tools**. Copy the request below into the **Query Editor** and click **Execute** (▶) :


    CREATE  TABLE webhooks (
        measured_at text ,
        serial_number text ,
        measurement_point text ,
        channel text,
        type text,
        status text,
        value text);

![](https://getefento.com/wp-content/uploads/2021/05/Create-table.png)

# Python Server

## **Before you start**

In order to make the server work, you will need:

-   **Flask** – Flask is a micro framework used for development of web applications. If you want to learn more about Flask check out [this website](https://flask.palletsprojects.com/en/2.0.x/). You can install and import Flask in pyCharm IDE or using pip ($ pip install -U Flask)
-   **psycopg2** – one of the most popular PostgreSQL database adapter for Python. If You want to know more check out [this website](https://www.psycopg.org/docs/).

### **How it works?**

Script we are going to write sets up http server. The server is constantly listening for data sent by Efento webhook (webhooh sends the data as JSON over REST. One message can contain multiple measurements from one sensor). Once a new messages comes, server parses the data, saves it in the data base and returns “201” status code to the Efento CLoud. This means that the message has been successfully parsed and save in the database. If anything goes wrong (e.g. database is down), server will respond with “500” status code to Efento Cloud. In that case, webhook will retry to send the same data after a while, after several failed attempts the webhook will be disabled.

![](https://getefento.com/wp-content/uploads/2021/05/Server-algorithm.png)
## **Efento webhook configuration**

Log in to Efento Cloud through your web browser. Navigate to **Settings** -> **Webhooks**.

![Settings-webhooks](https://user-images.githubusercontent.com/86711805/220581931-cc0bf06e-c189-4648-b9d6-080eb874c111.png)

To assign measurement point to the webhook click the plus in the URL column.

![Webhooks-add-url](https://user-images.githubusercontent.com/86711805/220581829-3c3166b0-f195-4bdc-a7fc-e808b9805d7d.png)

Next In the **URL** field, enter the server address (domain or IP of the computer/server where the Python script is running) and confirm it click in the **save** button.

![Webhook-server-address](https://user-images.githubusercontent.com/86711805/220582466-cd4545e4-63e3-460c-a8f7-bdf2e05c9a37.png)

## **Results**

When you run the script, all the data coming form the webhooh will be saved in the database. To view the measurements open pgAdmin 4, select your database, then open **Tools** > **Query Tools**.

Enter the request below into the **Query Editor** and select **Execute** (▶) :

> **SELECT**  * **FROM** measurements;

![Webhooks-result](https://user-images.githubusercontent.com/86711805/220581691-ee32cb79-10ae-42ae-b001-57e079b235da.png)

