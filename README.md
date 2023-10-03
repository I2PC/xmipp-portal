## Xmipp Portal

> http://xmipp.i2pc.es

## Set up

### Dependencies

```
$ cd xmipp-portal
$ virtualenv --python /usr/bin/python2 env
$ env/bin/pip install -r requirements.txt
```

## Run

## Development server

```
$ env/bin/python manage.py runserver
```

## Production server (Apache)

```
<VirtualHost *:80>
  ServerName xmipp.i2pc.es
  Alias /static /home/ubuntu/xmipp-portal/staticfiles

  <Directory /home/ubuntu/xmipp-portal/staticfiles>
    Require all granted
  </Directory>

  <Directory /home/ubuntu/xmipp-portal/main>
    <Files wsgi.py>
      Require all granted
    </Files>
  </Directory>

  WSGIDaemonProcess xmipp-portal python-home=/home/ubuntu/xmipp-portal/env python-path=/home/ubuntu/xmipp-portal
  WSGIProcessGroup xmipp-portal
  WSGIScriptAlias / /home/ubuntu/xmipp-portal/main/wsgi.py
</VirtualHost>
```

## Admin interface (requires password)

> http://xmipp.i2pc.es/admin/

## Wiki

The old XMIPP wiki uses TWiki. To convert it to a Github wiki we may use [twiki2markdown](https://github.com/jcodagnone/twiki2markdown).

First, locate the root directory of the TWiki, a directory usually named `TWiki` that contains one `txt`/`txt.v` file per page. Copy this directory to your machine and then run:

```
$ org=ORGANISATION; repo=REPO
$ git clone https://github.com/jcodagnone/twiki2markdown
$ cd twiki2markdown
$ git clone git@github.com:$org/$repo.wiki.git
# tested with Ruby 2.3.0
$ ruby -I lib bin/twiki2markdown -v -f /path/to/TWiki -t $repo.wiki/
$ cd $repo.wiki/
$ git push
```
