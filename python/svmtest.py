from initial import *
from scikits.learn import svm
from scikits.learn.externals import joblib

rel = """
import svmtest
reload(svmtest)
from svmtest import *
"""

#logfile = open('svmtest.log','a')

loadstuff = '''
clfP,clfA = joblib.load('svmmodels/linearModel/clfP.pkl'), joblib.load('svmmodels/linearModel/clfA.pkl')
Dt,cpt,cat = loadData('Btest')
test2(clfP,clfA,Dt,cpt,cat)
'''

imstuff = '''
ao0 = caffe.io.load_image(BDATA_FOLDER+BDATA_TEST[402])
ao1 = caffe.io.load_image(BDATA_FOLDER+BDATA_TEST[1633])
po0 = caffe.io.load_image(BDATA_FOLDER+BDATA_TEST[1621])
po1 = caffe.io.load_image(BDATA_FOLDER+BDATA_TEST[1768])
'''

printstuff = '''
h = plt.subplot(2,2,1)
h = plt.imshow(ao0)
h = plt.title('animal only '+BDATA_TEST[402])
h = plt.subplot(2,2,2)
h = plt.imshow(ao1)
h = plt.title('animal only '+BDATA_TEST[1633])
h = plt.subplot(2,2,3)
h = plt.imshow(po0)
h = plt.title('plastic only '+BDATA_TEST[1621])
h = plt.subplot(2,2,4)
h = plt.imshow(po1)
h = plt.title('plastic only '+BDATA_TEST[1768])
'''
def log(s):
	stdlog(s)
	logfile = open('svmtest.log','a')
	ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S -- ')
	#print ts+s
	logfile.write(ts+s)
	logfile.write('\n')
	logfile.close()

def loadData(tp='Btrain'):
	d = {'Btrain':'data_4096s/BtrainM.npy',
		'Btest':'data_4096s/BtestM.npy',
		'Bval':'data_4096s/BvalM.npy',
		'Atrain':'data_4096s/AtrainM.npy',
		'Atest':'data_4096s/AtestM.npy',
		'Aval':'data_4096s/AvalM.npy',
		'all':'data_4096s/ALLDATAR.npy'}
	tD = np.load(d[tp])
	if tD.shape[1] == 4099:
		ids = tD[:,0:2]
		cp = (tD[:,2] == 1) | (tD[:,2] == 3)
		ca = (tD[:,2] == 2) | (tD[:,2] == 3)
		D = tD[:,3:]
		return D,cp,ca,ids
	else:
		cp = (tD[:,0] == 1) | (tD[:,0] == 3)
		ca = (tD[:,0] == 2) | (tD[:,0] == 3)
		D = tD[:,1:]
	return D,cp,ca

def demo(num=10,kwargs={'kernel':'rbf', 'gamma':0.7, 'C':1.0}):
	D,cp,ca = loadData()
	Dr = D[0:num,[689,3659]]#,1444]]
	cpr,car = cp[0:num],ca[0:num]
	
	clfP = svm.SVC(**kwargs)
	log('fitting plastic')
	t = time.time()
	clfP.fit(Dr,cpr)
	log('in %f sec' % (time.time()-t) )
	plotClf(clfP,Dr,cpr)
	return clfP,Dr,cpr
	
	#clfA = svm.SVC()
	#log('fitting animals'
	#t = time.time()
	#clfA.fit(Dr,car)
	#log('in',str(time.time()-t),'sec'
	
def plotClf(clf,X,y):
	h = .02
	
	x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
	y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
	xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                     np.arange(y_min, y_max, h))
	
	Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

	# Put the result into a color plot
	Z = Z.reshape(xx.shape)
	plt.contourf(xx, yy, Z, cmap=plt.cm.Paired, alpha=0.8)

	# Plot also the training points
	plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.Paired)
	plt.xlabel('Sepal length')
	plt.ylabel('Sepal width')
	plt.xlim(xx.min(), xx.max())
	plt.ylim(yy.min(), yy.max())
	plt.xticks(())
	plt.yticks(())
	plt.show()
	
def fitting(D,cp,ca,kwargs={'kernel':'linear', 'C':1.0}):
	#clfP = svm.SVC(kernel='rbf', gamma=0.7, C=1.0)
	#clfA = svm.SVC(kernel='rbf', gamma=0.7, C=1.0)
	
	clfP = svm.SVC(**kwargs)
	clfA = svm.SVC(**kwargs)

	log('fitting plastic')
	t = time.time()
	clfP.fit(D,cp)
	ttime = time.time()-t
	log('in %f sec' % (time.time()-t) )
	log('fitting animals')
	t = time.time()
	clfA.fit(D,ca)
	ttime += (time.time()-t)
	log('in %f sec' % (time.time()-t) )
	return clfP,clfA,ttime

def test(clf,X,y):
	t = time.time()
	good = 0
	num = len(y)
	for i in range(0,num):
		if clf.predict([X[i,:]])[0] == y[i]:
			good += 1
	log('test in %f sec' % (time.time()-t) )
	log('%d of %d correct: %f' % (good,num,float(good)/float(num)))
	return good,num

def test2(clfP,clfA,X,yp,ya):
	t = time.time()
	gBoth = gPonly = gAonly = fBoth = 0
	num = len(yp)
	for i in range(0,num):
		tp = clfP.predict([X[i,:]])[0] == yp[i]
		ta = clfA.predict([X[i,:]])[0] == ya[i]
		if tp and ta:
			gBoth += 1
		elif tp:
			gPonly += 1
			#print 'plastic only',i
		elif ta:
			gAonly += 1
			#print 'fauna only',i
		else:
			fBoth += 1
	log('test in %f sec' % (time.time()-t) )
	log('of %d items: % 4d correct, % 4d plastic only correct, % 4d animals only correct, % 4d both wrong' % (num,gBoth,gPonly,gAonly,fBoth) )
	ans = ((time.time()-t), (num,gBoth,gPonly,gAonly,fBoth) )
	return ans

