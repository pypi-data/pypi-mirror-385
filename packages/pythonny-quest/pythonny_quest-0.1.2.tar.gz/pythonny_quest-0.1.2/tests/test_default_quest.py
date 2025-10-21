# pip install pythonny_quest
from pyquest import Quest

quest = Quest()
for i, task in enumerate(quest.tasks):
    print(i, task)
