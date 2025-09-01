import sys

def lex(code):
 if not isinstance(code,str): return ("error","`lex` function expected a string")
 word=""
 c=i=0
 res=[]
 while i<len(code):
  if code[i]=='"':
   i+=1
   c=1
   while i<len(code):
    if code[i]=='\\':
     i+=1
     if code[i]=='n': word+="\n"
     elif code[i]=='t': word+="\t"
     elif code[i]=='r': word+="\r"
     elif code[i]=='\\': word+="\\"
     elif code[i]=='"': word+='"'
     else: word+="\\"+code[j]
     i+=1
    if code[i]=='"': c=0
    if c==0: break
    word+=code[i]
    i+=1
   if c!=0: return ("error","Unclosed string")
   res.append(("constant",'s'+word))
   word=""
  elif code[i]=='-':
   if i+1<len(code) and code[i+1].isdigit():
    i+=1
    while i<len(code):
     if not code[i].isdigit(): break
     word+=code[i]
     i+=1
    res.append(("constant",'n-'+word))
    word=""
  elif code[i].isdigit():
   while i<len(code):
    if not code[i].isdigit(): break
    word+=code[i]
    i+=1
   res.append(("constant",'n'+word))
   word=""
  elif code[i].isalpha() or code[i]=='_':
   while i<len(code):
    if not (code[i].isalnum() or code[i]=='_'): break
    word+=code[i]
    i+=1
   res.append(("name",word))
   word=""
  elif code[i]=='%':
   while i<len(code) and code[i]!='\n': i+=1
  if i<len(code):
   if code[i] in "+-*/:.=!": res.append(("operation",code[i]))
   elif code[i] in "<>":
    if i+1>=len(code) or code[i+1]!='=': res.append(("operation",code[i]))
    else: res.append(("operation",code[i]+'=')); i+=1
   elif code[i]==';': res.append(("eol",code[i]))
  i+=1
 return tuple(res)

