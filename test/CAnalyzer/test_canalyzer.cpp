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
