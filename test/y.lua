class x
begin
    function:: void main()
    begin
        real a = 1;
        real b = 5 * 4;
        if (b  < 20.0 or b >= 20.0)
        then
          a = 5*b;
        else
          a = 1.2;
        end
        print(a);
        return;
    end
end
