#!/bin/bash

if [ $# == 0 ] 
then
    read -p 'Option : ' opt

    if [ $opt == 'compose' ]
    then
        read -p 'To : ' to
        read -p 'Subject : ' subj
        read -p 'Message : ' msg
        read -p 'Attachments : ' filepath
        read -p 'Action : ' act
        read -p 'Time : ' timestamp

        echo python /home/varad/python/gmail_cli/gmail_cli.py --recipient $to --subject $subj --message_text $msg --attachments $filepath --action $act | at $timestamp

    elif [ $opt == 'search' ]
    then
        echo 'Not yet implemented'
    fi
fi

