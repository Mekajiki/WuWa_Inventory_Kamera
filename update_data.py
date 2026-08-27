# nanoka.cc から characters/weapons/echoes/sonata DB を強制再生成する
from updater.databaseUpdater import DataUpdater

DataUpdater().updateFromNanoka(force=True)
print('done')
