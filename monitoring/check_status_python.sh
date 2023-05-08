#!/bin/bash

ERROR=0

echo "Checking process status..."
RESULT=`ps axu | grep flask | grep -v grep | wc -l` # TODO: Filter by app name instead of flask -> Could be more than one flask app running!!

if [ $RESULT -eq 1 ]
then
    echo "Process RUNNING properly"
else
    echo "ERROR! Process NOT RUNNING!!"
    ERROR=1
fi

echo "Checking listening port..."
RESULT=`nc -z localhost 5000 | grep succeeded | wc -l`

if [ $RESULT -eq 1 ]
then
    echo "Port LISTENING properly"
else
    echo "ERROR! Port NOT LISTENING!!"
    ERROR=1
fi

echo "Checking web service..."
RESULT=`curl http://localhost:5000/`

if [ $? -eq 0 ]
then
    echo "Web RUNNING properly"
else
    echo "ERROR! Web NOT RUNNING!!"
    ERROR=1
fi

exit $ERROR