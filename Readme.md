# Info
This project is for extracting lab test values from a lab test report. It gives the values for each test item as well as the confidence level. The lab test that can be processed for now are bloodTest, stoolTest, urineTest and psa. For images of these tests, see images in *_test folders.  Other lab tests can also be processed by adding necessary classes to /home/ubuntu/labtestocr/flaskocr/labtestocr.py. 

The main techniques involved are Tesseract OCR (for recognizing text in an image) and regular expression (for extracting values for a specific test item). 

For image pre-processing, a useful website is https://www.imgonline.com.ua/eng/improve-scanned-text.php  It improves image quality and thus OCR results for some images, but not all.

The project is currently located at our AWS server ml.siuvo.com.

## Folder information
Folder flaskocr contains the main python program labtestocr.py, where the classes bloodTest, urineTest, stoolTest, psa are. Swagger interface set up programs are also here.

*_test folders contain labtest reports downloaded from the Internet, images after processing (resize, contrast-stretch), tesseract outputs(.txt, .box etc.), initial result analysis programs.

Page_dewarp-master/Image-Contrast-Enhancement/photo-enhancer are cloned from Github, for improving image properties, which don't seem to help much.

Medicine_instructions contains tesseract results for some medicine instruction images.

## Installing and Running instruction
First you need to install Tesseract engine follow the instructions in [Installation_and_training.md](Installation_and_training.md).

Then setup python programs
```
$ pip3 install virtualenv ## install the package for creating a virtual environment for python
$ virtualenv venv  ## create the virtual environment
$ source venv/bin/activate  ## activate the virtual environment
(venv) $ cd venv
(venv) :~/venv$ git clone https://<username>@bitbucket.org/shufu/labtestocr.git
(venv) :~/venv$ cd labtestocr
(venv) :~/venv/labtestocr$ pip3 install -r requirements.txt
```

To set up swagger interface for Labtest_OCR, run 
```bash
(venv) :~/venv/tesseract/flakocr$ pm2 start 'python3 labtestocr_swagger.py' ## from folder flaskocr
```

The resulting swagger interface can be view from http://localhost:5000/. In my case http://ml.siuvo.com:5000/.

For an example of bloodTest report to test in swagger:

https://1.bp.blogspot.com/-QkiATzoGUko/XFL9ZvmNO7I/AAAAAAAACM4/0xr7hVD0bqsvxmfAHxLIu1gtRjDD2yYQQCLcBGAs/s1600/c1-1.jpg

For an example of urineTest report:

https://gss0.baidu.com/9fo3dSag_xI4khGko9WTAnF6hhy/zhidao/pic/item/0dd7912397dda144a7a23964b0b7d0a20df486b8.jpg

For an example of stoolTest report:

http://askimg.39.net/topic/20150319/785494.jpg

For an example of psa report:

http://wap.xcgwk.com/uploads/allimg/170419/1-1F419103348.jpg

# Installing and training Tesseract
see [Installation_and_training.md](Installation_and_training.md)

## Running tesseract from command line

$ tesseract imagepath outputfilepath(without file extension) -l chi_sim --psm 6 configs
 
Example:

```bash
$ tesseract ~/tesseract/blood_test/test.jpeg ~/tesseract/blood_test/test -l chi_sim --psm 6 -c preserve_interword_spaces=1 whitelist_blood.txt
```

- 'whitelist_blood.txt' should be in folder /usr/local/share/tessdata/configs, can also replace it with other configs in the folder, like 'box', 'tsv', 'pdf' to get box/tsv/pdf output from tesseract; 

- '-c preserve_interword_spaces=1' is for changing tesseract default settings, the parameters that can be set can be viewed with 'tesseract --print-parameters' (there's a hundreds of them, useful ones are 'preserve_interword_spaces', 'tessedit_write_images'); 

- '--psm 6' is for setting the segmentation method, view it with 'tesseract --help-extra';

- '-l chi_sim' is for setting language to chi_sim, the available languages can be viewd with 'tesseract --list-langs', too add available langs, download .traineddata file and put it in /usr/local/share/tessdata

##### Jingjing LIN, 2019-07