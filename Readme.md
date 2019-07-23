*_test folders contain labtest report images downloaded from the Internet (Chinese version), images after processing (resize, contrast-stretch), tesseract output(txt, box etc.), initial result analysis

flaskocr floder contains python module labtestocr, where the classes bloodtest, urinetest, stooltest, psa are (these classes will be imported by siuvo_ml_swagger.py in folder tf_pose/tf_pose_estimation)

page_dewarp-master is cloned from Github, for dewarping images, which is not necessarily useful for low quality images

medicine_instructions contain tesseract result for medicine instruction images