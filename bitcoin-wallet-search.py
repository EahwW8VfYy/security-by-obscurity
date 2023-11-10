# Security By Obscurity: A Google Data Science Capstone Project: Futile Bitcoin Wallet Searching
# Illustrate the (in)feasibility of generating a random seeds,
# addresses from those seeds, and checking the Bitcoin blockchain for balances on those addresses.

# References
# https://github.com/meherett/python-hdwallet
# https://developer.bitcoin.org/reference/rpc/
# https://mempool.space/address/bc1pufqpggdegatz8uwzeqzukxcaymfd5uln965uuejpxwctmk2txe8sxspadz (picked at random for test address)
# https://bitcoin.stackexchange.com/questions/117554/what-does-enabling-coinstatsindex-in-my-bitcoin-conf-file-do-for-my-node (coinstatsindex=1)
# https://github.com/bitcoin-abe/bitcoin-abe (heavy-duty btc-core -> db) maybe for Part II

# Requirements: requirements.txt

# Libraries
from hdwallet import HDWallet
from hdwallet.utils import generate_entropy
from hdwallet.symbols import BTC as SYMBOL
from typing import Optional

import json
import requests
import time
import pprint




########################
## hdwallet generator ##
########################
# return a new bitcoin hdwallet object (128-bit)

def newWallet():

	# Choose strength 128, 160, 192, 224 or 256
	STRENGTH: int = 128  # Default is 128
	# Choose language english, french, italian, spanish, chinese_simplified, chinese_traditional, japanese or korean
	LANGUAGE: str = "english"  # Default is english
	# Generate new entropy hex string
	ENTROPY: str = generate_entropy(strength=STRENGTH)
	# Secret passphrase for mnemonic
	PASSPHRASE: Optional[str] = None  # "meherett"

	# Initialize Bitcoin mainnet HDWallet
	hdwallet: HDWallet = HDWallet(symbol=SYMBOL, use_default_path=False)
	# Get Bitcoin HDWallet from entropy
	hdwallet.from_entropy(
		entropy=ENTROPY, language=LANGUAGE, passphrase=PASSPHRASE
	)

	# Derivation from path
	hdwallet.from_path("m/44'/0'/0'/0/0")


	# Print all Bitcoin HDWallet information's
	#print(json.dumps(hdwallet.dumps(), indent=4, ensure_ascii=False))

	# return a dict of lists of first x of each address type from hdwallet
	return hdwallet




##########################
## rpc settings & setup ##
##########################
# RPC setup and host class

rpcport = 8332
rpcuser = 'bitcoin'
rpcpassword = 'bitcoin'
rpcip = '127.0.0.1'
serverURL = 'http://' + str(rpcuser) + ':' + str(rpcpassword)+ '@' + str(rpcip)+":" + str(rpcport)

# This catches errors in the conection that might be encountered
class RPCHost(object):
	def __init__(self, url):
		self._session = requests.Session()
		self._url = url
		self._headers = {'content-type': 'application/json'}
	def call(self, rpcMethod, *params):
		payload = json.dumps({"method": rpcMethod, "params": list(params), "jsonrpc": "2.0"})
		tries = 5
		hadConnectionFailures = False
		while True:
			try:
				response = self._session.post(self._url, headers=self._headers, data=payload)
			except requests.exceptions.ConnectionError:
				tries -= 1
				if tries == 0:
					raise Exception('Failed to connect for remote procedure call.')
				hadFailedConnections = True
				print("Couldn't connect for remote procedure call, will sleep for five seconds and then try again ({} more tries)".format(tries))
				time.sleep(10)
			else:
				if hadConnectionFailures:
					print('Connected for remote procedure call after retry.')
				break
		if not response.status_code in (200, 500):
			raise Exception('RPC connection failure: ' + str(response.status_code) + ' ' + response.reason)
		responseJSON = response.json()
		if 'error' in responseJSON and responseJSON['error'] != None:
			raise Exception('Error in RPC call: ' + str(responseJSON['error']))
		return responseJSON['result']

# RPC call host
host = RPCHost(serverURL)




###################################
## address lookup w btc-core RPC ##
###################################

# clear current call if exists
results = host.call('scantxoutset', 'abort')

# num of seeds to produce, target 649500 due to RPC request size
# targeting 649500 total addresses (21650 seeds * 6 address types * first 5 wallets each)
# 650k was the upper bound for the bitcoin core rpc api request for me, your results may vary
num_seeds = 21650

# search loop
while True:

	# test RPC conn / get latest block
	latest_block = host.call('getblockcount')
	print (f'\n---------------------\nlatest block = {latest_block}\n---------------------\n')

	# init start time
	start = time.time()
	print (f'starting time ({time.ctime()})...\n')

	# hdwallets storage vars
	hdwallets = []
	hdwallets_json = []
	hdwallets_addresses = []

	# save num_seeds hdwallets in hdwallets list
	print (f'creating wallets & deriving addresses...\n')
	for x in range(num_seeds):

		# generate new hdwallet
		hdwallets.append (newWallet())

	# for each hdwallet, build addresses
	for hdwallet in hdwallets:

		# get hdwallet_json
		wallet_json = hdwallet.dumps()
		hdwallets_json.append(wallet_json)
		address_types = wallet_json['addresses']

		# get hdwallet addresses
		for a in address_types:
			addresses = [] #temp list
			for x in range (5):
				address_call = "hdwallet." + a + "_address()"
				hdwallet.clean_derivation() #remove derivation path for reset
				hdwallet.from_path("m/44'/0'/0'/0/" + str(x)) #increment hd path
				addresses.append (eval(address_call))
			hdwallets_addresses.append(addresses) #add list of addresses to address type key

	#testing
	#pprint.pprint (hdwallets)
	#print('\n\n')
	#pprint.pprint (hdwallets_json)
	#print('\n\n')
	#pprint.pprint (hdwallets_addresses)

	# join mnemonics
	mnemonics = str(';'.join([each['mnemonic'] for each in hdwallets_json]))
	#print (f'mnemonics = {mnemonics}')

	# num consolidated wallets
	print (f'{len(hdwallets)} consolidated wallets...\n')

	# # initialize results.csv
	# f=open(f"results.csv","a+")
	# f.write('mnemonics,total_btc,processing_time_minutes,num_addresses,addresses,timestamp\n')
	# f.close()

	#addresses_all master list
	addresses_all = [x for y in hdwallets_addresses for x in y]

	#print all addresses
	print (f'{len(addresses_all)} consolidated addresses...\n')
	#pprint.pprint (addresses_all)

	#starting rpc search
	print (f'searching btc-core for addresses...\n')

	# test results / real call to btc-core RPC
	results = host.call('scantxoutset', 'start', [f'addr({address})' for address in addresses_all])

	# end time, time elapsed
	end = time.time()
	minutes = (end-start)/60
	print (f'{len(addresses_all)} addresses searched in: {minutes} minutes...\n')

	# save results to file
	f=open(f"support/results.csv","a+")
	f.write(str(mnemonics)+','+str(results['total_amount'])+','+str(minutes)+','+str(len(addresses_all))+','+str(' '.join(addresses_all))+','+time.ctime()+'\n')
	f.close()
	print ('results saved to csv...\n')

	# results
	print (f"wallet balance total = {results['total_amount']}")
	if (results['total_amount'] == 0):
		print (f'no wallets found\n')
	else:
		print (f'NON-ZERO BALANCE - WALLET(S) FOUND!!!\n')
		print (f"addresses = {str(' '.join(addresses_all))}\n\nmnemonics: {mnemonics}\n")
		exit ()
