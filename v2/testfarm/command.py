import utils


class Command(object) :
	def __init__(self, commandline, info=None, ok=None, **stats) :
		self.commandline = commandline
		self.info = info
		self.ok = ok
		self.stats = stats


	def run(self, subst=dict(), cwd=None) :
		log = utils.buffer()
		error = utils.quotedFile(log, "\033[31m", "\033[0m")
		ok = utils.run(
			self.commandline.format(**subst),
			log = log,
			err = error,
			fatal = False,
			message = '',
			cwd = cwd,
			)
		output = log.output()
		if self.ok is not None : ok = self.ok(output, ok)
		info = None if self.info is None else self.info(output)
		stats = dict([
			(stat, retriever(output) if callable(retriever) else retriever )
			for stat, retriever in self.stats.iteritems()
			])

		return output, ok, info, stats



