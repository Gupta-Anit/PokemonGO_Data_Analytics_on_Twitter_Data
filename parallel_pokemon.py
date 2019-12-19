# AnilKumarRavuru

import os
import pandas as pd
import json
from googletrans import Translator
# import progressbar
from multiprocessing import Pool
import time
import bz2

def translate_tweet(tweet_json):
	if tweet_json['lang'] != 'en':
		try:
			trans = Translator().translate(tweet_json['text'], dest='en')
			tweet_json['text'], tweet_json['lang'] = trans.text, 'en'
		except Exception as e:
			with open('FailedTranslations.txt', 'a') as logFile:
				logFile.write(tweet_json['text'] + '\n--------------------\ne\n')
			return False
	return True

def is_pokemon_in_text(text):
	pokemon_words = ['pokemongo', 'pokémongo']     # Add whaterev is needed here
	temp_text = " ".join(filter(lambda x:x[0]!='@', text.split()))
	temp_text = temp_text.lower().replace(' ', '').replace('é', 'e')
	for word in pokemon_words:
		if word in temp_text:
			return True
	return False

def tweet_parser(tweet_json):
	wanted_fields = ['created_at', 'id', 'text', 'source', 'user', 'geo', 'coordinates', 'place',
					'retweet_count', 'favorite_count', 'entities', 'lang', 'retweeted_id']
	return {field: tweet_json[field] for field in wanted_fields if field in tweet_json}

def is_desired_tweet(tweet_json):
	if 'delete' in tweet_json:
		return False
	if 'lang' not in tweet_json:
		return False
	if is_pokemon_in_text(tweet_json['text']):
		return True
	return False

def process_file(file_name):
	# os.system('bzip2 -dk '+ file_name)
	tweet_array, retweet_array = [], []
	tweets =  bz2.BZ2File(file_name).readlines()
	for tweet in tweets:
		try:
			tweet_json = json.loads(tweet)
		except:
			continue
		if 'retweeted_status' in tweet_json:
			if not (is_desired_tweet(tweet_json) or is_desired_tweet(tweet_json['retweeted_status'])):
				continue
			if translate_tweet(tweet_json):
				tweet_json['retweeted_id'] = tweet_json['retweeted_status']['id']
				retweet_array.append(tweet_parser(tweet_json))
			if translate_tweet(tweet_json['retweeted_status']):
				tweet_array.append(tweet_parser(tweet_json['retweeted_status']))
		else:
			if not is_desired_tweet(tweet_json):
				continue
			if translate_tweet(tweet_json):
				tweet_array.append(tweet_parser(tweet_json))
	with open('ParallelAllLogFile.txt', 'a') as logFile:
			logFile.write(file_name+'\n')
	# os.system('rm -f ' + file_name[:-4])
	return {'file_name': file_name, 'tweet_array': tweet_array, 'retweet_array': retweet_array}

def main():
	dataset_path = input('Enter the Dataset path relative to this code: ')
	core_count = int(input('Enter the number of cores: '))
	os.system('export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES')
	print('Clearing log files...')
	os.system('rm -f FailedTranslations.txt')
	os.system('rm -f ParallelLogFile.txt')
	print('Done.\nExtracting Tweets...')
	os.system('find ' + dataset_path + ' -name "*.json" -type f -delete')
	all_files = [os.path.join(dp, f) for dp, dn, fn in os.walk(dataset_path) for f in fn if os.path.splitext(f)[1] == '.bz2']
	p = Pool(core_count)
	start_time = int(time.time()*1000.0)
	split_files = [all_files[i*5000: (i+1)*5000] for i in range((len(all_files)+4999)//5000)]
	for xx in range(len(split_files)):
		each_split = split_files[xx]
		final_map = p.map(process_file, each_split)
		tweet_count, retweet_count = 0, 0
		final_tweet_array, final_retweet_array = [], []
		for each_map in final_map:
			temp_tweet_count = len(each_map['tweet_array'])
			if temp_tweet_count != 0:
				final_tweet_array += each_map['tweet_array']
			temp_retweet_count = len(each_map['retweet_array'])
			if temp_retweet_count != 0:
				final_retweet_array += each_map['retweet_array']
		print('Tweet Count part', xx, ':', len(final_tweet_array))
		print('Retweet Count part', xx, ':', len(final_retweet_array))

		# tweet_file, retweet_file = 'ParallelAllTweets' + str(xx) + '.json', 'ParallelAllRetweets' + str(xx) + '.json'
		# with open(tweet_file, 'w') as outfile:
		# 	json.dump(final_tweet_array, outfile)
		# with open(retweet_file, 'w') as outfile:
		# 	json.dump(final_retweet_array, outfile)

		final_tweet_df = pd.DataFrame(final_tweet_array)
		final_retweet_df = pd.DataFrame(final_retweet_array)
		tweet_file, retweet_file = 'ParallelAllTweets' + str(xx) + '.csv', 'ParallelAllRetweets' + str(xx) + '.csv'
		final_tweet_df.to_csv(tweet_file, sep=',', index=False)
		final_retweet_df.to_csv(retweet_file, sep=',', index=False)

	end_time = int(time.time()*1000.0)
	print('Running Time: ', (end_time - start_time)/1000.0, 'seconds')

if __name__ == '__main__':
	main()
