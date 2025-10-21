# Pythonny Quest

## Experiments

### shy

### workbench
- most promising/reliable approach, based on ipython API
- requires more student interaction with new variables/functions, e.g. quest() or help(quest) or quest.check() or quest.score()
- [ ] put the working example script into new pythonny package

### pexpect
- would have to emulate entire terminal and listen to entire keyboard, passing through everything back and forth

### prompttoolkit
- can detect ctrl-V and other pasting commmands by user
- [ ] integrate with workbench

### pymux
Almost works for what I need, but seems to only work in Python 3.9 or earlier.  Also relies on pydoc which requires old Pythons as well and produces the following warnings:
```bash
/home/hobs/code/public-by-others/pymux/.venv/lib/python3.12/site-packages/docopt.py:165: SyntaxWarning: invalid escape sequence '\S'
  name = re.findall('(<\S*?>)', source)[0]
/home/hobs/code/public-by-others/pymux/.venv/lib/python3.12/site-packages/docopt.py:166: SyntaxWarning: invalid escape sequence '\['
  value = re.findall('\[default: (.*)\]', source, flags=re.I)
/home/hobs/code/public-by-others/pymux/.venv/lib/python3.12/site-packages/docopt.py:207: SyntaxWarning: invalid escape sequence '\['
  matched = re.findall('\[default: (.*)\]', description, flags=re.I)
/home/hobs/code/public-by-others/pymux/.venv/lib/python3.12/site-packages/docopt.py:456: SyntaxWarning: invalid escape sequence '\S'
  split = re.split('\n *(<\S+?>|-\S+?)', doc)[1:]
```

These seem to be caused by the newer Python parsing of regexesconflict

Pythonny Chat is developed with Aider!
```