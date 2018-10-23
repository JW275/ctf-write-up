# HITCON 2018 baby_tcache
> pwn, heap, tcache

## 설명
heap내용을 출력해주는 메뉴가 존재하지 않아 leak이 불가능하기 때문에, blind로 exploit해야한다.
이 때문에 쓸만한 포인터를 잘 찾아내는 것이 중요하다.
exploit은 children_tcache의 연장선이며, 이 때문에 poison null byte의 트리거 방법은 여기에 적지 않는다.

## 취약점
children_tcache와 마찬가지로 off by one 취약점이 발생한다.
조금 다른점이라면 문자열을 할당받은 heap에 `read()`글 통해 직접 받아내기 때문에 뒤에 무조건적으로 null byte가 붙진 않는다.
null byte는 무조건 `heap[size]`에 들어간다.

## Exploit
우선 children_tcache에서 한 것처럼 poison null byte를 이용하여 dup chunk를 만들어낸다.
그 후 인접한 chunk(최대한 인접해야 brute forcing의 확률을 높일 수 있다. 주소가 1 byte이상 차이가 나게되면 heap의 주소도 확률적으로 맞춰야하기 때문에 확률이 줄어든다.)를 unsorted bin으로 만들어 libc의 주소(main_arena의 주소)를 만들어 준다.
그 후 dup chunk를 두 번 free시킨 뒤 fd를 libc주소 들어가 있는 chunk를 가르키게 만들면 libc leak이 없더라도 libc에 값을 쓸 수 있게 된다.

이제 libc 안에서 어떤 값을 변조해야 PC를 control할 수 있는지 삽질해야한다. 원래 `__malloc_hook`이나 `__free_hook`을 덮는것이 일반적이지만 기본적으로 null로 초기화 되어있기 때문에 leak없이는 힘들다.
내가 사용한 방법은 `_morecore`라는 함수포인터를 덮는 것이었다. 이 함수는 top chunk의 크기보다 malloc에서 요청한 크기가 더 클 경우 사용된다.(단, 크기가 너무 크면 다른 함수가 사용됨.)

이를 위해 `_morecore`를 one gadget(magic gadget)으로 덮고 top chunk를 다 소모시키면 트리거 된다.
`main_arena`와 `_morecore`의 주소는 2byte 차이, `_morecore`와 one gadget의 주소는 3byte 차이가 나지만 memory page의 특성상 하위 1.5 byte는 확정적으로 맞출 수 있기 때문에 사실상 1.5 byte brute forcing이 된다.(1/4096)

