import praw
import requests
#from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import csv
import os
#import psycopg2
#import matplotlib.pyplot as plt


    
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
            #print sub,
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
        # comments, more_comments = self.filter_comments(praw.helpers.flatten_tree(praw.helpers.flatten_tree(self.submission.comments)))
        return comments, more_comments

    def build_comment_dict(self, com):
        d = {}
        d['id'] = com.name
        try: 
            d['author_name'] = com.author.name
        except:
            d['author_name'] = 'No Data'
        # d['author_id'] = com.author.fullname
        d['praw_id'] = com.id
        field_list = ['parent_id', 'body', 'ups', 'downs','score', 'gilded', 'controversiality', 'subreddit', 'subreddit_id']
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

class SQL_Queries:
    def __init__(self):
        # self.conn = psycopg2.connect(dbname='msd', user='postgres', host='/tmp') # for local machine
        self.conn = psycopg2.connect(dbname='reddit_toxicity', user='ubuntu', password = 'bllby2088',  host='/var/run/postgresql/') # for server
        self.c = self.conn.cursor()

    def insert_dataframe(self, df, table):
        # ensuring unique values in index
        df = df.reset_index().drop('index',axis = 1)

        for i in range(len(df)):
            # could potentially do this all in one command instead of looping
            vals = tuple(df.ix[i].values)
            vals_new = vals
            for idx, i in enumerate(vals):
                try:
                    i_s = str(i)
                    vals_new[idx] = i_s.encode('ascii','ignore')
                except:
                    pass
            try:
                self.c.execute(
                        '''
                        INSERT INTO %s VALUES %s;
                        ''' % (str(table), str(vals_new))
                        )
            except:
                print 'error'
            #print 'INSERT INTO %s VALUES %s;' % (str(table), str(tuple(df.ix[i].values)))

        self.conn.commit()

    def insert_row(self, dic):
        pass