stack=[]
udk={}
__repl=True
def run(tokens):
 global stack,udk,__repl
 if not isinstance(tokens,tuple): return ("error","`parse` function expected a tuple of string")
 if tokens[0]=="error": return tokens[1]
 builtinKeyword=("out","rout","dup","pop","exit")
 kwbod=[]
 afterKwDef=ifTrue=False
 a=b=""
 c=i=0
 while i<len(tokens):
  if tokens[i][0]=="constant":
   while i<len(tokens):
    if tokens[i][0]!="constant": break
    stack.append(tokens[i][1])
    i+=1
  if i<len(tokens):
   if tokens[i][0]=="name":
    if tokens[i][1]=="out":
     try: print(stack.pop()[1:],end="")
     except IndexError: return ("error","`out` keyword has no data to print")
    elif tokens[i][1]=="rout":
     try: print(stack.pop(0)[1:],end="")
     except IndexError: return ("error","`out` keyword has no data to print")
    elif tokens[i][1]=="dup":
     try: stack.append(stack[-1])
     except IndexError: return ("error","`dup` keyword has no data to copy")
    elif tokens[i][1]=="pop":
     try: stack.pop()
     except IndexError: return ("error","`pop` keyword has no data to pop")
    elif tokens[i][1]=="if":
     i+=1
     if i>len(tokens): return ("error","'if' expected statement(s)")
     while i<len(tokens):
      if tokens[i][0]=="operation" and tokens[i][1]=='.':
       if c>0: c-=1
       else: break
      if (tokens[i][0]=="operation" and tokens[i][1]==':') or (tokens[i][0]=="name" and tokens[i][1] in ["if","else"]): c+=1
      kwbod.append(tokens[i])
      i+=1
     kwbod.append(("eol",";"))
     a=stack.pop()
     if a=="n1":
      res=run(tuple(kwbod))
      if res[0]=="error": return res
      ifTrue=True
     elif a=="n0":
      kwbod=[]
      i+=1
      if i<len(tokens) and tokens[i][0]=="name" and tokens[i][1]=="else":
       i+=1
       if i>=len(tokens): return ("error","'else' expected statement(s)")
       while i<len(tokens):
        if tokens[i][0]=="operation" and tokens[i][1]=='.':
         if c>0: c-=1
         else: break
        if (tokens[i][0]=="operation" and tokens[i][1]==':') or (tokens[i][0]=="name" and tokens[i][1] in ["if","else"]): c+=1
        kwbod.append(tokens[i])
        i+=1
       kwbod.append(("eol",";"))
       if not ifTrue:
        res=run(tuple(kwbod))
        if res[0]=="error": return res
        else: return ("error","`if`,`else` expected a 1-bit binary value (0;1)")
     kwbod=[]
    elif tokens[i][1]=="exit":
     if __repl: __repl=False
    else:
     try: run(udk[tokens[i][1]])
     except KeyError: return ("error",f"`{tokens[i][1]}` not defined")
    i+=1
   elif tokens[i][0]=="operation":
    if tokens[i][1]=='+':
     if len(stack)<2: return ("error","'+' expected at least 2 numbers in stack")
     if stack[-1][0]!=stack[-2][0] and (stack[-1][0]!='n' or stack[-2][0]!='n'):
      return ("error","`+` expected parameters' type to be number")
     b=stack.pop(); a=stack.pop()
     stack.append('n'+str(int(a[1:])+int(b[1:])))
     a=b=""
    elif tokens[i][1]=='-':
     if len(stack)<2: return ("error","'-' expected at least 2 numbers in stack")
     if stack[-1][0]!=stack[-2][0] and (stack[-1][0]!='n' or stack[-2][0]!='n'):
      return ("error","`-` expected parameters' type to be number")
     b=stack.pop(); a=stack.pop()
     stack.append('n'+str(int(a[1:])-int(b[1:])))
     a=b=""
    elif tokens[i][1]=='*':
     if len(stack)<2: return ("error","'*' expected at least 2 numbers in stack")
     if stack[-1][0]!=stack[-2][0] and (stack[-1][0]!='n' or stack[-2][0]!='n'):
      return ("error","`*` expected parameters' type to be number")
     b=stack.pop(); a=stack.pop()
     stack.append('n'+str(int(a[1:])*int(b[1:])))
     a=b=""
    elif tokens[i][1]=='/':
     if len(stack)<2: return ("error","'/' expected at least 2 numbers in stack")
     if stack[-1][0]!=stack[-2][0] and (stack[-1][0]!='n' or stack[-2][0]!='n'):
      return ("error","`/` expected parameters' type to be number")
     b=stack.pop(); a=stack.pop()
     stack.append('n'+str(int(int(a[1:])/int(b[1:]))))
     a=b=""
    elif tokens[i][1]=='=':
     if len(stack)<2: return ("error","'=' expected at least 2 numbers in stack")
     if stack[-1][0]!=stack[-2][0] and (stack[-1][0]!='n' or stack[-2][0]!='n'):
      return ("error","`=` expected parameters' type to be number")
     b=stack.pop(); a=stack.pop()
     stack.append("n1" if int(a[1:])==int(b[1:]) else "n0")
     a=b=""
    elif tokens[i][1]=='!':
     if len(stack)<2: return ("error","'!' expected at least 2 numbers in stack")
     if stack[-1][0]!=stack[-2][0] and (stack[-1][0]!='n' or stack[-2][0]!='n'):
      return ("error","`!` expected parameters' type to be number")
     b=stack.pop(); a=stack.pop()
     stack.append("n1" if int(a[1:])!=int(b[1:]) else "n0")
     a=b=""
    elif tokens[i][1]=='<':
     if len(stack)<2: return ("error","'<' expected at least 2 numbers in stack")
     if stack[-1][0]!=stack[-2][0] and (stack[-1][0]!='n' or stack[-2][0]!='n'):
      return ("error","`<` expected parameters' type to be number")
     b=stack.pop(); a=stack.pop()
     stack.append("n1" if int(a[1:])<int(b[1:]) else "n0")
     a=b=""
    elif tokens[i][1]=='>':
     if len(stack)<2: return ("error","'>' expected at least 2 numbers in stack")
     if stack[-1][0]!=stack[-2][0] and (stack[-1][0]!='n' or stack[-2][0]!='n'):
      return ("error","`>` expected parameters' type to be number")
     b=stack.pop(); a=stack.pop()
     stack.append("n1" if int(a[1:])>int(b[1:]) else "n0")
     a=b=""
    elif tokens[i][1]=='<=':
     if len(stack)<2: return ("error","'<=' expected at least 2 numbers in stack")
     if stack[-1][0]!=stack[-2][0] and (stack[-1][0]!='n' or stack[-2][0]!='n'):
      return ("error","`<=` expected parameters' type to be number")
     b=stack.pop(); a=stack.pop()
     stack.append("n1" if int(a[1:])<=int(b[1:]) else "n0")
     a=b=""
    elif tokens[i][1]=='>=':
     if len(stack)<2: return ("error","'>=' expected at least 2 numbers in stack")
     if stack[-1][0]!=stack[-2][0] and (stack[-1][0]!='n' or stack[-2][0]!='n'):
      return ("error","`>=` expected parameters' type to be number")
     b=stack.pop(); a=stack.pop()
     stack.append("n1" if int(a[1:])>=int(b[1:]) else "n0")
     a=b=""
    elif tokens[i][1]==':':
     i+=1
     if i>len(tokens) or tokens[i][0]!="name": return ("error","':' expected a name")
     if tokens[i][1] in builtinKeyword: return ("error","':' didn't expect a pre-defined keyword")
     name=tokens[i][1]
     i+=1
     while i<len(tokens):
      if tokens[i][0]=="operation" and tokens[i][1]=='.':
       if c>0: c-=1
       else: break
      if (tokens[i][0]=="operation" and tokens[i][1]==':') or (tokens[i][0]=="name" and tokens[i][1] in ["if","else"]): c+=1
      kwbod.append(tokens[i])
      i+=1
     kwbod.append(("eol",";"))
     i-=1
     udk[name]=tuple(kwbod)
     name=""; kwbod=[]; afterKwDef=True
    i+=1
  if not afterKwDef:
   if i>=len(tokens) or tokens[i][0]!="eol":
    __repl=True
    return ("error","Expected a semicolon (;)")
  afterKwDef=False
  ifTrue=False
  i+=1
 return ("null","null")

def repl():
 while __repl:
  code=input("AUPL>")
  res=run(lex(code))
  if res[0]=="error": print("ERROR:",res[1])
 return

def main() -> None:
 if len(sys.argv)>1:
  __repl=False
  with open(sys.argv[1],"r") as fin:
   tokens=lex(fin.read())
   res=run(tokens)
   if res[0]=="error": print("ERROR:",res[1])
 else:
  repl()
 return

if __name__=="__main__":
 main()
