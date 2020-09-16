/*
 *  CAnalyzer test
 *
 *  Copyright (c) Honda Research Institute Europe GmbH
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions are
 *  met:
 *
 *  1. Redistributions of source code must retain the above copyright notice,
 *     this list of conditions and the following disclaimer.
 *
 *  2. Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *  3. Neither the name of the copyright holder nor the names of its
 *     contributors may be used to endorse or promote products derived from
 *     this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 *  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 *  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 *  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 *  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 *  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 *  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 *  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 *  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 *  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 *  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */


int var1 = 10;

int foo(int);

int foo(int x)
{
    return x + 1;
}

float bar(float x, int);

float bar(float);

float bar(float x, int y) { return 0.0; }

float bar(float baz) { return 1.0; }

float bar(float moo);

typedef float myfloat;


float bar(myfloat myparam);

void variadicfn(int firstparam, ...) { }

typedef const int * intptr;

#define MYMACRO extern "C" {

#define MYMACROFN(__x, __y) (__x + __y)

enum MyEnum {
    Value1, Value2, Value3
};

template<typename T, int X>
T adder(T y) {
    return X + T(y);
}

template<class T1, class T2>
T1 coerce(T2 param) {
    return T1(param);
}

struct MyStruct {
    void print(char *);
private:
    int foo;
    template<int N> int fooplussomething() { return N + foo; }
public:
    float bar;
    int getFoo() { return foo; }
protected:
    bool baz;
    MyStruct(int);
    bool isBaz() { return baz; }
public:
    MyStruct(int x, float y): MyStruct(x) {
        bar = y;
    }

    template<typename T> T coerceFoo() { return T(foo); }
};



MyStruct::MyStruct(int x) {
    foo = x;
}

void MyStruct::print(char *message) {}

struct MyStruct;


namespace ns1 {
    float foo;

    struct mystruct {};

    class myclass {};

    union myunion {};

    enum myenum { MyValue1, MyValue2 };

    typedef int mytypedef;

    void myfunction(int x) {}

    template<typename T>
    void mytemplatefunction(T x) {}

    template<typename T>
    class mytemplateclass {};

    namespace ns2 {
        float foo;

        struct mystruct {};

        class myclass {};

        union myunion {};

        enum myenum { MyValue1, MyValue2 };

        typedef int mytypedef;

        void myfunction(int x) {}

        template<typename T>
        void mytemplatefunction(T x) {}

        template<typename T>
        class mytemplateclass {};

        void ns2fn();
    }

    void ns2::ns2fn() {}
}
