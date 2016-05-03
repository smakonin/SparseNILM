# The piNILM Project
Copyright (c) 2016 by Stephen Makonin

Last modified: May 3, 2016.

This project allows SparseNILM to run on a Raspberry Pi 2B+ and 3 and disaggregate your smart meter reading using a [Rainforest EMU2](https://rainforestautomation.com/rfa-z105-2-emu-2/) in real-time.

## RPi Setup & Config

I recommend flashing the SD card with Raspbian JESSIE LITE. Here are the steps to get SparseNILM running on your RPi:

1. Once you boot the RPi for the first time run `sudo raspi-config` and reboot.
2. Setup wifi using `sudo wpa_cli` and use the following commands:
	* `list_networks`
	* `add_network`
	* `set_network 0 ssid "<replace with the ssid>"`
	* `set_network 0 psk "<replace with the psk>"`
	* `enable_network 0`
	* `reconnect`
	* `list_networks`
	* `status`
	* `save_config`
	* `quit`
3. Apply general OS updates:
	* `sudo apt update`
	* `sudo apt upgrade`
	* `sudo apt install vim` (optional)
4. SparseNILM uses Python 3.x, so remove Python 2.7 and install 3.x and needed modules/libraries:
	* `sudo apt remove python2.7`
	* `sudo apt-get autoremove`
	* `sudo apt install python3 python3-rpi.gpio python3-serial python3-pip python3-pandas`
5. Finally, we need to setup git to download SparseNILM from GitHub:
	* `sudo apt install git`
	* `git config --global user.name "<insert your name here>"`
	* `git config --global user.email your_email@example.com`
	* `git clone https://github.com/smakonin/SparseNILM.git`
6. Optionally if you have a GitHub account run:
	* `ssh-keygen -t rsa -b 4096 -C "your_email@example.com”`
	* THEN copy and paste the key into GitHub account settings

## Building a Model for SparseNILM

First you must build a model using the `train_SSHMM.py`. Create a dataset file in `~/SparseNILM/datasets’ with the prefix “BCH”; (e.g., BCH_datafile1.csv). The dataset file should be *comma seperated value* or CSV with he first line having header info. For example:

```
TimeStamp,Mains,Load1,Load2,…
1333263600,60.7,0,0.7,…
1333263660,60.7,0,0.9,…
1333263720,60.6,0,0.9,…
1333263780,44.7,0,0.9,0.1,39.1,0,0,0,0,0.4,1.1,1.3,0.5,0.2,0,0.2,0,0.5,0.1,0.1
```

The columns named `Load1` and `Load2` can be names of your choosing — to identify/name each load. Do not use spaces in the names. 

For creating a dataset, it is recommented that you create the CSV file on your local computer and then secure copy that file to the RPi. For exmaple, `scp BCH_datafile1.csv pi@192.168.1.x:./SparseNILM/datasets/`

Here is an example of how to create a model:

```
cd ~/SparseNILM
./train_SSHMM.py bch1 BCH_datafile1 1 24000 denoised 8 1 l1+l2,l3
```

In the above example we create a model named `bch1` from the dataset called `BCH_datafile1` with a precision of 1, max observed value of 24000W, only using the loads we specify, each loads having a max of 8 states with only 1 testing fold. We are building a model that disaggregates 2 appliances. We combine the `l1` and `l2` columns in the dataset because it is the same appliance that run on both L1 and L2. Appliance `l3` is only on one leg. We use a single fold because we are not testing against another dataset. We are building a model to disaggregate using live data from the smart meter via an EMU2.

Here is a description of command-line parameters for `train_SSHMM.py`:

```
USAGE: ./train_SSHMM.py [modeldb] [dataset] [precision] [max obs] [denoised] [max states] [folds] [ids]

       [modeldb]    - file name of model (omit file ext).
       [dataset]    - file name of dataset to use (omit file ext).
       [precision]  - number; e.g. 10 would convert A to dA.
       [max obs]    - The max observed value, e.g. 200.1 A.
       [denoised]   - denoised aggregate reads, else noisy.
       [max states] - max number of states a each load can have.
       [folds]      - number usually set to 10, 1 means data same for train/test.
       [ids]        - e.g. CDE,FGE(,...) -- case sensitive!
```


## Running SparseNILM Live

Once a model is build we run SparseNILM live. For example:

```
cd ~/SparseNILM
./disagg_EMU2.py bch1 1 W SparseViterbi /dev/ttyACM0
```

Here is a description of command-line parameters for `disagg_EMU2.py`:

```
USAGE: ./disagg_EMU2.py [modeldb] [precision] [measure] [algo name] [device]

       [modeldb]       - file name of model (omit file ext).
       [precision]     - number; e.g. 10 would convert A to dA.
       [measure]       - the measurement, e.g. A for current
       [algo name]     - specifiy the disaggregation algorithm to use.
       [device]        - usually /dev/ttyACM0 in a RPi.
```
