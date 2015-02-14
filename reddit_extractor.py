import praw
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


	
class SubredditExtractor:

    def __init__(self):
        self.r = praw.Reddit('Idibon PRAW - Reddit comment analysis')
        self.url = None
        self.submissions = None
        pass

    def fit(self, url):
        self.url = url 
        sub_dict = self.r.request_json(self.url)
        self.submissions = sub_dict['data']['children']

        # create article dataframe
        sub_dics = [self.get_article_data(sub) for sub in self.submissions]
        df_subs = pd.DataFrame(sub_dics)

        # build comment dataframe
        df_comments_list = []
        for sub in self.submissions:
            print sub,
            CA = CommentsFromArticle()
            df_temp, comment_list_temp = CA.fit_submission(sub)
            df_comments_list += comment_list_temp

        df_comments = pd.DataFrame(df_comments_list)
        # df_comments = pd.concat(df_comments_list)
        return df_comments, df_subs, df_comments_list, sub_dics






    def get_article_data(self, submission):
        '''
        INPUT: submission object
        OUTPUT: dic w/ :
        - author
        - title
        - url
        - domain
        - ups
        - upvote_ratio
        - num_comments
        - name
        - gilded
        - subreddit
        - subreddit_id
        '''
        d = {}
        d['id'] = submission.__dict__['name']
        field_list = ['author', 'title', 'url', 'domain', 'ups', 'upvote_ratio','num_comments', 'gilded', 'subreddit', 'subreddit_id']
        for i in field_list:
            try:
                d[i] = submission.__dict__[i]
            except:
                d[i] = 'No Data'
        return d





# class ArticleData:
#     '''
#     '''
#     def __init__(self):
#         pass

#     def fit(self, url):

#         pass

class CommentsFromArticle:
    '''
    INPUT: article url and/or id
    OUTPUT: dataframe with following columns
    - id
    - username
    - comment body
    - upvotes
    - downvotes
    - score
    - upvote ratio
    - gilded?
    - root?
    - parent
    - subreddit
    - subreddit_id
    - controversiality
    - 
    '''
    def __init__(self):
        self.r = praw.Reddit('Idibon PRAW - Reddit comment analysis')
        self.url = None
        self.submission = None
        pass

    def fit(self, url):
        self.url = url
        self.submission = self.r.get_submission(self.url)
        df, comment_dics = fit_submission(self.submission)
        return df, comment_dics

    def fit_submission(self, submission):
        self.submission = submission
        comments, more_comments = self.get_comment_objs()
        comment_dics = []
        for comment in comments:
            comment_dics.append(self.build_comment_dict(comment))

        df = pd.DataFrame(comment_dics)
        # df.set_index('id')
        return df, comment_dics


    def get_comment_objs(self):
        # listing = self.r.request_json(url)
        # use below for only root
        # comments, more_comments = self.filter_comments(self.submission.comments)
        # comments, more_comments = self.filter_comments(self.submission._comments_by_id.values())
        comments, more_comments = self.filter_comments(praw.helpers.flatten_tree(self.submission.comments))
        return comments, more_comments

    def build_comment_dict(self, com):
        d = {}
        d['id'] = com.name
        d['praw_id'] = com.id
        field_list = ['parent_id','author', 'body', 'ups', 'downs','score', 'gilded', 'controversiality', 'subreddit', 'subreddit_id']
        for i in field_list:
            try:
                d[i] = com.__dict__[i]
            except:
                d[i] = 'No Data'
        return d


    def filter_comments(self, com_list):
        comments = filter(lambda x: type(x) == praw.objects.Comment, com_list)
        more_comments = filter(lambda x: type(x) == praw.objects.MoreComments, com_list)
        return comments, more_comments



'''
Important notes
- r.get_info(thing_id) --> whatever object the id is
- if parent_id == link_id --> comment is root
- looks like id of parent != childs parent_id --> adds on tx_ to front of id 
where x is number, parent_id == name!

'''





