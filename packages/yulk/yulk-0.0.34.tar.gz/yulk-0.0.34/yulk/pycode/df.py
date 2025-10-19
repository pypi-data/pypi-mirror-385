# 2025.10.27 cp from  file/py/df.py 
import  requests, builtins
import pandas as pd
from collections import Counter 
builtins.icall	= lambda name: globals().get(name,  getattr(builtins, name) if hasattr(builtins, name) else eval(name) )  # en.framehas
builtins.empty	= lambda: pd.DataFrame([]) # onerow(word='overcame', snt='I overcame')
builtins.newdf	= lambda **kwargs: ( df:= pd.DataFrame([]),  [df.insert(len(df.columns),column=k, value=v if isinstance(v, list) else [v]) for k,v in kwargs.items()],	df)[-1]
builtins.jsondf = lambda djson: ( df:= pd.DataFrame( djson.get('data',[])), df.attrs.update(djson.get('attrs',{})))[0] 
builtins.testdf	= pd.DataFrame({"Name": ["Alice", "Bob", "Charlie"], "Age": [25, 30, 35], "Email": ["alice@example.com", "bob@example.com", "charlie@example.com"], "Join Date": ["2023-01-01", "2022-05-15", "2021-11-20"]	})

pd.DataFrame.asjson = lambda self: {"attrs":self.attrs, "data": self.to_dict('records') } 
pd.DataFrame.value	= lambda self: self.values[0, 0] if len(self) > 0 else None  # scalar
pd.DataFrame.scalar	= lambda self: self.values[0, 0] if len(self) > 0 else None  # scalar
pd.DataFrame.colname= lambda self, x: self.columns[x] if isinstance(x, int) else x  # df.colname(0) or df.colname('word')
pd.DataFrame.colsum = lambda self, x=-1: self[ self.colname(x) ].sum()  # for testing only 
pd.DataFrame.tosql	= lambda self, **kwargs:  "\n".join([ '(' +  ','.join([ f"'{row[c]}'" if isinstance(row[c], str) else str(row[c]) for c in self.columns]) + '),' for index, row in self.iterrows()])

pd.DataFrame.asc	= lambda self, col=-1: self.sort_values(by=self.colname(col))
pd.DataFrame.desc	= lambda self, col=-1: self.sort_values(by=self.colname(col), ascending=False)
pd.DataFrame.sort	= lambda self, col=-1: self.sort_values(by=self.colname(col), ascending=False)

pd.DataFrame.line	= lambda self, x=0, y=1, **kwargs: self.plot(x=self.colname(x), y=self.colname(y), kind='line', **kwargs)
pd.DataFrame.pie	= lambda self, x=0, y=1, **kwargs: self.plot(x=self.colname(x), y=self.colname(y), kind='pie', **kwargs)
pd.DataFrame.bar	= lambda self, x=0, y=1, **kwargs: self.plot(x=self.colname(x), y=self.colname(y), kind='bar', **kwargs)
pd.DataFrame.bars	= lambda self, y=[1,2], x=0, **kwargs: self.plot(x=self.colname(x), y=[ self.colname(z) for z in y], kind='bar', **kwargs) # default two bars
pd.DataFrame.barh	= lambda self, x=0, y=1, **kwargs: self.plot(x=self.colname(x), y=self.colname(y), kind='barh', **kwargs)
pd.DataFrame.barhs	= lambda self, y=[1,2], x=0, **kwargs: self.plot(x=self.colname(x), y=[ self.colname(z) for z in y], kind='barh', **kwargs) # default two bars
pd.DataFrame.hist	= lambda self, **kwargs: self.plot.hist(**kwargs) # bins=20
pd.DataFrame.box	= lambda self, x=0, y=1, **kwargs: self.plot(x=self.colname(x), y=self.colname(y), kind='box', **kwargs)
pd.DataFrame.kde	= lambda self, x=0, y=1, **kwargs: self.plot(x=self.colname(x), y=self.colname(y), kind='kde', **kwargs) # density
pd.DataFrame.area	= lambda self, x=0, y=1, **kwargs: self.plot.area(**kwargs) #stacked=False
pd.DataFrame.scatter= lambda self, x=0, y=1, **kwargs: self.plot.scatter(x=self.colname(x), y=self.colname(y),**kwargs) 
#hexbin

