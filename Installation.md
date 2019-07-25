# Info
Commands for buliding tesseract, tesstrain tools from source, and further training tesseract at Ubuntu 16.04 on AWS, Jingjing LIN, 2019-07

## Useful links
https://github.com/tesseract-ocr // contains everything about tesseract (different langdata, tessdata etc.)

https://github.com/tesseract-ocr/tesseract // the source for tesseract, has information about how to use or install tesseract etc.

https://github.com/tesseract-ocr/tesseract/wiki/Compiling // about how to build tesseract from source, as of 2017-06, only tesseract built from source support whitelist, otherwise whitelist is not supported

https://github.com/tesseract-ocr/tesseract/wiki/ImproveQuality // about how to improve image quality for better tesseract result, imagemagick is a very powerful image processing engine, python also provides several very good image processing packages, like opencv-python, Pillow. The main things to do are resizing, contrast enhancement, and image dewarp

https://github.com/tesseract-ocr/tesseract/wiki/TrainingTesseract-4.00 // about how to train tesseract to better fit our purpose

https://github.com/tesseract-ocr/tesseract/wiki/AddOns // AddOns for tesseract, has different wrapper for different programming languages

https://groups.google.com/forum/#!forum/tesseract-ocr // Google group where you can ask questions when having problem, usually there will be people reply to you within one day

## Running instructions
tesseract imagepath outputfilepath(without file extension) -l chi_sim --psm 6 configs

// running tesseract from terminal:

Example:

tesseract ~/tesseract/lab_test_result/test.jpeg ~/tesseract/blood_test/test -l chi_sim --psm 6 -c preserve_interword_spaces=1 whitelist_blood.txt

whitelist_blood.txt should be in folder /usr/local/share/tessdata/configs, can also replace it with other configs in the folder, like 'box', 'tsv', 'pdf' to get box/tsv/pdf output from tesseract; 

