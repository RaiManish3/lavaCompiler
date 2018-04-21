class Main
begin

  function::void main()
  begin

      int wflag = 0, tflag = 0;
      int dflag = 0;
--      char c;
    String c="d";

      if(c=="w" or c == "W")
      then	
          wflag = 1;
      else
          if(c=="t" or c=="T")
          then
              tflag=1;
          else
              if(c=="d")
              then
                  dflag=1;
              end
          end
      end
      print(wflag);
      print(tflag);
      print(dflag);
    return;
  end

end
