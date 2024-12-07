* An application that converts Bright Data proxies format to a different format suitable for making an HTTP request.

* Built using Python 3.10.0.

* Install the dependencies in the ```requirements.txt``` file.


* To build an executable file:
```
pyinstaller --onedir --add-data ".env:." --add-data "logo.ico:." --add-data "Proxy Extractor.log;." --windowed --clean --icon=logo.ico --name "Proxy Extractor" main.py
```


* If it fails, update the following dependency:
```
pip install --upgrade PyInstaller pyinstaller-hooks-contrib
```