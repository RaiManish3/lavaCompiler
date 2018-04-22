class Main
begin
    declare::int f(int x);
    declare::real g(real x);
    function::void main()
    begin
        int x = f(1);
        real y = g(1.0);
        print(x);
        print(y);
        return;
    end

    function:: int f(int x)
    begin
        print(x);
        return 3*12+1;
    end

    function:: real g(real x)
    begin
        print(x);
        return 3 * 12 + 1.0;
    end
end
