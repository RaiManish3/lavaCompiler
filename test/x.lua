class x
begin
    declare:: int f();
    function:: void main()
      begin
        int x = f();
        return;
      end

    function:: int f()
      begin
        print(3);
        int a = 1;
        return a;
      end
end
