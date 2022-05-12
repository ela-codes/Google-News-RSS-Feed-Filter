# 6.0001/6.00 Problem Set 5 - RSS Feed Filter
# Name: Aena Teodocio
# Collaborators:
# Time: Around 5 hours maybe. 

import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz

punc = string.punctuation

#-----------------------------------------------------------------------

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
          #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
          #  pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret

#======================
# Data structure design
#======================

class NewsStory(object):
    def __init__(self, guid, title, description, link, pubdate):
        """
        Initializes a NewsStory object.

        Contains the following attributes:
        self.guid (str): A globally unique identifier for this news story.
        self.title (str): The new story's headline.
        self.description (str): A paragraph or so summarizing the news story.
        self.link (str): A link to a website with the entire story.
        self.pubdate (datetime): Date the news was published.
        
        """
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate

    def get_guid(self):
        """
        Returns: self.guid
        """
        return self.guid

    def get_title(self):
        """
        Returns: self.title 
        """
        return self.title

    def get_description(self):
        """
        Returns: self.description 
        """
        return self.description

    def get_link(self):
        """
        Returns: self.link 
        """
        return self.link

    def get_pubdate(self):
        """
        Returns: self.pubdate
        """
        return self.pubdate
        
#======================
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError
        

# PHRASE TRIGGERS

class PhraseTrigger(Trigger):
    def __init__(self, phrase):
        """
        Initializes a new PhraseTrigger.
        
        phrase (str): A phrase to be used as a news story trigger. 
                      Each word must be separated by a space.
        """
        self.phrase = phrase

     
    def is_phrase_in(self, text):
        """
        Returns True if the whole phrase is in text. False otherwise.

        text (str): the text from which to search the phrase trigger from.
        """
        phrase = self.phrase.lower()
        mytext = text.lower()
        split_phrase = self.phrase.split() 

        if len(split_phrase) > 1 and " " not in text:
            if text.isalpha():
                return False
            else:
                for i in mytext:
                    if i in punc:
                        mytext = mytext.replace(i, " ")
                mytext = ' '.join(mytext.split())
                return mytext == phrase

        else:
            text_stripped = mytext.translate(str.maketrans('', '', punc)).split()
            for i in range(len(text_stripped)-len(split_phrase)+1):
                try_text = ' '.join(text_stripped[i:i+len(split_phrase)])
                if try_text == phrase:
                    return True
            return False


class TitleTrigger(PhraseTrigger):
    def evaluate(self, story):
        """
        Returns True if the phrase is in the story's title. False otherwise.

        story (a NewsStory object): the class object from which to search the phrase in.
        """
        return self.is_phrase_in(story.get_title())
    

class DescriptionTrigger(PhraseTrigger):
    def evaluate(self, story):
        """
        Returns True if the phrase is in the story's description. False otherwise.

        story (a NewsStory object): the class object from which to search the phrase in.
        """
        return self.is_phrase_in(story.get_description())


# TIME TRIGGERS

class TimeTrigger(Trigger):
    def __init__(self, time):
        """
        Initializes a new TimeTrigger.
        
        time (str): A time to be used as a time trigger. 
                    Timezone is EST and is in format of "%d %b %Y %H:%M:%S". 
                    Example -> "3 Oct 2016 17:00:10"
        """
        self.tz = pytz.timezone('US/Eastern')
        converted_time = datetime.strptime(time, "%d %b %Y %H:%M:%S")
        converted_time = datetime.replace(converted_time, tzinfo=self.tz)
        self.time = converted_time


class BeforeTrigger(TimeTrigger):
    def evaluate(self, story):
        """
        Returns True if the story was published before the given time trigger. False otherwise.

        story (a NewsStory object): the class object from which to search the phrase in.
        """        
        story_time = datetime.replace(story.get_pubdate(), tzinfo=self.tz)
        return story_time < self.time

