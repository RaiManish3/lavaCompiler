class Main
begin
    function:: void main()
    begin
        real a = 2;
        real b = 5 * 4;
        print(b);
        if (b < 20.0)
        then
          a = 5*b;
        else
          a = 1.2;
        end
        print(a);
        return;
    end
end
