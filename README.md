## Demo video

[![Demo video](https://img.youtube.com/vi/z38qVcFXYyQ/0.jpg)](https://www.youtube.com/watch?v=z38qVcFXYyQ)

## How to start

### Get OpenErrorPro
```markdown
- sudo apt-get update
- sudo apt-get install git
- git clone https://github.com/mbsa-tud/OpenErrorPro.git
- cd OpenErrorPro
```

### Get PRISM
- download the PRISM model checker from http://www.prismmodelchecker.org/download.php
- extract it to the OpenErrorPro folder e.g.
```markdown 
OpenErrorPro/prism-4.4-linux64
```
- run the install script:
```markdown
sh OpenErrorPro/prism-4.4-linux64/install.sh
```
- install JRE:
```markdown
sudo apt-get install default-jre
```
- check that prism is working:
```markdown
./prism-4.4-linux64/bin/xprism
```

### Setup OpenErrorPro
- open 
```markdown
epl_prism.py
```
- setup the path to the prism bin folder:
```markdown
self.prism_dir = "/home/errorpro/Desktop/OpenErrorPro/prism-4.4-linux64/bin"
```

### Install python3 libs
```markdown
- sudo apt-get install python3-pyside
- sudo apt-get install python3-colorama
- sudo apt-get install python3-matplotlib
- sudo apt-get install python3-pygraphviz
- sudo apt-get install python3-pyqt4
```

### Run
```markdown
- python3 errorpro.py
```

## VM

Check out our [Virtual machine](https://)

## License

The license infromation will follow soon, the software is not released yet.
