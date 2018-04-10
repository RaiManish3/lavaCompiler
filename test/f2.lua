class x
begin
    declare::int f(String x);
    function::void main()
    begin
        int x = f("hello");
        print(x);
        return;
    end

    function:: int f(String x)
    begin
        print(x);
        return 3;
    end
end