'-c preserve_interword_spaces=1' is for changing tesseract default settings, the parameters that can be set can be viewed with 'tesseract --print-parameters' (there's a hundreds of them, useful ones are 'preserve_interword_spaces', 'tessedit_write_images'); 

--psm 6 is for setting the segmentation method, view it with 'tesseract --help-extra';

'-l chi_sim' is for setting language to chi_sim, the available languages can be viewd with 'tesseract --list-langs'

/usr/local/share/tessdata

// tessdata folder, need to download extra traineddata to this folder for tesseract to work with other languages than eng

/usr/local/share/tessdata/configs/

// location of configs for tesseract, for running tesseract from terminal, need to put your whitelist here, when using tesserocr, there's no need to add config files here though


## Installation
### Install Dependencies
sudo apt-get install g++ # or clang++ (presumably) // I chose g++

sudo apt-get install autoconf automake libtool

sudo apt-get install pkg-config

sudo apt-get install libpng-dev

sudo apt-get install libjpeg8-dev

sudo apt-get install libtiff5-dev

sudo apt-get install zlib1g-dev

for building training tools:

sudo apt-get install libicu-dev

sudo apt-get install libpango1.0-dev

sudo apt-get install libcairo2-dev

sudo apt-get install libleptonica-dev // Error: Unable to locate package libleptonica-dev

Installed Leptonica1.78.0 manually following http://www.leptonica.org/source/README.html#BUILDING

### Install Tesseract
(I accidentally build tesseract inside leptonica-1.78.0 folder, need to cd to root when build tesseract to avoid this)
After installing the dependencies above, install tesseract with training:

git clone https://github.com/tesseract-ocr/tesseract.git

cd tesseract

./autogen.sh

./configure

make

sudo make install

sudo ldconfig

make training

sudo make training-install

#### Install extra tessdata
(have to do this for chi_sim to work)

git clone https://github.com/tesseract-ocr/tessdata.git // this will clone all the traineddata from github, there should be a better way to just download one traineddata

then move the necessary .traineddata(like chi_sim.traineddata) to /usr/local/share/tessdata

#### Install ScrollView.jar 
// for training purpose, to show tesseract segment result, didn't really use in the end, doesn't seem to work on a server, need display, can probably work with Xterm

Sudo apt-get install default-jdk to install javac

Downloaded ScrollView.jar to tesseract/java

Make ScrollVIew.jar

export SCROLLVIEW_PATH=$PWD/java

#### Install necessary fonts for tesstraining: 
(Will need to download extra fonts for training Chinese, see later)

sudo apt install ttf-mscorefonts-installer

sudo apt install fonts-dejavu

fc-cache -vf // this is probably for checking fonts available


## Set up for tessturotial (training English): 
Follow instructions in the following link: https://github.com/tesseract-ocr/tesseract/wiki/TrainingTesseract-4.00, If you run into some problems, refer to notes below 

mkdir ~/tesstutorial

cd ~/tesstutorial

mkdir langdata

cd langdata

sudo wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/radical-stroke.txt

sudo wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/common.punc

sudo wget https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/master/font_properties

sudo wget https://raw.githubusercontent.com/tesseract-ocr/langdata/master/Latin.unicharset

sudo wget https://raw.githubusercontent.com/tesseract-ocr/langdata/master/Latin.xheights

mkdir eng

cd eng

sudo wget https://raw.githubusercontent.com/tesseract-ocr/langdata/master/eng/eng.training_text

sudo wget https://raw.githubusercontent.com/tesseract-ocr/langdata/master/eng/eng.punc

sudo wget https://raw.githubusercontent.com/tesseract-ocr/langdata/master/eng/eng.numbers

sudo wget https://raw.githubusercontent.com/tesseract-ocr/langdata/master/eng/eng.wordlist

cd ~/tesstutorial

git clone --depth 1 https://github.com/tesseract-ocr/tesseract.git

cd tesseract/tessdata
##### no need to mkdir best here, will cause problem later

sudo wget https://github.com/tesseract-ocr/tessdata_best/raw/master/eng.traineddata

sudo wget https://github.com/tesseract-ocr/tessdata_best/raw/master/heb.traineddata

sudo wget https://github.com/tesseract-ocr/tessdata_best/raw/master/chi_sim.traineddata

### Training from scratch

src/training/tesstrain.sh --fonts_dir /usr/share/fonts --lang eng --linedata_only \
  --noextract_font_properties --langdata_dir ../langdata \
  --tessdata_dir ./tessdata --output_dir ~/tesstutorial/engtrain

src/training/tesstrain.sh --fonts_dir /usr/share/fonts --lang eng --linedata_only \
  --noextract_font_properties --langdata_dir ../langdata \
  --tessdata_dir ./tessdata \
  --fontlist "Impact Condensed" --output_dir ~/tesstutorial/engeval

(If it runs into error, copy paste the code and run again)

The above command created engeval and engtrain in tesstutorial folder

mkdir -p ~/tesstutorial/engoutput

lstmtraining --debug_interval 100 \

  --traineddata ~/tesstutorial/engtrain/eng/eng.traineddata \
  
  --net_spec '[1,36,0,1 Ct3,3,16 Mp3,3 Lfys48 Lfx96 Lrx96 Lfx256 O1c111]' \
  
  --model_output ~/tesstutorial/engoutput/base --learning_rate 20e-4 \
  
  --train_listfile ~/tesstutorial/engtrain/eng.training_files.txt \
  
  --eval_listfile ~/tesstutorial/engeval/eng.training_files.txt \
  
  --max_iterations 5000 &>~/tesstutorial/engoutput/basetrain.log

In a separate window monitor the log file:

tail -f ~/tesstutorial/engoutput/basetrain.log

Test training result on ‘Impact’ font:

lstmeval --model ~/tesstutorial/engoutput/base_checkpoint \

  --traineddata ~/tesstutorial/engtrain/eng/eng.traineddata \
  
  --eval_listfile ~/tesstutorial/engeval/eng.training_files.txt
  
High error rate

On 4500 or so fonts:

lstmeval --model tessdata/best/eng.traineddata --traineddata ~/tesstutorial/engtrain/eng/eng.traineddata --eval_listfile ~/tesstutorial/engeval/eng.training_files.txt

low error rate

on full model:

--model tessdata/best/eng.traineddata --traineddata ~/tesstutorial/engtrain/eng/eng.traineddata --eval_listfile

~/tesstutorial/engtrain/eng.training_files.txt

Lowest error rate

### Training Chinese

##### There are a lot of things that need to be tuned for the training for a very good result fitted to your purpose, for example, the training text used (number of necessary characters added), the fonts used for training, the iterations etc.. chi_sim is harder than Latin, you probably need to retrain a few layers instead of fine tuning just a few characters. By doing the following I can successfully recognize arrows, but to get a very good OCR result this is far from enough.

The question I asked when having problem training might be helpful to you:

https://groups.google.com/forum/?utm_medium=email&utm_source=footer#!topic/tesseract-ocr/F2iuSvajHqA

Also refer to: https://github.com/tesseract-ocr/tesseract/wiki/TrainingTesseract-4.00

### Fine tuning chi_sim (adding ↓)

At tesstutorial/langdata/

mkdir chi_sim

cd chi_sim

wget https://raw.githubusercontent.com/tesseract-ocr/langdata/master/chi_sim/chi_sim.training_text

wget https://raw.githubusercontent.com/tesseract-ocr/langdata/master/chi_sim/chi_sim.punc

wget https://raw.githubusercontent.com/tesseract-ocr/langdata/master/chi_sim/chi_sim.numbers

wget https://raw.githubusercontent.com/tesseract-ocr/langdata/master/chi_sim/chi_sim.wordlist

(attention: files in langdata_lstm are much larger than files in langdata, will result in failure when training because the .training_text file is too large)

grep ↓ langdata/chi_sim/chi_sim.training_text (nothing will show up)

use nano to insert new chars (↓) to chi_sim.training_text

from tesstutorial/tesseract run

src/training/tesstrain.sh --fonts_dir /usr/share/fonts --lang chi_sim --linedata_only \
  --noextract_font_properties --langdata_dir ../langdata \
  --tessdata_dir ./tessdata --output_dir ~/tesstutorial/trainarrows

#### Problem: could not find font named ' ' 
(https://groups.google.com/forum/?utm_medium=email&utm_source=footer#!topic/tesseract-ocr/5vLEamZ43Kg Google group question I asked when have this problem)

text2image --find_fonts --text ./langdata/chi_sim/chi_sim.training_text --outputbase ./langdata/chi_sim/  --min_coverage 0.999  --fonts_dir=/usr/share/fonts/

how to install fonts?

Sudo apt-get install *** (need to find from the web)

fc-list :lang=zh (list all Chinese fonts available in the system)

fc-match Arial (find Arial fonts available?)

Some fonts cannot be found and installed from internet, install and add the following fonts to src/training/language-specific.sh instead (these need to also be found in langdata/font_properties, otherwise need to add them to font_properties too).

   "AR PL UKai HK" \
   
   "AR PL UKai TW" \
    
   "AR PL UKai TW MBE" \
    
   "AR PL UKai Patched" \
   
   "AR PL UMing CN, Light," \
   
   "AR PL UMing HK Light" \
   
   "AR PL UMing TW Light" \
   
   "AR PL UMing TW MBE Light" \
   
   "AR PL UMing Patched Light" \
   
   "Arial Unicode MS Regular" \
   
Useful links about how to slove this problem:

https://github.com/tesseract-ocr/tesseract/wiki/Fonts

https://github.com/tesseract-ocr/langdata_lstm/blob/master/chi_sim/okfonts.txt

https://github.com/tesseract-ocr/langdata/blob/master/font_properties

### Continue after solve the font problem
After installing necessary fonts, from tesstutorial/tesseract run

src/training/tesstrain.sh --fonts_dir /usr/share/fonts --lang chi_sim --linedata_only \

  --noextract_font_properties --langdata_dir ../langdata \
  
  --tessdata_dir ./tessdata --output_dir ~/tesstutorial/trainarrows
  
(this step creates training data, the training text created here is equivalent to the text used to train base tesseract not langdata_lstm)

src/training/tesstrain.sh --fonts_dir /usr/share/fonts --lang chi_sim --linedata_only \

  --noextract_font_properties --langdata_dir ../langdata \
  
  --tessdata_dir ./tessdata \
  
  --fontlist " AR PL UKai TW " --output_dir ~/tesstutorial/evalarrows
  
(create evaluation data for the font in fontlist)

combine_tessdata -e tessdata/best/chi_sim.traineddata \

  ~/tesstutorial/trainarrows2/chi_sim.lstm
  
(created chi_sim.lstm file)

lstmtraining --model_output ~/tesstutorial/trainarrows/arrows \

  --continue_from ~/tesstutorial/trainarrows/arrows_checkpoint\
  
  --traineddata ~/tesstutorial/trainarrows/chi_sim/chi_sim.traineddata \
  
  --old_traineddata tessdata/best/chi_sim.traineddata \
  
  --train_listfile ~/tesstutorial/trainarrows/chi_sim.training_files.txt \
  
  --max_iterations 3600

combine_tessdata -d tesstutorial/tesseract/tessdata/best/chi_sim.traineddata

result:

Version string:4.00.00alpha:chi_sim:synth20170629:[1,48,0,1Ct3,3,16Mp3,3Lfys64Lfx96Lrx96Lfx512O1c1]

0:config:size=1966, offset=192

17:lstm:size=12152851, offset=2158

18:lstm-punc-dawg:size=282, offset=12155009

19:lstm-word-dawg:size=590634, offset=12155291

20:lstm-number-dawg:size=82, offset=12745925

21:lstm-unicharset:size=258834, offset=12746007

22:lstm-recoder:size=72494, offset=13004841

23:version:size=84, offset=13077335

lstmeval --model ~/tesstutorial/trainarrows/arrows_checkpoint \

  --traineddata ~/tesstutorial/trainarrows/chi_sim/chi_sim.traineddata \
  
  --eval_listfile ~/tesstutorial/trainarrows/chi_sim.training_files.txt

lstmeval --model ~/tesstutorial/trainarrows/arrows_checkpoint \

  --traineddata ~/tesstutorial/trainarrows/chi_sim/chi_sim.traineddata \
  
  --eval_listfile ~/tesstutorial/evalarrows/chi_sim.training_files.txt 2>&1 |
  grep ↑

lstmtraining --stop_training \

  --continue_from ~/tesstutorial/trainarrows/arrows_checkpoint \
  
  --traineddata ~/tesstutorial/trainarrows/chi_sim/chi_sim.traineddata \
  
  --model_output ~/tesstutorial/trainarrows/chi_sim.traineddata

### Adding ± to chi_sim

grep ± langdata/chi_sim/chi_sim.training_text

nano langdata/chi_sim/chi_sim.training_text, then inserted ± 

src/training/tesstrain.sh --fonts_dir /usr/share/fonts --lang chi_sim --linedata_only \

  --noextract_font_properties --langdata_dir ../langdata \
  
  --tessdata_dir ./tessdata --output_dir ~/tesstutorial/trainplusminuszh

src/training/tesstrain.sh --fonts_dir /usr/share/fonts --lang chi_sim --linedata_only \

  --noextract_font_properties --langdata_dir ../langdata \
  
  --tessdata_dir ./tessdata \
  
  --fontlist " AR PL UKai TW " --output_dir ~/tesstutorial/evalplusminuszh

combine_tessdata -e tessdata/best/chi_sim.traineddata \

  ~/tesstutorial/trainplusminuszh/chi_sim.lstm

lstmtraining --model_output ~/tesstutorial/trainplusminuszh/plusminuszh \

  --continue_from ~/tesstutorial/trainplusminuszh/chi_sim.lstm \
  
  --traineddata ~/tesstutorial/trainplusminuszh/chi_sim/chi_sim.traineddata \
  
  --old_traineddata tessdata/best/chi_sim.traineddata \
  
  --train_listfile ~/tesstutorial/trainplusminuszh/chi_sim.training_files.txt \
  
  --max_iterations 3600