pd.DataFrame.addfunc  = lambda self, name, col=0, **kwargs: (  # addfunc('idf') , single col as the input, in most cases, addfunc('logbnc', (1,2,3))
		myf:= icall(name), 
		self.insert(len(self.columns),column=f"{name}{len(self.columns)}" if name in self.columns else name, value=[ myf( *[row[x] for x in col],**kwargs) if isinstance(col, tuple) else myf( row[col],**kwargs) for _, row in self.iterrows()]),
		self)[-1]
pd.DataFrame.append  = lambda self, name, **kwargs: self.addfunc(name, col=-1, **kwargs)

pd.DataFrame.addkv  = lambda self,k,v, **kwargs: ( ## add newdf(k1,v1,... )   | pd.DataFrame([]).addkv('one', 12).addkv('two', 'xxx')
		self.insert(len(self.columns),column=k, value=v if isinstance(v, list) else [v]),
		self)[-1]

pd.DataFrame.interlist	= lambda self, col1,col2 : ( ## used in wordinsnt
		self.insert(len(self.columns),column=f"{col1}_{col2}", value=[ [w for w in row[col1] if w in row[col2]] for index, row in self.iterrows()]),
		self)[-1]

pd.DataFrame.addperc	= lambda self, col=-1, **kwargs: (
	colsum:=self[ self.columns[col] ].sum() +0.0001, 
	self.insert(len(self.columns),column=self.columns[col]+ '%', value=[ round(100*row[col]/colsum,2)  for row in self.values]),
	self) [-1]
pd.DataFrame.addsum	= lambda self, col=-1, **kwargs: (
	colsum:=self[ self.columns[col] ].sum() , 
	self.assign(sum=colsum)) [-1]

pd.DataFrame.keyness = lambda self, df2, x1=0, y1=1, x2=0, y2=1, **kwargs: ( 
		dic1:= {row[x1]: row[y1] for _, row in self.iterrows()}, 
		dic2:= {row[x2]: row[y2] for _, row in df2.iterrows()}, 
		sum1:= sum(dic1.values()) + 0.0001,
		sum2:= sum(dic2.values()) + 0.0001,
		words:= list(set(list(dic1.keys()) +  list(dic2.keys()))),
		rows:= [ {self.columns[x1]: w, self.columns[y1]: dic1.get(w,0), f"{df2.columns[y2]}2":dic2.get(w,0), "keyness": loglike(dic1.get(w,0), dic2.get(w,0), sum1, sum2) }  for w in words],
		pd.DataFrame(sorted(rows, key=lambda x: x['keyness'])), #, reverse=True
		)[-1] #df.sort_values('keyness', inplace=True),

pd.DataFrame.rmcol = lambda self, col: ( 
		self.drop(col if isinstance(col, str) else self.columns[col], axis=1,  inplace=True, errors='ignore'),
		self)[-1]
pd.DataFrame.connect = lambda self, *args, **kwargs: (  # connect(dep,p,gp) 
		sepa := kwargs.get('sepa', ''), 
		colname:= kwargs.get('name', f"col{len(self.columns)}" ), 
		self.assign( **{ colname: [ sepa.join([ row[w] if w in self.columns else w for w in args]) for index,row in self.iterrows()]})
		)[-1]

pd.DataFrame.counter	= lambda self, col=-1, by=None: pd.DataFrame(  Counter([ row[col] for _, row in self.iterrows()]).most_common(), columns=[self.columns[col],'count']) if by is None else (
        si:=Counter(), 
        [ si.update({row[col]:row[by]}) for _, row in self.iterrows()], 
        pd.DataFrame(  si.most_common(), columns=[self.columns[col],'count'])
)[-1] 

if __name__ == "__main__":	pass

'''
dataframe = pd.DataFrame({'A':[9, 4, 4, 5, 7], 'B':[2, 4, 2, 8, 1]}) 
dataframe.plot(linestyle='dashed', 
               color=['k','r'], 
               marker='o', 
               xticks=[0, 1, 2, 3, 4], yticks=np.arange(0, 10.0, 0.5), xlim=[-0.25, 4.25],
               title='dataframe photo');

import numpy as np
a = np.random.randn(100)
df = pd.DataFrame({'length':a }) 
df.plot.hist(bins=20);
'''