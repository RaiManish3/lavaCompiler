class Main
begin
  function :: void main()
  begin
      int i=6;
      for(;i<= 8 and i>= 6 and i~= 7; i=i+1)
      begin
          if(i<=0)
          then 
              print("yes\n");
          else
              print("no\n");
          end
      end
      return;
  end
end
