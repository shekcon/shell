
# Subshell


### [x] $ *(printenv HOME) (leu leu) && echo shekcon*
  > bash$
  ```
  bash: syntax error near unexpected token `('
  ```
  > intek-sh$
  ~~~
  intek-sh: syntax error near unexpected token `('
  ~~~
### [x] $ *(echo world || echo haha*
  > bash$
  ```
  bash: syntax error
  ```
  > intek-sh$
  ~~~
  intek-sh: parse token error "("
  ~~~
### [x] $ *(echo world) || echo haha*
  > bash$
  ```
  world
  ```
  > intek-sh$
  ~~~
  world
  ~~~

### [x] $ *echo (hello world hehe || echo haha*
  > bash$
  ```
  bash: syntax error near unexpected token \`hello'
  ```
  > intek-sh$
  ~~~
  intek-sh: parse token error "("
  ~~~ 
### [x] $ *echo hello world) hehe || echo haha*
  > bash$
  ```
  bash: syntax error near unexpected token `)'
  ```
  > intek-sh$
  ```
  intek-sh: syntax error near unexpected token `)'
  ```

### [x] $ *echo (hello world) hehe*
  > bash
  ```
  bash: syntax error near unexpected token `hello'
  ```
  > intek-sh$
  ~~~
  intek-sh: syntax error near unexpected token `('
  ~~~
### [x] $ *cd .. && pwd && (cd .. && pwd && export LOGNAME=shekcon && printenv LOGNAME) && pwd && printenv LOGNAME*
  > bash
  ```
  /home/shekcon
  /home
  shekcon
  /home/shekcon
  shekcon
  ```
  > intek-sh$
  ~~~
  /home/shekcon
  /home
  shekcon
  /home/shekcon
  shekcon
  ~~~


### [x] $ *(export HOME=INTEK LSANG=shekcon && printenv HOME && printenv LSANG ) && printenv HOME && printenv LSANG*
  > bash$
  ```
  INTEK
  shekcon
  /home/shekcon
  ```
  > intek-sh$
  ~~~
  INTEK
  shekcon
  /home/shekcon
  ~~~

# Syntax shell

### [x] $ *echo haha || echo \`"\` haha*
  > bash$
  ```
  haha
  ```
  > intek-sh$
  ~~~
  haha
  ~~~

### [x] $ *echo haha && echo \`"`*
  > bash$
  ```
  haha
  bash: command substitution: systax error \`"'

  ```
  > intek-sh$
  ~~~
  haha
  intek-sh: parse token error `"'

  ~~~

### [x] $ *echo haha && echo \`"` hehe*
  > bash$
  ```
  haha
  bash: command substitution: systax error \`"'
  hehe
  ```
  > intek-sh$
  ~~~
  haha
  intek-sh: parse token error `"'
  hehe
  ~~~

### [x] $ *(echo haha && echo \`"` hehe) && echo haha*
  > bash$
  ```
  haha
  bash: command substitution: systax error \`"'
  hehe
  haha
  ```
  > intek-sh$
  ~~~
  haha
  intek-sh: parse token error """
  hehe
  haha
  ~~~

### Test case
shekcon@Intek:~$ echo && | echo a
bash: syntax error near unexpected token `|'
shekcon@Intek:~$ echo && || echo a
bash: syntax error near unexpected token `||'
shekcon@Intek:~$ echo | && echo a
bash: syntax error near unexpected token `&&'
shekcon@Intek:~$ && echo haha
bash: syntax error near unexpected token `&&'
shekcon@Intek:~$ | echo haha
bash: syntax error near unexpected token `|'
shekcon@Intek:~$ || echo haha
bash: syntax error near unexpected token `||'
shekcon@Intek:~$ echo > lsang && || haha
bash: syntax error near unexpected token `||'
shekcon@Intek:~$ echo > lsang < && haha
bash: syntax error near unexpected token `&&'
shekcon@Intek:~$ echo > lsang < > && haha
bash: syntax error near unexpected token `>'
shekcon@Intek:~$ echo > lsang < > haha && haha
bash: syntax error near unexpected token `>'
shekcon@Intek:~$ echo > lsang < > haha && haha <
bash: syntax error near unexpected token `>'
shekcon@Intek:~$ < echo > lsang && echo haha
bash: echo: No such file or directory
shekcon@Intek:~$ < echo > lsang > && echo haha
bash: syntax error near unexpected token `&&'
shekcon@Intek:~$ echo "hello world" >> haha < ls.txt && echo `hello world` ||
> echo haha >>lsang.txt | grep a
bash: ls.txt: No such file or directory
shekcon@Intek:~$ cd De
Deployment/ Desktop/    
shekcon@Intek:~$ cd Deployment/Test/
shekcon@Intek:~/Deployment/Test$ echo "hello world" >> haha < ls.txt && echo `hello world` || echo haha >>lsang.txt | grep a

Command 'hello' not found, but can be installed with:

sudo apt install hello            
sudo apt install hello-traditional


shekcon@Intek:~/Deployment/Test$ echo "hello world" && echo `hdawd world` || echo haha
hello world
hdawd: command not found

shekcon@Intek:~/Deployment/Test$ < haha echo >
bash: syntax error near unexpected token `newline'
shekcon@Intek:~/Deployment/Test$ 
shekcon@Intek:~/Deployment/Test$ < haha echo >
bash: syntax error near unexpected token `newline'
shekcon@Intek:~/Deployment/Test$ < haha echo > ||
bash: syntax error near unexpected token `||'
shekcon@Intek:~/Deployment/Test$ < haha echo > dawd |
> |
bash: syntax error near unexpected token `|'
ls > ls.out | grep a | grep b
ls -la >> ls.out
< ls.in ls > ls.out | grep a || echo haha
< ls.in ls > ls.out | grep a && echo haha
< ls.in ls > ls.out | grep ls < ls.out
< file > new ls | grep a
<file >new ls | grep a
echo ${dawdaw } || echo haha
bash: ${dawdaw }: bad substitution
< ls > haha | grep a