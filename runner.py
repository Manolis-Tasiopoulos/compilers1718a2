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
		self.bool_list = []
		self.local_var = ''
		self.parenthesis_val = ''		
		self.not_check = False
		self.print_val = ''
		self.print_val_no_var = ''
		self.print_check = False		
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
			if self.val not in self.st:
				self.st[self.val] = None
			else:
				raise ParseError('SyntaxError: You must to choose different names for var')
			self.local_var = self.val
			self.match('IDENTIFIER')
			
			self.match('=')						
			self.expr()			
			self.st[self.local_var] = self.bool_list[0]
			self.bool_list.clear()
			print(self.st)		

		elif self.la == 'print':
			self.print_check = True					
			self.match('print')
			self.print_val = self.val
			self.expr()	
			
			if self.print_val in self.st and self.st != {}:
				print(self.st[self.print_val])
			elif self.print_val_no_var != '':
				print (self.print_val_no_var)
			else:
				raise ParseError('SyntaxError: Initialize before print')
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
					
			op = self.multiple_logop() 
			self.term()
			self.termTail()	
			
			if op == 'and':
				result = self.compute_and(self.bool_list[0] , self.bool_list[1])			
			else:	
				result = self.compute_or(self.bool_list[0] , self.bool_list[1]) 
			
			print(result)

			if self.not_check == True:
				self.parenthesis_val = result
				
			if self.print_check == True:
				self.print_val_no_var = result
			
			self.bool_list.clear()
			self.bool_list.append(result)	
			
			self.not_check = False
			self.print_check = False			
		
			return result
				
	
		elif self.la in ('IDENTIFIER','print',None,')'):
			return
		else:			
			raise ParseError('SyntaxError: Expected <and> or <or> ')
	def term(self):	
		if self.la in ('(', 'IDENTIFIER', 'LOGVALTRUE', 'LOGVALFALSE', 'not'):

			if self.la in ('LOGVALTRUE' ,'LOGVALFALSE','IDENTIFIER'):
				self.bool_list.append( self.factor() )
				return
			self.factor()
			self.factorTail()			
		else:
			raise ParseError('SyntaxError: Expected ( or id or Boolean ')
	def factorTail(self):
		if self.la == 'not':			
			self.single_logop()
			self.not_check = True
			not_result = self.compute_not(self.factor())
			self.factorTail()
			self.bool_list.append(not_result)			
			if self.print_check == True:				
				self.print_val_no_var = not_result			
			
			return not_result			

		elif self.la in ('and','or','IDENTIFIER','print',None,')'):
			return
		else:			
			raise ParseError('SyntaxError: Expected <not> or NULL')
	def factor(self):	
		if self.la == '(':
			self.match('(')
			self.expr()
			if self.not_check == True:										
				not_result = self.compute_not(self.parenthesis_val)
				self.bool_list.clear()
				self.bool_list.append(not_result)				
				self.not_check = False
			self.match(')')
		elif self.la == 'IDENTIFIER':
			temp_name = self.val						
			self.match('IDENTIFIER')
			return self.st[temp_name]			
		elif self.la == 'LOGVALTRUE':
			self.match('LOGVALTRUE')						
			return 'true'
		elif self.la == 'LOGVALFALSE':
			self.match('LOGVALFALSE')
			return 'false'
		elif self.la in ('and','or','not','IDENTIFIER','print',None,')'):
			return
		else:
			raise ParseError("SyntaxError: Expected ( or id or Boolean")
	def multiple_logop(self):	
		if self.la == 'and':
			self.match('and')
			return 'and'
		elif self.la == 'or':
			self.match('or')
			return 'or'		
		else:
			raise ParseError('SyntaxError: Expected <and> or <or>')
	def single_logop(self):		
		if self.la == 'not':
			self.match('not')
			return 'not'		
		else:
			raise ParseError('SyntaxError: Expected <not> ')

	def compute_not(self, boolean):
		if boolean == 'true':
			return 'false'
		else:
			return 'true'
	def compute_and(self, boolean_a, boolean_b):
		if boolean_a == 'true' and boolean_b == 'true':
			return 'true'
		else:
			return 'false'
	def compute_or(self, boolean_a, boolean_b):
		if boolean_a == 'true' and boolean_b == 'true':
			return 'true'
		else:
			return 'false'
		
parser = MyParser()
with open('input.txt') as fp:
	try:
		print('Checking Syntax \n')
		parser.parse(fp)
		print('Syntax is correct !!')
	except ParseError as perr:
		print(perr)

	
