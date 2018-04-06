class x
begin
    declare:: int f(String x, int m);
    function:: void main()
      begin
        int a = 3, b =7, t = 1;
        while(a <= 10)
        begin
          t = t * b;
          a = a - 1;
          print(t);
        end
        return;
      end

--     function:: int f()
--       begin
--         print(3);
--         int a = 1;
--         return a;
--       end
end
