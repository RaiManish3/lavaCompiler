class x
begin
    declare:: int f(String x, int m);
    function:: void main()
      begin
        real a;
        int x = f("hello", 5);
        return;
      end

--     function:: int f()
--       begin
--         print(3);
--         int a = 1;
--         return a;
--       end
end
