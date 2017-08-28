import math

class progress_demonstrator:

    def __init__(self,totnum):
        self._totnum = totnum

    def progress_show(self,currentnum,marker = '*',title=''):
        assert currentnum <= self._totnum, '[-]current num should LE totnum!'
        pct = currentnum/self._totnum*100
        toshow = '{:} : {:} {:.2f}%'.format(title,marker*math.ceil(pct),pct)
        print(toshow)

if __name__=='__main__':
    t = progress_demonstrator(500)
    for dumi in range(100):
        t.progress_show(title='TEST',currentnum=dumi+1)