class AfterTrigger(TimeTrigger):
    def evaluate(self, story):
        """
        Returns True if the story was published after the given time trigger. False otherwise.

        story (a NewsStory object): the class object from which to search the phrase in.
        """   
        story_time = datetime.replace(story.get_pubdate(), tzinfo=self.tz)
        return story_time > self.time


# COMPOSITE TRIGGERS

class NotTrigger(Trigger):
    def __init__(self, t):
        """
        Initializes a new NotTrigger. 
        
        t : An instance of a Trigger object.
        """
        self.t = t
    
    def evaluate(self, story):
        """
        Returns the inverted boolean result from the given Trigger.

        story (a NewsStory object): the class object from which to search the phrase in.
        """           
        return not self.t.evaluate(story)


class OrTrigger(Trigger):
    def __init__(self, t1, t2):
        """
        Initializes a new OrTrigger. 
        
        t1, t2 : Two unique instances of a Trigger object.
        """        
        self.t1 = t1
        self.t2 = t2
    
    def evaluate(self, story):
        """
        Returns True if one (or both) of the result from the given triggers is True.

        story (a NewsStory object): the class object from which to search the phrase in.
        """            
        return self.t1.evaluate(story) or self.t2.evaluate(story)


class AndTrigger(Trigger):
    def __init__(self, t1, t2):
        """
        Initializes a new AndTrigger. 
        
        t1, t2 : Two unique instances of a Trigger object.
        """           
        self.t1 = t1
        self.t2 = t2
    
    def evaluate(self, story):
        """
        Returns True only if both of the results from the given triggers are True.

        story (a NewsStory object): the class object from which to search the phrase in.
        """       
        return self.t1.evaluate(story) and self.t2.evaluate(story)


#======================
# Filtering
#======================


def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    filtered_stories = []
    for s in stories:
        for trigger in triggerlist:
            if trigger.evaluate(s) == True:
                filtered_stories.append(s)
    return filtered_stories



#======================
# User-Specified Triggers
#======================

def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """

    trigger_file = open(filename, 'r')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)


    # line is the list of lines that you need to parse and for which you need
    # to build triggers
    
    trig_type = {'TITLE': TitleTrigger, 'DESCRIPTION': DescriptionTrigger,
    'AFTER': AfterTrigger, 'BEFORE': BeforeTrigger, 'NOT': NotTrigger, 'AND': AndTrigger,
    'OR': OrTrigger}  # dict that maps trigger keywords and corresponding classes
    
    user_trig = {}  # user defined trigger dict
    added_trig = []  # trigger list 

    for i in lines:
        i = i.split(',')  # split into list to access indices

        if i[1] == 'AND' or i[1] == 'OR':  # if current line is defining AND / OR trigger
            user_trig[i[0]] = trig_type[i[1]](user_trig[i[2]], user_trig[i[3]])


        elif i[0] != 'ADD':  # if current line is defining a trigger besides AND / OR 
            user_trig[i[0]] = trig_type[i[1]](i[2])

        else:  # otherwise get the previously defined triggers and add them to trigger list
            for trig in i[1:]:
                added_trig.append(user_trig[trig])

    return added_trig


SLEEPTIME = 120 #seconds -- how often we poll

def main_thread(master):
    try:
        triggerlist = read_trigger_config('triggers.txt')
        
        # HELPER CODE - you don't need to understand this!
        # Draws the popup window that displays the filtered stories
        # Retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)

        t = "Google Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []
        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:

            print("Polling . . .", end=' ')
            # Get stories from Google's Top Stories RSS news feed
            stories = process("http://news.google.com/news?output=rss")

            # Get stories from Yahoo's Top Stories RSS news feed
            # stories.extend(process("http://news.yahoo.com/rss/topstories")) 
            # Uncommented the above due to error from getting description items in Yahoo.

            stories = filter_stories(stories, triggerlist)

            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)


            print("Sleeping...")
            time.sleep(SLEEPTIME)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()

