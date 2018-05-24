import plex

"""
<Program> -> Stmt_list #

Stmt_list -> Stmt Stmt_list | e
Stmt -> id = Expr | print Expr
Expr -> Term Term_tail
Term_tail -> Multiple_logop Term Term_tail | e
Term -> Factor Factor_tail
Factor_tail -> Single_logop Factor Factor_tail | e
Factor -> (Expr) | id | logval | e
Multiple_logop -> and | or 
Single_logop -> not

"""
class ParseError(Exception):
	pass

class MyParser:
	def __init__(self):
		self.st = {}
	def create_scanner(self,fp):
		
		logvalTrue = plex.NoCase( plex.Str('true','t','1') ) 
		logvalFalse = plex.NoCase( plex.Str('false','f','0') )
		digit = plex.Range('09')
		letter = plex.Range('azAZ')

		
		identifier = letter + plex.Rep(letter|digit)
		keyword = plex.Str('print')
		Moperator = plex.Str('and','or')
		Soperator = plex.Str('not') 
		equals = plex.Str("=")
		parenthesis = plex.Any("()")
		space = plex.Rep1(plex.Any(' \n\t'))	

		lexicon = plex.Lexicon([
			(keyword, plex.TEXT),
			(Moperator,plex.TEXT),
			(Soperator,plex.TEXT),
			(logvalTrue, 'LOGVALTRUE'),
			(logvalFalse, 'LOGVALFALSE'),
			(identifier,'IDENTIFIER'),
			(space,plex.IGNORE),
			(Moperator,plex.TEXT),
			(Soperator,plex.TEXT),		
			(parenthesis,plex.TEXT),			
			(equals,plex.TEXT)			
			])

		self.scanner = plex.Scanner(lexicon,fp)
		self.la, self.val = self.next_token()

	def parse(self,fp):
		self.create_scanner(fp)		
		self.stmtList()
		
	def match(self,token):		
		if self.la == token:
			self.la,self.val = self.next_token()				
		else:			
			raise ParseError("Cant match self.la with current token ( self.la: {} current token: {} )".format(self.la,token))
			
	def next_token(self):
		return self.scanner.read()
	def getValue(self,token,text):
		pass


	def stmtList(self):		
		if self.la in ('IDENTIFIER', 'print'):
			self.stmt()
			self.stmtList()
		elif self.la is None:
			return

	def stmt(self):		
		if self.la == 'IDENTIFIER':
			self.match('IDENTIFIER')
			self.match('=')
			self.expr()
		elif self.la == 'print':
			self.match('print')
			self.expr()
		else:
			raise ParseError('SyntaxError: Expected id or print command')
			
	def expr(self):		
		if self.la in ('(', 'IDENTIFIER', 'LOGVALTRUE', 'LOGVALFALSE', 'not'):
			self.term()
			self.termTail()
		else:
			raise ParseError('SyntaxError: Expected ''('' or id or Boolean ')

	def termTail(self):	
		if self.la in ('and', 'or'):			
			self.multiple_logop()
			self.term()
			self.termTail()
		elif self.la in ('IDENTIFIER','print',None,')'):
			return
		else:
			raise ParseError('SyntaxError: Expected <and> or <or> ')
	def term(self):	
		if self.la in ('(', 'IDENTIFIER', 'LOGVALTRUE', 'LOGVALFALSE', 'not'):
			self.factor()
			self.factorTail()
		else:
			raise ParseError('SyntaxError: Expected ( or id or Boolean ')
	def factorTail(self):
		if self.la == 'not':			
			self.single_logop()
			self.factor()
			self.factorTail()
		elif self.la in ('and','or','IDENTIFIER','print',None,')'):
			return
		else:
			raise ParseError('SyntaxError: Expected <not> or NULL')
	def factor(self):	
		if self.la == '(':
			self.match('(')
			self.expr()
			self.match(')')
		elif self.la == 'IDENTIFIER':
			self.match('IDENTIFIER')
		elif self.la == 'LOGVALTRUE':
			self.match('LOGVALTRUE')
		elif self.la == 'LOGVALFALSE':
			self.match('LOGVALFALSE')
		elif self.la in ('and','or','not','IDENTIFIER','print',None,')'):
			return
		else:
			raise ParseError("SyntaxError: Expected ( or id or Boolean")
	def multiple_logop(self):	
		if self.la == 'and':
			self.match('and')
		elif self.la == 'or':
			self.match('or')		
		else:
			raise ParseError('SyntaxError: Expected <and> or <or>')
	def single_logop(self):		
		if self.la == 'not':
			self.match('not')		
		else:
			raise ParseError('SyntaxError: Expected <not> ')
		
parser = MyParser()
with open('input.txt') as fp:
	try:
		print('Checking Syntax \n')
		parser.parse(fp)
		print('Syntax is correct !!')
	except ParseError as perr:
		print(perr)

	
