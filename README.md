# Slack Workout Bot
A bot that tracks workouts on Slack. 

## Setup
You will need the following to implement this bot:
1. This repo forked/cloned
2. A Heroku account (or something else to host it; we used Heroku)
	a. Heroku CLI installed
3. A Slack workspace that you have the permissions to add a bot to
4. Psql installed (you can uninstall once you have set up the database)

##Create the Slack App
Start by heading over to https://api.slack.com/, clicking "Start Building," and then proceed to name your bot and add it to your workspace. Your app has now been officially created!

##Setting up Heroku
Head to Heroku and, upon logging in, you should be presented with a list of your preexisting apps. Towards the top right, click "New" and then select "Create new app." Name your app accordingly, the US region is fine and you don't need to add it to any pipelines.

In the Deploy tab now, select Github as your deployment method. You will have to connect your Github account to Heroku. Then link the app to the cloned repository. I recommend setting up automatic deploys below this. You can deploy your app shortly after as well!

Once your app has been deployed, clicking "Open app" will now send you to a page with a URL something like <your-app-name>.herokuapp.com. Keep this URL handy, as you will need while setting up your app in Slack.

###Config Vars
Now is the time to input the config vars the app needs. Head over to the "Settings" tab and click "Reveal Config Vars." You should see the DATABASE_URL there already; Heroku will automatically input that for you. For this app, you need the BOT_OAUTH_ACCESS_TOKEN and OAUTH_ACCESS_TOKEN. You can get these from Slack by:

1. Navigate to api.slack.com, and get to your app's page
2. On the left sidebar, select "OAuth & Permissions" under "Features"
3. There, you will find your BOT_OAUTH_ACCESS_TOKEN and OAUTH_ACCESS_TOKEN labelled as such.
4. Copy each token, navigate to Heroku, and paste them as values for their respective key: BOT_OAUTH_ACCESS_TOKEN or OAUTH_ACCESS_TOKEN

Those are the only two config vars you will need for this app.

###Provisioning and Setting up Database
From the Heroku dashboard, click the Resources tab (or alternatively click "Configure Add-ons" from the overview tab) then search for and provision Heroku Postgres. The free Hobby Dev plan suffices for the bot. 

Now that your app has a database, you need to create the table for your app to store data in.

####Setting up Database
Open up command prompt/terminal. You will need the Heroku CLI installed, as well as Psql. You can look up the commands for Heroku CLI online, but if you don't want to look into that you can run the commands in the following order:

1. heroku login
	a. you should be prompted to login via browser after this
2. heroku pg:psql -a <bot name as it appears on heroku>
3. CREATE TABLE <database name> (name text, num_posts SMALLINT, num_workouts SMALLINT, workout_score numeric(4, 1), last_post DATE, slack_id CHAR(9), last_time BIGINT);
	a. the database name should match what is in the code. depending on what repo you cloned, it will likely be tribe_data

That's it for command line statements! You can double check that your table was created with the \d command after.

##Slack Permissions

###App Permissions
In the left sidebar, head to "Event Subscriptions" underneath "Features." Flip the "Enable Events" switch to On, then input the URL you got earlier (<your-app-name>.herokuapp.com). Once it is verified, you will be able to select which events your app subscribes to.

Subscribe to the following Workspace Events:
message.channels
message.groups
message.im
reaction_added
reaction_removed

Subscribe to the following Bot Events:
app_mention
message.channels
message.im
reaction_added
reaction_removed

Make sure to save these changes. Once you do, you'll be prompted to reinstall your app. Once you have done so, you should have a functional workout bot in your channel!

README written by Sam Loop.