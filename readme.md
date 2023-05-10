$create a mysql db called emaildb
-> create database emaildb; 

$create a table called mails
-> create table mails( 
-> s_no varchar(255),
-> message_id message_id(255),
-> From varchar(255),
-> To varchar(255),
-> Subject varchar(255), 
-> Date varchar(255),
-> labels varchar(255));


gmail_auth.py for fetching mails to db

filters.py for filtering the mails from db and doing actions on them

rules.json is for mentioning the rules