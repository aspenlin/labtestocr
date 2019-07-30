To log in to a remote server via ssh, from your pem folder:
```bash
$ ssh -i shufu.pem ubuntu@ml.siuvo.com
```
To use jupyter notebook for remote server, at remote:
```bash
$ jupyter notebook --no-browser --port=8888
```
at local run the following and open jupyter notebook at http://localhost:8887
```bash
$ ssh -i shufu.pem -N -f -L localhost:8887:localhost:8888 ubuntu@ml.siuvo.com
```

Use Sublime text for editing files at remote server:
```bash
$ ssh -i **.pem -R 52698:localhost:52698 ubuntu@ml.siuvo.com
$ sudo rsub -f filename ## need to install rsub for remote server
```

Transfer files between local and remote server, at local:
```bash
$ scp -i shufu.pem filename ubuntu@ml.siuvo.com:~ ## to transfer a folder use -r
```
For showing graphical result at the remote, use xterm. With macOS as local use xquartz.

##### Jingjing LIN, 2019-07