def list_dics_tocsv(l, filename):
    toCSV = l
    keys = toCSV[0].keys()
    with open(filename + '.csv', 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(toCSV)

def fix_encoding_listdics(listdics):
    new_list = []
    for i in listdics:
        new_d = {}
        for key in i:
            if type(i[key]) == unicode:
                new_d[key] = i[key].encode('ascii','ignore')
            else:
                new_d[key] = str(i[key])


        new_list.append(new_d)
    return new_list


def get_subreddit_df(subreddit_list):
    subreddit_dics = []
    SE_ = SubredditExtractor()
    for i in subreddit_list:
        d = {}
        d['name'] = i
        d['subscribers'] = SE_.r.get_subreddit(i).subscribers
        subreddit_dics.append(d)
    return pd.DataFrame(subreddit_dics)

def get_file_names(path):
    all_files = os.listdir(path)
    comment_files = []
    sub_files = []
    for i in all_files:
        l = i.split('_')[1]
        if l[0] == 'c':
            comment_files.append(i)
        else:
            sub_files.append(i)

    return comment_files, sub_files

def combine_files(file_list, filename):
    fout = open(filename, "a")
    for line in open(file_list[0]):
        fout.write(line)
    for i in file_list[1:]:
        f = open(i)
        f.next()
        for line in f:
            fout.write(line)
        f.close()
    fout.close()




'''
Important notes
- r.get_info(thing_id) --> whatever object the id is
- if parent_id == link_id --> comment is root
- looks like id of parent != childs parent_id --> adds on tx_ to front of id 
where x is number, parent_id == name!

'''

if __name__ == '__main__':

    # subreddits = [u'/r/parenting',
    #  u'/r/AskReddit',
    #  u'/r/Parenting',
    #  u'/r/funny',
    #  u'/r/gamegrumps',
    #  u'/r/fffffffuuuuuuuuuuuu',
    #  u'/r/goats',
    #  u'/r/getmotivated',
    #  u'/r/all',
    #  u'/r/worldnews',
    #  u'/r/justneckbeardthings',
    #  u'/r/chivalrygame.',
    #  u'/r/amish',
    #  u'/r/relationships',
    #  u'/r/justiceporn',
    #  u'/r/serialpodcast',
    #  u'/r/music',
    #  u'/r/minimalism',
    #  u'/r/eurovision',
    #  u'/r/MakeupAddiction',
    #  u'/r/muacirclejerk',
    #  u'/r/zen',
    #  u'/r/doctorwho',
    #  u'/r/pics',
    #  u'/r/photoshopbattles',
    #  u'/r/redditgetsdrawn',
    #  u'/r/ArtistLounge',
    #  u'/r/AskReddit',
    #  u'/r/ICanDrawThat',
    #  u'/r/food',
    #  u'/r/shittyfoodporn',
    #  u'/r/funny',
    #  u'/r/pics',
    #  u'/r/leagueoflegends',
    #  u'/r/leagueoflegends',
    #  u'/r/motorcycles',
    #  u'/r/cringepics',
    #  u'/r/relationships',
    #  u'/r/opieandanthony',
    #  u'/r/firstworldanarchists']

    # subreddits = ['/r/ArtistLounge',
    # '/r/chivalrygame',
    # '/r/MakeupAddiction',
    # '/r/muacirclejerk'
    # ]

    # subreddits = [u'/r/todayilearned', u'/r/science', u'/r/IAmA', u'/r/videos',
    #    u'/r/gaming', u'/r/movies', u'/r/Music', u'/r/aww',
    #    u'/r/technology', u'/r/news', u'/r/gifs', u'/r/bestof',
    #    u'/r/askscience', u'/r/explainlikeimfive', u'/r/WTF',
    #    u'/r/EarthPorn', u'/r/AdviceAnimals', u'/r/books', u'/r/television',
    #    u'/r/politics', u'/r/LifeProTips', u'/r/sports',
    #    u'/r/mildlyinteresting', u'/r/DIY', u'/r/Fitness', u'/r/space',
    #    u'/r/Showerthoughts', u'/r/Jokes', u'/r/tifu',
    #    u'/r/InternetIsBeautiful', u'/r/GetMotivated', u'/r/nottheonion',
    #    u'/r/gadgets', u'/r/dataisbeautiful', u'/r/Futurology',
    #    u'/r/Documentaries', u'/r/listentothis', u'/r/personalfinance',
    #    u'/r/nosleep', u'/r/Art', u'/r/creepy', u'/r/OldSchoolCool',
    #    u'/r/UpliftingNews', u'/r/WritingPrompts', u'/r/TwoXChromosomes',
    #    u'/r/atheism', u'/r/woahdude', u'/r/trees', u'/r/4chan',
    #    u'/r/programming']

    # subreddits = [u'/r/programming', u'/r/Games', u'/r/sex', u'/r/Android',
    #    u'/r/reactiongifs', u'/r/gameofthrones', u'/r/malefashionadvice',
    #    u'/r/Frugal', u'/r/YouShouldKnow', u'/r/Minecraft', u'/r/pokemon',
    #    u'/r/HistoryPorn', u'/r/comics', u'/r/AskHistorians',
    #    u'/r/interestingasfuck', u'/r/nfl', u'/r/tattoos',
    #    u'/r/JusticePorn', u'/r/FoodPorn', u'/r/facepalm', u'/r/Unexpected',
    #    u'/r/wheredidthesodago', u'/r/wallpapers', u'/r/TrueReddit',
    #    u'/r/pcmasterrace', u'/r/soccer', u'/r/cringe',
    #    u'/r/gentlemanboners', u'/r/GameDeals', u'/r/conspiracy',
    #    u'/r/geek', u'/r/skyrim', u'/r/buildapc', u'/r/oddlysatisfying',
    #    u'/r/AbandonedPorn', u'/r/loseit', u'/r/hiphopheads', u'/r/cats',
    #    u'/r/nba', u'/r/europe', u'/r/anime', u'/r/apple', u'/r/FiftyFifty',
    #    u'/r/RoomPorn', u'/r/talesfromtechsupport', u'/r/StarWars',
    #    u'/r/circlejerk', u'/r/shittyaskscience', u'/r/MakeupAddiction',
    #    u'/r/wow', u'/r/breakingbad']

    # subreddits = ['/r/gaming',
    # '/r/smashbros',
    # '/r/sex',
    # '/r/soccer',
    # '/r/blackpeopletwitter',
    # '/r/pcmasterrace',
    # '/r/ImGoingToHellForThis',
    # '/r/atheism',
    # '/r/shitredditsays',
    # '/r/theredpill',
    # '/r/headphones',
    # ]

    subreddits = ['/r/sex',
 '/r/guns',
 '/r/pics',
 '/r/whatisthisthing',
 '/r/pettyrevenge',
 '/r/baconreader',
 '/r/DIY',
 '/r/keto',
 '/r/buildapc',
 '/r/web_design',
 '/r/FanTheories',
 '/r/listentothis',
 '/r/oddlysatisfying',
 '/r/Whatcouldgowrong',
 '/r/TrollXChromosomes',
 '/r/fffffffuuuuuuuuuuuu',
 '/r/hearthstone',
 '/r/quityourbullshit',
 '/r/talesfromtechsupport',
 '/r/ImGoingToHellForThis',
 '/r/AdviceAnimals',
 '/r/aww',
 '/r/HistoryPorn',
 '/r/breakingbad',
 '/r/nonononoyes',
 '/r/OldSchoolCool',
 '/r/itookapicture',
 '/r/SubredditDrama',
 '/r/futurama',
 u'/r/goats',
 '/r/leagueoflegends',
 '/r/environment',
 '/r/movies',
 u'/r/chivalrygame.',
 '/r/GetMotivated',
 '/r/reactiongifs',
 '/r/cringepics',
 '/r/GameDeals',
 u'/r/ICanDrawThat',
 '/r/europe',
 '/r/offbeat',
 '/r/Android',
 '/r/asoiaf',
 '/r/AnimalsBeingJerks',
 '/r/youdontsurf',
 '/r/sports',
 '/r/bicycling',
 '/r/cars',
 '/r/UnexpectedThugLife',
 '/r/geek',
 '/r/worldnews',
 '/r/bestof',
 '/r/Cooking',
 '/r/TrueReddit',
 '/r/CityPorn',
 '/r/outside',
 '/r/programming',
 '/r/Showerthoughts',
 '/r/NoFap',
 '/r/YouShouldKnow',
 '/r/food',
 u'/r/opieandanthony',
 u'/r/music',
 '/r/EarthPorn',
 '/r/NetflixBestOf',
 '/r/writing',
 u'/r/parenting',
 '/r/Drugs',
 u'/r/getmotivated',
 '/r/lifehacks',
 '/r/math',
 '/r/politics',
 '/r/shitredditsays',
 '/r/Games',
 '/r/space',
 '/r/chemicalreactiongifs',
 '/r/travel',
 '/r/wow',
 '/r/montageparodies',
 '/r/OutOfTheLoop',
 '/r/funny',
 '/r/humor',
 '/r/firstworldproblems',
 u'/r/muacirclejerk',
 '/r/Fallout',
 '/r/science',
 '/r/interestingasfuck',
 '/r/worldcup',
 '/r/MapPorn',
 '/r/cringe',
 '/r/investing',
 '/r/photography',
 '/r/TheLastAirbender',
 '/r/gameofthrones',
 '/r/4chan',
 '/r/circlejerk',
 '/r/loseit',
 '/r/askscience',
 '/r/worldpolitics',
 '/r/LifeProTips',
 '/r/comicbooks',
 '/r/minimalism',
 '/r/malefashionadvice',
 u'/r/redditgetsdrawn',
 '/r/netsec',
 u'/r/all',
 '/r/southpark',
 '/r/nosleep',
 '/r/progresspics',
 '/r/explainlikeimfive',
 '/r/conspiracy',
 '/r/adventuretime',
 '/r/tipofmytongue',
 '/r/dataisbeautiful',
 '/r/gadgets',
 '/r/Unexpected',
 '/r/nfl',
 '/r/AskReddit',
 '/r/BuyItForLife',
 '/r/news',
 '/r/doctorwho',
 '/r/bodyweightfitness',
 '/r/FiftyFifty',
 '/r/learnprogramming',
 '/r/Steam',
 '/r/headphones',
 '/r/howtonotgiveafuck',
 '/r/cats',
 '/r/Art',
 '/r/MakeupAddiction',
 '/r/motorcycles',
 '/r/gentlemanboners',
 '/r/TalesFromRetail',
 '/r/standupshots',
 '/r/freebies',
 '/r/thatHappened',
 '/r/AskWomen',
 '/r/UpliftingNews',
 '/r/everymanshouldknow',
 '/r/truegaming',
 '/r/blackpeopletwitter',
 '/r/self',
 '/r/gifs',
 '/r/IAmA',
 '/r/apple',
 '/r/spaceporn',
 '/r/JusticePorn',
 '/r/AlienBlue',
 '/r/tf2',
 '/r/AskHistorians',
 '/r/Music',
 '/r/nba',
 '/r/frugalmalefashion',
 '/r/gamedev',
 u'/r/eurovision',
 u'/r/serialpodcast',
 '/r/CrazyIdeas',
 u'/r/amish',
 '/r/theredpill',
 '/r/getdisciplined',
 '/r/personalfinance',
 '/r/pcmasterrace',
 '/r/woahdude',
 u'/r/shittyfoodporn',
 '/r/videos',
 '/r/iphone',
 '/r/relationships',
 '/r/DestinyTheGame',
 '/r/facepalm',
 '/r/todayilearned',
 '/r/mildlyinteresting',
 '/r/wallpaper',
 '/r/MURICA',
 '/r/shutupandtakemymoney',
 '/r/skyrim',
 u'/r/gamegrumps',
 '/r/trees',
 '/r/InternetIsBeautiful',
 '/r/Documentaries',
 '/r/CrappyDesign',
 '/r/hockey',
 '/r/Jokes',
 '/r/offmychest',
 '/r/firstworldanarchists',
 '/r/howto',
 '/r/SkincareAddiction',
 '/r/holdmybeer',
 '/r/community',
 '/r/WTF',
 '/r/shittyaskscience',
 '/r/nottheonion',
 '/r/Bitcoin',
 '/r/gaming',
 '/r/Fitness',
 '/r/zelda',
 '/r/running',
 '/r/TwoXChromosomes',
 '/r/youtubehaiku',
 '/r/tifu',
 '/r/LearnUselessTalents',
 u'/r/ArtistLounge',
 '/r/dadjokes',
 '/r/AbandonedPorn',
 '/r/creepy',
 '/r/soccer',
 '/r/announcements',
 '/r/PerfectTiming',
 '/r/books',
 '/r/scifi',
 u'/r/zen',
 '/r/seduction',
 '/r/technology',
 '/r/business',
 '/r/DoesAnybodyElse',
 '/r/hiphopheads',
 '/r/recipes',
 '/r/history',
 '/r/PS4',
 '/r/Astronomy',
 '/r/StarWars',
 '/r/slowcooking',
 '/r/smashbros',
 '/r/polandball',
 '/r/philosophy',
 '/r/pokemon',
 '/r/Economics',
 '/r/behindthegifs',
 '/r/WritingPrompts',
 '/r/RoomPorn',
 '/r/Libertarian',
 '/r/wallpapers',
 '/r/psychology',
 '/r/linux',
 u'/r/Parenting',
 '/r/comics',
 '/r/AskMen',
 '/r/starcraft',
 '/r/fullmoviesonyoutube',
 '/r/LadyBoners',
 '/r/Futurology',
 '/r/electronicmusic',
 '/r/television',
 '/r/GlobalOffensive',
 '/r/atheism',
 u'/r/justneckbeardthings',
 '/r/photoshopbattles',
 '/r/FoodPorn',
 '/r/wikipedia',
 '/r/creepyPMs',
 '/r/wheredidthesodago',
 '/r/CFB',
 '/r/canada',
 '/r/anime',
 '/r/Frugal',
 '/r/TumblrInAction',
 '/r/LucidDreaming',
 '/r/Celebs',
 '/r/chivalrygame',
 '/r/Foodforthought',
 u'/r/justiceporn',
 '/r/IWantToLearn',
 '/r/harrypotter',
 '/r/Guitar',
 '/r/changemyview',
 '/r/tattoos',
 '/r/thewalkingdead',
 '/r/EatCheapAndHealthy',
 '/r/DotA2',
 '/r/entertainment',
 '/r/BlackPeopleTwitter',
 '/r/battlestations',
 '/r/GrandTheftAutoV',
 '/r/mildlyinfuriating',
 '/r/Minecraft',
 '/r/QuotesPorn',
 '/r/beer']


    # SQ = SQL_Queries()
    # SE = SubredditExtractor()
    # url = 'http://www.reddit.com' + subreddits[0]
    # df_comments, df_subs, df_comments_list, sub_dics = SE.fit(url)
    # SQ.insert_dataframe(df_comments, 'comments_text')

    SE = SubredditExtractor()
    for subreddit in subreddits:
        print subreddit
        try: 
            url = 'http://www.reddit.com' + subreddit
            df_comments, df_subs, df_comments_list, sub_dics = SE.fit(url)
            # print 'subdics ', sub_dics[:2]
            new_coms_list = fix_encoding_listdics(df_comments_list)
            list_dics_tocsv(new_coms_list, subreddit[3:] + '_comments')
            new_subs_list = fix_encoding_listdics(sub_dics)
            list_dics_tocsv(new_subs_list, subreddit[3:] + '_subs')
        except:
            print 'error: ', subreddit

    # df_comments.head().to_csv(open(subreddits[0][3:] + '_comments.csv'))
    # df_subs.head().to_csv(open(subreddits[0][3:] + '_comments.csv'))



