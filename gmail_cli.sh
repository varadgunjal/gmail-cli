#!/bin/bash

if [ $# == 0 ] 
then
    # read -p 'From: ' from
    read -p 'To : ' to
    read -p 'Subject : ' subj
    read -p 'Message : ' msg
    read -p 'Attachments : ' filepath
    read -p 'Action : ' act
    read -p 'Time : ' timestamp
fi

echo python gmail_cli.py --recipient $to --subject $subj --message_text $msg --attachments $filepath --action $act | at $timestamp