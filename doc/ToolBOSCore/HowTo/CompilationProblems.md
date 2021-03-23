###  Compilation problems

Enable very strict compilation settings in your CMakeLists.txt :

    add_definitions(-Wextra)
    
####  Utilities:
      
Check predefined macros and their values:

    $ gcc -E -dM - < /dev/null
    #define __DBL_MIN_EXP__ (-1021)
    #define __UINT_LEAST16_MAX__ 65535
    #define __FLT_MIN__ 1.17549435082228750797e-38F
    #define __UINT_LEAST8_TYPE__ unsigned char
    #define __INTMAX_C(c) c ## L
    #define __CHAR_BIT__ 8
    #define __UINT8_MAX__ 255
    #define __WINT_MAX__ 4294967295U
    #define __ORDER_LITTLE_ENDIAN__ 1234
    #define __SIZE_MAX__ 18446744073709551615UL
    [...]
    
Show from where a certain symbol is coming (e.g. "printf"):

    $ gcc -Wl,-y,printf main.c
    /tmp/ccehkm0g.o: reference to printf
    /lib/x86_64-linux-gnu/libc.so.6: definition of printf
    
Trace which files the linker is considering: 

    $ gcc -Wl,-t main.c
    /usr/bin/ld: mode elf_x86_64
    /usr/lib/gcc/x86_64-linux-gnu/4.6/../../../x86_64-linux-gnu/crt1.o
    /usr/lib/gcc/x86_64-linux-gnu/4.6/../../../x86_64-linux-gnu/crti.o
    /usr/lib/gcc/x86_64-linux-gnu/4.6/crtbegin.o
    /tmp/ccYCg1bh.o
    -lgcc_s (/usr/lib/gcc/x86_64-linux-gnu/4.6/libgcc_s.so)
    /lib/x86_64-linux-gnu/libc.so.6
    (/usr/lib/x86_64-linux-gnu/libc_nonshared.a)elf-init.oS
    /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
    -lgcc_s (/usr/lib/gcc/x86_64-linux-gnu/4.6/libgcc_s.so)
    /usr/lib/gcc/x86_64-linux-gnu/4.6/crtend.o
    /usr/lib/gcc/x86_64-linux-gnu/4.6/../../../x86_64-linux-gnu/crtn.o