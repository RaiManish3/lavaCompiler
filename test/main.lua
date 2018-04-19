class Main
begin

    declare :: int foo();

    function :: void main()
      begin
        int a,b,c,d,e;
        a=2;
        b=3;
        c=1;
        d=0;
        e=10;

        -- case 1
        a = b + c - d / e * b % 10;
        print(a);
        
        -- case 2
        if (c ~= 0)
          then
            if (d ~= 0)
              then
                d = d + 1;
              else
                d = d - 1;
              end
          end
        print(d);

        -- case 3
        for(int i =0; i<100;)
        begin
            i = i + 1;
            a = a + 1;
        end
        print(a);

        -- case 4
        a = foo();
        print(a);

        -- case 5
        if (c ~=0 and d ~= 0)
          then
            d = d + 1;
          else 
            if ( (d & e) ~= 0)
              then
                e = e + 1;
              else
                d = d - 1;
              end
          end
          print(d);
          print(e);

        return;
      end

    function:: int foo()
      begin
        --print("hello");
        return 31;
      end

end
