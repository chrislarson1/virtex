## Docs Build Instructions

To generate virtex documentation run the following commands:

1. `$ pip install sphinx-press-theme`
   

2. `$ cd /path/to/virtex/docs`


3. `sys.path.insert(0, os.path.abspath('../virtex'))` >> `conf.py`


4. `extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.viewcode']` >> `conf.py`


5. `html_theme = 'press'` >> `conf.py` 


6. `$ sphinx-apidoc -o source/ ../virtex/`

   
7. `$ make clean && make html`
