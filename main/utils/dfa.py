# http://blog.csdn.net/woshiaotian/article/details/10047675

from ..models.system import IllegalWord

__all__ = ['check_bad_words']

class Node(object):
	def __init__(self):
		self.children = None

def add_word(root, word):
	node = root
	for i in range(len(word)):
		if node.children == None:
			node.children = {}
			node.children[word[i]] = Node()
		elif word[i] not in node.children:
			node.children[word[i]] = Node()
		node = node.children[word[i]]

def init():
	root = Node()
	
	for row in IllegalWord.objects.all():
		add_word(root, row.word)
	return root

def is_contain(message, root):
	for i in range(len(message)):
		p = root
		j = i
		while (j < len(message) and p.children != None and message[j] in p.children):
			p = p.children[message[j]]
			j = j + 1

		if p.children == None:
			return True
	
	return False

# DFA Algorithm
def check_bad_words(message):
	return is_contain(message, root)

root = init()
