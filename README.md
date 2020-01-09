# Slack Workout Bot
A bot that tracks workouts on Slack. There is also functionality for polls and practice attendance tracking 

## Setup
You will need the following to implement this bot:
1. This repo forked/cloned
2. A Heroku account (or something else to host it; we used Heroku)
	* Heroku CLI installed
3. A Slack workspace that you have the permissions to add a bot to
    * the workspace must have a channel named bot_testing
4. Psql installed (you can uninstall once you have set up the database)

## Create the Slack App
Start by heading over to [the slack api docs](https://api.slack.com/), clicking **Start Building**, and then proceed to name your bot and add it to your workspace. Your app has now been officially created!

## Setting up Heroku
Head to Heroku and, upon logging in, you should be presented with a list of your preexisting apps. Towards the top right, click **New** and then select **Create new app**. Name your app accordingly, the US region is fine and you don't need to add it to any pipelines.

In the Deploy tab now, select Github as your deployment method. You will have to connect your Github account to Heroku. Then link the app to the cloned repository. I recommend setting up automatic deploys below this. You can deploy your app shortly after as well!

Once your app has been deployed, clicking **Open app** will now send you to a page with a URL something like _your-app-name_.herokuapp.com. Keep this URL handy, as you will need while setting up your app in Slack.

### Config Vars
Now is the time to input the config vars the app needs. Head over to the **Settings** tab and click **Reveal Config Vars**. You should see the **DATABASE_URL** there already; Heroku will automatically input that for you. For this app, you need the **BOT_OAUTH_ACCESS_TOKEN** and **OAUTH_ACCESS_TOKEN**. You can get these from Slack by:

1. Navigate to [the slack api docs](https://api.slack.com/), and get to your app's page
2. On the left sidebar, select **OAuth & Permissions** under **Features**
3. There, you will find your **BOT_OAUTH_ACCESS_TOKEN** and **OAUTH_ACCESS_TOKEN** labelled as such.
4. Copy each token, navigate to Heroku, and paste them as values for their respective key: **BOT_OAUTH_ACCESS_TOKEN** or **OAUTH_ACCESS_TOKEN**
5. Create a config var named **ENABLE_CALENDAR** and set the value to either **True** or **False** (set to false if you are not familiar with this)
6. Create a config var named **ADMIN_ID** and set the value to the slack id of the person or people in charge of the bot. They will have access to special admin commands. They will look like *UNSD1MM6G* and multiple can be added if you seperate with a comma
7. create a config var named **VERBOSITY** and set the value to **1**. 
    * This variable controls how often the bot will post to its debugging channel. at level 0 it will post everything, 1 will post only info or error, 2 will post only errors and 3 will post nothing. If a message does not get posted it will be written to the heroku logs instead

### Provisioning and Setting up Database
From the Heroku dashboard, click the Resources tab (or alternatively click **Configure Add-ons** from the overview tab) then search for and provision Heroku Postgres. The free Hobby Dev plan suffices for the bot. 

Now that your app has a database, you need to create the table for your app to store data in.

#### Setting up Database

##### Automatic
The bot will automatically configure its own tables if you type in the command **!setup**. This must be done after you have configured all permissions as __detailed below in **slack permissions**__

##### Manual
Alternatively you can setup the tables yourself.
Open up command prompt/terminal. You will need the Heroku CLI installed, as well as Psql. You can look up the commands for Heroku CLI online, but if you don't want to look into that you can run the commands in the following order:
Each table name should match what is in the code. These names are hard coded and your bot will fail without it. It is easy enough to change if you care to though.

1. heroku login
	* you should be prompted to login via browser after this
2. heroku pg:psql -a <bot name as it appears on heroku>
3. Run the following commands to create the required tables
```
CREATE TABLE tribe_data (name text not null constraint tribe_data_pkey primary key, num_posts smallint default 0, num_workouts smallint, workout_score numeric(4, 1), last_post date, slack_id varchar(9));

CREATE TABLE tribe_workouts (name varchar, slack_id char(9), workout_type varchar, workout_date date);

CREATE TABLE tribe_poll_data (ts numeric(16, 6), slack_id char(9), title text, options text [], channel char(9), anonymous boolean);

CREATE TABLE tribe_poll_responses (ts numeric(16, 6), real_name text, slack_id char(9), response_num smallint);

CREATE TABLE reaction_info (date date, yes text, no text, drills text, injured text, timestamp text);
```
That's it for command line statements! You can double check that your tables were created with the \d command after.


## Slack Permissions

### App Permissions
In the left sidebar, head to **Event Subscriptions** underneath **Features**. Flip the **Enable Events** switch to On, then input the URL you got earlier (_your-app-name_.herokuapp.com). Once it is verified, you will be able to select which events your app subscribes to.

Subscribe to the following Workspace Events:
* message.channels
* message.groups
* message.im
* reaction_added
* reaction_removed

Subscribe to the following Bot Events:
* app_mention
* message.channels
* message.im
* reaction_added
* reaction_removed

Make sure to save these changes. Once you do, you'll be prompted to reinstall your app. Once you have done so, you should have a functional workout bot in your channel!


This marks the end of the setup requirements. Continue reading if you wish to extend this bot for your own teams needs

## Extending the bot for your team

Adding commands for the bot should be a simple task. The bot automatically recognizes instance methods of the Slack Response class with the name command_commandname or admincommand_commandname as valid commands. In order to add a command, simply create a new method named command_yourcommand. Then it will be as if the user is calling the methods command_yourcommand when they type !yourcommand into the slack workspace in any channel that the bot is in. 

README written by Sam Loop.
