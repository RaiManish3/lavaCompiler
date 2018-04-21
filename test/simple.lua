class XYZ
begin
    int ss=24;
    String s1="yko";
    String s2="yjo";
    String h="hello";
    String y="xo";

    function XYZ(int x)
    begin
        print(x);
    end

    function XYZ(String x,int j)
    begin
        print(x);
        print(j);
    end

    function::void foo()
    begin
        print("Yo I'm in foor");
        return;

    end
    function XYZ()
    begin
    end
end
class Main
begin
    int x = 2;
    String y = "hello";
    boolean z = false;
    function ::void foo(String x, int y)
    begin
        print(x);
        print(y);
        return;
    end
    function::void main()
      begin
        foo("hello",3);
        XYZ mz=new XYZ(4);
        XYZ nz=new XYZ("hello2",11);
        XYZ tz=new XYZ();
        if(tz.s1~=tz.s2)
            then
            print("Not Equal");
            else
            print("Equal");
        end
        --String s3=s1+s2;
        --print(s3);
        return;
        String j=tz.y+tz.y;
        int n;
        int m = (n = 3);
        return;
      end
end
