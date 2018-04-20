class Main
begin
    int x = 2;
    String y = "hello";
    boolean z = false;
    function::void main()
      begin
        real x[][] = {{1.0, 2.0, 3.0},{4.0, 5.0, 6.0}};
        int y[][] = {{1, 2, 3},{4, 5, 6}};
        x[1][2] = 12;
        for(int i=0; i<2; i = i +1)
        begin
          for(int j=0; j<3; j = j +1)
          begin
            print(y[i][j]);
          end
        end
        int n;
        int m = (n = 3);
        print(this.x);
        print(this.y);
        print(this.z);
        return;
      end
end
