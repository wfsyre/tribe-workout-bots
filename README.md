There are two bots in the repo, one for github and one for slack. 
Both are intended to be workout counting a scoring bots, but could easily be repurposed for many other tasks

Requirements for both bots:
-You will need a Heroku account (you can use the free option) https://signup.heroku.com/login

Requirements for Groupme Bot (in addition to the requirements for both bots)
-A Groupme Dev account (for the groupme bot) https://dev.groupme.com/
-A registered GroupMe Bot (register on the groupme dev page)
-A registered GroupMe Application (also on the groupme dev page, this enables direct messaging automation)
  -If you do not need to DM people, then you can skip registering an application

Requirements for the slack bot (in addition to the requirements for both bots)
-I'll let you know when I finish

Instructions to set up the GroupMe bot for your team:
1. Set up your own github repo with my code in it
  - cd into the folder you want your project folder to be in
  - git clone https://github.com/wfsyre/tribe-workout-bots.git
  - Go to github.
  - Log in to your account.
  - Click the new repository button in the top-right.
  - Click the “Create repository” button.
  - Now, follow those instructions.
2. Set Up Groupme Dev
  - After creating your account, create 2 bots, one for debugging that you will but in a group with yourself
    and one that will communicate with your team that you will put in a group with your team in it.
  - note the Bot ID of each Bot
  - note the location of your access token (should be a button in the top right of the page)
  - Keep this page open as you set up Heroku
3. Set up Heroku
  - got to https://heroku.com/login and log in
  - on the dashboard, click the new button on the top right and select "Create a new app"
  - name your app
  - select the deploy tab and select GitHub under the deployment method
  - connect your github
  - type your repo name that you created with my code in it and select the master branch
  - enable automatic deploys if they aren't already enabled
    - every time you push new code, it will be re-deployed to Heroku
  - click the overview tab
  - click "Configure Add-ons" and add a Heroku Postgres Database with the Hobby Dev plan (free)
  - click the settings tab, we'll be setting your config vars
  - You should create the following: (key: value)
  (ACCESS_TOKEN: your groupme access token found in the upper right hand corner of the groupme.dev page)
  (DATABASE_URL: should have been filled in automatically) -Don't do anything to this one
  (TRIBE_BOT_ID: the ID of the bot you created in groupme dev)
    -This is the bot that will communicate with your team
  (TEST_BOT_ID: the ID of the bot that is in your debugging groupme group)
    -Thi is the bot you will use to set some things up and monitor progress
  - Scroll down to "Domain and Certificates"
  - copy your app domain
4. Back to groupme dev
  - edit both your bots and set thier callback urls to the value you copied from heroku
5. Set up your PostgresSQL database
  - Go to your Debugging Groupme
  - type the following 
  - !fix CREATE TABLE tribe_data (name text, num_posts SMALLINT, num_workouts SMALLINT, workout_score numeric(4, 1), last_post DATE, id  INT)
  
6. Enjoy your new bot!

    
  
  