def getpos(v0=10,v1=11):
	prange = [{'kernel':'poly', 'degree':x, 'C':1.0} 
					for x in range(2,v0)]
	rrange = [{'kernel':'rbf', 'gamma':float(x)/10, 'C':1.0} 
					for x in range(0,v1) ]
	lrange = [{'kernel':'linear','C':1.0}]
	return prange+rrange+lrange

def useval():
	allpos = getpos()
	D,cp,ca = loadData()
	Dv,cpv,cav = loadData('Bval')
	
	#D,cp,ca = D[:10,:],cp[:10],ca[:10]
	
	for d in allpos:
		log('using param: '+str(d))
		clfP,clfA,t = fitting(D,cp,ca,kwargs=d)
		#dirname = str(d.values()).replace(', ','_').replace('\'','')
		#if not os.path.isdir('svmmodels/'+dirname): os.mkdir('svmmodels/'+dirname)
		#joblib.dump(clfP, 'svmmodels/'+dirname+'/clfP.pkl')
		#joblib.dump(clfA, 'svmmodels/'+dirname+'/clfA.pkl')
		log('testing...')
		test2(clfP,clfA,Dv,cpv,cav)

def main():
	D,cp,ca = loadData()
	#num = 500
	#clfP,clfA = fitting(D[:num,:],cp[:num],ca[:num])
	clfP,clfA = fitting(D,cp,ca)
	joblib.dump(clfP, 'svmmodels/test/SVMl_clfP.pkl')
	joblib.dump(clfA, 'svmmodels/test/SVMl_clfA.pkl')

def main2():
	clfP = joblib.load('svmmodels/test/SVMl_clfP.pkl')
	clfA = joblib.load('svmmodels/test/SVMl_clfA.pkl')
	Dt,cpt,cat = loadData('Btest')
	log('testing...')
	test2(clfP,clfA,Dt,cpt,cat)
	log('testing plastic')
	test(clfP,Dt,cpt)
	log('testing animals')
	test(clfA,Dt,cat)

from multiprocessing import Pool
D,cp,ca,Dv,cpv,cav = None,None,None,None,None,None
def usevalMs(d):
	#log('using param: '+str(d))
	log('training '+str(d) )
	clfP,clfA,t = fitting(D,cp,ca,kwargs=d)
	#dirname = str(d.values()).replace(', ','_').replace('\'','')
	#if not os.path.isdir('svmmodels/'+dirname): os.mkdir('svmmodels/'+dirname)
	#joblib.dump(clfP, 'svmmodels/'+dirname+'/clfP.pkl')
	#joblib.dump(clfA, 'svmmodels/'+dirname+'/clfA.pkl')
	log('testing '+str(d) )
	ans = test2(clfP,clfA,Dv,cpv,cav)
	return (str(d.values()).replace(', ','_').replace('\'',''),t,ans,len(ca))

def writeOutput(filename,output):
	outputfile = open(filename,'w')
	ans = '% 14s | % 7s | % 7s | % 5s | % 5s | % 5s | % 5s | % 5s | % 5s | % 5s | % 5s | % 5s\n' % ('type','Ttrain','Ttest','Dsize', 'Vsize','Bco','Pco','Aco','Bfa','Bac','Pac','Aac')
	outputfile.write(ans)

	for d,t,a,s in output:
		(tt),(n,bg,pg,ag,bf) = a
		ans = '% 14s | % 7.1f | % 7.1f | % 5d | % 5d | % 5d | % 5d | % 5d | % 5d | %.3f | %.3f | %.3f \n' % (d,t,tt,s,n,bg,pg,ag,bf,float(bg)/float(n),float(bg+pg)/float(n),float(bg+ag)/float(n))
		outputfile.write(ans)

def usevalM(S=10):
	ttot = time.time()
	global D,cp,ca,Dv,cpv,cav
	D,cp,ca = loadData()
	Dv,cpv,cav = loadData('Bval')
	D,cp,ca = D[:S,:],cp[:S],ca[:S]
	
	pool = Pool(4)
	allpos = getpos()
	output = pool.map(usevalMs, allpos)
	log('total took %f sec' % (time.time()-ttot))
	writeOutput('svmout/svmtest_%05d_.out'%S,output)

def makefit():
	log('training linear model')
	t = time.time()
	D,cp,ca = loadData()
	clfP,clfA,tt = fitting(D,cp,ca)
	dirname = 'linearModel'
	if not os.path.isdir('svmmodels/'+dirname): os.mkdir('svmmodels/'+dirname)
	joblib.dump(clfP, 'svmmodels/'+dirname+'/clfP.pkl')
	joblib.dump(clfA, 'svmmodels/'+dirname+'/clfA.pkl')
	log('model trained and saved in %.2f sec' % (time.time() -t) )

if __name__ == '__main__':
	D,cp,ca = loadData('Btrain')
	clfP,clfA,tt = fitting(D,cp,ca)
	D2,cp2,ca2 = loadData('Btest')
	print test2(clfP,clfA,D2,cp2,ca2)
	#makefit()
	#main()
	#main2()
	#usevalM(200)
	#usevalM(14)
	#usevalM(140)
	#usevalM(1400)
	#usevalM(14000)
