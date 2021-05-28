# melo-aid-backend

## How to run
1. pip3 install -r requirements.txt
2. wget https://storage.googleapis.com/magentadata/models/onsets_frames_transcription/tflite/onsets_frames_wavinput.tflite
3. python3 -m flask run

## VM setup
1. Install the necessary linux libraries
``` 
sudo apt install python3 libsndfile1 open-ssl python3-pip lib-ssl net-tools apache2
```
2. Restart the VM and install wsgi connector library
``` 
sudo reboot
sudo apt install libapache2-mod-wsgi-py3
```
3. Move the apache server conf file to the required directory and change the permission of home directory (Do it only if apache is throwing error).
```
cd melo-aid-backend
sudo mv server_conf/website.conf /etc/apache2/sites-available/
chmod 755 /home/meloaid
```
4. Disable default site and enable custom site, then  reload apache.
```
sudo a2dissite 000-default.conf
sudo a2ensite website.conf
sudo systemctl reload apache2
```
