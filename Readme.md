# Info
This project is for extracting lab test results from a lab test report, the lab test that can be processed for now are bloodTest, stoolTest, urineTest and psa. For examples of these tests, see images in *_test folders. Other lab tests can also be processed by adding necessary classes to flaskocr/labtestocr.py.

## Folder information
Folder flaskocr contains the main python module labtestocr.py, where the classes bloodTest, urineTest, stoolTest, psa are. Swagger interface set up programs are also here.

*_test folders contain labtest reports downloaded from the Internet, images after processing (resize, contrast-stretch), tesseract outputs(.txt, .box etc.), initial result analysis programs.

Page_dewarp-master/Image-Contrast-Enhancement/photo-enhancer are cloned from Github, for improving image properties, which don't seem to help much.

Medicine_instructions contains tesseract results for some medicine instruction images.

## Installing and Running instruction
```
$ pip3 install virtualenv ## install the tool for creating a virtual environment for python
$ virtualenv venv  ## create the virtual environment
$ source venv/bin/activate  ## activate the virtual environment
(venv) $ cd venv
(venv) $ git clone https://jingjinglin@bitbucket.org/shufu/tesseract.git
(venv) $ cd tesseract
(venv) $ pip3 install -r requirements.txt
```
To exit the virtual environment
```bash
$ deactivate
```

To set up swagger interface for Labtest_OCR, run 
```bash
$ pm2 start 'python3 labtestocr_swagger.py' ## from folder flaskocr
```

The resulting swagger interface can be view from: http://yourip:5000/

For an example of bloodTest report:

https://1.bp.blogspot.com/-QkiATzoGUko/XFL9ZvmNO7I/AAAAAAAACM4/0xr7hVD0bqsvxmfAHxLIu1gtRjDD2yYQQCLcBGAs/s1600/c1-1.jpg

For an example of urineTest report:

https://gss0.baidu.com/9fo3dSag_xI4khGko9WTAnF6hhy/zhidao/pic/item/0dd7912397dda144a7a23964b0b7d0a20df486b8.jpg

For an example of stoolTest report:

http://askimg.39.net/topic/20150319/785494.jpg

For an example of psa report:

http://wap.xcgwk.com/uploads/allimg/170419/1-1F419103348.jpg

# Installing and training Tesseract
see [Installation_and_training.md](Installation_and_training.md)