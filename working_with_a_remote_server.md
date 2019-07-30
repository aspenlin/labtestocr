To log in to a remote server via ssh, from your pem folder
```bash
$ ssh -i **.pem username@ip
```
To use jupyter notebook for remote server:

at remote:
```bash
$ jupyter notebook --no-browser --port=8888
```
at local run the following and open jupyter notebook at http://localhost:8887
```bash
$ ssh -i **.pem -N -f -L localhost:8887:localhost:8888 username@ip
```

Use Sublime text for editing files at remote server:
```bash
$ ssh -i **.pem -R 52698:localhost:52698 username@ip
$ sudo rsub -f filename ## need to install rsub for remote server
```

Transfer files between local and remote server, at local:
```bash
$ scp -i **.pem filename username@ip:~ ## to transfer a folder use -r
```