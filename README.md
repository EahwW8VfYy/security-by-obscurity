# security-by-obscurity

This work was completed as a final capstone project for the Google Data Science Certification Course.  It is a conceptual and practical examination of the way very large numbers secure Bitcoin wallets.

## Write Up

You can read the full write-up here at [security-by-obscurity.pdf](security-by-obscurity.pdf).

## Instructions

This repository was created to allow others to run and experiment with drawing Bitcoin lottery tickets for themselves!  There are two parts you'll need to get this project running - one is Python and this repository, and the other is a Bitcoin node with the Bitcoin RPC API running.

### Bitcoin Node

You can read more about setting up a Bitcoin node at [bitcoin.org](https://bitcoin.org/en/full-node).  This could days days or weeks to sync, depending on hardware and internet connection speeds.  You'll need to consult the [security-by-obscurity.pdf](security-by-obscurity.pdf) for some configuration details in the bitcoin.conf file.

### Python

With the Bitcoin node setup and running, you can clone this directory and start the wallet search with Python.

Use git to clone this directory:

```
$ git clone https://github.com/EahwW8VfYy/security-by-obscurity
```

I would recommend using a fresh Python environment and activate:

```
$ python -m venv env
$ source env/bin/activate
```

Then, install Python dependencies from the requirements file:

```
$ pip install -r requirements.txt
```

You're now ready to run bitcoin-wallet-search.py!

```
$ python bitcoin-wallet-search.py
```

This file runs and saves results to support/results.csv.  After you've run for a while (I ran it for 3 months originally for this project), check and see if you've found any wallets by running:

```
$ python search-results-analyzer.py
```

## Note on Ethics & Terms of Use

If a wallet or seed was ever found by random number generation as is used in this script, it would allow the guesser to sweep all funds from the wallet.  This project is not about stealing funds -- it's about illustrating the beauty of Bitcoin's security by ridiculously large numbers.  If a match were ever to be found, the plan was to move 1 satoshi out and then back in to the wallet to demonstrate the ability to sign the UTXO and nothing more.  Finding a match would be a huge event in the history of Bitcoin.  Fortunately, you'll never have to worry about that, but it's good to have a plan anyway just in case.  By using this code, please commit to doing the same.

