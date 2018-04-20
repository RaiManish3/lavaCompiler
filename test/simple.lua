class Main
begin
    function::void main()
      begin
        real x[][] = {{1.0, 2.0, 3.0},{4.0, 5.0, 6.0}};
        x[1][2] = 12;
        for(int i=0; i<2; i = i +1)
        begin
          for(int j=0; j<3; j = j +1)
          begin
            print(x[i][j]);
          end
        end
        return;
      end
end
