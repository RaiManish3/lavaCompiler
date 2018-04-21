class Main 
begin

  function :: void main()
  begin
      int i = 0,a[] = {1,2,3};
      if(i<=3)
      then
          a[i]=a[i]+1;
      end

      if(i>=2)
      then
          a[i]=a[i]-1;
      else
          a[i]=a[i]+2;
      end
      print(a[0]);
      return;
  end

end
