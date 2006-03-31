#! /usr/bin/python
import sys, time

semfilename = 'semaphore.dat'

def encue_process_and_wait(id):
	print 'encue and wait:', id
	encue_process_to_semaphore(id)
	while True:
		if not head_process() or head_process() == id:
			print 'exiting wait:', id
			break
		time.sleep(0.300)
		

def encue_process_to_semaphore(id):
	f = open(semfilename)
	content = f.read().strip()
	if content:
		sem = eval(content)
	else:
		sem = []
	f.close()
	sem.append(id)
	f = open(semfilename, 'w')
	f.write(str(sem))
	f.close()

def head_process():
	f = open(semfilename)
	content = f.read()
	if not content: #TODO file not exist
		return None
	sem = eval(content)
	f.close()
#	print 'head. sem is ',sem
	return sem[0]

def deencue_process(id):
	f = open(semfilename)
	content = f.read()
	f.close()
	if not content:
		return
	sem = eval(content)
	if id != sem[0]:
		print 'Warning: found unexpected id %s. Probably was killed' % id
	sem = sem[1:]
	f = open(semfilename, 'w')
	f.write(str(sem))
	f.close()

def main():
	if len(sys.argv)==3:
		name = sys.argv[1]
		t = int(sys.argv[2])
	else:
		name = 'default'
		t = 4
	while True:
		encue_process_and_wait(name)
		print '===================  doing some process: ', name 
		time.sleep(t)
		deencue_process(name)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print 'user canceled. lets clean the cue'
		open(semfilename, 'w')
