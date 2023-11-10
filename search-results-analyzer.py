# analyze the results.csv generated from bitcoin-wallet-search.py

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# load results.csv to dataframe
df = pd.read_csv('support/results.csv', usecols=['mnemonics','total_btc','processing_time_minutes','num_addresses','timestamp'])

# add column, calculation of addresses per min to approximate speed of request
df['addresses_per_minute'] = df['num_addresses'] / df['processing_time_minutes']

# add column, calculation of key, imputed by # of addresses
# we actually count them below
df['number_of_keys'] = (df['num_addresses']) / 30

# print all records
print (f'\n---------------------\nAll Searches Dataframe\n---------------------\n')
print (df)

# look for any duplicated mnemonics, highly unlikely!
# break out ';' delimited list of mnemonics into new dataframe
print (f'\n---------------------\nAny Duplicated Mnemonics?\n---------------------\n')
mnemonics = df.assign(mnemonics=df['mnemonics'].str.split(';')).explode('mnemonics')
# print ('mnemonics array:')
# print (mnemonics)

# there are some blank records, remove blank mnemonics
# otherwise blanks count as 'duplicates'
blank_mnemonics = mnemonics[mnemonics["mnemonics"].str.strip()==''].index
mnemonics.drop(blank_mnemonics, inplace=True)

# now check for duplicated mnemonics
mnemonics_duplicated = mnemonics[mnemonics.duplicated(subset = ['mnemonics'], keep=False)]
if (len(mnemonics_duplicated)):
	print ('duplicate mnemonics found - you may have won the lottery!')
else:
	print (f'no duplicated mnemonics were found in {len(mnemonics):,} mnemonics')

# check for non-zero total_btc balance
print (f'\n---------------------\nChecking non-zero total_btc balances\n(indicating a wallet has been found):\n---------------------\n')
df_address_hits = df[(df['total_btc'] != 0)]
if df_address_hits.empty:
	print ("No wallets have been found :(")
else:
	print ("OK, you might want to check these :)")
	print (df_address_hits)

# summary stats
print (f'\n---------------------\nSummary Stats\n---------------------\n')
print (f'total number of addresses searched: {int(df["num_addresses"].sum() - len(df)):,}')
print (f'total number of mnemonics searched: {len(mnemonics):,}')
print (f'in total time: {int(df["processing_time_minutes"].sum()/60/24)} days')
print (f'mean processing time: {int(df["processing_time_minutes"].mean())} minutes per Bitcoin RPC API request')

# distribution of bip39 words from mnemonics: should be distributed pretty evenly!
# break out mnemonics into individual words!
print (f'\n---------------------\nBIP39 Word Analysis\n---------------------\n')
bip39words = mnemonics['mnemonics'].str.split(' ').explode('mnemonics')
print (bip39words)

# plot bip39 words on horizontal bar chart for visual in write-up
plt.style.use('support/tufte-bar.mplstyle')
bip39plt = bip39words.value_counts().sort_index(ascending=True).plot.barh()
plt.gcf().set_size_inches(3, 10) # set size
plt.gcf().subplots_adjust(left=0.5) #labels
for i, t in enumerate(bip39plt.get_yticklabels()): # hide every nth label for space
    if (i % 64) != 0:
        t.set_visible(False)
plt.savefig('support/bip39words-skinny.png', transparent=True)
print ('\nsaved bip39words bar chart to support/')

# determine statistical randomness of words
# ouput series to csv for testing
# https://github.com/stevenang/randomness_testsuite/blob/master/Main.py
# saved in rand-test-results.txt
bip39words.value_counts().sort_index(ascending=True).to_csv('support/bip39words.csv', index=False)
print ('saved bip39words word count csv to support/\n')

