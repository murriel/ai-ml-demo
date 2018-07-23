import re
from collections import defaultdict, Counter

import Algorithmia
import json

q = "Hello! What keyword would you like to find?"
print q
a = raw_input()
print "your query is " + a
aq = '"' + a + '"'

client = Algorithmia.client(a_api_key)
def pull_tweets():
    input = {
        "query": aq,
        "numTweets": "700",
        "auth": {
            "app_key": t_app_key,
            "app_secret": t_app_secret,
            "oauth_token": t_oauth_token,
            "oauth_token_secret": t_oauth_token_secret
        }
    }

    twitter_algo = client.algo("twitter/RetrieveTweetsWithKeyword/0.1.3")
    result = twitter_algo.pipe(input).result
    tweet_list = [tweets['text'] for tweets in result]
    print 'pull tweets'
    return tweet_list

def process_text():
    """Remove emoticons, numbers etc. and returns list of cleaned tweets."""
    data = pull_tweets()
    regex_remove = "(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^RT|http.+?"
    stripped_text = [
        re.sub(regex_remove, '',
               tweets).strip() for tweets in data
    ]
    print 'process text'
    return '. '.join(stripped_text)

def get_ner():
    """Get named entities from the NER algorithm using clean tweet data."""
    data = process_text()
    ner_algo = client.algo(
        'StanfordNLP/NamedEntityRecognition/0.1.1').set_options(timeout=600)
    ner_result = ner_algo.pipe(data).result
    print 'get ner'
    return ner_result

def group_data():
    data = get_ner()
    default_dict = defaultdict(list)
    for items in data:
        for k, v in items:
            if 'LOCATION' in v or 'ORGANIZATION' in v:
                default_dict[v].append(k)
    ner_list = [{keys: Counter(values)}
            for (keys, values) in default_dict.items()]
    print "test"
    fn = "results-" + a
    f = open(fn,'w')

    json.dump(ner_list, f)
    print ner_list
    return ner_list

if __name__ == '__main__':
    group_data()
print 'complete'
