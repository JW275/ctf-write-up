# HITCON 2018 children_tcache
> pwn, heap, tcache

## 설명
같은 대회 문제인 baby_tcache 다음으로 나온 문제다. 하지만 CTF특징인 baby, easy 같은 단어가 붙으면 더 어려워 진다는 점을 증명하듯 baby보다 children이 더 쉽다.
(heap 내용을 print해주는 메뉴가 존재하여 leak이 가능하다.)
다만, 두 문제에서 입력해준 문자열을 heap에 저장하는 방식이 조금 다르고 이에 따라 특징이 조금 다르므로 유의해야한다.

## 취약점
새로운 heap을 할당하는 과정에서 입력해준 size만큼 읽은 뒤 이를 strcpy를 이용하여 복사한다.
strcpy는 복사할때 맨 뒤에 null byte를 붙여주는데 malloc할때 size+1이 아닌 size가 들어가므로 null byte를 한개 오버플로 시킬 수 있다. (off by one)

## Exploit
baby와 다르게 leak이 가능하다는 장점을 이용해야하는데 문제는 우리가 입력해준 문자열을 strcpy를 이용하여 복사해준다는 문제가 있다.
이는 결국 끝에 null byte가 붙어버려 uninitialize 되어있다 하여도 안에 들어있던 값을 읽어내지 못하게 된다는 문제점이다.
이 때문에 우선 leak 없이 취약점을 한 번 공격해야한다.

poison null byte기법을 이용하는데 정석적인 방법으로는 익스플로잇이 불가능하다.
heap chunk를 삭제하는 루틴에서 삭제할 heap을 0xDA로 덮어버리기 때문에 fake prev size를 만들어 주는 것이 불가능하다.

하지만 poison null byte의 목적은 free되지 않은 heap chunk를 무시하고 top chunk로 덮어버리기 위함인데 이 부분에서 중요한 것은 top chunk 직전의 heap chunk의 prev in use bit가 0이며 prev size가 정상적이지 않은 값이여야 한다.
해당 조건을 맞추기 위해 정석적인 방법으로는 특정 청크를 free시켜 prev size를 세팅 시켜준뒤 off by one을 통해 청크의 크기를 줄여 나중에 이 청크를 이용하더라도 prev size와 다음 청크의 prev in use에 영향을 주지 못하게 한다.
하지만 크기를 줄이고 적절한 위치에 fake prev size가 존재하지 않으면 libc에서 invalid한 chunk로 판단하고 프로그램이 죽게된다.

하지만 poison null byte의 조건을 off by one을 이용하여 다른 방식으로 맞춰줄 수 있다.
`chunk A | chunk B | chunk C | top chunk` 와 같은식으로 heap에 할당시킨다. 이때 C의 size는 00으로 끝나게 만든다.
또한, B는 tcache에 들어갈 수 있도록 해야한다. 나중에 A와 B 둘 다 free를 한번 씩 시킬건데 A와 B 둘 다 tcache가 아닌 unsorted bin에 들어갈 경우 두 청크가 합쳐지게된다.
위와 같이 할당해주면 C의 size부분은 0xX01과 같이 되어있을 것이다. 이때 B의 off by one을 이용하여 C의 prev in use를 0으로 덮어 버리고 prev size를 A + B의 크기로 세팅해준다.
그 뒤 C를 해제하면 prev in use 플래그를 보고 앞 청크와 합치려할 것이고, prev size를 보고 B가 해제되지 않았음에도 A까지 top chunk로 합쳐진다.

poison null byte를 이용하여 dup chunk를 만들고 한쪽을 unsorted bin으로 만들어 libc주소를 알아낼 수 있다.
그리고 tcache에서 꺼내올때는 size가 valid한지 체크하지 않고, tcache는 double free를 체크하지 않기때문에 이후에는 쉽게 exploit이 가능하다.
